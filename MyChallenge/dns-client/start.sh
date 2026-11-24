#!/bin/bash
ulimit -c unlimited
exec /usr/sbin/sshd -D
