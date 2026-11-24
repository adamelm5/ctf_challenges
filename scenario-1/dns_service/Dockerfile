FROM gcc:4.9

RUN echo "deb [trusted=yes check-valid-until=no] http://archive.debian.org/debian jessie main" > /etc/apt/sources.list
RUN echo "Acquire::Check-Valid-Until \"false\";" > /etc/apt/apt.conf.d/99no-check-valid-until
RUN echo "Acquire::AllowInsecureRepositories \"true\";" > /etc/apt/apt.conf.d/99allow-insecure

RUN apt-get update && apt-get install -y --no-install-recommends wget libc6-dev && rm -rf /var/lib/apt/lists/*

# Retrograder libc6 vers la version vulnerable (avant le correctif deb8u3)
RUN wget -q http://archive.debian.org/debian/pool/main/g/glibc/libc6_2.19-18+deb8u2_amd64.deb -O /tmp/libc6.deb && \
    dpkg -i --force-downgrade /tmp/libc6.deb && \
    rm /tmp/libc6.deb

WORKDIR /app
COPY resolver.c /app/resolver.c
RUN gcc -o resolver resolver.c

EXPOSE 8053
CMD ["./resolver"]
