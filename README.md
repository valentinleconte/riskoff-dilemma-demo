# RiskOff Dilemma — Interactive Demonstration (EN / FR)

A self-contained, **bilingual** pedagogical notebook that demonstrates the resolution of the
*"RiskOff lag / pre-market news effect"* dilemma — **is the unlagged news tone look-ahead, or a
legitimate ex-ante signal?** — end-to-end, with **only open-source libraries** and a small
**key-free** public dataset. Audited 2026-06-22; every number is recomputed live.

> Built so **Valentin** and **Anne-Lise** can share **one** environment — **no API or subscription
> duplication, no additional cost**. The data is public and contains no secrets.

## Open it (one click)

| Notebook | Google Colab | Binder |
|---|---|---|
| English | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/valentinleconte/riskoff-dilemma-demo/blob/main/notebooks/dilemma_demo_en_colab.ipynb) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/valentinleconte/riskoff-dilemma-demo/main?labpath=notebooks/dilemma_demo_en_jupyter.ipynb) |
| Français | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/valentinleconte/riskoff-dilemma-demo/blob/main/notebooks/dilemma_demo_fr_colab.ipynb) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/valentinleconte/riskoff-dilemma-demo/main?labpath=notebooks/dilemma_demo_fr_jupyter.ipynb) |

*(The badges work once this scaffold is pushed to the public repo `valentinleconte/riskoff-dilemma-demo`.
To use a different repo, edit `REPO_USER/REPO_NAME/REPO_BRANCH` at the top of `build_dilemma_demo.py`
and re-run it, or set the `RISKOFF_RAW` env var.)*

## What's inside

```
data/        riskoff_merged_daily.csv (1198 rows) · provenance_by_year.json  — public, key-free
notebooks/   dilemma_demo_{en,fr}_{jupyter,colab}.ipynb                       — 4 variants
environment.yml · requirements*.txt · postBuild · runtime.txt                — optimized config
scripts/     install_kernel.sh · launch_jupyterlab.sh · launch_tunnel_*.sh   — local + tunnel
ACCESS_AND_HOSTING.md                                                        — full sharing guide
```

Each notebook has its **own optimized kernel + configuration**:

| Variant | Kernel | Configuration source |
|---|---|---|
| `*_jupyter.ipynb` | `riskoff-demo` (conda/venv) | `environment.yml` / `requirements.txt` (pinned) |
| `*_colab.ipynb` | Colab `python3` | a setup cell `pip`-installs from `requirements-colab.txt` |
| Binder | built from `environment.yml` | reproducible image (repo2docker) |

The notebooks fetch the two small data files from this repo at runtime (with a local `./data/`
fallback), then run the demonstration: **provenance (ex-ante) → signal → 3-leg backtest → the lag
sign-flip & signal-to-noise → surrogate null + oracle → vol-matching → verdict → an interactive
ipywidgets playground** ("the dilemma in motion").

## Three ways to share one environment (full guide: `ACCESS_AND_HOSTING.md`)

1. **Google Colab** — open the Colab badge, then **Share → Editor** with your collaborator.
   Real-time co-editing, free, zero setup. (Google URL, not a public IP; 12 h sessions.)
2. **Binder** — open the Binder badge for a **free public URL**. Reproducible, zero install.
   Ephemeral (no persistence) and OSS-only — never put secrets in the repo.
3. **Self-hosted JupyterLab via Cloudflare Tunnel** — the true **public-IP / public-URL** path.
   One shared server, free, secure (token + HTTPS + optional Zero-Trust MFA), persistent.

   ```bash
   bash scripts/install_kernel.sh          # one-time: create the riskoff-demo kernel
   bash scripts/launch_jupyterlab.sh       # shell 1: start JupyterLab (prints a token)
   bash scripts/launch_tunnel_cloudflared.sh   # shell 2: prints a public https URL
   ```

## Why this avoids API/subscription duplication and cost

The audited notebook is **vectorbtpro-optional** (a NumPy engine twin reconciled to |ΔSharpe| = 0),
and the data is the already-derived public market/tone series — **no GDELT/Bloomberg feed, no GPU, no
paid library, no per-user key**. Sharing **one** environment (any of the three above) means a single
set of (free) dependencies serves both authors. Estimated cost: **€0**.
