from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "max-age=60")
        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):

        if self.path == "/":
            self.send_json({
                "backend": "A",
                "status": "running"
            })

        elif self.path == "/api/status":
            self.send_json({
                "backend": "A",
                "status": "ok"
            })

        else:
            self.send_json({
                "error": "Not Found"
            }, 404)

    def log_message(self, format, *args):
        print(format % args)


server = HTTPServer(("0.0.0.0", 3001), Handler)

print("Backend A running on port 3001")

server.serve_forever()
