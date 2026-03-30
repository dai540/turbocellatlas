# Theory and Design

This page explains the reasoning behind TurboCell Atlas as a system, not just as a code package.

## Problem framing

Atlas-scale single-cell retrieval has two competing needs:

- we want a rich embedding space that preserves biological structure
- we want a search layer that remains cheap enough to operate at scale

If we optimize only for representation quality, memory and latency become painful. If we optimize only for retrieval compression, we risk damaging the biological meaning of the nearest neighbors. TurboCell Atlas therefore splits the problem in two.

## Representation layer versus retrieval layer

The representation layer answers:

- how should cells be embedded?
- what similarity notion is biologically meaningful?

The retrieval layer answers:

- how can we search that space efficiently?
- how much approximation is acceptable before reranking?

This repository assumes that a strong embedding model, such as SCimilarity, can remain upstream and mostly unchanged during Phase 1. The engineering novelty sits in the retrieval layer.

## Why TurboQuant

TurboQuant is attractive here because it offers a route toward aggressive compression while keeping candidate generation computationally cheap. The key intuition is that after random rotation, scalar quantization becomes effective, and the inner-product-oriented version can be improved by storing residual sign information.

In this repository:

- `TurboQuantMSE` is the simpler reconstruction-oriented variant
- `TurboQuantProd` adds a residual sign-based correction to better support inner-product retrieval

## Why exact reranking is mandatory

Approximate candidate generation is a means, not the end.

In single-cell atlas work, small ranking differences can matter because they affect:

- cell-type or state interpretation
- enrichment calculations
- what examples a scientist inspects first
- whether a query appears close to a pathological niche or not

For that reason, TurboCell Atlas treats exact reranking in the original embedding space as part of the default architecture rather than an optional refinement.

## Codebook fitting strategy

The current implementation uses a practical paper-based approach:

1. sample normalized random vectors
2. observe the rotated coordinate distribution
3. fit a one-dimensional scalar codebook with Lloyd iterations
4. quantize each rotated coordinate independently

This keeps the implementation inspectable and deterministic.

## Architecture

### 1. Configuration

`tca.config` validates search settings such as bit width, candidate counts, quantizer type, and random seed.

### 2. Quantization

`tca.quantization` owns:

- random rotation
- scalar codebook fitting
- `mse` and `prod` encoding and decoding
- exact top-k helper

### 3. Retrieval pipeline

`tca.pipeline` owns:

- index construction
- metadata filtering
- compressed candidate scoring
- exact reranking
- result packaging

### 4. Input/output

`tca.io` currently supports local array and metadata files, with optional `.h5ad` loading when `anndata` is available.

### 5. Benchmark adapters

`tca.benchmarks` keeps comparison backends separate from the core quantizer so the package can stay small while still supporting fair evaluation.

## Intended extension path

The package is designed to grow in this order:

1. direct SCimilarity-compatible embedding ingestion
2. public benchmark subsets and reproducible reports
3. CELLxGENE Census loaders and slicing helpers
4. richer experiment manifests and logging
5. incremental atlas update workflows
