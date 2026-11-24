FROM python:3.11-slim@sha256:673719e071ecf27434fd2635bbd8d00f49f4fdd81f243143438a42ced8bedf60

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY --chown=10001:10001 app.py index.html app.js style.css /app/
USER 10001:10001
EXPOSE 8080
CMD ["python", "/app/app.py"]
