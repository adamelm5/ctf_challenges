#!/usr/bin/env bash
# Génère une clé API partagée au démarrage du challenge (32 hex aléatoires).
# Elle est lue par config_sync.py ET log_ingest au démarrage, via .env.
set -e
ENV_FILE="$(dirname "$0")/.env"
if [ ! -f "$ENV_FILE" ]; then
  API_KEY=$(openssl rand -hex 16)
  echo "API_KEY=${API_KEY}" > "$ENV_FILE"
  echo "[init_env] Clé API générée dans $ENV_FILE"
else
  echo "[init_env] $ENV_FILE existe déjà, conservé."
fi
