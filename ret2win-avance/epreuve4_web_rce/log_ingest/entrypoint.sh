#!/bin/bash
# Firewall : bloque tout trafic sortant TCP non local,
# autorise le DNS sortant (UDP/53) vers l'attaquant uniquement.
set -e
ATTACKER_IP="10.0.20.50"
iptables -F OUTPUT
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A OUTPUT -p udp --dport 53 -d "$ATTACKER_IP" -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -p tcp -j REJECT
iptables -A OUTPUT -p udp -j REJECT
exec su appuser -c "java -jar /app/log-ingest.jar"
