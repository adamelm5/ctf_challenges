import hashlib
import hmac
import os
import re
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from http.cookies import CookieError, SimpleCookie
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CONTROLLER_URL = os.environ.get("CONTROLLER_URL", "http://ctf-controller:8080")
PORTAL_TOKEN = os.environ.get("CTF_INTERNAL_TOKEN", "local-dev-token-change-me")
WEB_ROOT = Path(__file__).parent
SESSION_PATTERN = re.compile(r"([0-9a-f]{32})\.([0-9a-f]{64})")


class Handler(BaseHTTPRequestHandler):
    server_version = "HospitalCTFPortal/1.0"

    def _ensure_session(self) -> None:
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get("Cookie", ""))
        except CookieError:
            cookie = SimpleCookie()
        morsel = cookie.get("ctf_session")
        match = SESSION_PATTERN.fullmatch(morsel.value) if morsel else None
        if match:
            session_id, signature = match.groups()
            expected = hmac.new(
                PORTAL_TOKEN.encode(),
                session_id.encode(),
                hashlib.sha256,
            ).hexdigest()
            if hmac.compare_digest(signature, expected):
                self.session_id = session_id
                return
        self.session_id = secrets.token_hex(16)
        signature = hmac.new(
            PORTAL_TOKEN.encode(),
            self.session_id.encode(),
            hashlib.sha256,
        ).hexdigest()
        self.new_cookie = (
            "ctf_session={}.{}; Path=/; HttpOnly; SameSite=Strict; Max-Age=86400"
        ).format(self.session_id, signature)

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; object-src 'none'; base-uri 'none'; "
            "frame-ancestors 'none'",
        )
        if hasattr(self, "new_cookie"):
            self.send_header("Set-Cookie", self.new_cookie)
        self.end_headers()
        self.wfile.write(body)

    def _proxy(self) -> None:
        body = None
        if self.command == "POST":
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send(400, "application/json", b'{"error":"Invalid request"}')
                return
            if length < 1 or length > 1024:
                self._send(400, "application/json", b'{"error":"Invalid request"}')
                return
            body = self.rfile.read(length)
        request = Request(
            CONTROLLER_URL + self.path,
            data=body,
            headers={
                "X-Portal-Token": PORTAL_TOKEN,
                "X-CTF-Session": self.session_id,
                "Content-Type": self.headers.get("Content-Type", "application/json"),
            },
            method=self.command,
        )
        try:
            response = urlopen(request, timeout=4)
        except HTTPError as error:
            response = error
        except (URLError, TimeoutError, OSError):
            self._send(502, "application/json", b'{"error":"Controller unavailable"}')
            return
        with response:
            self._send(
                response.status,
                response.headers.get("Content-Type", "application/json"),
                response.read(8192),
            )

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._send(200, "application/json", b'{"status":"ok"}')
        elif self.path.startswith("/api/"):
            self._ensure_session()
            self._proxy()
        elif self.path == "/":
            self._ensure_session()
            self._send(
                200,
                "text/html; charset=utf-8",
                (WEB_ROOT / "index.html").read_bytes(),
            )
        elif self.path == "/app.js":
            self._send(
                200,
                "text/javascript; charset=utf-8",
                (WEB_ROOT / "app.js").read_bytes(),
            )
        elif self.path == "/style.css":
            self._send(
                200,
                "text/css; charset=utf-8",
                (WEB_ROOT / "style.css").read_bytes(),
            )
        else:
            self._send(404, "text/plain; charset=utf-8", b"Not found")

    def do_POST(self) -> None:
        if self.path.startswith("/api/"):
            self._ensure_session()
            self._proxy()
        else:
            self._send(404, "text/plain; charset=utf-8", b"Not found")

    def log_message(self, format: str, *args: object) -> None:
        super().log_message(format, *args)


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    server.daemon_threads = True
    server.serve_forever()


if __name__ == "__main__":
    main()
