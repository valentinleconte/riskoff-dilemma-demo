#!/usr/bin/env bash
# Create the optimized 'riskoff-demo' kernel locally (conda preferred; venv fallback).
set -euo pipefail
if command -v conda >/dev/null 2>&1; then
  conda env create -f environment.yml || conda env update -f environment.yml
  conda run -n riskoff-demo python -m ipykernel install --user --name riskoff-demo --display-name "Python (riskoff-demo)"
  echo "OK: conda env 'riskoff-demo' + kernel registered."
else
  python3 -m venv .venv && . .venv/bin/activate
  pip install -U pip && pip install -r requirements.txt
  python -m ipykernel install --user --name riskoff-demo --display-name "Python (riskoff-demo)"
  echo "OK: venv '.venv' + kernel registered."
fi
