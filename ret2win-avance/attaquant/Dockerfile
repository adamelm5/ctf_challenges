# Conteneur attaquant unique, utilisé pour les 4 épreuves.
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
      openssh-server gcc gdb python3 python3-pip nano binutils \
      net-tools iproute2 tcpdump nmap arp-scan tshark \
      iptables iputils-ping dnsutils openssl \
    && rm -rf /var/lib/apt/lists/*

# Outils pwn (épreuve 1) + scapy (épreuve 2) + crypto (épreuve 3) + web (épreuve 4)
RUN pip3 install pwntools ROPgadget scapy pycryptodome requests

RUN mkdir /var/run/sshd && ssh-keygen -A
RUN useradd -m -s /bin/bash analyste && \
    echo "analyste:ENSEIRB2026" | chpasswd
RUN echo "AllowUsers analyste" >> /etc/ssh/sshd_config

# Binaire vulnérable fourni à l'analyste (épreuve 1) — recompilé sur place
COPY epreuve1_pwn/files/vuln_dns_server.c /home/analyste/
COPY epreuve1_pwn/files/note_incident.txt /home/analyste/
RUN gcc -fstack-protector-all -pie -fPIE \
      -o /home/analyste/vuln_dns_server /home/analyste/vuln_dns_server.c \
    && rm /home/analyste/vuln_dns_server.c

# Écouteur DNS d'exfiltration Log4Shell (outil fourni, pas une solution)
COPY epreuve4_web_rce/solution/dns_listener.py /home/analyste/tools/dns_listener.py

RUN chown -R analyste:analyste /home/analyste
WORKDIR /home/analyste
EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
