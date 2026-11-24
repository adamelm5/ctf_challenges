# ---------------------------------------------------------------------
# Stage 1 : compilation d'OpenSSL 1.0.2h (CVE-2016-2107, volontairement
# vulnérable) depuis l'archive officielle du projet OpenSSL sur GitHub.
# ---------------------------------------------------------------------
FROM ubuntu:22.04 AS openssl-build

RUN apt-get update && apt-get install -y \
      build-essential perl wget ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
RUN wget -q https://github.com/openssl/openssl/releases/download/OpenSSL_1_0_2h/openssl-1.0.2h.tar.gz \
    && tar xzf openssl-1.0.2h.tar.gz

WORKDIR /build/openssl-1.0.2h
RUN ./config --prefix=/opt/openssl-1.0.2h --openssldir=/opt/openssl-1.0.2h/ssl shared \
    && make depend \
    && make -j"$(nproc)" \
    && make install_sw

# ---------------------------------------------------------------------
# Stage 2 : image finale ext101
# ---------------------------------------------------------------------
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
      python3 python3-pip iproute2 ebtables \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install scapy

# OpenSSL 1.0.2h compilé au stage précédent (réellement vulnérable à
# CVE-2016-2107, car construit sans aucun correctif ultérieur).
COPY --from=openssl-build /opt/openssl-1.0.2h/ /opt/openssl-1.0.2h/
ENV LD_LIBRARY_PATH=/opt/openssl-1.0.2h/lib
ENV PATH=/opt/openssl-1.0.2h/bin:$PATH

COPY sip_ua.py arp_guard.py config_sync.py entrypoint_ext101.sh /opt/
RUN chmod +x /opt/*.py /opt/entrypoint_ext101.sh

ENV FLAG_SRC="ENSEIRB{placeholder_flag}"
ENTRYPOINT ["/opt/entrypoint_ext101.sh"]
