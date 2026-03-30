import numpy as np

from tca.config import TurboQuantConfig
from tca.pipeline import SearchIndex


def test_search_returns_ranked_items():
    rng = np.random.default_rng(42)
    embeddings = rng.normal(size=(60, 48)).astype(np.float32)
    metadata = [
        {"cell_id": f"cell-{i}", "disease": "ild" if i % 2 == 0 else "control", "study": f"s{i % 3}"}
        for i in range(60)
    ]
    config = TurboQuantConfig(bit_width=3, candidate_k=20, rerank_k=5, seed=11, quantizer_kind="prod")
    index = SearchIndex.from_embeddings(embeddings=embeddings, metadata=metadata, config=config)

    results = index.search(embeddings[0], filters={"disease": "ild"})

    assert len(results.items) == 5
    assert results.items[0].metadata["disease"] == "ild"
    assert results.items[0].score >= results.items[-1].score


def test_exact_search_matches_self_hit():
    rng = np.random.default_rng(9)
    embeddings = rng.normal(size=(30, 16)).astype(np.float32)
    metadata = [{"cell_id": f"cell-{i}"} for i in range(30)]
    index = SearchIndex.from_embeddings(
        embeddings=embeddings,
        metadata=metadata,
        config=TurboQuantConfig(bit_width=2, candidate_k=10, rerank_k=3, seed=4, quantizer_kind="mse"),
    )

    results = index.search_exact(embeddings[7])

    assert results.items[0].item_id == "cell-7"


def test_unknown_filter_returns_no_results():
    rng = np.random.default_rng(3)
    embeddings = rng.normal(size=(12, 8)).astype(np.float32)
    metadata = [{"cell_id": f"cell-{i}", "disease": "ild"} for i in range(12)]
    index = SearchIndex.from_embeddings(
        embeddings=embeddings,
        metadata=metadata,
        config=TurboQuantConfig(bit_width=2, candidate_k=6, rerank_k=3, seed=2, quantizer_kind="mse"),
    )

    results = index.search(embeddings[0], filters={"missing_key": "x"})

    assert results.items == []
    assert results.filtered_count == 0
