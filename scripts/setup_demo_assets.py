from __future__ import annotations

import argparse
import shutil
import tarfile
from pathlib import Path
from urllib.request import urlretrieve


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT.parent / "artifacts" / "data"
MODEL_URL = "https://zenodo.org/records/10685499/files/model_v1.1.tar.gz?download=1"
DATA_URL = "https://zenodo.org/records/13685881/files/GSE136831_subsample.h5ad?download=1"


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return
    urlretrieve(url, destination)


def extract_model(archive_path: Path, target_dir: Path) -> None:
    if target_dir.exists():
        return
    target_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "r:gz") as handle:
        handle.extractall(target_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download demo assets for TurboCell Atlas.")
    parser.add_argument("--force", action="store_true", help="Redownload and re-extract assets.")
    args = parser.parse_args()

    dataset_path = DATA_DIR / "GSE136831_subsample.h5ad"
    model_archive = DATA_DIR / "model_v1.1.tar.gz"
    model_dir = DATA_DIR / "model_v1.1"

    if args.force:
        if dataset_path.exists():
            dataset_path.unlink()
        if model_archive.exists():
            model_archive.unlink()
        if model_dir.exists():
            shutil.rmtree(model_dir)

    download(DATA_URL, dataset_path)
    download(MODEL_URL, model_archive)
    extract_model(model_archive, DATA_DIR)

    print(f"Dataset: {dataset_path}")
    print(f"Model archive: {model_archive}")
    print(f"Model dir: {model_dir}")


if __name__ == "__main__":
    main()
