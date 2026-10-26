"""Main experiment of the article (Sections 4-5): reader-side results (Table 3), unseen reader groups (Table 4),
paired comparisons (Table 5), reliability engines (Tables 6-7), vocabulary size (Fig. 5), the fuzzy word models
(Table 2, Fig. 4) and the worked example (Table 9). Writes results/results.json.
usage (from the repository root): python -m readcal.experiment
"""
import json
import os
import numpy as np
from scipy.stats import spearmanr

from readcal.core import *  # noqa: F401,F403

# ReadCal's own fuzzy rule engine is the primary reliability estimator; the logistic models are baselines
PRIMARY = "fuzzy_rules"
main = evaluate(PS[(PRIMARY, "strict")], Y)
lenient = evaluate(PS[(PRIMARY, "lenient")], YM)

# --------------------------------------------------------------------------- reliability quality and sensitivity
SENS_METHODS = ["official10", "crisp15", "type1_15", "it2_15"]
by_estimator = {}
for name in ESTIMATORS:
    for lab, y in (("strict", Y), ("lenient", YM)):
        split, per_reader = random_protocol(PS[(name, lab)], y, SENS_METHODS, with_oracle=False)
        by_estimator.setdefault(name, {})[lab] = {m: {k: float(np.mean(split[m][k])) for k in ("ece", "worst", "brier", "large")}
                                                  for m in SENS_METHODS}
# per-phrase bins: how well the claims given each phrase match its reading (full reader set, for diagnosis)
bins = {}
for name in ESTIMATORS:
    for lab, y in (("strict", Y), ("lenient", YM)):
        p = PS[(name, lab)]
        for m in ("official10", "it2_15"):
            voc = vocab_of(m)
            idx = choose(m, R, GR, p)
            out = {}
            for h in np.unique(idx):
                sel = idx == h
                out[CANON[voc[h]]] = {"n": int(sel.sum()), "mean_p": float(p[sel].mean()), "acc": float(y[sel].mean()),
                                      "reader_mad": float(np.abs(R[:, voc[h]] - y[sel].mean()).mean())}
            bins.setdefault(name, {}).setdefault(lab, {})[m] = out
by_bandwidth = {}
for bw in (0.03, 0.05, 0.08, 0.12):
    for lab, y in (("strict", Y), ("lenient", YM)):
        split, _ = random_protocol(PS[(PRIMARY, lab)], y, ["type1_15", "it2_15"], bw=bw, with_oracle=False)
        by_bandwidth.setdefault(str(bw), {})[lab] = {m: float(np.mean(split[m]["ece"])) for m in ("type1_15", "it2_15")}

# how much of one person's reading can a few answers about other phrases predict? (5-fold cross-validated R^2)
others = [i for i in range(17) if i not in V10]
r2 = {}
perm = np.random.default_rng(3).permutation(len(R))
for j in V10:
    pred = np.zeros(len(R))
    for fold in np.array_split(perm, 5):
        tr = np.setdiff1d(perm, fold)
        A = np.hstack([R[tr][:, others], np.ones((len(tr), 1))])
        B = np.linalg.solve(A.T @ A + 0.1 * np.eye(A.shape[1]), A.T @ R[tr][:, j])
        pred[fold] = np.hstack([R[fold][:, others], np.ones((len(fold), 1))]) @ B
    r2[CANON[j]] = float(1 - ((pred - R[:, j]) ** 2).sum() / ((R[:, j] - R[:, j].mean()) ** 2).sum())


# --------------------------------------------------------------------------- how many phrases are needed?
def greedy_vocab(train, train_groups, p):
    """forward selection of phrases from the 15 that minimises the worst-group expected reader Brier loss over the
    claims (the same type-2 loss as the decoder; uses reliabilities only, no claim labels)."""
    losses = []
    for g in sorted(set(train_groups)):
        tg = train[train_groups == g]
        if len(tg) < 10:
            continue
        cs = np.array([moments(mf(tg[:, j], BW)) for j in V15])
        losses.append((cs[None, :, 0] - p[:, None]) ** 2 + cs[None, :, 1])
    loss = np.max(losses, axis=0)
    order, best = [], np.full(len(p), np.inf)
    for _ in range(len(V15)):
        cand = [j for j in range(len(V15)) if j not in order]
        j = cand[int(np.argmin([np.minimum(best, loss[:, c]).sum() for c in cand]))]
        order.append(j)
        best = np.minimum(best, loss[:, j])
    return order, loss


vocab_size = {}
for lab, y in (("strict", Y), ("lenient", YM)):
    p = PS[(PRIMARY, lab)]
    acc_k = {k: {"ece": [], "brier": [], "large": []} for k in range(2, len(V15) + 1)}
    for seed in range(5):
        perm = np.random.default_rng(seed).permutation(len(R))
        for fold in np.array_split(perm, 5):
            tr_idx = np.setdiff1d(perm, fold)
            order, loss = greedy_vocab(R[tr_idx], GR[tr_idx], p)
            for k in acc_k:
                sub = order[:k]
                idx = np.array(sub)[loss[:, sub].argmin(1)]
                e, b, lg, _ = reader_scores(idx, y, R[fold], V15)
                acc_k[k]["ece"].append(e.mean())
                acc_k[k]["brier"].append(b.mean())
                acc_k[k]["large"].append(lg.mean())
    order_full, _ = greedy_vocab(R, GR, p)
    vocab_size[lab] = {"order": [CANON[V15[j]] for j in order_full],
                       "by_k": {str(k): {m: float(np.mean(v)) for m, v in d.items()} for k, d in acc_k.items()}}

# --------------------------------------------------------------------------- codebook description and an example
codebook = []
for i in V15:
    mfs = [mf(R[GR == g, i], BW) for g in GROUPS]
    lmf, umf = np.min(mfs, 0), np.max(mfs, 0)
    cl, cr = km_centroid(lmf, umf)
    codebook.append({"word": CANON[i], "official": OFFICIAL.get(CANON[i]), "mean": float(R[:, i].mean()),
                     "sd": float(R[:, i].std()), "median": float(np.median(R[:, i])), "centroid": [float(cl), float(cr)],
                     "group_means": {g: float(R[GR == g, i].mean()) for g in GROUPS},
                     "lmf": [round(float(x), 4) for x in lmf], "umf": [round(float(x), 4) for x in umf]})

agreement = {lab: float(spearmanr(PS[("fuzzy_rules", lab)], PS[("ext_lr", lab)]).correlation) for lab in ("strict", "lenient")}
P = PS[(PRIMARY, "strict")]
full = {m: choose(m, R, GR, P) for m in METHODS}
best, best_key = None, (False, False, -1, -1)
for pi in range(len(data)):
    sel = np.where(G == pi)[0]
    if 4 <= len(sel) <= 6 and 0 < Y[sel].sum() < len(sel):
        diff = sum(CANON[V10[full["official10"][i]]] != CANON[V15[full["it2_15"][i]]] for i in sel)
        spread = P[sel].max() - P[sel].min()
        good = (P[sel][Y[sel] == 1].max() > 0.75) and (P[sel][Y[sel] == 0].min() < 0.2)
        key = (good, len(set(full["it2_15"][sel])) >= 3, diff, spread)
        if key > best_key:
            best, best_key = pi, key
sel = np.where(G == best)[0]
F_ex = rule_fire(X[sel], FR_FULL.qs)
example = []
for k, i in enumerate(sel):
    top = int(F_ex[k].argmax())
    lv = [LEVELS[top // 3], LEVELS[top % 3]]
    example.append({"sentence": sent_text[i], "label": ann_all[i], "p": float(P[i]),
                    "official10": CANON[V10[full["official10"][i]]], "type1_15": CANON[V15[full["type1_15"][i]]],
                    "it2_15": CANON[V15[full["it2_15"][i]]], "rule_levels": lv, "rule_theta": float(FR_FULL.theta[top]),
                    "inputs": [float(X[i, c]) for c in RULE_IN]})

summary = {"stage1": stage1, "rulebook": rulebook, "readers_raw": int(n_raw), "readers_kept": int(len(R)),
           "group_sizes": {g: int((GR == g).sum()) for g in GROUPS}, "primary": PRIMARY, "main": main,
           "lenient": lenient, "by_estimator": by_estimator, "by_bandwidth": by_bandwidth, "anchor_r2": r2, "rules_vs_lr_spearman": agreement, "vocab_size": vocab_size, "bins": bins,
           "codebook": codebook, "example": example, "example_passage": int(best)}
os.makedirs(RESULTS_DIR, exist_ok=True)
json.dump(summary, open(os.path.join(RESULTS_DIR, "results.json"), "w"), indent=1)

print(json.dumps({k: {e: {l: {m: round(v, 3) for m, v in d.items() if m != "diagram"} for l, d in x.items()}
                      for e, x in stage1["estimators"].items()} for k in ["x"]}, indent=0))
for name, res in (("STRICT", main), ("LENIENT", lenient)):
    print("==", name, "official speaker-side", round(res["official_speaker_ece"], 4), "oracle", round(res["oracle15"], 4),
          "p shares", round(res["share_p_below_035"], 2), round(res["share_p_035_065"], 2), round(res["share_p_above_065"], 2))
    for m in METHODS:
        x = res["random"][m]
        print(f"  {m:11s} R-ECE {x['ece'][0]:.4f}+-{x['ece'][1]:.4f} worst {x['worst'][0]:.4f} large {x['large'][0]:.3f} "
              f"brier {x['brier'][0]:.4f} auroc {x['auroc'][0]:.3f}")
    print("  wins", res["split_wins"])
    for k, v in res["paired"].items():
        print("  paired", k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()})
    for m in METHODS:
        print("  LOGO", m, {g: round(v["ece"], 4) for g, v in res["logo"][m].items()})
    print("  usage it2_15", res["usage"]["it2_15"])
print("primary", PRIMARY, "agreement", agreement)
for e_, d_ in by_estimator.items():
    for l_, x_ in d_.items():
        print("  by estimator", e_, l_, {m: {k: round(v, 4) for k, v in mm.items()} for m, mm in x_.items()})
print("by bandwidth", json.dumps(by_bandwidth))
for lab_, v_ in vocab_size.items():
    print("vocab", lab_, v_["order"][:8], {k: round(d["ece"], 4) for k, d in v_["by_k"].items()})
print("anchor R2", {k: round(v, 2) for k, v in r2.items()})
for e in example:
    print(f"  {e['label']:18s} p={e['p']:.2f} off={e['official10']:16s} it2={e['it2_15']:16s} rule={e['rule_levels']} {e['rule_theta']:.2f} | {e['sentence'][:60]}")
