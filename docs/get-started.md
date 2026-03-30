# Get Started

## Install

```bash
pip install -e .[io,bench,dev]
```

Or create a local environment with:

```bash
conda env create -f environment.yml
```

## Demo assets

```bash
python scripts/setup_demo_assets.py
```

## First files to inspect

- `configs/wetlab_metadata_template.csv`
- `notebooks/wet_lab_walkthrough.ipynb`

## First search

```bash
tca search ^
  --embeddings data/reference.npy ^
  --metadata data/reference.jsonl ^
  --query data/query.npy ^
  --output artifacts/results.json
```
