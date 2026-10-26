"""Checks behind Sections 3.4 and 5.3: (1) the centroid and spread of the kernel-based fuzzy sets equal the mean and
the variance (+ b^2) of a group's readings; (2) a non-fuzzy decoder built on empirical means and variances chooses
almost the same phrases as ReadCal and reaches a similar reader calibration error. Writes results/nonfuzzy.json.
usage (from the repository root): python -m readcal.nonfuzzy
"""
import json
import os
import numpy as np

from readcal.core import *  # noqa: F401,F403

out = {}
dc, dv = [], []
for g in GROUPS:
    for j in V15:
        x = R[GR == g, j]
        c, s2 = moments(mf(x, BW))
        dc.append(abs(c - x.mean()))
        dv.append(abs(s2 - (x.var() + BW ** 2)))
out["centroid_minus_mean"] = {"mean": float(np.mean(dc)), "max": float(np.max(dc))}
out["spread_minus_variance_plus_b2"] = {"mean": float(np.mean(dv)), "max": float(np.max(dv))}


def choose_empirical(train, train_groups, p, robust):
    tr = train[:, V15]
    if not robust:
        return ((tr.mean(0)[None, :] - p[:, None]) ** 2 + tr.var(0)[None, :]).argmin(1)
    losses = [(tr[train_groups == g].mean(0)[None, :] - p[:, None]) ** 2 + tr[train_groups == g].var(0)[None, :]
              for g in sorted(set(train_groups)) if (train_groups == g).sum() >= 10]
    return np.max(losses, axis=0).argmin(1)


for lab, y in (("strict", Y), ("lenient", YM)):
    p = PS[("fuzzy_rules", lab)]
    err = {k: [] for k in ("empirical_pooled", "empirical_group_robust", "type1_15", "it2_15")}
    same = {"empirical_pooled_vs_type1": [], "empirical_group_robust_vs_it2": []}
    for seed in range(5):
        perm = np.random.default_rng(seed).permutation(len(R))
        for fold in np.array_split(perm, 5):
            tr = np.setdiff1d(perm, fold)
            i1, i2 = choose("type1_15", R[tr], GR[tr], p), choose("it2_15", R[tr], GR[tr], p)
            e1, e2 = choose_empirical(R[tr], GR[tr], p, False), choose_empirical(R[tr], GR[tr], p, True)
            for k, idx in (("type1_15", i1), ("it2_15", i2), ("empirical_pooled", e1), ("empirical_group_robust", e2)):
                err[k].append(reader_scores(idx, y, R[fold], V15)[0].mean())
            same["empirical_pooled_vs_type1"].append(float((e1 == i1).mean()))
            same["empirical_group_robust_vs_it2"].append(float((e2 == i2).mean()))
    out[lab] = {"r_ece": {k: float(np.mean(v)) for k, v in err.items()},
                "same_phrase_share": {k: float(np.mean(v)) for k, v in same.items()}}
    print(lab, out[lab])

os.makedirs(RESULTS_DIR, exist_ok=True)
json.dump(out, open(os.path.join(RESULTS_DIR, "nonfuzzy.json"), "w"), indent=1)
print("written", os.path.join(RESULTS_DIR, "nonfuzzy.json"))
