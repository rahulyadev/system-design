import http from "node:http";
import mysql from "mysql2/promise";

const integer = (name, fallback) => {
  const value = Number(process.env[name] ?? fallback);
  if (!Number.isInteger(value) || value <= 0) {
    throw new Error(`${name} must be a positive integer`);
  }
  return value;
};

const apiPort = integer("API_PORT", 58072);
const database = process.env.DB_NAME ?? "sd_beg_070_t02";
const user = process.env.DB_USER ?? "app";
const password = process.env.DB_PASSWORD ?? "sd_beg_070_t02_app_local";

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

const shardAmPool = mysql.createPool(poolOptions(integer("SHARD_AM_PORT", 55711)));
const shardNzPool = mysql.createPool(poolOptions(integer("SHARD_NZ_PORT", 55712)));

const normalizeKey = (rawKey) => {
  if (typeof rawKey !== "string") {
    throw new TypeError("key must be a string");
  }
  const key = rawKey.toLowerCase();
  if (!/^[a-z][a-z0-9_-]{0,63}$/.test(key)) {
    throw new RangeError("key must match ^[a-z][a-z0-9_-]{0,63}$");
  }
  return key;
};

const ownerForKey = (rawKey) => {
  const key = normalizeKey(rawKey);
  const shard = key[0] <= "m" ? "am" : "nz";
  return {
    key,
    shard,
    pool: shard === "am" ? shardAmPool : shardNzPool
  };
};

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

const handle = async (request, response) => {
  const url = new URL(request.url, `http://${request.headers.host ?? "127.0.0.1"}`);

  if (request.method === "GET" && url.pathname === "/health") {
    send(response, 200, {
      status: "ok",
      shard_am_server_id: await serverIdentity(shardAmPool),
      shard_nz_server_id: await serverIdentity(shardNzPool)
    });
    return;
  }

  if (request.method === "POST" && url.pathname === "/records") {
    const body = await readJson(request);
    if (typeof body.value !== "string" || body.value.length < 1 || body.value.length > 200) {
      send(response, 422, { error: "value must contain 1-200 characters" });
      return;
    }
    let owner;
    try {
      owner = ownerForKey(body.key);
    } catch (error) {
      send(response, 422, { error: error.message });
      return;
    }
    await owner.pool.execute(
      "INSERT INTO records(key_name, value_text) VALUES (?, ?) " +
        "ON DUPLICATE KEY UPDATE value_text = VALUES(value_text)",
      [owner.key, body.value]
    );
    send(response, 201, {
      key: owner.key,
      value: body.value,
      shard: owner.shard,
      server_id: await serverIdentity(owner.pool)
    });
    return;
  }

  const match = request.method === "GET" && url.pathname.match(/^\/records\/([^/]+)$/);
  if (match) {
    let owner;
    try {
      owner = ownerForKey(decodeURIComponent(match[1]));
    } catch (error) {
      send(response, 422, { error: error.message });
      return;
    }
    const [rows] = await owner.pool.execute(
      "SELECT key_name, value_text FROM records WHERE key_name = ?",
      [owner.key]
    );
    const identity = await serverIdentity(owner.pool);
    if (!rows[0]) {
      send(response, 404, { error: "not_found", shard: owner.shard, server_id: identity });
      return;
    }
    send(response, 200, {
      key: rows[0].key_name,
      value: rows[0].value_text,
      shard: owner.shard,
      server_id: identity
    });
    return;
  }

  send(response, 404, { error: "route_not_found" });
};

const server = http.createServer((request, response) => {
  handle(request, response).catch((error) => send(response, 500, { error: error.message }));
});

await Promise.all([serverIdentity(shardAmPool), serverIdentity(shardNzPool)]);
server.listen(apiPort, "127.0.0.1", () => {
  console.log(`REFERENCE_API_READY port=${apiPort}`);
});

const shutdown = async () => {
  server.close();
  await Promise.all([shardAmPool.end(), shardNzPool.end()]);
};

process.on("SIGTERM", () => shutdown().finally(() => process.exit(0)));
process.on("SIGINT", () => shutdown().finally(() => process.exit(0)));
