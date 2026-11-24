FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 iproute2 && \
    rm -rf /var/lib/apt/lists/*
COPY sip_ua.py /sip_ua.py
CMD ["python3", "-u", "/sip_ua.py"]
