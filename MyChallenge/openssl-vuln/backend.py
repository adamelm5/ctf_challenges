import http.server, base64, subprocess, os, urllib.parse
KEY = "30313233343536373839616263646566"
IV  = "66656463626139383736353433323130"

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == "/":
            with open("/opt/cookie.bin", "rb") as f:
                cookie = base64.b64encode(f.read()).decode()
            body = b"<html><body><h1>Espace personnel</h1><p>Session active.</p></body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Set-Cookie", "session=" + cookie + "; Path=/")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif p.path == "/api/check":
            data = urllib.parse.parse_qs(p.query).get("data", [""])[0]
            try:
                ct = base64.b64decode(data)
                if len(ct) == 0 or len(ct) % 16 != 0:
                    return self._r(403)
                proc = subprocess.Popen(
                    ["openssl", "enc", "-d", "-aes-128-cbc", "-K", KEY, "-iv", IV],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                proc.communicate(ct)
                self._r(200 if proc.returncode == 0 else 403)
            except Exception:
                self._r(400)
        else:
            self._r(404)
    def _r(self, code):
        self.send_response(code); self.send_header("Content-Length", "0"); self.end_headers()
    def log_message(self, *a): pass

http.server.HTTPServer(("127.0.0.1", 5000), H).serve_forever()
