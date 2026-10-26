"""Shared parts of ReadCal: claims and self-consistency features of the LLM, the fuzzy reliability engine and the
baseline estimators (cross-fitted by passage, isotonic calibration), the survey readers and their screening, the type-1
and interval type-2 fuzzy word models, the decoders, and the reader-side evaluation protocol.

Importing this module loads the data from data/ (or the folder in READCAL_DATA) and computes the cross-fitted
reliabilities of all three engines, which takes a few minutes. All random choices use fixed seeds.
"""
import csv
import json
import math
import os
import re
import sys
from collections import Counter
import numpy as np
from scipy.stats import wilcoxon
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("READCAL_DATA", os.path.join(ROOT, "data"))
RESULTS_DIR = os.environ.get("READCAL_RESULTS", os.path.join(ROOT, "results"))
DS, PROBLY, FAGEN = (os.path.join(DATA_DIR, f) for f in ("dataset.json", "probly.csv", "survey-results.csv"))
SCREEN = 0.5                   # minimum Spearman correlation with the median reader profile

# --------------------------------------------------------------------------- LLM claims and consistency features
data = json.load(open(DS, encoding="utf8"))
STOP = set("""a an the of and or in on at to for from by with as is was were be been are it its this that he she his her
they their them who which also after before into during while than then there where when one two first""".split())
FEATURES = ["mean word surprise", "max word surprise", "mean word support", "min word support", "mean bigram support",
            "min bigram support", "mean entity support", "min entity support", "position", "log length",
            "passage support"]


def toks(text):
    return re.findall(r"[a-z0-9]+", text.lower())


feats, labels, labels_major, groups_p, sent_text, ann_all = [], [], [], [], [], []
for pi, ex in enumerate(data):
    samples = [toks(s) for s in ex["gpt3_text_samples"]]
    corpus = Counter(t for s in samples for t in s) + Counter(toks(ex["gpt3_text"]))
    n_tok, vocab = sum(corpus.values()), len(corpus) + 1
    sets = [set(s) for s in samples]
    bisets = [set(zip(s, s[1:])) for s in samples]
    n_sent = len(ex["gpt3_sentences"])
    rows, psup = [], []
    for k, (sent, ann) in enumerate(zip(ex["gpt3_sentences"], ex["annotation"])):
        tk = toks(sent) or ["empty"]
        nll = [-math.log((corpus[t] + 1) / (n_tok + vocab)) for t in tk]
        content = [t for t in tk if t not in STOP and not t.isdigit()] or tk
        sup = [np.mean([t in s for s in sets]) for t in content]
        bg = list(zip(tk, tk[1:])) or [(tk[0], tk[0])]
        bsup = [np.mean([b in s for s in bisets]) for b in bg]
        raw = re.findall(r"[A-Za-z0-9]+", sent)
        ent = [w.lower() for i, w in enumerate(raw) if (w[0].isupper() and i > 0) or w.isdigit()]
        esup = [np.mean([t in s for s in sets]) for t in ent] or [np.mean(sup)]
        rows.append([np.mean(nll), np.max(nll), np.mean(sup), np.min(sup), np.mean(bsup), np.min(bsup),
                     np.mean(esup), np.min(esup), k / max(n_sent - 1, 1), math.log(len(tk))])
        psup.append(np.mean(sup))
        labels.append(1.0 if ann == "accurate" else 0.0)
        labels_major.append(0.0 if ann == "major_inaccurate" else 1.0)
        groups_p.append(pi)
        sent_text.append(sent)
        ann_all.append(ann)
    for r_ in rows:
        r_.append(float(np.mean(psup)))
    feats.extend(rows)
X, Y, YM, G = np.array(feats), np.array(labels), np.array(labels_major), np.array(groups_p)
BASIC, ALL, RULE_IN = [0, 1, 2, 3], list(range(11)), [7, 10]
LEVELS = ["low", "medium", "high"]


# --------------------------------------------------------------------------- reliability estimators
def tri_mfs(x, q):
    """low / medium / high triangular sets with peaks at the 10th, 50th and 90th percentiles (shoulders at ends)."""
    lo, md, hi = q
    m_lo = np.clip((md - x) / (md - lo + 1e-12), 0, 1)
    m_hi = np.clip((x - md) / (hi - md + 1e-12), 0, 1)
    return np.stack([m_lo, np.clip(1 - m_lo - m_hi, 0, 1), m_hi], 1)


def rule_fire(Xa, qs):
    """firing strength (product t-norm) of the 9 rules; rule index = 3*level(entity support) + level(passage support)."""
    F = np.ones((len(Xa), 1))
    for c, q in zip(RULE_IN, qs):
        m = tri_mfs(Xa[:, c], q)
        F = (F[:, :, None] * m[:, None, :]).reshape(len(Xa), -1)
    return F


class FuzzyRules:
    """zero-order TSK rule base whose consequents live on the log-odds scale: the output is
    sigma(b + sum_r phi_r(x) theta_r), with phi_r the normalised firing strengths. Consequents are fitted by
    L2-regularised logistic regression (default strength), so each rule alone gives sigma(b + theta_r)."""

    def fit(self, Xa, y):
        self.qs = [np.quantile(Xa[:, c], [0.1, 0.5, 0.9]) for c in RULE_IN]
        F = rule_fire(Xa, self.qs)
        self.support = F.sum(0)
        self.m = LogisticRegression(max_iter=3000).fit(F / F.sum(1, keepdims=True), y)
        b, th = self.m.intercept_[0], self.m.coef_[0]
        self.theta = 1 / (1 + np.exp(-(b + th)))
        return self

    def score(self, Xa):
        F = rule_fire(Xa, self.qs)
        return self.m.predict_proba(F / F.sum(1, keepdims=True))[:, 1]


class LR:
    def __init__(self, cols):
        self.cols = cols

    def fit(self, Xa, y):
        self.mu, self.sd = Xa[:, self.cols].mean(0), Xa[:, self.cols].std(0) + 1e-9
        self.m = LogisticRegression(max_iter=2000).fit((Xa[:, self.cols] - self.mu) / self.sd, y)
        return self

    def score(self, Xa):
        return self.m.predict_proba((Xa[:, self.cols] - self.mu) / self.sd)[:, 1]


ESTIMATORS = {"basic_lr": lambda: LR(BASIC), "ext_lr": lambda: LR(ALL), "fuzzy_rules": FuzzyRules}


def fit_calibrated(make, Xtr, ytr, Xte, seed):
    """estimator + isotonic calibration fitted on inner out-of-fold scores."""
    oof = np.zeros(len(ytr))
    idx = np.random.default_rng(seed).permutation(len(ytr))
    for f in np.array_split(idx, 5):
        m = np.ones(len(ytr), bool)
        m[f] = False
        oof[f] = make().fit(Xtr[m], ytr[m]).score(Xtr[f])
    iso = IsotonicRegression(y_min=0.01, y_max=0.99, out_of_bounds="clip").fit(oof, ytr)
    return iso.predict(make().fit(Xtr, ytr).score(Xte))


def crossfit(name, y):
    p = np.zeros(len(y))
    passages = np.random.default_rng(0).permutation(len(data))
    for k, fold in enumerate(np.array_split(passages, 5)):
        te = np.isin(G, fold)
        p[te] = fit_calibrated(ESTIMATORS[name], X[~te], y[~te], X[te], k)
    return p


def auroc(s, y):
    from scipy.stats import rankdata
    r = rankdata(s)
    pos = y == 1
    n1, n0 = pos.sum(), (~pos).sum()
    return float((r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def ece(p, y, bins=10):
    edges = np.quantile(p, np.linspace(0, 1, bins + 1))
    b = np.clip(np.searchsorted(edges[1:-1], p, side="right"), 0, bins - 1)
    return float(sum((b == k).mean() * abs(y[b == k].mean() - p[b == k].mean()) for k in range(bins) if (b == k).any()))


def diagram(p, y, bins=10):
    edges = np.linspace(0, 1, bins + 1)
    b = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    return [[float(p[b == k].mean()), float(y[b == k].mean()), int((b == k).sum())] for k in range(bins) if (b == k).sum() >= 10]


PS = {}
stage1 = {"sentences": int(len(Y)), "passages": len(data), "accurate_share": float(Y.mean()),
          "not_major_share": float(YM.mean()), "estimators": {}}
for lab, y in (("strict", Y), ("lenient", YM)):
    for name in ESTIMATORS:
        p = crossfit(name, y)
        PS[(name, lab)] = p
        stage1["estimators"].setdefault(name, {})[lab] = {"auroc": auroc(p, y), "ece": ece(p, y),
                                                         "brier": float(np.mean((p - y) ** 2)),
                                                         "diagram": diagram(p, y)}
stage1["single_feature_auroc"] = {FEATURES[j]: [auroc(X[:, j], Y), auroc(X[:, j], YM)] for j in range(11)}
rulebook = {}
for lab, y in (("strict", Y), ("lenient", YM)):
    fr = FuzzyRules().fit(X, y)
    rulebook[lab] = {"inputs": [FEATURES[c] for c in RULE_IN], "peaks": [[float(v) for v in q] for q in fr.qs],
                     "theta": [float(t) for t in fr.theta], "support": [float(s) for s in fr.support]}
    if lab == "strict":
        FR_FULL = fr

# --------------------------------------------------------------------------- human readers and fuzzy codebooks
CANON = ["Almost Certain", "Highly Likely", "Very Good Chance", "Probable", "Likely", "Probably", "We Believe",
         "Better Than Even", "About Even", "We Doubt", "Improbable", "Unlikely", "Probably Not", "Little Chance",
         "Almost No Chance", "Highly Unlikely", "Chances Are Slight"]


def norm(n):
    n = n.strip().strip('"').strip().lower()
    return "almost certain" if n == "almost certainly" else n


def load(path, group_fn):
    rows = list(csv.reader(open(path, newline="", encoding="utf8")))
    head = [norm(h) for h in rows[0]]
    idx = [head.index(c.lower()) for c in CANON]
    vals, grp = [], []
    for r_ in rows[1:]:
        try:
            vals.append([float(r_[i]) / 100 for i in idx])
            grp.append(group_fn(r_, rows[0]))
        except (ValueError, IndexError):
            continue
    return np.array(vals), grp


Rz, gz = load(PROBLY, lambda r_, h: "Online community")
Rf, gf = load(FAGEN, lambda r_, h: "Students" if r_[h.index("Your Highest Level of Education")].startswith("Currently pursuing an undergraduate") else "Graduates and others")
R = np.vstack([Rz, Rf])
GR = np.array(gz + gf)
med_all = np.median(R, axis=0)


def spearman(a, b):
    return np.corrcoef(np.argsort(np.argsort(a)), np.argsort(np.argsort(b)))[0, 1]


keep = np.array([spearman(r_, med_all) >= SCREEN for r_ in R])
n_raw = len(R)
R, GR = R[keep], GR[keep]
GROUPS = ["Online community", "Students", "Graduates and others"]

OFFICIAL = {"Almost Certain": 0.93, "Highly Likely": 0.95, "Likely": 0.83, "Probable": 0.75, "Probably": 0.75,
            "About Even": 0.50, "Probably Not": 0.30, "Unlikely": 0.165, "Highly Unlikely": 0.05,
            "Almost No Chance": 0.07}
V10 = [CANON.index(w) for w in OFFICIAL]
V15 = [i for i in range(17) if CANON[i] not in ("We Believe", "We Doubt")]
official_vals = np.array(list(OFFICIAL.values()))
GRID = np.linspace(0, 1, 101)
BW = 0.05


def mf(values, bw):
    """type-1 membership function: Gaussian kernel density of readers' answers, scaled to a peak of 1."""
    dens = np.exp(-0.5 * ((GRID[:, None] - values[None, :]) / bw) ** 2).sum(1)
    return dens / dens.max()


def moments(mu):
    c = (GRID * mu).sum() / mu.sum()
    return c, ((GRID - c) ** 2 * mu).sum() / mu.sum()


def km_centroid(lmf, umf):
    x = GRID
    cl = min(((x[:k] * umf[:k]).sum() + (x[k:] * lmf[k:]).sum()) / (umf[:k].sum() + lmf[k:].sum() + 1e-12) for k in range(1, len(x)))
    cr = max(((x[:k] * lmf[:k]).sum() + (x[k:] * umf[k:]).sum()) / (lmf[:k].sum() + umf[k:].sum() + 1e-12) for k in range(1, len(x)))
    return cl, cr


METHODS = ["official10", "crisp10", "type1_10", "it2_10", "crisp15", "type1_15", "it2_15"]


def vocab_of(method):
    return V10 if method.endswith("10") else V15


def choose(method, train, train_groups, p, bw=BW):
    voc = vocab_of(method)
    tr = train[:, voc]
    if method == "official10":
        return np.abs(p[:, None] - official_vals[None, :]).argmin(1)
    if method.startswith("crisp"):
        return np.abs(p[:, None] - np.median(tr, 0)[None, :]).argmin(1)
    if method.startswith("type1"):
        cs = np.array([moments(mf(tr[:, j], bw)) for j in range(len(voc))])
        return ((cs[None, :, 0] - p[:, None]) ** 2 + cs[None, :, 1]).argmin(1)
    if method.startswith("it2"):
        losses = []
        for g in sorted(set(train_groups)):
            tg = tr[train_groups == g]
            if len(tg) < 10:
                continue
            cs = np.array([moments(mf(tg[:, j], bw)) for j in range(len(voc))])
            losses.append((cs[None, :, 0] - p[:, None]) ** 2 + cs[None, :, 1])
        return np.max(losses, axis=0).argmin(1)
    raise ValueError(method)


def reader_scores(word_idx, y, readers, voc):
    """per-reader calibration error, Brier score and share of large (>0.15) misreadings; mean AUROC over 20 readers."""
    k = len(voc)
    counts = np.bincount(word_idx, minlength=k)
    acc = np.bincount(word_idx, weights=y, minlength=k) / np.maximum(counts, 1)
    w = counts / counts.sum()
    perceived = readers[:, voc]
    gap = np.abs(acc[None, :] - perceived)
    r_ece = (w[None, :] * gap).sum(1)
    brier = (w[None, :] * (acc[None, :] * (1 - perceived) ** 2 + (1 - acc[None, :]) * perceived ** 2)).sum(1)
    large = (w[None, :] * (gap > 0.15)).sum(1)
    auc = [auroc(r_[word_idx], y) for r_ in perceived[:20]]
    return r_ece, brier, large, float(np.mean(auc))


def oracle_scores(y, readers, p):
    """personal oracle: each reader receives the phrase whose own reading is closest to p (a floor, not a method)."""
    out = []
    for r_ in readers:
        idx = np.abs(r_[V15][None, :] - p[:, None]).argmin(1)
        out.append(reader_scores(idx, y, r_[None, :], V15)[0][0])
    return np.array(out)


def top_decile(x):
    return float(np.sort(x)[-max(1, int(np.ceil(0.1 * len(x)))):].mean())


def random_protocol(p, y, methods=METHODS, bw=BW, with_oracle=True):
    """5 seeds x 5 reader folds. Returns per-split summaries and per-reader errors averaged over seeds."""
    split = {m: {k: [] for k in ("ece", "worst", "brier", "large", "auroc")} for m in methods}
    per_reader = {m: np.zeros((5, len(R))) for m in list(methods) + (["oracle15"] if with_oracle else [])}
    for seed in range(5):
        perm = np.random.default_rng(seed).permutation(len(R))
        for fold in np.array_split(perm, 5):
            tr_idx = np.setdiff1d(perm, fold)
            for m in methods:
                idx = choose(m, R[tr_idx], GR[tr_idx], p, bw)
                e, b, lg, a = reader_scores(idx, y, R[fold], vocab_of(m))
                split[m]["ece"].append(e.mean())
                split[m]["worst"].append(top_decile(e))
                split[m]["brier"].append(b.mean())
                split[m]["large"].append(lg.mean())
                split[m]["auroc"].append(a)
                per_reader[m][seed, fold] = e
            if with_oracle:
                per_reader["oracle15"][seed, fold] = oracle_scores(y, R[fold], p)
    return split, {m: v.mean(0) for m, v in per_reader.items()}


def paired(per_reader, a, b, rng):
    d = per_reader[a] - per_reader[b]
    boots = [rng.choice(d, len(d)).mean() for _ in range(2000)]
    return {"mean_diff": float(d.mean()), "ci": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
            "wilcoxon_p": float(wilcoxon(d).pvalue), "readers_better": int((d < 0).sum())}


def evaluate(p, y):
    split, per_reader = random_protocol(p, y)
    out = {"random": {m: {k: [float(np.mean(v)), float(np.std(v))] for k, v in d.items()} for m, d in split.items()}}
    out["oracle15"] = float(per_reader["oracle15"].mean())
    out["oracle15_worst"] = top_decile(per_reader["oracle15"])
    for m in METHODS:
        out["random"][m]["worst_reader_level"] = top_decile(per_reader[m])
    wins = {}
    for a_, b_ in (("it2_15", "official10"), ("it2_15", "crisp15"), ("it2_15", "type1_15"), ("it2_15", "it2_10"),
                   ("it2_10", "official10")):
        for k in ("ece", "worst"):
            dlt = np.array(split[a_][k]) - np.array(split[b_][k])
            wins[f"{a_}-{b_}:{k}"] = int((dlt < 0).sum())
    out["split_wins"] = wins
    rng = np.random.default_rng(11)
    out["paired"] = {f"{a_}-{b_}": paired(per_reader, a_, b_, rng) for a_, b_ in
                     (("it2_15", "official10"), ("it2_15", "crisp15"), ("it2_15", "type1_15"), ("it2_15", "it2_10"))}
    out["logo"] = {}
    for m in METHODS:
        out["logo"][m] = {}
        for g in GROUPS:
            te = GR == g
            idx = choose(m, R[~te], GR[~te], p)
            e, b, lg, a = reader_scores(idx, y, R[te], vocab_of(m))
            out["logo"][m][g] = {"ece": float(e.mean()), "worst": top_decile(e), "large": float(lg.mean())}
    idx = choose("official10", R, GR, p)
    counts = np.bincount(idx, minlength=10)
    acc = np.bincount(idx, weights=y, minlength=10) / np.maximum(counts, 1)
    out["official_speaker_ece"] = float(((counts / counts.sum()) * np.abs(acc - official_vals)).sum())
    out["usage"] = {}
    for m in METHODS:
        voc = vocab_of(m)
        share = np.bincount(choose(m, R, GR, p), minlength=len(voc)) / len(p)
        out["usage"][m] = {CANON[voc[i]]: round(float(s), 3) for i, s in enumerate(share) if s > 0}
    out["share_p_below_035"] = float((p < 0.35).mean())
    out["share_p_035_065"] = float(((p >= 0.35) & (p <= 0.65)).mean())
    out["share_p_above_065"] = float((p > 0.65).mean())
    return out


