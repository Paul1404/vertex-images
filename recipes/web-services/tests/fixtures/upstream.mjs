import { createServer } from 'node:http';

createServer((request, response) => {
  if (request.url === '/railway-health.php') {
    response.writeHead(200, { 'content-type': 'text/plain', 'cache-control': 'no-store' });
    response.end('ok');
    return;
  }
  response.writeHead(200, { 'content-type': 'application/json' });
  response.end(JSON.stringify({
    path: request.url,
    host: request.headers.host,
    protocol: request.headers['x-forwarded-proto'],
  }));
}).listen(9000, '0.0.0.0');
