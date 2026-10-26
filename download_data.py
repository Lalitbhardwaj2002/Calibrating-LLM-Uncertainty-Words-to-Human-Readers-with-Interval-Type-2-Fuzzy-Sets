"""Download the three public data sets used in the article into data/ from fixed versions and verify their SHA-256.
usage: python download_data.py           download missing files and check all of them
       python download_data.py --check   only check the files already in data/
"""
import hashlib
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
FILES = {
    "dataset.json": (
        "https://huggingface.co/datasets/potsawee/wiki_bio_gpt3_hallucination/resolve/"
        "b3cfb73209a8c51582fa1d9b7fe7e45fec5529b2/dataset.json",
        "9fea0263501d74b192b6f75dae5c25a67db7938e096df4aab18c65c42e83189c"),
    "probly.csv": (
        "https://raw.githubusercontent.com/zonination/perceptions/1dc967af4b8532114f89943cf9e588ec17e0b30d/probly.csv",
        "235c1b22fc8bd096f8235b93e8d4801bcaf5b6f042dd90cc81a0d3afa45e4ee9"),
    "survey-results.csv": (
        "https://raw.githubusercontent.com/wadefagen/datasets/d588d8f527f04771f8d3cc630cc29da53024cbc0/"
        "Perception-of-Probability-Words/survey-results.csv",
        "9fe1e4fbb463c04a3dbbf430dd5b094a9717e99263d55b9e4cb2c60e3c8ee285"),
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    check_only = "--check" in sys.argv[1:]
    os.makedirs(DATA_DIR, exist_ok=True)
    ok = True
    for name, (url, digest) in FILES.items():
        path = os.path.join(DATA_DIR, name)
        if not os.path.exists(path):
            if check_only:
                print(f"missing  {name}")
                ok = False
                continue
            print(f"download {name}")
            urllib.request.urlretrieve(url, path)
        if sha256(path) == digest:
            print(f"ok       {name}")
        else:
            print(f"MISMATCH {name}: the file differs from the version used in the article")
            ok = False
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
