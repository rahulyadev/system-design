import http from "node:http";
import mysql from "mysql2/promise";

const integer = (name, fallback) => {
  const value = Number(process.env[name] ?? fallback);
  if (!Number.isInteger(value) || value <= 0) {
    throw new Error(`${name} must be a positive integer`);
  }
  return value;
};

const apiPort = integer("API_PORT", 58071);
const database = process.env.DB_NAME ?? "sd_beg_070_t01";
const user = process.env.DB_USER ?? "app";
const password = process.env.DB_PASSWORD ?? "sd_beg_070_t01_app_local";

const poolOptions = (port) => ({
  host: "127.0.0.1",
  port,
  user,
  password,
  database,
  waitForConnections: true,
  connectionLimit: 4,
  maxIdle: 4,
  idleTimeout: 30_000,
  enableKeepAlive: true
});

const primaryPool = mysql.createPool(poolOptions(integer("SOURCE_PORT", 55701)));
const replicaPool = mysql.createPool(poolOptions(integer("REPLICA_PORT", 55702)));

const send = (response, status, body) => {
  response.writeHead(status, { "content-type": "application/json" });
  response.end(JSON.stringify(body));
};

const readJson = async (request) => {
  let body = "";
  for await (const chunk of request) {
    body += chunk;
    if (body.length > 32_768) {
      throw new Error("request body too large");
    }
  }
  return JSON.parse(body || "{}");
};

const serverIdentity = async (pool) => {
  const [rows] = await pool.query("SELECT @@server_id AS server_id");
  return Number(rows[0].server_id);
};

const selectItem = async (pool, id) => {
  const [rows] = await pool.execute(
    "SELECT id, name FROM items WHERE id = ?",
    [id]
  );
  return rows[0] ?? null;
};

const handle = async (request, response) => {
  const url = new URL(request.url, `http://${request.headers.host ?? "127.0.0.1"}`);

  if (request.method === "GET" && url.pathname === "/health") {
    send(response, 200, {
      status: "ok",
      primary_server_id: await serverIdentity(primaryPool),
      replica_server_id: await serverIdentity(replicaPool)
    });
    return;
  }

  if (request.method === "POST" && url.pathname === "/items") {
    const body = await readJson(request);
    if (!Number.isInteger(body.id) || body.id <= 0) {
      send(response, 422, { error: "id must be a positive integer" });
      return;
    }
    if (typeof body.name !== "string" || body.name.length < 1 || body.name.length > 120) {
      send(response, 422, { error: "name must contain 1-120 characters" });
      return;
    }
    await primaryPool.execute(
      "INSERT INTO items(id, name) VALUES (?, ?) ON DUPLICATE KEY UPDATE name = VALUES(name)",
      [body.id, body.name]
    );
    send(response, 201, {
      id: body.id,
      name: body.name,
      served_by: "primary",
      server_id: await serverIdentity(primaryPool)
    });
    return;
  }

  const match = request.method === "GET" && url.pathname.match(/^\/items\/(\d+)$/);
  if (match) {
    const id = Number(match[1]);
    const consistency = url.searchParams.get("consistency") ?? "eventual";
    if (!new Set(["eventual", "strong"]).has(consistency)) {
      send(response, 422, { error: "consistency must be eventual or strong" });
      return;
    }
    const pool = consistency === "strong" ? primaryPool : replicaPool;
    const servedBy = consistency === "strong" ? "primary" : "replica";
    const item = await selectItem(pool, id);
    const identity = await serverIdentity(pool);
    if (!item) {
      send(response, 404, { error: "not_found", served_by: servedBy, server_id: identity });
      return;
    }
    send(response, 200, { ...item, served_by: servedBy, server_id: identity });
    return;
  }

  send(response, 404, { error: "route_not_found" });
};

const server = http.createServer((request, response) => {
  handle(request, response).catch((error) => {
    send(response, 500, { error: error.message });
  });
});

await Promise.all([serverIdentity(primaryPool), serverIdentity(replicaPool)]);
server.listen(apiPort, "127.0.0.1", () => {
  console.log(`REFERENCE_API_READY port=${apiPort}`);
});

const shutdown = async () => {
  server.close();
  await Promise.all([primaryPool.end(), replicaPool.end()]);
};

process.on("SIGTERM", () => shutdown().finally(() => process.exit(0)));
process.on("SIGINT", () => shutdown().finally(() => process.exit(0)));
