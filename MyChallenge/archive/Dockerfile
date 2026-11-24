FROM ghcr.io/christophetd/log4shell-vulnerable-app:latest

# Création manuelle de l'utilisateur archive (uid 1000, sans useradd)
RUN echo "archive:x:1000:1000::/home/archive:/bin/sh" >> /etc/passwd && \
    echo "archive:x:1000:" >> /etc/group && \
    mkdir -p /home/archive && \
    chown -R 1000:1000 /home/archive /app

USER 1000:1000
