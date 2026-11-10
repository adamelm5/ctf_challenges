import hashlib
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

FLAG = "ENSEIRB{G3s11ght_1s_R34l!Puppet_Master}"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        hostname = socket.gethostname()
        expected_token = hashlib.sha256(hostname.encode()).hexdigest()
        client_token = self.headers.get("X-Analyst-Token")
        
        if self.path == "/flag" and client_token == expected_token:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(FLAG.encode())
        else:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Access Denied. Invalid Token.")

if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8080), Handler).serve_forever()
