#!/bin/bash
# Routeur passerelle entre pbx_net_a et pbx_net_b.
set -e

# Fixe les MAC par interface (compose v3 ne le permet pas directement)
ip link set dev eth0 address 02:42:aa:bb:cc:10 || true  # côté A
ip link set dev eth1 address 02:42:aa:bb:cc:20 || true  # côté B

# Active le forwarding IPv4
sysctl -w net.ipv4.ip_forward=1

# Forward simple entre les deux interfaces
iptables -F FORWARD
iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT
iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT

tail -f /dev/null
