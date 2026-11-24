#!/usr/bin/env python3
"""
Outil fourni (pas une solution) : écouteur DNS passif.
Capture les requêtes de résolution que provoque un payload JNDI/Log4Shell
en mode blind/OOB (log_ingest ne peut sortir qu'en DNS UDP/53 vers ce
conteneur). N'effectue aucune attaque : il journalise simplement les noms
de domaine interrogés.

Usage : sudo python3 dns_listener.py [--port 53]
"""
import socket
import struct
import argparse
import datetime


def parse_qname(data, offset):
    labels = []
    while True:
        length = data[offset]
        if length == 0:
            offset += 1
            break
        offset += 1
        labels.append(data[offset:offset + length].decode(errors="replace"))
        offset += length
    return ".".join(labels), offset


def handle_query(data, addr):
    try:
        qname, next_off = parse_qname(data, 12)
        qtype = struct.unpack("!H", data[next_off:next_off + 2])[0]
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] requete DNS de {addr[0]}:{addr[1]} -> {qname} (type={qtype})")
    except Exception as e:
        print(f"[!] paquet DNS non parse: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=53)
    args = ap.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", args.port))
    print(f"[dns_listener] en ecoute sur UDP/{args.port}...")
    while True:
        data, addr = sock.recvfrom(4096)
        handle_query(data, addr)


if __name__ == "__main__":
    main()
