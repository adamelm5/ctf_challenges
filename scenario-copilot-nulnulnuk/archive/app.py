import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


INTERNAL_TOKEN = os.environ.get("CTF_INTERNAL_TOKEN", "local-dev-token-change-me")
FLAG_PATH = Path(os.environ.get("CTF_FLAG_FILE", "/archive-data/flag"))


class Handler(BaseHTTPRequestHandler):
    def _reply(self, status: int, payload: dict[str, str]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._reply(200, {"status": "ok"})
        elif self.path == "/diagnostics":
            self._reply(
                200,
                {
                    "mode": "simulation",
                    "evidence": (
                        "Revue simulée : log4j-core 2.14.1 est mentionné dans "
                        "l’inventaire; la résolution JNDI est désactivée. "
                        "Seul un identifiant inerte est journalisé; aucun "
                        "mécanisme de recherche ni code externe n’est exécuté."
                    ),
                },
            )
        elif self.path == "/internal/flag":
            provided = self.headers.get("X-CTF-Internal-Token", "")
            if not hmac.compare_digest(provided, INTERNAL_TOKEN):
                self._reply(403, {"error": "Forbidden"})
                return
            try:
                flag = FLAG_PATH.read_text(encoding="utf-8").strip()
            except OSError:
                self._reply(503, {"error": "Archive data unavailable"})
                return
            if not flag:
                self._reply(503, {"error": "Archive data is empty"})
                return
            self._reply(200, {"principal": "archive", "flag": flag})
        else:
            self._reply(404, {"error": "Not found"})

    def log_message(self, format: str, *args: object) -> None:
        super().log_message(format, *args)


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8093), Handler)
    server.daemon_threads = True
    server.serve_forever()


if __name__ == "__main__":
    main()
