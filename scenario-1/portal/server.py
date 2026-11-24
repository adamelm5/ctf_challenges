#!/usr/bin/env python3
import http.server
import socketserver
import base64
import subprocess
import urllib.parse
import binascii

AES_KEY = bytes.fromhex("00112233445566778899aabbccddeeff")
AES_IV  = bytes.fromhex("0102030405060708090a0b0c0d0e0f10")
PLAINTEXT_TOKEN = b"medecin_7f3a9c"

KEY_HEX = binascii.hexlify(AES_KEY).decode()
IV_HEX  = binascii.hexlify(AES_IV).decode()

def aes_cbc_encrypt(plaintext):
    p = subprocess.Popen(
        ["openssl", "enc", "-aes-128-cbc", "-K", KEY_HEX, "-iv", IV_HEX],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, _ = p.communicate(input=plaintext)
    if p.returncode != 0:
        raise ValueError("echec chiffrement")
    return stdout

def aes_cbc_decrypt(ciphertext):
    p = subprocess.Popen(
        ["openssl", "enc", "-d", "-aes-128-cbc", "-K", KEY_HEX, "-iv", IV_HEX],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, _ = p.communicate(input=ciphertext)
    if p.returncode != 0:
        raise ValueError("padding invalide")
    return stdout

ENCRYPTED_COOKIE = aes_cbc_encrypt(PLAINTEXT_TOKEN)

class PortalHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            with open("/app/index.html", "rb") as f:
                self.wfile.write(f.read())
        elif self.path == "/login":
            cookie_b64 = base64.b64encode(ENCRYPTED_COOKIE).decode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Set-Cookie", "session=" + cookie_b64 + "; Path=/")
            self.end_headers()
            self.wfile.write(("Cookie de session : " + cookie_b64 + "\n").encode())
        elif self.path.startswith("/check"):
            if "?" in self.path:
                query = self.path.split("?", 1)[1]
            else:
                query = ""
            params = {}
            for q in query.split("&"):
                if "=" in q:
                    k, v = q.split("=", 1)
                    params[urllib.parse.unquote(k)] = urllib.parse.unquote(v)
            cookie_b64 = params.get("cookie", "")
            try:
                ciphertext = base64.b64decode(cookie_b64)
                aes_cbc_decrypt(ciphertext)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK\n")
            except Exception:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Invalid padding\n")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    PORT = 80
    httpd = socketserver.TCPServer(("0.0.0.0", PORT), PortalHandler)
    print("Portail en ecoute sur le port " + str(PORT))
    httpd.serve_forever()
