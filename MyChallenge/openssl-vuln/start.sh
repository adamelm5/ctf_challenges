#!/bin/bash
HOST="${HOST_IP:-127.0.0.1}"
printf "HOSPITAL NETWORK - Maintenance access\nSSH: ssh netops@%s -p 2223\nPassword: N3T-7QX-29\n" "$HOST" \
  | openssl enc -e -aes-128-cbc -K 30313233343536373839616263646566 \
    -iv 66656463626139383736353433323130 -out /opt/cookie.bin
python3 /opt/backend.py &
nginx -g "daemon off;"
