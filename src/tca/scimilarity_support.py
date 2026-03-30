from __future__ import annotations

from pathlib import Path

import anndata as ad
import numpy as np


def embed_h5ad_with_scimilarity(
    h5ad_path: str | Path,
    model_path: str | Path,
    *,
    buffer_size: int = 2048,
) -> tuple[np.ndarray, ad.AnnData]:
    try:
        from scimilarity import CellEmbedding
        from scimilarity.utils import align_dataset, lognorm_counts
    except ImportError as exc:
        raise ImportError(
            "scimilarity is required for embed_h5ad_with_scimilarity. Install with the 'scimilarity' extra."
        ) from exc

    adata = ad.read_h5ad(h5ad_path)
    cell_embedding = CellEmbedding(str(model_path))
    adata = align_dataset(adata, cell_embedding.gene_order)
    adata = lognorm_counts(adata)
    embeddings = cell_embedding.get_embeddings(adata.X, buffer_size=buffer_size).astype(np.float32)
    return embeddings, adata
