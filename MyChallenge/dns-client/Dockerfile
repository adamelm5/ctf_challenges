FROM debian:stretch
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server gcc libc6-dev curl vim net-tools && rm -rf /var/lib/apt/lists/*
COPY dns-check.c /tmp/dns-check.c
RUN gcc -o /usr/local/bin/dns-check /tmp/dns-check.c && rm /tmp/dns-check.c
COPY sshd_config /etc/ssh/sshd_config
COPY start.sh /start.sh
RUN chmod +x /start.sh && \
    useradd -m -s /bin/bash netops && echo "netops:N3T-7QX-29" | chpasswd && \
    mkdir -p /var/run/sshd
EXPOSE 22
CMD ["/start.sh"]
