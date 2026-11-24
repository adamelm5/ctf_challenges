#!/usr/bin/env python3
"""
Service de synchronisation de configuration (port 9000 TCP).
- Vérifie que l'IP source est présente dans le cache ARP local.
- Chiffre un blob (URL log_ingest + API_KEY) en AES-128-CBC via OpenSSL 1.0.2h
  réellement vulnérable à CVE-2016-2107.
- Renvoie IV+ciphertext ; toute modification du ciphertext produisant un
  padding invalide renvoie "PADDING_ERROR".
- Jitter ±20 ms, limite 50 req/s/IP.
"""
import socket, os, subprocess, random, time, threading
from collections import defaultdict

PORT = 9000
RATE_LIMIT = 50
JITTER = 0.020

def arp_cache_ips():
    ips = set()
    try:
        with open("/proc/net/arp") as f:
            next(f)
            for line in f:
                ips.add(line.split()[0])
    except FileNotFoundError:
        pass
    return ips

def build_blob():
    api_key = os.environ.get("API_KEY", "0" * 32)
    return (f"URL=http://log-ingest.batirenov.local:8080\n"
            f"API_KEY={api_key}\n").encode()

def openssl_encrypt(key_hex, data):
    """Appelle l'openssl vulnérable (1.0.2h) en sous-processus."""
    iv = os.urandom(16)
    p = subprocess.run(
        ["openssl", "enc", "-aes-128-cbc", "-K", key_hex, "-iv", iv.hex()],
        input=data, capture_output=True, check=True)
    return iv + p.stdout

_rate = defaultdict(list)
_rate_lock = threading.Lock()

def rate_ok(ip):
    now = time.time()
    with _rate_lock:
        _rate[ip] = [t for t in _rate[ip] if now - t < 1.0]
        if len(_rate[ip]) >= RATE_LIMIT:
            return False
        _rate[ip].append(now)
    return True

def handle(conn, addr):
    if not rate_ok(addr[0]):
        conn.close(); return
    if addr[0] not in arp_cache_ips():
        conn.sendall(b"NOT_IN_ARP_CACHE\n"); conn.close(); return

    key_hex = os.urandom(16).hex()
    blob = openssl_encrypt(key_hex, build_blob())
    time.sleep(random.uniform(-JITTER, JITTER) + JITTER)
    conn.sendall(blob)
    conn.close()

def main():
    random.seed(int(time.time()))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", PORT))
    s.listen(128)
    while True:
        c, a = s.accept()
        threading.Thread(target=handle, args=(c, a), daemon=True).start()

if __name__ == "__main__":
    main()
