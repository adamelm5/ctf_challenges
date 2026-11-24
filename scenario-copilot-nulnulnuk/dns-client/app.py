import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import URLError
from urllib.request import urlopen


AUTHORITY_URL = os.environ.get(
    "DNS_AUTHORITY_URL", "http://dns-authoritative:8092"
)


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
            return
        if self.path != "/report":
            self._reply(404, {"error": "Not found"})
            return
        try:
            with urlopen(
                AUTHORITY_URL + "/records/archive.hospital.test", timeout=3
            ) as response:
                record = json.loads(response.read(2048))
        except (URLError, TimeoutError, OSError, json.JSONDecodeError):
            self._reply(503, {"error": "DNS simulation service unavailable"})
            return
        if record.get("mode") != "simulated-record":
            self._reply(502, {"error": "Invalid simulated DNS record"})
            return
        self._reply(
            200,
            {
                "evidence": (
                    "Audit simulé : libc6 2.19-18+deb8u10 (amd64) est indiquée; "
                    "le resolver est dynamique et NSS suit files puis dns. "
                    "La fiche de paquet est corrigée; aucune résolution DNS "
                    "réelle ni aucun crash n’est exécuté."
                ),
                "resolved_name": record["name"],
                "resolved_address": record["address"],
                "mode": "simulation",
            },
        )

    def log_message(self, format: str, *args: object) -> None:
        super().log_message(format, *args)


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8091), Handler)
    server.daemon_threads = True
    server.serve_forever()


if __name__ == "__main__":
    main()
