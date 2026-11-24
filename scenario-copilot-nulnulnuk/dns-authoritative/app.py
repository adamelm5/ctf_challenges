import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def _reply(self, status: int, payload: dict[str, str]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._reply(200, {"status": "ok"})
        elif self.path == "/records/archive.hospital.test":
            self._reply(
                200,
                {
                    "name": "archive.hospital.test",
                    "address": "192.0.2.44",
                    "mode": "simulated-record",
                },
            )
        else:
            self._reply(404, {"error": "Not found"})

    def log_message(self, format: str, *args: object) -> None:
        super().log_message(format, *args)


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8092), Handler)
    server.daemon_threads = True
    server.serve_forever()


if __name__ == "__main__":
    main()
