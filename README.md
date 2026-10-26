# Calibrating LLM Uncertainty Words to Human Readers with Interval Type-2 Fuzzy Sets

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23656987.svg)](https://doi.org/10.5281/zenodo.23656987)

Code for the article of the same title by **Lalit Bhardwaj** and **M. K. Sharma**
(Department of Mathematics, Chaudhary Charan Singh University, Meerut, U.P., India).

Large language models qualify doubtful statements with hedges such as "likely", but a hedge protects a reader only if
the reader takes it to mean what the system intends. The article measures this **reader calibration gap** on held-out
survey readers and proposes **ReadCal**, an interval type-2 fuzzy system that

1. estimates the reliability of each claim from the LLM's self-consistency with a nine-rule fuzzy engine,
2. models how 165 survey respondents read 15 probability phrases as interval type-2 fuzzy sets, and
3. chooses, for each claim, the phrase with the lowest expected Brier loss for the worst-served reader group,
   with the fired rule as a rationale.

This repository reproduces every experiment, table and figure of the article from public data.

## Quick start

```bash
pip install -r requirements.txt
python run_all.py
```

`run_all.py` downloads the data (fixed versions, SHA-256 checked), runs all analyses and writes the outputs to
`results/`. It takes about a minute on a laptop. All random choices use fixed seeds, so the numbers are identical to
the article; reference outputs are in `expected_results/`.

The code was run with Python 3.11 and the package versions in `requirements.txt`. The figures use Times New Roman;
where that font is missing, matplotlib substitutes another serif font.

## Where each result comes from

| Article | Module | Output |
|---|---|---|
| Table 2, Fig. 4 (type-2 word models) | `readcal/experiment.py` | `results/results.json` (`codebook`) |
| Table 3 (reader-side results), Table 5 (paired tests) | `readcal/experiment.py` | `main`, `lenient` |
| Table 4 (unseen reader groups) | `readcal/experiment.py`, `readcal/robustness.py` | `logo`, `logo_tests` |
| Tables 6 and 7 (reliability engines) | `readcal/experiment.py`, `readcal/robustness.py` | `stage1`, `by_estimator`, `engine_tests` |
| Table 8 (official mappings, screening, context shifts) | `readcal/robustness.py` | `results/robustness.json` |
| Table 9 (worked example) | `readcal/experiment.py` | `example` |
| Section 3.4 and 5.3 (fuzzy summaries and moments, non-fuzzy decoder) | `readcal/nonfuzzy.py` | `results/nonfuzzy.json` |
| Section 5.3 (group differences, vocabulary stability, heterogeneous groups) | `readcal/robustness.py` | `results/robustness.json` |
| Fig. 1 (flowchart) | `readcal/flowchart.py` | `results/figures/fig1_flowchart.png` |
| Figs. 2-5 | `readcal/figures.py` | `results/figures/` |
| All tables as text | `readcal/tables.py` | `results/tables.md` |

`readcal/core.py` holds the shared parts: claim features, the fuzzy reliability engine and the logistic baselines
(cross-fitted by passage with isotonic calibration), survey screening, the type-1 and interval type-2 word models,
the decoders and the evaluation protocol (5 x 5 reader splits, leave-one-group-out, paired Wilcoxon tests).
Each module can also be run on its own from the repository root, for example `python -m readcal.experiment`.

## Data

| File | Source | Version | Licence |
|---|---|---|---|
| `dataset.json` | WikiBio GPT-3 hallucination data set (Manakul et al., 2023), <https://huggingface.co/datasets/potsawee/wiki_bio_gpt3_hallucination> | revision `b3cfb73` | CC BY-SA 3.0 (downloaded, not redistributed) |
| `probly.csv` | Zonination, Perceptions of probability, <https://github.com/zonination/perceptions> | commit `1dc967a` | MIT (copy included in `data/`) |
| `survey-results.csv` | W. Fagen-Ulmschneider, Perception of probability words, <https://github.com/wadefagen/datasets> | commit `d588d8f` | no licence stated (downloaded, not redistributed) |

`python download_data.py --check` verifies that the files in `data/` are exactly the versions used in the article.
No new data were collected.

## Citation

Please cite the article. The code is archived on Zenodo: version 1.0.0 at <https://doi.org/10.5281/zenodo.23656988>, all versions at <https://doi.org/10.5281/zenodo.23656987>. Citation metadata are in `CITATION.cff`.

## Licence

The code is released under the MIT licence (`LICENSE`). The data keep the licences of their sources.
