import http from "node:http";

// Learner starter: deliberately incomplete. Build two mysql2 connection pools,
// route mutations and consistency-sensitive reads to the primary, and route
// eligible eventual reads to the replica. Keep target selection in one small
// function and include the queried @@server_id in evidence.

const port = Number(process.env.API_PORT ?? 58071);

async function handle(_request, response) {
  response.writeHead(501, { "content-type": "application/json" });
  response.end(JSON.stringify({
    error: "not_implemented",
    next: "Write your prediction in ATTEMPT.md, then implement the routing boundary."
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
