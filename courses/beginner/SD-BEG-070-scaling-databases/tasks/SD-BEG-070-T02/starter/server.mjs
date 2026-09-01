import http from "node:http";

// Learner starter: deliberately incomplete. Define one normalization and
// ownership function, build two mysql2 pools, and make both POST and GET use
// that same boundary before executing SQL. Prove placement with @@server_id
// and direct wrong-shard queries.

const port = Number(process.env.API_PORT ?? 58072);

async function handle(_request, response) {
  response.writeHead(501, { "content-type": "application/json" });
  response.end(JSON.stringify({
    error: "not_implemented",
    next: "Write the a/m/n/z boundary prediction in ATTEMPT.md before coding."
  }));
}

const server = http.createServer((request, response) => {
  handle(request, response).catch((error) => {
    response.writeHead(500, { "content-type": "application/json" });
    response.end(JSON.stringify({ error: error.message }));
  });
});

server.listen(port, "127.0.0.1", () => {
  console.log(`Learner starter listening on http://127.0.0.1:${port}`);
});
