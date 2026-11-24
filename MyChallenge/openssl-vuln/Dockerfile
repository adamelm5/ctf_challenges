FROM debian:jessie
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx openssl python3 ca-certificates && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -newkey rsa:2048 -days 3650 \
      -keyout /etc/nginx/ssl/server.key -out /etc/nginx/ssl/server.crt \
      -subj "/CN=hospital.local"
COPY nginx.conf /etc/nginx/nginx.conf
COPY backend.py /opt/backend.py
COPY start.sh /start.sh
RUN chmod +x /start.sh
EXPOSE 8443
CMD ["/start.sh"]
