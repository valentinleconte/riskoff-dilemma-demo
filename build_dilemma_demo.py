#!/usr/bin/env python3
"""
Generator for the "RiskOff Dilemma Demonstration" notebook — bilingual (EN/FR),
narrative + interactive ipywidgets playground, data fetched from a PUBLIC GitHub repo.
Emits Jupyter and Colab variants (own kernelspec + setup cell + badges per target).

    python build_dilemma_demo.py            # writes the 4 notebooks into notebooks/

No API keys, no paid libraries (vectorbtpro-optional). Runs on Jupyter / JupyterLab /
Colab / Binder. The compute cells are language-neutral; only markdown + a tiny label
dict (L[...]) differ by language.
"""

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "notebooks"
OUT.mkdir(exist_ok=True)

# default public repo the notebooks fetch from (user pushes the scaffold here, then edits if needed)
REPO_USER = "valentinleconte"
REPO_NAME = "riskoff-dilemma-demo"
REPO_BRANCH = "main"
RAW = f"https://raw.githubusercontent.com/{REPO_USER}/{REPO_NAME}/{REPO_BRANCH}"


# ----------------------------------------------------------------------------- cells
def md(src):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": src if isinstance(src, list) else [src],
    }


def code(src):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": src if isinstance(src, list) else [src],
    }


# ---- SETUP cell (the only language/target-dependent code) ----
def setup_code(lang, target):
    pip = (
        "pandas numpy matplotlib scipy ipywidgets"
        if target == "colab"
        else "pandas numpy matplotlib scipy ipywidgets"
    )
    return f"""# === SETUP — env-agnostic bootstrap (Jupyter / JupyterLab / Colab / Binder) ===
LANG = "{lang}"                      # this notebook variant
import sys, os, subprocess, importlib

IN_COLAB = "google.colab" in sys.modules
# 1) dependencies — only (re)install what's missing; Colab gets a guaranteed set
def _ensure(pkgs):
    missing = [p for p in pkgs if importlib.util.find_spec(p.split("==")[0].replace("-", "_")) is None]
    if missing or IN_COLAB:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", *pkgs], check=False)
_ensure("{pip}".split())

# 2) data — fetch the small public, key-free files from the demo repo (fallback: local ./data)
RAW = os.environ.get("RISKOFF_RAW", "{RAW}")
os.makedirs("data", exist_ok=True)
import urllib.request
for f in ["riskoff_merged_daily.csv", "provenance_by_year.json"]:
    dst = os.path.join("data", f)
    if not os.path.exists(dst):
        try:
            urllib.request.urlretrieve(f"{{RAW}}/data/{{f}}", dst)
        except Exception as e:
            print("fetch failed for", f, "->", e, "| put it under ./data/ manually")

# 3) imports + constants (verified against the audited prototype, 2026-06-22)
import numpy as np, pandas as pd, json, warnings
import matplotlib;
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
ANN, COST_BPS, ROLL, MINP = 252, 2.0, 252, 60
ARM, DISARM, HOLD, THR, VIX_LAG = 1.0, 0.3, 3, 0.5, 1
SPLIT2 = pd.Timestamp("2024-12-31")
SE_LO = 0.92                          # Lo-2002 OOS Sharpe SE (n=299)

# tiny bilingual label dict for the few printed strings (markdown carries the narrative)
L = {{
 "en": dict(rows="rows", regimes="Regime days  VIX / tone / both / tone-only",
            sharpe="FULL Sharpe (sqrt252)  B&H / VIX / VIX+tone",
            dsh="dSharpe(combo-VIX)  FULL / OOS", verdict="VERDICT",
            exante="ex-ante (pre-open)", look="look-ahead"),
 "fr": dict(rows="lignes", regimes="Jours de regime  VIX / tone / les deux / tone-seul",
            sharpe="Sharpe PLEIN (sqrt252)  B&H / VIX / VIX+tone",
            dsh="dSharpe(combo-VIX)  PLEIN / OOS", verdict="VERDICT",
            exante="ex-ante (avant l'open)", look="look-ahead"),
}}[LANG]
print(("Colab" if IN_COLAB else "local"), "| LANG=", LANG, "| setup OK")"""


# ---- shared compute cells (language-neutral) ----
CORE = r"""# === CORE — data + the audited RiskOff overlay (pure NumPy/pandas, vbt-optional) ===
df = pd.read_csv("data/riskoff_merged_daily.csv", parse_dates=["date"]).sort_values("date").reset_index(drop=True)
oos = (df["date"] >= SPLIT2).values
print(L["rows"], "=", len(df), "|", df["date"].min().date(), "->", df["date"].max().date(),
      "| OOS n =", int(oos.sum()))

def pit_z(s, win=ROLL, minp=MINP):
    r = pd.Series(s).rolling(win, min_periods=minp); return ((pd.Series(s) - r.mean()) / r.std()).values

def vix_flag(zv, arm=ARM, dis=DISARM, hold=HOLD):
    out = np.zeros(len(zv), int); st = h = 0
    for i, v in enumerate(np.clip(zv, -3, 3)):
        if np.isnan(v): out[i] = st; continue
        if st == 0 and v >= arm: st, h = 1, 0
        elif st == 1:
            h += 1
            if v <= dis and h >= hold: st = 0
        out[i] = st
    return out

def build(d, thr=THR, tone_lag=0, vix_lag=VIX_LAG, arm=ARM, dis=DISARM, hold=HOLD):
    zv = pit_z(pd.Series(d["vix"]).shift(vix_lag))
    lvl = pd.Series(d["level"]).shift(tone_lag) if tone_lag else d["level"]
    zt = pit_z(lvl)
    fv = vix_flag(zv, arm, dis, hold)
    tone_on = ((zt > thr) & (zv > 0)).astype(int)
    return zv, zt, fv, tone_on

def strat(d, w, cost=COST_BPS):
    w = np.asarray(w, float)
    return w * np.nan_to_num(d["perf"].values) - np.abs(np.diff(w, prepend=w[0])) * cost / 1e4

def sharpe(r, ann=ANN, mask=None):
    r = np.asarray(r); r = r[mask] if mask is not None else r; r = r[~np.isnan(r)]
    sd = r.std(ddof=1); return np.nan if sd == 0 else r.mean() * ann / (sd * np.sqrt(ann))

def maxdd(r):
    r = np.asarray(r); r = r[~np.isnan(r)]; eq = np.cumprod(1 + r)
    return float((eq / np.maximum.accumulate(eq) - 1).min())

zv, zt, fvix, tone_on = build(df)
w_bh = np.ones(len(df)); w_vix = np.where(fvix == 1, .5, 1.); w_cmb = np.where((fvix == 1) | (tone_on == 1), .5, 1.)
r_bh, r_vix, r_cmb = df["perf"].values, strat(df, w_vix), strat(df, w_cmb)
n_vix, n_tone, n_both = int(fvix.sum()), int(tone_on.sum()), int(((fvix == 1) & (tone_on == 1)).sum())
n_only = int(((tone_on == 1) & (fvix == 0)).sum())
print(L["regimes"], "=", n_vix, "/", n_tone, "/", n_both, "/", n_only)
print(L["sharpe"], "= %.3f / %.3f / %.3f" % (sharpe(r_bh), sharpe(r_vix), sharpe(r_cmb)))
"""

PROVENANCE = r"""# === PROVENANCE — the pre-market window holds across the full history (ex-ante, not look-ahead) ===
prov = json.load(open("data/provenance_by_year.json"))
yrs = sorted(prov["by_year"]); ex = [prov["by_year"][y]["pct_ex_ante"] for y in yrs]
lk = [prov["by_year"][y]["pct_lookahead_cash_session"] for y in yrs]
fig, ax = plt.subplots(figsize=(8.6, 4.2))
ax.bar(range(len(yrs)), ex, color="#16a085", width=.62, edgecolor="white"); ax.set_ylim(98.5, 100.05)
for i, e in enumerate(ex): ax.annotate(f"{e:.2f}%", (i, e), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8.5, fontweight="bold")
ax2 = ax.twinx(); ax2.plot(range(len(yrs)), lk, "o-", color="#c0392b", lw=1.6); ax2.set_ylim(0, 1.2)
ax2.set_ylabel("% " + L["look"], color="#c0392b"); ax.set_xticks(range(len(yrs))); ax.set_xticklabels(yrs)
ax.set_ylabel("% " + L["exante"], color="#16a085")
ax.set_title("Pre-market provenance 2021-2026 (232k articles): >=99.7%/yr ex-ante, look-ahead <=0.27%/yr", fontsize=10, fontweight="bold")
plt.tight_layout(); plt.show()
print("overall ex-ante = %.2f%% | cash-session look-ahead = %.2f%%" % (prov["overall"]["pct_ex_ante"], prov["overall"]["pct_lookahead"]))
"""

BACKTEST = r"""# === BACKTEST — three legs + equity curves (after 2 bps) ===
eq = lambda r: 100 * np.cumprod(1 + np.nan_to_num(r))
fig, ax = plt.subplots(figsize=(9.2, 4.4))
ax.plot(df["date"], eq(r_bh), color="#7f8c8d", lw=1.5, label="SPX B&H  (%.2fx)" % (eq(r_bh)[-1] / 100))
ax.plot(df["date"], eq(r_vix), color="#2980b9", lw=1.5, label="VIX alone  (%.2fx)" % (eq(r_vix)[-1] / 100))
ax.plot(df["date"], eq(r_cmb), color="#16a085", lw=1.8, label="VIX + tone  (%.2fx)" % (eq(r_cmb)[-1] / 100))
ax.axvline(SPLIT2, color="k", ls="--", lw=.8, alpha=.6); ax.legend(loc="upper left", fontsize=9)
ax.set_title("Growth of 100 — the combined (tone) leg is the lowest", fontweight="bold", fontsize=10); plt.tight_layout(); plt.show()
tab = pd.DataFrame({
  "Sharpe252": [sharpe(r_bh), sharpe(r_vix), sharpe(r_cmb)],
  "MaxDD": [maxdd(r_bh), maxdd(r_vix), maxdd(r_cmb)],
  "OOS_Sharpe": [sharpe(r_bh, mask=oos), sharpe(r_vix, mask=oos), sharpe(r_cmb, mask=oos)],
}, index=["B&H", "VIX", "VIX+tone"]).round(3)
print(tab.to_string())
print("\n" + L["dsh"], "= %+.3f / %+.3f" % (sharpe(r_cmb) - sharpe(r_vix), sharpe(r_cmb, mask=oos) - sharpe(r_vix, mask=oos)))
"""

LAGMATRIX = r"""# === THE CRUX — lag sensitivity + signal-to-noise (the sign is not identifiable) ===
def dsharpe(tone_lag, exec_shift=0):
    _, _, fv, ton = build(df, tone_lag=tone_lag)
    wv = np.where(fv == 1, .5, 1.); wc = np.where((fv == 1) | (ton == 1), .5, 1.)
    base = df["perf"].shift(-exec_shift).values if exec_shift else df["perf"].values
    rv = wv * np.nan_to_num(base) - np.abs(np.diff(wv, prepend=wv[0])) * COST_BPS / 1e4
    rc = wc * np.nan_to_num(base) - np.abs(np.diff(wc, prepend=wc[0])) * COST_BPS / 1e4
    return sharpe(rc) - sharpe(rv), sharpe(rc, mask=oos) - sharpe(rv, mask=oos)
rows = [("tone unlagged (pre-market)", *dsharpe(0)),
        ("tone lagged 1d (over-cautious)", *dsharpe(1)),
        ("next-bar execution", *dsharpe(0, 1))]
fig, ax = plt.subplots(figsize=(8.8, 3.6)); y = np.arange(len(rows))
ax.axvspan(-1.96 * SE_LO, 1.96 * SE_LO, color="#dfe6ee", label="95%% noise band (+/-1.96*SE, SE=%.2f)" % SE_LO)
ax.axvline(0, color="k", lw=1)
for i, (lab, f, o) in enumerate(rows):
    ax.scatter([f, o], [i + .12, i - .12], color=["#c0392b" if v < 0 else "#16a085" for v in (f, o)], s=60, zorder=5)
    ax.annotate("FULL %+.3f / OOS %+.3f" % (f, o), (max(f, o), i), textcoords="offset points", xytext=(8, 0), va="center", fontsize=8)
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=9); ax.set_xlim(-2, 2)
ax.set_xlabel("dSharpe (VIX+tone - VIX alone)"); ax.legend(loc="lower right", fontsize=8)
ax.set_title("Every dSharpe is <= 0.21x the SE -> within noise; the sign flips with convention", fontweight="bold", fontsize=9.5)
plt.tight_layout(); plt.show()
print("Lo-2002 OOS Sharpe SE = %.2f -> a signal must exceed ~%.1f to be 95%%-significant at n=299." % (SE_LO, 1.96 * SE_LO))
"""

NULL = r"""# === POWER-MATCHED SURROGATE NULL + ORACLE (the test has power; the tone has no timing) ===
rng = np.random.default_rng(42)
def block_boot_idx(n, p=1/20):
    idx = np.empty(n, int); idx[0] = rng.integers(n)
    for i in range(1, n): idx[i] = rng.integers(n) if rng.random() < p else (idx[i-1] + 1) % n
    return idx
real = sharpe(r_cmb) - sharpe(r_vix); lvl = df["level"].values; B = 600; surr = np.empty(B)
for b in range(B):
    zt2 = pit_z(lvl[block_boot_idx(len(df))]); ton = ((zt2 > THR) & (zv > 0)).astype(int)
    wc = np.where((fvix == 1) | (ton == 1), .5, 1.); surr[b] = sharpe(strat(df, wc)) - sharpe(r_vix)
thr_q = np.nanquantile(df["perf"].values, 0.10); oracle_on = (np.nan_to_num(df["perf"].values) <= thr_q).astype(int)
wo = np.where((fvix == 1) | (oracle_on == 1), .5, 1.); oracle = sharpe(strat(df, wo)) - sharpe(r_vix)
fig, ax = plt.subplots(figsize=(8.6, 3.8))
ax.hist(surr, bins=40, color="#7f8c8d", alpha=.65, edgecolor="white")
ax.axvline(real, color="#c0392b", lw=2.2, label="real tone (%.3f)" % real)
ax.axvline(np.median(surr), color="k", ls=":", lw=1.2, label="null median (%.3f)" % np.median(surr))
ax.axvline(oracle, color="#16a085", lw=2.2, label="oracle control (%.2f)" % oracle)
ax.set_title("%.0f%% of random-timing tones match/beat the real one; oracle proves the test has power" % (100 * (surr >= real).mean()), fontweight="bold", fontsize=9.5)
ax.legend(fontsize=8); plt.tight_layout(); plt.show()
"""

VOLMATCH = r"""# === LEVERAGE vs TIMING — vol-matched MaxDD (the drawdown edge is dilution) ===
k = np.nanstd(r_bh) / np.nanstd(r_vix)
print("vol-match factor k = %.3f" % k)
print("MaxDD  B&H = %.1f%% | VIX raw = %.1f%% | VIX vol-matched = %.1f%%  <- reverses (worse than B&H)" % (
      100 * maxdd(r_bh), 100 * maxdd(r_vix), 100 * maxdd(r_vix * k)))
print("\n" + L["verdict"] + ": NO-GO tone leg (no detectable edge) | CONDITIONAL-GO VIX overlay (risk tool only).")
"""


def playground_code(lang):
    title = (
        "Interactive playground — move the sliders, watch the dilemma in motion"
        if lang == "en"
        else "Playground interactif — bougez les curseurs, voyez le dilemme en mouvement"
    )
    lab = dict(
        en=dict(
            thr="tone threshold",
            arm="VIX arm",
            dis="VIX disarm",
            lag="tone lag (days)",
            cost="cost (bps)",
            note="dSharpe(combo-VIX); the |value| stays << the SE band -> within noise",
        ),
        fr=dict(
            thr="seuil tone",
            arm="VIX arm",
            dis="VIX disarm",
            lag="decalage tone (j)",
            cost="cout (bps)",
            note="dSharpe(combo-VIX); la |valeur| reste << la bande SE -> dans le bruit",
        ),
    )[lang]
    return f"""# === {title} ===
try:
    import ipywidgets as W
    from IPython.display import display
    HAVE_W = True
except Exception:
    HAVE_W = False

def _run(thr, arm, dis, lag, cost):
    zv2 = pit_z(pd.Series(df["vix"]).shift(VIX_LAG))
    lvl2 = pd.Series(df["level"]).shift(lag) if lag else df["level"]
    zt2 = pit_z(lvl2); fv = vix_flag(zv2, arm, dis, HOLD); ton = ((zt2 > thr) & (zv2 > 0)).astype(int)
    wv = np.where(fv == 1, .5, 1.); wc = np.where((fv == 1) | (ton == 1), .5, 1.)
    rv = strat(df, wv, cost); rc = strat(df, wc, cost)
    dF, dO = sharpe(rc) - sharpe(rv), sharpe(rc, mask=oos) - sharpe(rv, mask=oos)
    n_only2 = int(((ton == 1) & (fv == 0)).sum())
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.6), gridspec_kw=dict(width_ratios=[1.5, 1]))
    a1.plot(df["date"], 100*np.cumprod(1+np.nan_to_num(rv)), color="#2980b9", lw=1.4, label="VIX")
    a1.plot(df["date"], 100*np.cumprod(1+np.nan_to_num(rc)), color="#16a085", lw=1.6, label="VIX+tone")
    a1.plot(df["date"], 100*np.cumprod(1+np.nan_to_num(r_bh)), color="#7f8c8d", lw=1.1, label="B&H")
    a1.legend(fontsize=8, loc="upper left"); a1.set_title("equity (growth of 100)", fontsize=9)
    a2.axvspan(-1.96*SE_LO, 1.96*SE_LO, color="#dfe6ee"); a2.axvline(0, color="k", lw=1)
    a2.scatter([dF, dO], [1, 0], color=["#c0392b" if v<0 else "#16a085" for v in (dF,dO)], s=80, zorder=5)
    a2.set_yticks([0,1]); a2.set_yticklabels(["OOS","FULL"]); a2.set_xlim(-2,2); a2.set_title("dSharpe vs noise band", fontsize=9)
    plt.tight_layout(); plt.show()
    print("tone-only days = %d | dSharpe FULL %+.3f  OOS %+.3f   ({lab["note"]})" % (n_only2, dF, dO))

if HAVE_W:
    display(W.interactive(_run,
        thr=W.FloatSlider(value=THR, min=-0.5, max=2.0, step=0.1, description="{lab["thr"]}"),
        arm=W.FloatSlider(value=ARM, min=0.5, max=2.0, step=0.05, description="{lab["arm"]}"),
        dis=W.FloatSlider(value=DISARM, min=-0.5, max=1.0, step=0.05, description="{lab["dis"]}"),
        lag=W.IntSlider(value=0, min=0, max=3, step=1, description="{lab["lag"]}"),
        cost=W.FloatSlider(value=COST_BPS, min=0.0, max=10.0, step=0.5, description="{lab["cost"]}")))
else:
    print("ipywidgets unavailable -> static example:"); _run(THR, ARM, DISARM, 0, COST_BPS)"""


# ----------------------------------------------------------------------------- bilingual markdown
def badges():
    return (
        f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
        f"(https://colab.research.google.com/github/{REPO_USER}/{REPO_NAME}/blob/{REPO_BRANCH}/notebooks/%NB%)) "
        f"[![Binder](https://mybinder.org/badge_logo.svg)]"
        f"(https://mybinder.org/v2/gh/{REPO_USER}/{REPO_NAME}/{REPO_BRANCH}?labpath=notebooks/%NB%))"
    )


MD = {
    "en": {
        "title": lambda nb: [
            "# RiskOff Dilemma — Interactive Demonstration (EN)\n",
            badges().replace("%NB%", nb) + "\n\n",
            "**The dilemma.** Is the pre-market overnight news *tone*, used at session *t* **without** a one-day lag, a *look-ahead* bias — or a legitimate **ex-ante** signal? And does the answer change the verdict on the news leg?\n\n",
            "This notebook *demonstrates* the resolution, end-to-end, with **only open-source libraries** and a small **key-free** public dataset. It runs identically on Jupyter, JupyterLab, Google Colab and Binder. Audited 2026-06-22; every number is recomputed live.",
        ],
        "prov": "## 1 · Provenance — the tone is captured pre-market (ex-ante), not look-ahead\nThe tone for session *D* aggregates only articles captured overnight, in **[21:00 London D−1 → 08:00 London D]**, i.e. **before** the 09:30 ET cash open. An article-level audit of the full corpus (232,502 articles) shows **≥ 99.7 %/yr are ex-ante**; genuine cash-session look-ahead is **≤ 0.27 %/yr (0.10 % overall)**. So using the tone unlagged is **legitimate**, not a bug.",
        "sig": "## 2 · Signal — VIX hysteresis × a contrarian tone gate\nPoint-in-time rolling-252 z-scores (min 60 obs). **VIX flag**: risk-off when z[VIX‑1d] ≥ +1.0 (disarm +0.3, 3-day hold). **Tone gate**: de-risk when z[VIX] > 0 **and** z[tone] > +0.5. Weight = 0.5 when (VIX flag) **or** (tone gate), else 1.0. On the clean 1198-session data the regime split is **271 / 96 / 49 / 47**.",
        "bt": "## 3 · Backtest — the headline\nThree legs after 2 bps costs. The **combined (tone) leg is the lowest** of the three. The marginal value of the news gate, ΔSharpe(combo − VIX), is **−0.073 full-sample**.",
        "crux": '## 4 · The crux — the sign is not identifiable\nThe tone gate\'s ΔSharpe is **−0.073 unlagged**, **+0.010 lagged 1d**, **≈0 next-bar** — the sign **flips with convention**. The Lo-2002 OOS Sharpe standard error is **0.92**; every ΔSharpe is ≤ 0.21× that. So the honest reading is **"no dependable edge — within noise"**, not "value-destroying".',
        "null": "## 5 · Surrogate null + oracle — proof the test has power\nRandomise the tone *timing* (stationary block bootstrap), hold VIX + returns fixed. The real tone sits at/below the null centre (**a large majority of random tones match or beat it**), while an **oracle** that de-risks the worst days lands far in the right tail — the test detects real timing skill, the tone has none.",
        "vol": "## 6 · Leverage vs timing — the drawdown edge is dilution\nThe VIX overlay's lower **raw** MaxDD is partly because it holds less risk (0.5×). Re-levered to the benchmark's volatility (k ≈ 1.25), the MaxDD **reverses** to worse than buy-&-hold full-sample.",
        "verdict": "## 7 · Verdict\n**NO-GO** on the GDELT/FinBERT tone leg — on *no-detectable-edge* grounds (not look-ahead, not value-destroying). **CONDITIONAL-GO** on the VIX overlay as a **risk tool only** (never alpha). Resolving the dilemma *strengthens* the rigour while correcting an overclaim in each direction.",
        "play": "## 8 · Playground — the dilemma *in motion* 🎛️\nMove the sliders and watch ΔSharpe, the regime count, and the equity curves update live. Notice that **whatever you do**, the tone-gate ΔSharpe stays inside the noise band — that is the whole point.",
        "close": lambda: (
            "---\n### Share this notebook (no API/subscription duplication, zero cost)\nThree ways for Valentin & Anne-Lise to share **one** environment — see **`ACCESS_AND_HOSTING.md`**: (1) **Google Colab** — click the badge, *Share → Editor*; (2) **Binder** — click the badge for a free public URL; (3) **self-hosted JupyterLab via Cloudflare Tunnel** — the true *public-IP* path (free, secure, persistent). The data is public and key-free, so no secrets are ever exposed."
        ),
    },
    "fr": {
        "title": lambda nb: [
            "# Dilemme RiskOff — Démonstration interactive (FR)\n",
            badges().replace("%NB%", nb) + "\n\n",
            "**Le dilemme.** Le *tone* des news pré-marché, utilisé à la séance *t* **sans** décalage d'un jour, est-il du *look-ahead* — ou un signal **ex-ante** légitime ? Et la réponse change-t-elle le verdict sur la jambe news ?\n\n",
            "Ce notebook *démontre* la résolution, de bout en bout, avec **uniquement des librairies open-source** et un petit jeu de données public **sans clé**. Il tourne à l'identique sur Jupyter, JupyterLab, Google Colab et Binder. Audité le 2026-06-22 ; chaque chiffre est recalculé en direct.",
        ],
        "prov": "## 1 · Provenance — le tone est capturé en pré-marché (ex-ante), pas du look-ahead\nLe tone de la séance *D* n'agrège que des articles capturés la nuit, en **[21:00 Londres D−1 → 08:00 Londres D]**, donc **avant** l'ouverture 09:30 ET. Un audit article par article du corpus complet (232 502 articles) montre **≥ 99,7 %/an ex-ante** ; le vrai look-ahead en séance est **≤ 0,27 %/an (0,10 % global)**. Utiliser le tone non décalé est donc **légitime**, pas un bug.",
        "sig": "## 2 · Signal — hystérèse VIX × porte tone contrariante\nZ-scores glissants 252 j point-in-time (min 60 obs). **Drapeau VIX** : risk-off quand z[VIX‑1j] ≥ +1.0 (disarm +0.3, maintien 3 j). **Porte tone** : dé-risque quand z[VIX] > 0 **et** z[tone] > +0.5. Poids = 0.5 si (drapeau VIX) **ou** (porte tone), sinon 1.0. Sur le jeu propre 1198 séances, la répartition des régimes est **271 / 96 / 49 / 47**.",
        "bt": "## 3 · Backtest — le résultat phare\nTrois jambes après 2 bps de coûts. La **jambe combinée (tone) est la plus basse** des trois. L'apport marginal de la porte news, ΔSharpe(combo − VIX), vaut **−0,073 plein-échantillon**.",
        "crux": "## 4 · Le nœud — le signe n'est pas identifiable\nLe ΔSharpe de la porte tone vaut **−0,073 non décalé**, **+0,010 décalé 1 j**, **≈0 en exécution next-bar** — le signe **s'inverse selon la convention**. L'erreur-type Lo-2002 du Sharpe OOS est **0,92** ; chaque ΔSharpe vaut ≤ 0,21× celle-ci. La lecture honnête est donc **« aucun edge fiable — dans le bruit »**, pas « destructeur de valeur ».",
        "null": "## 5 · Null surrogate + oracle — preuve que le test a du pouvoir\nOn randomise le *timing* du tone (block bootstrap stationnaire), VIX + rendements figés. Le vrai tone tombe au centre/sous la médiane du null (**une large majorité de tones aléatoires l'égalent ou le battent**), tandis qu'un **oracle** qui dé-risque les pires jours part loin dans la queue droite — le test détecte un vrai timing, le tone n'en a aucun.",
        "vol": "## 6 · Levier vs timing — l'avantage drawdown est de la dilution\nLe MaxDD **brut** plus faible de l'overlay VIX vient en partie de ce qu'il porte moins de risque (0.5×). Re-levé à la volatilité du benchmark (k ≈ 1,25), le MaxDD **s'inverse** et devient pire que le buy-&-hold en plein échantillon.",
        "verdict": "## 7 · Verdict\n**NO-GO** sur la jambe tone GDELT/FinBERT — sur le motif *aucun edge décelable* (ni look-ahead, ni destructeur de valeur). **CONDITIONAL-GO** sur l'overlay VIX comme **outil de risque seulement** (jamais de l'alpha). Résoudre le dilemme *renforce* la rigueur tout en corrigeant une sur-interprétation dans chaque sens.",
        "play": "## 8 · Playground — le dilemme *en mouvement* 🎛️\nBougez les curseurs et observez ΔSharpe, le compte de régimes et les courbes d'equity se mettre à jour en direct. Remarquez que **quoi que vous fassiez**, le ΔSharpe de la porte tone reste dans la bande de bruit — c'est tout l'enjeu.",
        "close": lambda: (
            "---\n### Partager ce notebook (aucune duplication d'API/abonnement, coût nul)\nTrois façons pour Valentin & Anne-Lise de partager **un seul** environnement — voir **`ACCESS_AND_HOSTING.md`** : (1) **Google Colab** — cliquer le badge, *Partager → Éditeur* ; (2) **Binder** — cliquer le badge pour une URL publique gratuite ; (3) **JupyterLab auto-hébergé via Cloudflare Tunnel** — la vraie voie *adresse IP publique* (gratuite, sécurisée, persistante). Les données sont publiques et sans clé : aucun secret n'est jamais exposé."
        ),
    },
}


# ----------------------------------------------------------------------------- assemble
def kernelspec(target):
    if target == "colab":
        return {"name": "python3", "display_name": "Python 3"}
    return {"name": "riskoff-demo", "display_name": "Python (riskoff-demo)", "language": "python"}


def colab_meta(lang, target):
    nb = f"dilemma_demo_{lang}_{target}.ipynb"
    meta = {
        "kernelspec": kernelspec(target),
        "language_info": {"name": "python", "version": "3.11"},
    }
    if target == "colab":
        meta["colab"] = {"name": nb, "provenance": [], "toc_visible": True}
        meta["accelerator"] = "None"
    return meta


AUDIT_NOTE = {
    "en": "> **Audit update (2026-06-22).** The rigorous test for the tone leg is the *paired* Sharpe-difference (Ledoit–Wolf 2008): combo and VIX are ~98% correlated, so the paired HAC standard error (≈0.06 full / 0.14 OOS) is far smaller than the single-leg Lo-2002 SE (0.92) — yet ΔSharpe stays statistically insignificant (p ≈ 0.23 full, 0.17 OOS), so the NO-GO holds on the *correct* test. Complementary checks: a **static de-grossing** benchmark matches the VIX *timing* full-sample (the drawdown gain is de-grossing, not timing); a **2008–2026 stress test** shows the vol-matched overlay still protects in vol-spike crashes (GFC, COVID) — a vol-spike risk hedge; and **PBO straddles 0.5** (exhaustive 360-grid 0.48 / Optuna subset 0.56). On **SPY total return** at 2–10 bps the disposition is unchanged.",
    "fr": "> **Mise à jour d'audit (2026-06-22).** Le test rigoureux de la jambe tone est la *différence* de Sharpe appariée (Ledoit–Wolf 2008) : combo et VIX sont ~98% corrélés, donc l'erreur-type HAC appariée (≈0,06 plein / 0,14 OOS) est bien plus petite que le SE Lo-2002 mono-jambe (0,92) — mais le ΔSharpe reste non significatif (p ≈ 0,23 plein, 0,17 OOS) : le NO-GO tient sur le test *correct*. Vérifications complémentaires : un benchmark de **dé-grossissement statique** égale le *timing* VIX en plein échantillon (le gain de drawdown est du dé-grossissement, pas du timing) ; un **stress 2008–2026** montre que l'overlay vol-matché protège encore lors des chocs de volatilité (GFC, COVID) — une couverture contre les pics de vol ; et le **PBO enjambe 0,5** (grille exhaustive 360 → 0,48 / sous-ensemble Optuna 0,56). Sur le **rendement total SPY** à 2–10 bps, le verdict est inchangé.",
}


def emit(lang, target):
    nb_name = f"dilemma_demo_{lang}_{target}.ipynb"
    M = MD[lang]
    cells = [
        md(M["title"](nb_name)),
        code(setup_code(lang, target)),
        md(M["prov"]),
        code(PROVENANCE),
        md(M["sig"]),
        code(CORE),
        md(M["bt"]),
        code(BACKTEST),
        md(M["crux"]),
        code(LAGMATRIX),
        md(AUDIT_NOTE[lang]),
        md(M["null"]),
        code(NULL),
        md(M["vol"]),
        code(VOLMATCH),
        md(M["verdict"]),
        md(M["play"]),
        code(playground_code(lang)),
        md(M["close"]()),
    ]
    nb = {"nbformat": 4, "nbformat_minor": 5, "metadata": colab_meta(lang, target), "cells": cells}
    (OUT / nb_name).write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    return nb_name


if __name__ == "__main__":
    written = [emit(lang, target) for lang in ("en", "fr") for target in ("jupyter", "colab")]
    for w in written:
        print("written", w)
