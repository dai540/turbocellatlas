import numpy as np

from turbocellatlas import SearchConfig, SearchIndex


def test_search_returns_expected_top_hit() -> None:
    embeddings = np.array(
        [
            [1.0, 0.0],
            [0.8, 0.2],
            [0.0, 1.0],
        ],
        dtype=np.float32,
    )
    metadata = [
        {"cell_id": "a", "disease": "IPF"},
        {"cell_id": "b", "disease": "IPF"},
        {"cell_id": "c", "disease": "Control"},
    ]

    index = SearchIndex(embeddings, metadata, SearchConfig(top_k=2))
    results = index.search(np.array([1.0, 0.0], dtype=np.float32))

    assert [item.item_id for item in results] == ["a", "b"]


def test_search_respects_metadata_filter() -> None:
    embeddings = np.array(
        [
            [1.0, 0.0],
            [0.9, 0.1],
            [0.0, 1.0],
        ],
        dtype=np.float32,
    )
    metadata = [
        {"cell_id": "a", "group": "x"},
        {"cell_id": "b", "group": "y"},
        {"cell_id": "c", "group": "y"},
    ]

    index = SearchIndex(embeddings, metadata)
    results = index.search(np.array([1.0, 0.0], dtype=np.float32), filters={"group": "y"})

    assert [item.item_id for item in results] == ["b", "c"]
