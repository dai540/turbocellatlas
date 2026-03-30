# TurboCell Atlas v0.2.0 Benchmark Report

- Dataset: `C:\Users\daiki\Desktop\codex\artifacts\data\GSE136831_subsample.h5ad`
- Model: `C:\Users\daiki\Desktop\codex\artifacts\data\scimilarity_py\scimilarity`
- Embedding: SCimilarity encoder v1 embedding + l2 normalization

## IPF alveolar macrophage centroid

| Method | Recall@100 | Top20 overlap | Avg latency ms | Candidate memory MB | Query mode |
| --- | ---: | ---: | ---: | ---: | --- |
| exact | 1.00 | 1.00 | 10.46 | 24.41 | broad |
| turboquant-prod-b2 | 0.62 | 0.70 | 47.51 | 1.72 | broad |
| turboquant-prod-b3 | 0.63 | 0.60 | 59.07 | 2.48 | broad |
| turboquant-prod-b4 | 0.58 | 0.65 | 55.03 | 3.24 | broad |
| faiss-pq-m8-nbits8 | 0.03 | 0.00 | 0.27 | 0.51 | broad |
| hnswlib-cosine | 1.00 | 1.00 | 0.35 | 31.69 | broad |

## IPF myofibroblast centroid

| Method | Recall@100 | Top20 overlap | Avg latency ms | Candidate memory MB | Query mode |
| --- | ---: | ---: | ---: | ---: | --- |
| exact | 1.00 | 1.00 | 11.98 | 24.41 | focused |
| turboquant-prod-b2 | 1.00 | 1.00 | 53.71 | 1.72 | focused |
| turboquant-prod-b3 | 1.00 | 1.00 | 47.34 | 2.48 | focused |
| turboquant-prod-b4 | 1.00 | 1.00 | 45.35 | 3.24 | focused |
| faiss-pq-m8-nbits8 | 0.30 | 0.05 | 0.17 | 0.51 | focused |
| hnswlib-cosine | 1.00 | 1.00 | 0.10 | 31.69 | focused |
