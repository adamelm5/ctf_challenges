#!/usr/bin/env python3
import base64
import urllib.request
import urllib.parse
import urllib.error

BASE = "http://localhost:8080"
IV = bytes.fromhex("0102030405060708090a0b0c0d0e0f10")

def oracle(cookie_bytes):
    b64 = base64.b64encode(cookie_bytes).decode()
    url = BASE + "/check?cookie=" + urllib.parse.quote(b64)
    try:
        with urllib.request.urlopen(url) as r:
            return r.status == 200
    except urllib.error.HTTPError as e:
        return e.code == 200

def get_cookie():
    with urllib.request.urlopen(BASE + "/login") as r:
        body = r.read().decode()
    b64 = body.strip().split(" : ")[-1]
    return base64.b64decode(b64)

def decrypt_block(prev_block, block):
    plain_dict = {}
    for pos in range(15, -1, -1):
        pad_val = 16 - pos
        found = None
        for guess in range(256):
            modified = bytearray(prev_block)
            for k in range(pos + 1, 16):
                modified[k] = prev_block[k] ^ plain_dict[k] ^ pad_val
            modified[pos] = prev_block[pos] ^ guess
            if oracle(bytes(modified) + block):
                if pad_val == 1:
                    modified2 = bytearray(modified)
                    modified2[14] ^= 0x01
                    if not oracle(bytes(modified2) + block):
                        continue
                found = guess
                break
        if found is None:
            raise RuntimeError("pas de guess valide pour pos " + str(pos))
        plain_dict[pos] = found ^ pad_val
    return bytes([plain_dict[i] for i in range(16)])

def main():
    ct = get_cookie()
    print("Cookie chiffre :", base64.b64encode(ct).decode())
    blocks = [IV] + [ct[i:i+16] for i in range(0, len(ct), 16)]
    plain = b""
    for i in range(1, len(blocks)):
        plain += decrypt_block(blocks[i-1], blocks[i])
    pad_len = plain[-1]
    if 1 <= pad_len <= 16:
        plain = plain[:-pad_len]
    print("Plaintext :", plain.decode("utf-8", errors="replace"))

if __name__ == "__main__":
    main()
