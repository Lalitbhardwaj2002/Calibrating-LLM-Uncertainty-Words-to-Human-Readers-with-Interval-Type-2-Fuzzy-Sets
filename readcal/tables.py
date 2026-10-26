"""Tables 2-9 and the key numbers quoted in the text of the article, written as Markdown to results/tables.md.
Run after experiment.py, robustness.py and nonfuzzy.py.
usage (from the repository root): python -m readcal.tables
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.environ.get("READCAL_RESULTS", os.path.join(ROOT, "results"))
r = json.load(open(os.path.join(RESULTS_DIR, "results.json")))
rb = json.load(open(os.path.join(RESULTS_DIR, "robustness.json")))
nf = json.load(open(os.path.join(RESULTS_DIR, "nonfuzzy.json")))
LABELS = (("Strict", "main", "strict"), ("Lenient", "lenient", "lenient"))
METHODS = [("official10", "Official meanings"), ("crisp15", "Crisp lookup"), ("it2_10", "ReadCal, 10 phrases"),
           ("type1_15", "ReadCal, type-1 decoder"), ("it2_15", "ReadCal")]
GROUPS = ["Online community", "Students", "Graduates and others"]
ENGINES = [("basic_lr", "Logistic, 4 basic features", 4), ("ext_lr", "Logistic, 11 features", 11),
           ("fuzzy_rules", "ReadCal fuzzy engine (9 rules)", 2)]
SOURCES = {"Almost Certain": "Kent, 87–99%", "Highly Likely": "IPCC “very likely”, 90–100%", "Likely": "IPCC, 66–100%",
           "Probably": "Kent “probable”, 63–87%", "Probable": "Kent, 63–87%",
           "About Even": "Kent “chances about even”, 40–60%", "Probably Not": "Kent, 20–40%", "Unlikely": "IPCC, 0–33%",
           "Highly Unlikely": "IPCC “very unlikely”, 0–10%", "Almost No Chance": "Kent “almost certainly not”, 2–12%"}
lines = ["# Tables of the article, recomputed", ""]


def fp(p):
    if p < 0.001:
        return "< 0.001"
    return f"{p:.3f}" if p < 0.01 else f"{p:.2f}"


def signed(x, nd=4):
    return f"{x:+.{nd}f}".replace("-", "−")


def table(title, head, rows):
    lines.extend([f"**{title}**", "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)])
    lines.extend("| " + " | ".join(str(c) for c in row) + " |" for row in rows)
    lines.append("")


# Table 2 ------------------------------------------------------------------------------------------------------------
rows = []
for c in sorted(r["codebook"], key=lambda c: -c["mean"]):
    off = "—" if c["official"] is None else f"{c['official']:.2f}"
    rows.append([c["word"].lower(), off, SOURCES.get(c["word"], "—"), f"{c['mean']:.2f} ({c['sd']:.2f})",
                 f"[{c['centroid'][0]:.2f}, {c['centroid'][1]:.2f}]"])
table("Table 2. Official meanings, sources and human readings (type-2 centroid: Karnik–Mendel centroid interval)",
      ["Phrase", "Official meaning", "Source and range", "Human mean (SD)", "Type-2 centroid"], rows)

# Table 3 ------------------------------------------------------------------------------------------------------------
rows = []
for name, key, lab in LABELS:
    sb = r["stage1"]["estimators"]["fuzzy_rules"][lab]["brier"]
    for i, (m, label) in enumerate(METHODS):
        v = r[key]["random"][m]
        rows.append([name if i == 0 else "", label, f"{v['ece'][0]:.3f} ± {v['ece'][1]:.3f}",
                     f"{v['worst'][0]:.3f} ± {v['worst'][1]:.3f}", f"{100 * v['large'][0]:.1f} ± {100 * v['large'][1]:.1f}%",
                     f"{v['brier'][0] - sb:.4f} ± {v['brier'][1]:.4f}", f"{v['auroc'][0]:.3f} ± {v['auroc'][1]:.3f}"])
table("Table 3. Reader-side results over 25 reader splits, mean ± SD",
      ["Labels", "Method", "R-ECE", "Worst 10%", "Large misread", "Excess Brier", "AUROC"], rows)

# Table 4 ------------------------------------------------------------------------------------------------------------
rows = []
for m, label in METHODS:
    if m == "it2_10":
        continue
    rows.append([label] + [f"{r[key]['logo'][m][g]['ece']:.3f}" for _, key, _ in LABELS for g in GROUPS])
rows.append(["ReadCal vs official, p"] + [fp(rb["logo_tests"][lab][g]["p"]) for _, _, lab in LABELS for g in GROUPS])
table("Table 4. R-ECE for unseen reader groups (leave-one-group-out; p: paired Wilcoxon test)",
      ["Method", "Online (S)", "Students (S)", "Graduates (S)", "Online (L)", "Students (L)", "Graduates (L)"], rows)

# Table 5 ------------------------------------------------------------------------------------------------------------
rows = []
COMP = [("it2_15-official10", "ReadCal vs official meanings"), ("it2_15-crisp15", "ReadCal vs crisp lookup"),
        ("it2_15-type1_15", "ReadCal vs type-1 decoder"), ("it2_15-it2_10", "ReadCal vs 10 phrases")]
for name, key, _ in LABELS:
    for i, (k, label) in enumerate(COMP):
        v = r[key]["paired"][k]
        rows.append([name if i == 0 else "", label, signed(v["mean_diff"]), f"[{signed(v['ci'][0])}, {signed(v['ci'][1])}]",
                     fp(v["wilcoxon_p"]), v["readers_better"]])
table("Table 5. Paired comparisons over 165 readers (negative differences favour ReadCal)",
      ["Labels", "Comparison", "Mean difference", "95% CI", "Wilcoxon p", "Readers better"], rows)

# Table 6 ------------------------------------------------------------------------------------------------------------
rows = []
for e, label, n_in in ENGINES:
    s = r["stage1"]["estimators"][e]
    rows.append([label, n_in] + [f"{s[lab][k]:.3f}" for lab in ("strict", "lenient") for k in ("auroc", "ece", "brier")])
table("Table 6. Claim reliability estimators",
      ["Estimator", "Inputs", "AUROC (S)", "ECE (S)", "Brier (S)", "AUROC (L)", "ECE (L)", "Brier (L)"], rows)

# Table 7 ------------------------------------------------------------------------------------------------------------
rows = []
for e, label, _ in ENGINES:
    auc = r["stage1"]["estimators"][e]
    for i, (name, _, lab) in enumerate(LABELS):
        sb = auc[lab]["brier"]
        cells = []
        for m in ("official10", "crisp15", "it2_15"):
            v = r["by_estimator"][e][lab][m]
            star = "*" if m == "it2_15" and rb["engine_tests"][e][lab]["p"] < 0.01 else ""
            cells.append(f"{v['ece']:.3f} ({v['brier'] - sb:.4f}){star}")
        head = f"{label} ({auc['strict']['auroc']:.2f} / {auc['lenient']['auroc']:.2f})" if i == 0 else ""
        rows.append([head, name] + cells)
table("Table 7. R-ECE (excess Brier loss) for each reliability engine (*: p < 0.01 against official meanings)",
      ["Engine (AUROC S / L)", "Labels", "Official meanings", "Crisp lookup", "ReadCal decoder"], rows)

# Table 8 ------------------------------------------------------------------------------------------------------------
om, cs, sc = rb["official_mapping"], rb["context_shift"], rb["screening"]


def row8(label, off, rc, p):
    return [label] + [x for lab in ("strict", "lenient") for x in (f"{off(lab):.3f}", f"{rc(lab):.3f}", fp(p(lab)))]


rows = [row8("Main analysis (official midpoints)", lambda l: om[l]["official10"]["ece"], lambda l: om[l]["it2_15"]["ece"],
             lambda l: om[l]["tests"]["readcal_vs_midpoint"]["p"]),
        row8("Narrowest official range containing p", lambda l: om[l]["official_interval"]["ece"],
             lambda l: om[l]["it2_15"]["ece"], lambda l: om[l]["tests"]["readcal_vs_interval"]["p"]),
        row8("Expected loss over official range", lambda l: om[l]["official_range"]["ece"], lambda l: om[l]["it2_15"]["ece"],
             lambda l: om[l]["tests"]["readcal_vs_range"]["p"]),
        row8(f"No respondents excluded ({sc['none']['readers']} readers)", lambda l: sc["none"][l]["official"],
             lambda l: sc["none"][l]["readcal"], lambda l: sc["none"][l]["test"]["p"])]
for k, label in (("up_0.05", "Readings 0.05 higher"), ("down_0.05", "Readings 0.05 lower"),
                 ("regress_0.15", "Readings 15% closer to 0.5"), ("regress_0.30", "Readings 30% closer to 0.5")):
    rows.append(row8(label, lambda l, k=k: cs[k][l]["official"], lambda l, k=k: cs[k][l]["readcal"],
                     lambda l, k=k: cs[k][l]["test"]["p"]))
table("Table 8. R-ECE of official meanings and ReadCal under alternative settings (p: paired Wilcoxon test)",
      ["Setting", "Official (S)", "ReadCal (S)", "p (S)", "Official (L)", "ReadCal (L)", "p (L)"], rows)

# Table 9 ------------------------------------------------------------------------------------------------------------
LAB = {"accurate": "accurate", "minor_inaccurate": "minor error", "major_inaccurate": "major error"}
rows = []
for e in r["example"]:
    s = e["sentence"]
    rows.append([s if len(s) <= 55 else s[:52].rsplit(" ", 1)[0] + " …", LAB[e["label"]], f"{e['p']:.2f}",
                 e["official10"].lower(), e["it2_15"].lower(),
                 f"E {e['rule_levels'][0]}, S {e['rule_levels'][1]} → {e['rule_theta']:.2f}"])
table("Table 9. ReadCal output for one GPT-3 passage (strict labels)",
      ["Sentence (shortened)", "Label", "p", "Official", "ReadCal", "Fired rule"], rows)

# numbers quoted in the text -------------------------------------------------------------------------------------------
lines += ["**Numbers quoted in the text**", ""]
for name, key, lab in LABELS:
    x = r[key]
    off = x["random"]["official10"]["ece"][0]
    lines.append(f"- {name}: official speaker-side error {x['official_speaker_ece']:.3f}, reader-side {off:.3f} "
                 f"(ratio {off / x['official_speaker_ece']:.1f}); personal oracle {x['oracle15']:.3f}; reliabilities "
                 f"below 0.35 / 0.35–0.65 / above 0.65: {x['share_p_below_035']:.0%} / {x['share_p_035_065']:.0%} / "
                 f"{x['share_p_above_065']:.0%}")
gd = rb["group_differences"]
lines.append(f"- Group means of a phrase differ by {gd['mean_range']:.3f} on average and at most {gd['max_range']:.3f}; "
             f"Kruskal–Wallis p < 0.05 for {gd['n_significant_0.05']} of 15 phrases")
lines.append(f"- Respondents removed by screening: {rb['removed_per_source']}; thresholds: " + "; ".join(
    f"{k}: {v['readers']} readers, p (S) {fp(v['strict']['test']['p'])}, p (L) {fp(v['lenient']['test']['p'])}"
    for k, v in rb["screening"].items()))
for lab in ("strict", "lenient"):
    lines.append(f"- Vocabulary stability ({lab}, 25 splits): {rb['vocab_stability'][lab]['phrase_counts']}")
for lam, v in rb["heterogeneous"].items():
    lines.append(f"- Heterogeneous groups (shift {lam}): mean centroid-interval width {v['mean_centroid_interval_width']:.3f}; " +
                 "; ".join(f"{lab}: worst group type-1 {v[lab]['type1_worst_group']:.4f} vs type-2 {v[lab]['it2_worst_group']:.4f}, "
                           f"shifted group difference {v[lab]['shifted_group_it2_vs_type1']['diff']:.4f} "
                           f"(p {fp(v[lab]['shifted_group_it2_vs_type1']['p'])}, better for "
                           f"{v[lab]['shifted_group_it2_vs_type1']['better']} of 45)" for lab in ("strict", "lenient")))
lines.append(f"- Fuzzy centroid minus mean reading: {nf['centroid_minus_mean']['mean']:.4f} on average "
             f"(max {nf['centroid_minus_mean']['max']:.4f})")
for lab in ("strict", "lenient"):
    lines.append(f"- Non-fuzzy decoder ({lab}): R-ECE {nf[lab]['r_ece']}, same phrase {nf[lab]['same_phrase_share']}")
lines.append(f"- Kernel bandwidth: {r['by_bandwidth']}")
lines.append(f"- Anchor-phrase R²: {r['anchor_r2']}")

os.makedirs(RESULTS_DIR, exist_ok=True)
open(os.path.join(RESULTS_DIR, "tables.md"), "w", encoding="utf8").write("\n".join(lines) + "\n")
print("written", os.path.join(RESULTS_DIR, "tables.md"))
