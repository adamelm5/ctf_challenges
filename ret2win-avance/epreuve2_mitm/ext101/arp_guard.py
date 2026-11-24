#!/usr/bin/env python3
"""
Watchdog ARP (non documenté dans la note d'incident).
- Vérifie UNIQUEMENT l'OUI (3 premiers octets) des paquets ARP prétendant
  représenter l'IP du routeur côté pbx_net_b (10.0.20.1).
- OUI attendu = "02:42:aa". Si OUI ≠, ebtables drop 60s + syslog UDP.
- Si OUI correct mais MAC différent du vrai : PAS de blocage (brèche volontaire).
- Détection reconnaissance (>15 who-has vers IP distinctes en <3s) : syslog seul.
"""
import time, subprocess, socket
from collections import deque
from scapy.all import sniff, ARP

ROUTER_IP_B   = "10.0.20.1"
EXPECTED_OUI  = "02:42:aa"
SYSLOG_SRV    = ("10.0.20.50", 514)  # attaquant en syslog UDP

def syslog(msg):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(f"<134>arp_guard {msg}".encode(), SYSLOG_SRV)
    except Exception:
        pass

def block_for_60s(mac):
    try:
        subprocess.run(["ebtables", "-A", "INPUT", "-s", mac, "-j", "DROP"],
                       check=False, capture_output=True)
        time.sleep(60)
        subprocess.run(["ebtables", "-D", "INPUT", "-s", mac, "-j", "DROP"],
                       check=False, capture_output=True)
    except FileNotFoundError:
        pass

who_has_window = deque()

def handle_pkt(pkt):
    if not pkt.haslayer(ARP):
        return
    arp = pkt[ARP]

    if arp.op == 1:  # who-has
        now = time.time()
        who_has_window.append((now, arp.pdst))
        while who_has_window and now - who_has_window[0][0] > 3.0:
            who_has_window.popleft()
        distinct = {ip for _, ip in who_has_window}
        if len(distinct) > 15:
            syslog(f"ARP reconnaissance suspected: {len(distinct)} distinct targets in <3s")

    if arp.psrc == ROUTER_IP_B or arp.pdst == ROUTER_IP_B:
        mac = arp.hwsrc if arp.psrc == ROUTER_IP_B else arp.hwdst
        if not mac:
            return
        oui = ":".join(mac.split(":")[:3]).lower()
        if oui != EXPECTED_OUI:
            syslog(f"ARP binding violation: IP={ROUTER_IP_B} claimed by MAC={mac}, "
                   f"expected OUI={EXPECTED_OUI}, rejected")
            block_for_60s(mac)

def main():
    sniff(filter="arp", prn=handle_pkt, store=False)

if __name__ == "__main__":
    main()
