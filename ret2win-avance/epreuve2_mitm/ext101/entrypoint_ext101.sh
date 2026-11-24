#!/bin/bash
# Démarre sip_ua, arp_guard et config_sync en parallèle.
set -e
python3 /opt/arp_guard.py &
python3 /opt/config_sync.py &
exec python3 -u /opt/sip_ua.py
