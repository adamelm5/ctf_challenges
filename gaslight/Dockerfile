FROM ubuntu:22.04
RUN apt-get update && apt-get install -y openssh-server python3 python3-pip binutils nano less && rm -rf /var/lib/apt/lists/*
RUN pip3 install requests
RUN mkdir /var/run/sshd && ssh-keygen -A
RUN useradd -m -s /bin/bash analyste && echo "analyste:ENSEIRB2026" | chpasswd
RUN echo "AllowUsers analyste" >> /etc/ssh/sshd_config

COPY files/ /home/analyste/
RUN chown -R analyste:analyste /home/analyste

# Lancement du serveur local en arrière-plan, puis SSH au premier plan
CMD python3 /home/analyste/server.py & /usr/sbin/sshd -D
