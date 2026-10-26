"""Figures 2-5 of the article from results/results.json (Times New Roman, sized for a 15.9 cm text width).
Fig. 1, the flowchart, is drawn by flowchart.py.
usage (from the repository root): python -m readcal.figures
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.environ.get("READCAL_RESULTS", os.path.join(ROOT, "results"))
r = json.load(open(os.path.join(RESULTS_DIR, "results.json")))
OUT = os.path.join(RESULTS_DIR, "figures")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 9})
BLUE, ORANGE, GREY, INK, GREEN = "#2457B5", "#A8521A", "#8A8A8A", "#1a1a1a", "#3B7D4F"


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# Fig. 2 the fuzzy engine: antecedent sets and the nine rule consequents -------------------------------------------
rb = r["rulebook"]["strict"]
fig, axes = plt.subplots(1, 3, figsize=(6.2, 2.15), dpi=300, gridspec_kw={"width_ratios": [1, 1, 0.95]})
names = ["Minimum entity support", "Passage support"]
for ax, q, nm in zip(axes[:2], rb["peaks"], names):
    x = np.linspace(0, 1, 401)
    lo, md, hi = q
    m_lo = np.clip((md - x) / (md - lo + 1e-12), 0, 1)
    m_hi = np.clip((x - md) / (hi - md + 1e-12), 0, 1)
    m_md = np.clip(1 - m_lo - m_hi, 0, 1)
    for m, lab, c in ((m_lo, "low", ORANGE), (m_md, "medium", GREY), (m_hi, "high", BLUE)):
        ax.plot(x, m, color=c, lw=1.2, label=lab)
    ax.set_xlabel(nm, fontsize=8)
    ax.set_ylim(0, 1.08)
    ax.set_xlim(0, 1)
    clean(ax)
axes[0].set_ylabel("Membership", fontsize=8)
axes[0].legend(fontsize=7, frameon=False, loc="center right")
th = np.array(rb["theta"]).reshape(3, 3)
ax = axes[2]
im = ax.imshow(th, cmap="Blues", vmin=0, vmax=1, origin="lower")
for i in range(3):
    for j in range(3):
        ax.text(j, i, f"{th[i, j]:.2f}", ha="center", va="center", fontsize=7.6,
                color="white" if th[i, j] > 0.55 else INK)
ax.set_xticks(range(3))
ax.set_xticklabels(["low", "med.", "high"], fontsize=7.4)
ax.set_yticks(range(3))
ax.set_yticklabels(["low", "med.", "high"], fontsize=7.4)
ax.set_xlabel("Passage support", fontsize=8)
ax.set_ylabel("Entity support", fontsize=8)
ax.set_title("Rule consequents", fontsize=8.2, pad=3)
for a, t in zip(axes, ("(a)", "(b)", "(c)")):
    a.text(-0.02, 1.02, t, transform=a.transAxes, fontsize=8.5, ha="right", va="bottom")
fig.tight_layout(pad=0.3)
fig.savefig(os.path.join(OUT, "fig2_fuzzy_engine.png"))
plt.close(fig)

# Fig. 3 the gap: official meaning vs human readings for 15 phrases ---------------------------------------------
cb = sorted(r["codebook"], key=lambda c: c["mean"])
fig, ax = plt.subplots(figsize=(6.2, 3.3), dpi=300)
for i, c in enumerate(cb):
    ax.plot([c["mean"] - c["sd"], c["mean"] + c["sd"]], [i, i], color=BLUE, lw=2.2, alpha=0.45, solid_capstyle="butt")
    ax.plot(c["mean"], i, "o", color=BLUE, ms=4.5)
    if c["official"] is not None:
        ax.plot(c["official"], i, "D", color=ORANGE, ms=4.5)
        ax.plot([c["official"], c["mean"]], [i, i], color=ORANGE, lw=0.8, ls=":")
ax.set_yticks(np.arange(len(cb)))
ax.set_yticklabels([c["word"].lower() for c in cb], fontsize=8.2)
ax.set_xlim(0, 1)
ax.set_xlabel("Probability", fontsize=8.5)
ax.plot([], [], "o", color=BLUE, ms=4.5, label="mean human reading")
ax.plot([], [], color=BLUE, lw=2.2, alpha=0.45, label="±1 SD (disagreement between readers)")
ax.plot([], [], "D", color=ORANGE, ms=4.5, label="official meaning (IPCC or Kent scale)")
ax.legend(loc="lower right", fontsize=7.6, frameon=False)
ax.grid(axis="x", color="#dddddd", lw=0.5)
clean(ax)
fig.tight_layout(pad=0.3)
fig.savefig(os.path.join(OUT, "fig3_official_vs_human.png"))
plt.close(fig)

# Fig. 4 type-2 fuzzy sets for six phrases ----------------------------------------------------------------------
grid = np.linspace(0, 1, 101)
cbd = {c["word"]: c for c in r["codebook"]}
words = ["Highly Likely", "Likely", "Very Good Chance", "About Even", "Little Chance", "Highly Unlikely"]
fig, axes = plt.subplots(2, 3, figsize=(6.2, 3.1), dpi=300, sharex=True, sharey=True)
for ax, w in zip(axes.ravel(), words):
    c = cbd[w]
    lmf, umf = np.array(c["lmf"]), np.array(c["umf"])
    ax.fill_between(grid, lmf, umf, color=BLUE, alpha=0.35, lw=0, label="footprint of uncertainty")
    ax.plot(grid, umf, color=BLUE, lw=0.8, label="upper membership function")
    ax.plot(grid, lmf, color=BLUE, lw=0.8, ls="--", label="lower membership function")
    if c["official"] is not None:
        ax.axvline(c["official"], color=ORANGE, lw=1.1, label="official meaning")
    ax.axvspan(c["centroid"][0], c["centroid"][1], ymin=0, ymax=0.06, color=INK, alpha=0.9, label="centroid interval")
    ax.set_title(f"“{w.lower()}” (SD {c['sd']:.2f})", fontsize=8.6, pad=2)
    ax.set_ylim(0, 1.08)
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0", "0.25", "0.5", "0.75", "1"], fontsize=7.6)
    clean(ax)
for ax in axes[1]:
    ax.set_xlabel("Probability", fontsize=8)
for ax in axes[:, 0]:
    ax.set_ylabel("Membership", fontsize=8)
h, l = axes[0, 0].get_legend_handles_labels()
want = ['upper membership function', 'lower membership function', 'footprint of uncertainty', 'official meaning', 'centroid interval']
hd = dict(zip(l, h))
fig.legend([hd[w] for w in want], want, loc="lower center", ncol=3, fontsize=7.6, frameon=False, bbox_to_anchor=(0.5, -0.01))
fig.tight_layout(pad=0.3, rect=(0, 0.115, 1, 1))
fig.savefig(os.path.join(OUT, "fig4_type2_sets.png"))
plt.close(fig)

# Fig. 5 vocabulary size (excess Brier loss) -----------------------------------------------------------------------
pb = {l: r["stage1"]["estimators"][r["primary"]][l]["brier"] for l in ("strict", "lenient")}
fig, axes = plt.subplots(1, 2, figsize=(6.2, 2.4), dpi=300, sharey=True)
for ax, lab, key, title in zip(axes, ("strict", "lenient"), ("main", "lenient"), ("(a) Strict labels", "(b) Lenient labels")):
    d = r["vocab_size"][lab]["by_k"]
    ks = sorted(int(k) for k in d)
    ax.plot(ks, [d[str(k)]["brier"] - pb[lab] for k in ks], marker="o", ms=3.2, color=BLUE, lw=1.0,
            label="ReadCal with k phrases")
    ax.axhline(r[key]["random"]["official10"]["brier"][0] - pb[lab], color=ORANGE, lw=1.0,
               label="official meanings (10 phrases)")
    ax.axvline(5, color=GREY, lw=0.6, ls=":")
    ax.set_xticks([2, 4, 5, 6, 8, 10, 12, 14])
    ax.set_xlabel("Number of phrases k", fontsize=8.5)
    ax.set_title(title, fontsize=9, pad=3)
    ax.legend(fontsize=7.2, frameon=False)
    clean(ax)
axes[0].set_ylabel("Brier loss caused by wording", fontsize=8.5)
fig.tight_layout(pad=0.3)
fig.savefig(os.path.join(OUT, "fig5_vocabulary_size.png"))
plt.close(fig)
print("figures written")
