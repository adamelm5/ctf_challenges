FROM debian:jessie

ENV DEBIAN_FRONTEND=noninteractive

RUN echo "deb [trusted=yes] http://archive.debian.org/debian jessie main" > /etc/apt/sources.list
RUN echo "deb [trusted=yes] http://archive.debian.org/debian-security jessie/updates main" >> /etc/apt/sources.list
RUN echo "Acquire::Check-Valid-Until \"false\";" > /etc/apt/apt.conf.d/99no-check-valid-until

RUN apt-get update && apt-get install -y --no-install-recommends python3 openssl && rm -rf /var/lib/apt/lists/*

RUN openssl version | grep -q "1.0.1" || (echo "ERREUR: OpenSSL nest pas en 1.0.1" && exit 1)

WORKDIR /app
COPY server.py /app/server.py
COPY index.html /app/index.html

EXPOSE 80
CMD ["python3", "/app/server.py"]
