"""Reproduce every experiment, table and figure of the article (about one minute on a laptop).
usage: python run_all.py
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    ("download_data.py", "data sets (fixed versions, SHA-256 checked)"),
    ("readcal.experiment", "main experiment: Tables 2-7 and 9, data for Figs. 2-5"),
    ("readcal.robustness", "tests and robustness analyses: Tables 4, 7 and 8, Section 5.3"),
    ("readcal.nonfuzzy", "fuzzy summaries versus moments, non-fuzzy decoder: Sections 3.4 and 5.3"),
    ("readcal.figures", "Figs. 2-5"),
    ("readcal.flowchart", "Fig. 1"),
    ("readcal.tables", "all tables and quoted numbers in results/tables.md"),
]

for target, what in STEPS:
    print(f"\n== {what}", flush=True)
    cmd = [sys.executable, target] if target.endswith(".py") else [sys.executable, "-m", target]
    if subprocess.run(cmd, cwd=ROOT).returncode != 0:
        sys.exit(f"step failed: {target}")
print("\nDone. Results are in results/: results.json, robustness.json, nonfuzzy.json, tables.md and figures/.")
