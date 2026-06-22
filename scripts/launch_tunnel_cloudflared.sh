#!/usr/bin/env bash
# Expose the local JupyterLab (127.0.0.1:8888) on a public HTTPS URL via Cloudflare Tunnel.
# Quick (ephemeral) mode — zero config, free, no domain needed:
#   1) install cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
#   2) start JupyterLab (scripts/launch_jupyterlab.sh) in another shell
#   3) run this; share the printed https://<random>.trycloudflare.com URL + the Jupyter token
set -euo pipefail
command -v cloudflared >/dev/null || { echo "install cloudflared first"; exit 1; }
cloudflared tunnel --url http://127.0.0.1:8888
# Named tunnel + Zero-Trust (MFA, persistent hostname) — see ACCESS_AND_HOSTING.md §3.
