import json

import numpy as np

from turbocellatlas.cli import main


def test_cli_search_writes_json(tmp_path) -> None:
    embeddings = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    query = np.array([1.0, 0.0], dtype=np.float32)
    embeddings_path = tmp_path / "embeddings.npy"
    query_path = tmp_path / "query.npy"
    output_path = tmp_path / "results.json"
    metadata_path = tmp_path / "metadata.jsonl"

    np.save(embeddings_path, embeddings)
    np.save(query_path, query)
    metadata_path.write_text('{"cell_id":"cell-1"}\n{"cell_id":"cell-2"}\n', encoding="utf-8")

    code = main(
        [
            "search",
            "--embeddings",
            str(embeddings_path),
            "--query",
            str(query_path),
            "--metadata",
            str(metadata_path),
            "--output",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert code == 0
    assert payload[0]["item_id"] == "cell-1"
