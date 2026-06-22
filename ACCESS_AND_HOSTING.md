# Accessibility & Hosting — sharing the RiskOff Dilemma notebooks at zero cost

**Goal:** let Valentin and Anne-Lise run and co-edit the bilingual demo from anywhere, sharing
**one** environment, with **no API/subscription duplication and no additional cost** — including a
true **public-IP / public-URL** option.

> **This repo is public**, so the badges below are **live** — click to open. The notebooks fetch
> their small, key-free dataset from this repo at runtime (with a local `./data/` fallback when run
> from a clone).

---

## Badges — click to open

| Notebook | Google Colab | Binder |
|---|---|---|
| **English** | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/valentinleconte/riskoff-dilemma-demo/blob/main/notebooks/dilemma_demo_en_colab.ipynb) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/valentinleconte/riskoff-dilemma-demo/main?labpath=notebooks/dilemma_demo_en_jupyter.ipynb) |
| **Français** | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/valentinleconte/riskoff-dilemma-demo/blob/main/notebooks/dilemma_demo_fr_colab.ipynb) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/valentinleconte/riskoff-dilemma-demo/main?labpath=notebooks/dilemma_demo_fr_jupyter.ipynb) |

*Colab opens the `*_colab.ipynb` variant; Binder opens the `*_jupyter.ipynb` variant.*

---

## 0. The cost problem, solved at the root

The reason notebook collaboration usually duplicates cost is that each collaborator stands up their
own environment, their own data feed, and their own paid keys (Bloomberg/Dow Jones feeds, a GPU
runtime, a vectorbtpro licence, a Colab Pro seat). This demo removes every one of those at the source:

- **No paid library** — the notebook is `vectorbtpro`-optional (a NumPy engine twin, reconciled to
  |ΔSharpe| = 0 in the 2026-06-22 audit). Only free OSS (numpy/pandas/scipy/matplotlib/ipywidgets).
- **No data feed / no key** — it ships a small *derived* public dataset (`data/*.csv|json`); GDELT and
  Yahoo Finance, if ever re-pulled, are free. **No secret is ever required.**
- **One shared environment** — all three options below put both authors on a *single* set of free
  dependencies, so nothing is duplicated.

**Net cost of every option in this document: €0.**

---

## 1. Decision matrix (pick per need)

| Dimension | **Google Colab** | **Binder (mybinder.org)** | **Self-hosted JupyterLab + Cloudflare Tunnel** |
|---|---|---|---|
| Public **IP / URL** | Google URL (not an IP) | Free public URL | **Yes — public HTTPS URL/IP** |
| Cost | €0 (free tier) | €0 | €0 (free tier of cloudflared) |
| Real-time co-editing | **Yes** (Share → Editor) | No (one session each) | Yes (JupyterLab RTC) |
| Persistence | Ephemeral (12 h cap) | **Ephemeral** (culled on idle) | **Persistent** (your machine) |
| Private data / keys | OK (Colab Secrets) | **Never** (public repo) | **OK** (stays on your host) |
| Setup effort | None | None | ~15 min one-time |
| Compute limits | 12 h, shared CPU/GPU | RAM/CPU caps, ~1 Mbit out | your machine's |
| Best for | quick co-editing | a citable public demo | a durable shared workspace |

**Recommendation.** Use **all three, for different jobs**: Colab for fast pair-work, Binder for a
public link in the paper/committee pack, and the **self-hosted tunnel** as the durable, private,
public-URL workspace. They share the same four notebooks and the same `environment.yml`.

---

## 2. Path A — Google Colab (zero-infra co-editing)

1. **Open** the EN or FR **Colab badge** (top of this file). It opens the `*_colab.ipynb` straight
   from GitHub — no download, no clone.
2. **Runtime ▸ Run all** (`⌘/Ctrl + F9`). The first cell `pip`-installs `ipywidgets` and fetches the
   two data files from this repo (≈ 1 s). No keys, no Drive mount required.
3. **Co-edit live:** **Share** (top-right) ▸ add your collaborator's Google account as **Editor**.
   *Or* **File ▸ Save a copy in Drive** into a **Shared Drive** you both can open. Edits then sync in
   real time, like a Google Doc.
4. If you ever need a private value, use **Colab Secrets** (`google.colab.userdata.get('NAME')`) — it
   is per-user and never written into the notebook. *This demo needs none.*

**Limits:** sessions end after ~12 h or on idle; the VM filesystem is ephemeral (persist to Drive).

---

## 3. Path B — Binder (free public, reproducible URL)

1. **Open** the EN or FR **Binder badge**. Binder builds a reproducible image from `environment.yml`
   (via repo2docker) and opens JupyterLab — **no install for the visitor**.
2. **First build takes ~2–5 min** (watch the build log; later opens are cached). `postBuild` confirms
   the widget stack.
3. When JupyterLab opens, **Run ▸ Run All Cells**. The page **URL is your citable public link** —
   paste it in the paper, committee pack, or for arXiv reviewers.

**Hard rules (security):** Binder is a *public* service — **never** commit secrets, API keys, or
private data to the repo. Sessions are **ephemeral** and resource-limited (RAM/CPU caps, ~1 Mbit
egress, idle-culling), so Binder is for *demonstration*, not heavy compute or persistence.

---

## 4. Path C — Self-hosted JupyterLab via Cloudflare Tunnel (the "public IP" path)

This is the option that literally answers "accessible via a public IP address," while staying free,
secure, and persistent. One person hosts (a laptop, a home server, or a free-tier VM); both connect.

### 4.1 Why a tunnel and not a raw open port

Exposing a port directly means opening inbound firewall rules and managing TLS yourself — fragile and
risky. **Cloudflare Tunnel** runs a lightweight `cloudflared` daemon that makes **outbound-only**
connections to Cloudflare's edge; traffic reaches your JupyterLab through Cloudflare over HTTPS, with
**no inbound ports opened**. It's free, and you can layer Zero-Trust access policies (identity, MFA,
country rules, service tokens) in front of it.

### 4.2 Quick start (ephemeral URL, zero config)

*Prerequisite: install `cloudflared` once — https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/ (macOS: `brew install cloudflared`).*

```bash
git clone https://github.com/valentinleconte/riskoff-dilemma-demo.git
cd riskoff-dilemma-demo
bash scripts/install_kernel.sh             # one-time: create the 'riskoff-demo' kernel
bash scripts/launch_jupyterlab.sh          # shell 1: JupyterLab on 127.0.0.1:8888 — PRINTS A TOKEN
bash scripts/launch_tunnel_cloudflared.sh  # shell 2: prints https://<random>.trycloudflare.com
```

**Share two things, privately:** the printed `https://…trycloudflare.com` URL **and** the JupyterLab
token (the URL is useless without the token). To stop: `Ctrl-C` in both shells. Done.

### 4.3 Production-grade (persistent hostname + MFA, still free)

1. Add a domain to a free Cloudflare account; install `cloudflared` and run `cloudflared tunnel login`.
2. `cloudflared tunnel create riskoff` → route a DNS hostname (e.g. `lab.yourdomain.com`) to
   `http://127.0.0.1:8888`.
3. In **Cloudflare Zero Trust → Access**, add an application policy on that hostname allowing only
   Valentin's and Anne-Lise's emails, with **one-time-PIN or MFA**. Now even the URL is useless to
   anyone else.
4. Run `cloudflared tunnel run riskoff` (optionally as a service) alongside JupyterLab.

### 4.4 Alternatives

- **ngrok** (`scripts/launch_tunnel_ngrok.sh`) — simplest, token/basic-auth, free tier gives an
  ephemeral URL. Run `ngrok config add-authtoken <token>` once, then the script. Good for a one-off.
- **Tailscale / Tailscale Funnel** — private mesh VPN; expose the lab only to your devices, or a public
  Funnel URL. Excellent if you don't want any public exposure at all.
- **JupyterHub** — if this ever grows past two people, JupyterHub gives each user their own server and
  (v5+) real-time collaboration sharing; heavier, still free/OSS.
- **Free-tier VM host** — Oracle Cloud "Always Free" or a small GCP/AWS free instance can be the
  persistent host instead of a laptop; same tunnel setup.

---

## 5. Security checklist (MECE)

- **Authentication** — JupyterLab **token** on every connection (the launch script generates a 32-byte
  one); add Cloudflare **Zero-Trust MFA** for the named-tunnel setup. Never run with `--token=''`.
- **Transport** — always HTTPS. Colab/Binder/Cloudflare terminate TLS for you; never serve plain HTTP
  over a raw public port.
- **Exposure** — bind JupyterLab to `127.0.0.1` and let the tunnel reach it (outbound-only); do **not**
  open inbound firewall ports.
- **Data** — the demo data is public and key-free, so nothing sensitive is shared; never add a secret
  to this public repo. For self-hosted, private data stays on your host.
- **Least privilege** — the named tunnel restricts access to two named identities; rotate the Jupyter
  token if it leaks; stop the tunnel when not in use.

---

## 6. Cost analysis

| Item | Colab | Binder | Self-hosted + Cloudflare Tunnel |
|---|---|---|---|
| Compute | €0 (free tier) | €0 (donated infra) | €0 (your machine) or free-tier VM |
| Public URL / tunnel | €0 | €0 | €0 (`trycloudflare` or free Cloudflare account) |
| Data feed / API keys | €0 (none needed) | €0 | €0 |
| Paid libraries (vbt, GPU) | €0 (not used) | €0 | €0 |
| **Total** | **€0** | **€0** | **€0** |

What *would* cost money (and is **not** required here): Colab Pro/Pro+ seats, a Bloomberg/Dow Jones
feed, a GPU runtime, a vectorbtpro licence, a paid static IP. Avoiding all of these is the point.

---

## 7. Troubleshooting (MECE)

| Symptom | Cause | Fix |
|---|---|---|
| **Badge opens a GitHub 404** | Repo private, or notebook path/branch changed | Confirm this repo is **Public** and the notebook is at `main`/`notebooks/dilemma_demo_*`. |
| **Colab: "Notebook not found"** | Branch/path in the badge ≠ repo | The notebook must be at `main`/`notebooks/dilemma_demo_*_colab.ipynb`. |
| **Notebook errors fetching data** (`HTTPError`/`URLError`) | The raw URL isn't reachable | `curl -sI https://raw.githubusercontent.com/valentinleconte/riskoff-dilemma-demo/main/data/riskoff_merged_daily.csv` should be `200`. When run from a clone, the notebook falls back to local `./data/`. |
| **Binder: "build failed"** | An unpinned/incompatible dep in `environment.yml` | Read the build-log line that failed; the pins are known-good as of 2026-06-22. |
| **Tunnel URL 502 / refuses** | JupyterLab not running, or wrong port | Start `scripts/launch_jupyterlab.sh` first (shell 1); the tunnel (shell 2) must point at `127.0.0.1:8888`. |
| **`cloudflared`/`ngrok`: command not found** | Not installed | Install per §4.2 / §4.4, then re-run. |

---

## 8. Recommendation for Valentin & Anne-Lise

- **Day-to-day pair work:** Google Colab (one shared notebook, *Share → Editor*).
- **Public/citable link** (paper, committee, arXiv): the **Binder** badge.
- **Durable private shared workspace on a public URL:** self-hosted JupyterLab + **Cloudflare
  Tunnel** (named tunnel + Zero-Trust MFA, §4.3).

All three run the *same* four notebooks and the *same* pinned `environment.yml`, so there is exactly
one environment to maintain and **nothing is duplicated**.

---

## Sources

- [Project Jupyter — The Binder Project](https://jupyter.org/binder) · [mybinder.org](https://mybinder.org/) · [Binder usage guidelines (limits, no secrets)](https://mybinder.readthedocs.io/en/latest/about/user-guidelines.html)
- [Google Colab FAQ](https://research.google.com/colaboratory/faq.html)
- [Cloudflare Tunnel — downloads & setup](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) · [Cloudflare Tunnel community: exposing JupyterLab](https://community.cloudflare.com/t/trying-to-expose-jupyterlab-with-tunnel/622502)
- [awesome-tunneling (ngrok/Cloudflare/Tailscale/ZeroTier alternatives)](https://github.com/anderspitman/awesome-tunneling)
- [JupyterHub (multi-user) docs](https://jupyterhub.readthedocs.io/) · [JupyterHub sharing access](https://jupyterhub.readthedocs.io/en/stable/reference/sharing.html)
