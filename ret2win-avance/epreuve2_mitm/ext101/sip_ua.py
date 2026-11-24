#!/usr/bin/env python3
"""
UA SIP ext101 (10.0.20.101) : répond aux INVITE/REGISTER d'ext100,
émet un flux RTP PCMU + DTMF RFC 2833.
Le flag est découpé en 10 fragments base32 au démarrage (seed = heure courante).
Un fragment par appel, encadré par DTMF '#' (début) et '*' (fin), avec bourrage.
Tous les 5 appels : signal 'config-sync-ready' (DTMF 0 répété).
"""
import socket, struct, random, time, base64, os, threading

SIP_PORT = 5060

def split_flag():
    flag = os.environ.get("FLAG_SRC", "ENSEIRB{placeholder_flag}")
    chunks = [flag[i::10] for i in range(10)]
    return [base64.b32encode(c.encode()).decode().rstrip("=") for c in chunks]

FRAGMENTS = split_flag()

def rtp_header(seq, ts, ssrc, pt=0):
    return struct.pack("!BBHII", 0x80, pt, seq & 0xffff, ts & 0xffffffff, ssrc)

def dtmf_packet(seq, ts, ssrc, event, volume=10, duration=160):
    """RFC 2833 : event_id(1) | flags E/R + volume(1) | duration(2 BE)."""
    flags = ((1 if duration >= 160 else 0) << 7) | (volume & 0x3f)
    payload = struct.pack("!BBH", event, flags, duration)
    return rtp_header(seq, ts, ssrc, pt=101) + payload

def send_dtmf(sock, dst, ssrc, digits, start_seq=0):
    seq, ts = start_seq, 0
    for d in digits:
        for _ in range(3):
            sock.sendto(dtmf_packet(seq, ts, ssrc, d), dst)
            seq += 1; ts += 160
        pcmu = rtp_header(seq, ts, ssrc, pt=0) + b"\xff" * 160
        sock.sendto(pcmu, dst)
        seq += 1; ts += 160
    return seq

def pick_fragment(call_idx):
    if call_idx % 5 == 0:
        return [0, 0, 0]
    frag = FRAGMENTS[call_idx % 10]
    padding_left  = [random.randint(0, 9) for _ in range(random.randint(1, 4))]
    padding_right = [random.randint(0, 9) for _ in range(random.randint(1, 4))]
    body = [ord(c) % 10 for c in frag]
    return padding_left + [11] + body + [10] + padding_right

def main():
    seed = int(time.time())
    random.seed(seed)
    print(f"[ext101] seed={seed}, fragments={FRAGMENTS}")

    sip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sip.bind(("0.0.0.0", SIP_PORT))
    sip.settimeout(5.0)

    call_idx = 0
    while True:
        try:
            data, addr = sip.recvfrom(4096)
        except socket.timeout:
            continue
        if data.startswith(b"REGISTER"):
            sip.sendto(b"SIP/2.0 200 OK\r\nContent-Length: 0\r\n\r\n", addr)
        elif data.startswith(b"INVITE"):
            sip.sendto(b"SIP/2.0 200 OK\r\nContent-Length: 0\r\n\r\n", addr)
            call_idx += 1
            dst = ("10.0.10.100", 20000)
            ssrc = random.getrandbits(32)
            digits = pick_fragment(call_idx)
            print(f"[ext101] call #{call_idx} -> DTMF {digits}")
            threading.Thread(target=send_dtmf, args=(sip, dst, ssrc, digits),
                             daemon=True).start()

if __name__ == "__main__":
    main()
