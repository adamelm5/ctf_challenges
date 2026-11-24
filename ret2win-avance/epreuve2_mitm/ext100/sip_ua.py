#!/usr/bin/env python3
"""
UA SIP minimal pour ext100 (10.0.10.100).
- S'enregistre auprès d'une registrar fictive auto-validée.
- Envoie périodiquement un INVITE vers ext101 via le routeur.
- Chaque SDP propose un port RTP audio aléatoire.
Aucune bibliothèque SIP externe : sockets UDP brutes.
"""
import socket, random, time, hashlib

EXT101_IP = "10.0.20.101"
SIP_PORT  = 5060
REGISTRAR = "10.0.10.1"     # routeur fait office de proxy/registrar fictif

def build_register(nonce=b"", cnonce=b"", user="ext100"):
    auth = ""
    if nonce:
        ha1 = hashlib.md5(f"{user}:batirenov:{cnonce.hex()}".encode()).hexdigest()
        ha2 = hashlib.md5(b"REGISTER:sip:batirenov.local").hexdigest()
        resp = hashlib.md5(f"{ha1}:{nonce.hex()}:{ha2}".encode()).hexdigest()
        auth = (f'Authorization: Digest username="{user}", '
                f'realm="batirenov", nonce="{nonce.hex()}", '
                f'response="{resp}", cnonce="{cnonce.hex()}"\r\n')
    return (
        f"REGISTER sip:batirenov.local SIP/2.0\r\n"
        f"From: <sip:{user}@batirenov.local>;tag={random.getrandbits(32):08x}\r\n"
        f"To: <sip:{user}@batirenov.local>\r\n"
        f"Call-ID: {random.getrandbits(64):016x}@ext100\r\n"
        f"CSeq: 1 REGISTER\r\n"
        f"Contact: <sip:{user}@10.0.10.100:5060>\r\n"
        f"{auth}"
        f"Content-Length: 0\r\n\r\n"
    ).encode()

def build_invite(call_id, rtp_port):
    sdp = (
        "v=0\r\n"
        f"o=ext100 0 0 IN IP4 10.0.10.100\r\n"
        "s=BatiRenov call\r\n"
        "c=IN IP4 10.0.10.100\r\n"
        "t=0 0\r\n"
        f"m=audio {rtp_port} RTP/AVP 0 101\r\n"
        "a=rtpmap:0 PCMU/8000\r\n"
        "a=rtpmap:101 telephone-event/8000\r\n"
        "a=fmtp:101 0-16\r\n"
    )
    return (
        f"INVITE sip:ext101@{EXT101_IP} SIP/2.0\r\n"
        f"Via: SIP/2.0/UDP 10.0.10.100:5060;branch=z9hG4bK{random.getrandbits(32):08x}\r\n"
        f"From: <sip:ext100@batirenov.local>;tag={random.getrandbits(32):08x}\r\n"
        f"To: <sip:ext101@{EXT101_IP}>\r\n"
        f"Call-ID: {call_id}\r\n"
        "CSeq: 1 INVITE\r\n"
        "Contact: <sip:ext100@10.0.10.100:5060>\r\n"
        "Content-Type: application/sdp\r\n"
        f"Content-Length: {len(sdp)}\r\n\r\n{sdp}"
    ).encode()

def main():
    seed = int(time.time())
    random.seed(seed)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", SIP_PORT))
    sock.settimeout(2.0)

    call_id_counter = 0
    while True:
        sock.sendto(build_register(), (REGISTRAR, SIP_PORT))
        try:
            sock.recvfrom(4096)
        except socket.timeout:
            pass

        call_id_counter += 1
        rtp_port = random.randint(16384, 32767)
        call_id = f"{random.getrandbits(64):016x}@ext100"
        print(f"[ext100] INVITE #{call_id_counter} -> ext101 (RTP {rtp_port})")
        sock.sendto(build_invite(call_id, rtp_port), (EXT101_IP, SIP_PORT))

        time.sleep(random.randint(60, 90))

if __name__ == "__main__":
    main()
