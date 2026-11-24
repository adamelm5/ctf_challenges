FROM maven:3.8-eclipse-temurin-11 AS build
WORKDIR /src
COPY pom.xml .
COPY src ./src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:11-jre
RUN apt-get update && apt-get install -y iptables && rm -rf /var/lib/apt/lists/*
RUN useradd -m -s /bin/bash appuser
COPY --from=build /src/target/log-ingest-*.jar /app/log-ingest.jar
COPY flag.txt /flag.txt
RUN chown appuser:appuser /flag.txt && chmod 400 /flag.txt
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
USER root
ENTRYPOINT ["/entrypoint.sh"]
