"""Statistical tests and robustness analyses of the article: paired tests for unseen reader groups (Table 4) and for
each reliability engine (Table 7), alternative official mappings, survey screening and simulated context shifts
(Table 8, Sections 4.2 and 5.5), between-group differences, vocabulary stability and the heterogeneous-group ablation
(Section 5.3). Writes results/robustness.json.
usage (from the repository root): python -m readcal.robustness
"""
import json
import os
import numpy as np
from scipy.stats import kruskal, wilcoxon

from readcal import core
from readcal.core import *  # noqa: F401,F403

out = {}
rng_b = np.random.default_rng(11)
LABS = (("strict", Y), ("lenient", YM))


def paired_stats(a, b):
    """mean difference a - b over readers, bootstrap 95% CI, Wilcoxon p and number of readers with a < b."""
    d = a - b
    boots = [rng_b.choice(d, len(d)).mean() for _ in range(2000)]
    return {"diff": float(d.mean()), "ci": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
            "p": float(wilcoxon(d).pvalue), "better": int((d < 0).sum()), "n": int(len(d))}


# alternative official mappings ---------------------------------------------------------------------------------------
RANGES = {"Almost Certain": (0.87, 0.99), "Highly Likely": (0.90, 1.00), "Likely": (0.66, 1.00),
          "Probable": (0.63, 0.87), "Probably": (0.63, 0.87), "About Even": (0.40, 0.60), "Probably Not": (0.20, 0.40),
          "Unlikely": (0.00, 0.33), "Highly Unlikely": (0.00, 0.10), "Almost No Chance": (0.02, 0.12)}
lo = np.array([RANGES[w][0] for w in OFFICIAL])
hi = np.array([RANGES[w][1] for w in OFFICIAL])


def choose_interval(p):
    """the phrase with the narrowest official range that contains p (closest value among equal widths)."""
    width = hi - lo
    inside = (p[:, None] >= lo[None, :]) & (p[:, None] <= hi[None, :])
    score = np.where(inside, width[None, :], 10 + np.abs(p[:, None] - (lo + hi)[None, :] / 2))
    return (score + np.abs(p[:, None] - official_vals[None, :]) * 1e-3).argmin(1)


def choose_range(p):
    """the phrase with the lowest expected Brier loss if its reading were uniform over its official range."""
    return ((official_vals[None, :] - p[:, None]) ** 2 + ((hi - lo) ** 2 / 12)[None, :]).argmin(1)


def choose(method, train, train_groups, p, bw=BW):  # noqa: F811  (adds the two mappings to core.choose)
    if method == "official_interval":
        return choose_interval(p)
    if method == "official_range":
        return choose_range(p)
    return core.choose(method, train, train_groups, p, bw)


def vocab_of(method):  # noqa: F811
    return V10 if method.endswith("10") or method.startswith("official") else V15


def protocol(p, y, methods, readers=None, groups=None, shift=None):
    """5 seeds x 5 reader folds; optional transformation of the held-out readings (simulated context shift)."""
    readers = R if readers is None else readers
    groups = GR if groups is None else groups
    split = {m: {"ece": [], "brier": []} for m in methods}
    per = {m: np.zeros((5, len(readers))) for m in methods}
    for seed in range(5):
        perm = np.random.default_rng(seed).permutation(len(readers))
        for fold in np.array_split(perm, 5):
            tr = np.setdiff1d(perm, fold)
            ev = readers[fold] if shift is None else np.clip(shift(readers[fold]), 0, 1)
            for m in methods:
                e, b, _, _ = reader_scores(choose(m, readers[tr], groups[tr], p), y, ev, vocab_of(m))
                split[m]["ece"].append(e.mean())
                split[m]["brier"].append(b.mean())
                per[m][seed, fold] = e
    return ({m: {k: float(np.mean(v)) for k, v in d.items()} for m, d in split.items()},
            {m: v.mean(0) for m, v in per.items()})


P_ = {lab: PS[("fuzzy_rules", lab)] for lab, _ in LABS}
stage1_brier = {lab: float(np.mean((P_[lab] - y) ** 2)) for lab, y in LABS}
out["stage1_brier_fuzzy"] = stage1_brier

out["official_mapping"] = {}
for lab, y in LABS:
    methods = ["official10", "official_interval", "official_range", "it2_10", "it2_15"]
    res, per = protocol(P_[lab], y, methods)
    out["official_mapping"][lab] = {m: {"ece": v["ece"], "excess_brier": v["brier"] - stage1_brier[lab]} for m, v in res.items()}
    out["official_mapping"][lab]["tests"] = {
        "readcal_vs_midpoint": paired_stats(per["it2_15"], per["official10"]),
        "readcal_vs_interval": paired_stats(per["it2_15"], per["official_interval"]),
        "readcal_vs_range": paired_stats(per["it2_15"], per["official_range"]),
        "readcal10_vs_midpoint": paired_stats(per["it2_10"], per["official10"])}
print("official mappings done")

# simulated context shifts of the held-out readings ---------------------------------------------------------------------
SHIFTS = {"up_0.05": lambda x: x + 0.05, "down_0.05": lambda x: x - 0.05,
          "regress_0.15": lambda x: x + 0.15 * (0.5 - x), "regress_0.30": lambda x: x + 0.30 * (0.5 - x)}
out["context_shift"] = {}
for name, f in SHIFTS.items():
    for lab, y in LABS:
        res, per = protocol(P_[lab], y, ["official10", "it2_15"], shift=f)
        out["context_shift"].setdefault(name, {})[lab] = {"official": res["official10"]["ece"], "readcal": res["it2_15"]["ece"],
                                                          "test": paired_stats(per["it2_15"], per["official10"])}
print("context shifts done")

# unseen reader groups (Table 4) and reliability engines (Table 7): paired tests against official meanings -------
out["logo_tests"] = {}
for lab, y in LABS:
    for g in GROUPS:
        te = GR == g
        e_off = reader_scores(choose("official10", R[~te], GR[~te], P_[lab]), y, R[te], V10)[0]
        e_rc = reader_scores(choose("it2_15", R[~te], GR[~te], P_[lab]), y, R[te], V15)[0]
        out["logo_tests"].setdefault(lab, {})[g] = paired_stats(e_rc, e_off)
out["engine_tests"] = {}
for name in ESTIMATORS:
    for lab, y in LABS:
        _, per = protocol(PS[(name, lab)], y, ["official10", "it2_15"])
        out["engine_tests"].setdefault(name, {})[lab] = paired_stats(per["it2_15"], per["official10"])
print("paired tests done")

# survey screening: removals per source, no exclusion, and other thresholds ------------------------------------------
source = np.array(["zonination"] * len(Rz) + ["fagen"] * len(Rf))
R_raw, GR_raw = np.vstack([Rz, Rf]), np.array(gz + gf)
rho = np.array([spearman(r_, np.median(R_raw, axis=0)) for r_ in R_raw])
out["removed_per_source"] = {s: int(((source == s) & (rho < SCREEN)).sum()) for s in ("zonination", "fagen")}
out["screening"] = {}
for t in (None, 0.3, 0.4, 0.5, 0.6, 0.7):
    keep_t = np.ones(len(R_raw), bool) if t is None else rho >= t
    key = "none" if t is None else str(t)
    out["screening"][key] = {"readers": int(keep_t.sum())}
    for lab, y in LABS:
        res, per = protocol(P_[lab], y, ["official10", "it2_15"], readers=R_raw[keep_t], groups=GR_raw[keep_t])
        out["screening"][key][lab] = {"official": res["official10"]["ece"], "readcal": res["it2_15"]["ece"],
                                      "test": paired_stats(per["it2_15"], per["official10"])}
print("screening done")

# between-group differences in the readings -------------------------------------------------------------------------
kw_p, ranges = [], []
for j in V15:
    samples = [R[GR == g, j] for g in GROUPS]
    kw_p.append(float(kruskal(*samples).pvalue))
    ranges.append(float(max(s.mean() for s in samples) - min(s.mean() for s in samples)))
out["group_differences"] = {"phrases": [CANON[j] for j in V15], "kruskal_p": kw_p, "range_of_group_means": ranges,
                            "n_significant_0.05": int(sum(p < 0.05 for p in kw_p)),
                            "mean_range": float(np.mean(ranges)), "max_range": float(np.max(ranges))}


# vocabulary stability over the 25 reader splits (five-phrase vocabularies, Section 5.3) ----------------------------
def greedy(train, train_groups, p, k):
    losses = []
    for g in sorted(set(train_groups)):
        tg = train[train_groups == g]
        if len(tg) < 10:
            continue
        cs = np.array([moments(mf(tg[:, j], BW)) for j in V15])
        losses.append((cs[None, :, 0] - p[:, None]) ** 2 + cs[None, :, 1])
    loss = np.max(losses, axis=0)
    order, best = [], np.full(len(p), np.inf)
    for _ in range(k):
        cand = [j for j in range(len(V15)) if j not in order]
        j = cand[int(np.argmin([np.minimum(best, loss[:, c]).sum() for c in cand]))]
        order.append(j)
        best = np.minimum(best, loss[:, j])
    return frozenset(CANON[V15[j]] for j in order)


out["vocab_stability"] = {}
for lab, _ in LABS:
    sets = []
    for seed in range(5):
        perm = np.random.default_rng(seed).permutation(len(R))
        for fold in np.array_split(perm, 5):
            tr = np.setdiff1d(perm, fold)
            sets.append(greedy(R[tr], GR[tr], P_[lab], 5))
    counts = {}
    for s in sets:
        for w in s:
            counts[w] = counts.get(w, 0) + 1
    out["vocab_stability"][lab] = {"distinct_sets": len(set(sets)),
                                   "phrase_counts": dict(sorted(counts.items(), key=lambda t: (-t[1], t[0])))}

# heterogeneous reader groups: the online group's readings are pulled towards 0.5 --------------------------------
shifted = GR == GROUPS[0]
out["heterogeneous"] = {}
for lam in (0.3, 0.5):
    Rh = R.copy()
    Rh[shifted] = Rh[shifted] + lam * (0.5 - Rh[shifted])
    widths = []
    for j in V15:
        mfs = [mf(Rh[GR == g, j], BW) for g in GROUPS]
        cl, cr = km_centroid(np.min(mfs, 0), np.max(mfs, 0))
        widths.append(cr - cl)
    out["heterogeneous"][str(lam)] = {"mean_centroid_interval_width": float(np.mean(widths))}
    for lab, y in LABS:
        mean_err = {m: [] for m in ("type1_15", "it2_15")}
        worst_group = {m: [] for m in ("type1_15", "it2_15")}
        per = {m: np.zeros((5, len(Rh))) for m in ("type1_15", "it2_15")}
        for seed in range(5):
            perm = np.random.default_rng(seed).permutation(len(Rh))
            for fold in np.array_split(perm, 5):
                tr = np.setdiff1d(perm, fold)
                for m in mean_err:
                    e = reader_scores(choose(m, Rh[tr], GR[tr], P_[lab]), y, Rh[fold], V15)[0]
                    mean_err[m].append(e.mean())
                    per[m][seed, fold] = e
                    worst_group[m].append(max(e[GR[fold] == g].mean() for g in GROUPS if (GR[fold] == g).any()))
        pr = {m: v.mean(0) for m, v in per.items()}
        out["heterogeneous"][str(lam)][lab] = {
            "type1_mean": float(np.mean(mean_err["type1_15"])), "it2_mean": float(np.mean(mean_err["it2_15"])),
            "type1_worst_group": float(np.mean(worst_group["type1_15"])), "it2_worst_group": float(np.mean(worst_group["it2_15"])),
            "shifted_group_it2_vs_type1": paired_stats(pr["it2_15"][shifted], pr["type1_15"][shifted])}

os.makedirs(RESULTS_DIR, exist_ok=True)
json.dump(out, open(os.path.join(RESULTS_DIR, "robustness.json"), "w"), indent=1)
print("written", os.path.join(RESULTS_DIR, "robustness.json"))
