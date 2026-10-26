# Data

Run `python download_data.py` from the repository root to place the data here. The script downloads fixed versions
and checks their SHA-256; `python download_data.py --check` only checks.

| File | Source and version | SHA-256 | Licence |
|---|---|---|---|
| `dataset.json` | huggingface.co/datasets/potsawee/wiki_bio_gpt3_hallucination, revision `b3cfb73209a8c51582fa1d9b7fe7e45fec5529b2` | `9fea0263501d74b192b6f75dae5c25a67db7938e096df4aab18c65c42e83189c` | CC BY-SA 3.0 |
| `probly.csv` | github.com/zonination/perceptions, commit `1dc967af4b8532114f89943cf9e588ec17e0b30d` | `235c1b22fc8bd096f8235b93e8d4801bcaf5b6f042dd90cc81a0d3afa45e4ee9` | MIT (`LICENSE-zonination-perceptions.txt`) |
| `survey-results.csv` | github.com/wadefagen/datasets, commit `d588d8f527f04771f8d3cc630cc29da53024cbc0`, folder `Perception-of-Probability-Words` | `9fe1e4fbb463c04a3dbbf430dd5b094a9717e99263d55b9e4cb2c60e3c8ee285` | none stated |

Only `probly.csv` is included in this repository, because its licence allows redistribution. The other two files are
downloaded from their sources.
