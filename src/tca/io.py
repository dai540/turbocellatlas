from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


def load_embeddings(path: str | Path) -> np.ndarray:
    file_path = Path(path)
    if file_path.suffix == ".npy":
        return np.load(file_path).astype(np.float32, copy=False)
    if file_path.suffix == ".npz":
        payload = np.load(file_path)
        if "embeddings" not in payload:
            raise ValueError("NPZ file must contain an 'embeddings' array")
        return payload["embeddings"].astype(np.float32, copy=False)
    raise ValueError(f"Unsupported embedding format: {file_path.suffix}")


def load_metadata(path: str | Path) -> list[dict[str, Any]]:
    file_path = Path(path)
    if file_path.suffix == ".jsonl":
        return [
            json.loads(line)
            for line in file_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    if file_path.suffix == ".json":
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("JSON metadata must be a list of objects")
        return payload
    if file_path.suffix == ".csv":
        with file_path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    raise ValueError(f"Unsupported metadata format: {file_path.suffix}")


def load_h5ad_embeddings(
    path: str | Path,
    *,
    embedding_key: str = "X",
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    try:
        import anndata as ad
    except ImportError as exc:
        raise ImportError("anndata is required to load .h5ad files. Install with `.[io]`.") from exc

    adata = ad.read_h5ad(path)
    if embedding_key == "X":
        matrix = np.asarray(adata.X, dtype=np.float32)
    else:
        if embedding_key not in adata.obsm:
            raise KeyError(f"Embedding key '{embedding_key}' was not found in adata.obsm")
        matrix = np.asarray(adata.obsm[embedding_key], dtype=np.float32)
    metadata = adata.obs.reset_index().to_dict(orient="records")
    return matrix, metadata


def save_json(path: str | Path, payload: Any) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
