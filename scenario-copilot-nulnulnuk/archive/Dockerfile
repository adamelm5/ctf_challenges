FROM python:3.11-slim@sha256:673719e071ecf27434fd2635bbd8d00f49f4fdd81f243143438a42ced8bedf60

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN groupadd --system --gid 10004 archive \
    && useradd --system --uid 10004 --gid archive --no-create-home --shell /usr/sbin/nologin archive
WORKDIR /app
COPY --chown=10004:10004 app.py /app/app.py
USER 10004:10004
EXPOSE 8093
CMD ["python", "/app/app.py"]
