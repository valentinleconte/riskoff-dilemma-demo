#!/usr/bin/env bash
# Start JupyterLab for sharing. Binds to 127.0.0.1 only; the tunnel (below) exposes it
# publicly. A strong token is required for every connection.
set -euo pipefail
TOKEN="${JUPYTER_TOKEN:-$(python3 -c 'import secrets;print(secrets.token_urlsafe(32))')}"
echo "JupyterLab token: $TOKEN   (share this privately with your collaborator)"
jupyter lab --no-browser --ip=127.0.0.1 --port=8888 \
  --ServerApp.token="$TOKEN" --ServerApp.allow_origin='*' \
  --ServerApp.disable_check_xsrf=False
