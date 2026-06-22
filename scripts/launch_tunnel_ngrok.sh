#!/usr/bin/env bash
# Alternative: ngrok. Free tier gives an ephemeral https URL; add basic-auth for a 2nd lock.
set -euo pipefail
command -v ngrok >/dev/null || { echo "install ngrok + 'ngrok config add-authtoken <token>' first"; exit 1; }
ngrok http 8888 --basic-auth="riskoff:${NGROK_PASS:-changeme}"
