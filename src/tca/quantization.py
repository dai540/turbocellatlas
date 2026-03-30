from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatArray = NDArray[np.float32]
IntArray = NDArray[np.int32]
SignArray = NDArray[np.int8]


def _l2_normalize(x: FloatArray, eps: float = 1e-12) -> FloatArray:
    norms = np.linalg.norm(x, axis=-1, keepdims=True)
    norms = np.maximum(norms, eps)
    return (x / norms).astype(np.float32, copy=False)


def _orthogonal_matrix(dimension: int, seed: int) -> FloatArray:
    rng = np.random.default_rng(seed)
    base = rng.normal(size=(dimension, dimension)).astype(np.float32)
    q, r = np.linalg.qr(base)
    signs = np.sign(np.diag(r))
    signs[signs == 0] = 1
    q = q * signs
    return q.astype(np.float32, copy=False)


def _sample_rotated_coordinate_distribution(
    dimension: int,
    n_samples: int,
    seed: int,
) -> FloatArray:
    rng = np.random.default_rng(seed)
    samples = rng.normal(size=(n_samples, dimension)).astype(np.float32)
    samples = _l2_normalize(samples)
    return samples[:, 0].astype(np.float32, copy=False)


def fit_scalar_codebook(
    bit_width: int,
    dimension: int,
    n_samples: int = 20000,
    seed: int = 0,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> FloatArray:
    if bit_width < 1:
        raise ValueError("bit_width must be >= 1")
    n_centroids = 2**bit_width
    data = np.sort(_sample_rotated_coordinate_distribution(dimension, n_samples, seed))
    quantiles = np.linspace(0.0, 1.0, n_centroids + 2, dtype=np.float32)[1:-1]
    centroids = np.quantile(data, quantiles).astype(np.float32)

    for _ in range(max_iter):
        boundaries = (centroids[:-1] + centroids[1:]) / 2.0
        labels = np.searchsorted(boundaries, data, side="left")
        updated = centroids.copy()
        for idx in range(n_centroids):
            mask = labels == idx
            if np.any(mask):
                updated[idx] = np.mean(data[mask], dtype=np.float32)
        shift = float(np.max(np.abs(updated - centroids)))
        centroids = updated
        if shift <= tol:
            break
    return centroids.astype(np.float32, copy=False)


@dataclass(slots=True)
class EncodedMSE:
    indices: IntArray


class TurboQuantMSE:
    def __init__(
        self,
        dimension: int,
        bit_width: int,
        *,
        seed: int = 0,
        monte_carlo_samples: int = 20000,
        lloyd_max_iter: int = 100,
        lloyd_tol: float = 1e-6,
    ) -> None:
        self.dimension = dimension
        self.bit_width = bit_width
        self.rotation = _orthogonal_matrix(dimension, seed)
        self._cached_query_bytes: bytes | None = None
        self._cached_query_rot: FloatArray | None = None
        self.codebook = fit_scalar_codebook(
            bit_width=bit_width,
            dimension=dimension,
            n_samples=monte_carlo_samples,
            seed=seed,
            max_iter=lloyd_max_iter,
            tol=lloyd_tol,
        )

    def encode(self, x: ArrayLike) -> EncodedMSE:
        array = np.asarray(x, dtype=np.float32)
        was_1d = array.ndim == 1
        if was_1d:
            array = array[None, :]
        rotated = array @ self.rotation.T
        boundaries = (self.codebook[:-1] + self.codebook[1:]) / 2.0
        indices = np.searchsorted(boundaries, rotated, side="left").astype(np.int32)
        return EncodedMSE(indices=indices[0] if was_1d else indices)

    def decode(self, encoded: EncodedMSE | ArrayLike) -> FloatArray:
        indices = encoded.indices if isinstance(encoded, EncodedMSE) else np.asarray(encoded, dtype=np.int32)
        was_1d = indices.ndim == 1
        if was_1d:
            indices = indices[None, :]
        quantized = self.codebook[indices]
        decoded = quantized @ self.rotation
        return decoded[0].astype(np.float32, copy=False) if was_1d else decoded.astype(np.float32, copy=False)

    def prepare_query(self, query: ArrayLike) -> FloatArray:
        query_arr = np.asarray(query, dtype=np.float32)
        key = query_arr.tobytes()
        if self._cached_query_bytes == key and self._cached_query_rot is not None:
            return self._cached_query_rot
        self._cached_query_bytes = key
        self._cached_query_rot = (query_arr @ self.rotation.T).astype(np.float32, copy=False)
        return self._cached_query_rot

    def approximate_inner_products(self, query: ArrayLike, encoded: EncodedMSE | ArrayLike) -> FloatArray:
        indices = encoded.indices if isinstance(encoded, EncodedMSE) else np.asarray(encoded, dtype=np.int32)
        query_rot = self.prepare_query(query)
        was_1d = indices.ndim == 1
        if was_1d:
            indices = indices[None, :]
        quantized = self.codebook[indices]
        scores = np.sum(quantized * query_rot[None, :], axis=1, dtype=np.float32)
        return np.asarray(float(scores[0]), dtype=np.float32) if was_1d else scores.astype(np.float32, copy=False)


@dataclass(slots=True)
class EncodedProd:
    indices: IntArray
    signs: SignArray
    residual_norms: FloatArray


class TurboQuantProd:
    def __init__(
        self,
        dimension: int,
        bit_width: int,
        *,
        seed: int = 0,
        monte_carlo_samples: int = 20000,
        lloyd_max_iter: int = 100,
        lloyd_tol: float = 1e-6,
    ) -> None:
        if bit_width < 2:
            raise ValueError("TurboQuantProd requires bit_width >= 2")
        self.dimension = dimension
        self.bit_width = bit_width
        self.mse_quantizer = TurboQuantMSE(
            dimension=dimension,
            bit_width=bit_width - 1,
            seed=seed,
            monte_carlo_samples=monte_carlo_samples,
            lloyd_max_iter=lloyd_max_iter,
            lloyd_tol=lloyd_tol,
        )
        rng = np.random.default_rng(seed + 1)
        self.projection = rng.normal(size=(dimension, dimension)).astype(np.float32)
        self.qjl_scale = np.float32(math.sqrt(math.pi / 2.0) / dimension)
        self._cached_query_bytes: bytes | None = None
        self._cached_query_rot: FloatArray | None = None
        self._cached_proj_query: FloatArray | None = None

    def encode(self, x: ArrayLike) -> EncodedProd:
        array = np.asarray(x, dtype=np.float32)
        was_1d = array.ndim == 1
        if was_1d:
            array = array[None, :]

        mse_encoded = self.mse_quantizer.encode(array)
        mse_decoded = self.mse_quantizer.decode(mse_encoded)
        residual = array - mse_decoded
        signs = np.sign(residual @ self.projection.T).astype(np.int8)
        signs[signs == 0] = 1
        residual_norms = np.linalg.norm(residual, axis=1).astype(np.float32)

        if was_1d:
            return EncodedProd(
                indices=mse_encoded.indices,
                signs=signs[0],
                residual_norms=np.asarray([residual_norms[0]], dtype=np.float32),
            )
        return EncodedProd(
            indices=mse_encoded.indices,
            signs=signs,
            residual_norms=residual_norms,
        )

    def decode(self, encoded: EncodedProd) -> FloatArray:
        indices = encoded.indices
        signs = encoded.signs
        norms = encoded.residual_norms

        was_1d = np.asarray(indices).ndim == 1
        if was_1d:
            indices = np.asarray(indices, dtype=np.int32)[None, :]
            signs = np.asarray(signs, dtype=np.int32)[None, :]
            norms = np.asarray(norms, dtype=np.float32)

        mse_part = self.mse_quantizer.decode(EncodedMSE(indices=indices))
        qjl_part = self.qjl_scale * norms[:, None] * (signs @ self.projection)
        decoded = mse_part + qjl_part
        return decoded[0].astype(np.float32, copy=False) if was_1d else decoded.astype(np.float32, copy=False)

    def prepare_query(self, query: ArrayLike) -> tuple[FloatArray, FloatArray]:
        query_arr = np.asarray(query, dtype=np.float32)
        key = query_arr.tobytes()
        if self._cached_query_bytes == key and self._cached_query_rot is not None and self._cached_proj_query is not None:
            return self._cached_query_rot, self._cached_proj_query
        self._cached_query_bytes = key
        self._cached_query_rot = self.mse_quantizer.prepare_query(query_arr)
        self._cached_proj_query = (self.projection @ query_arr).astype(np.float32, copy=False)
        return self._cached_query_rot, self._cached_proj_query

    def approximate_inner_products(self, query: ArrayLike, encoded: EncodedProd) -> FloatArray:
        query_rot, proj_query = self.prepare_query(query)

        indices = np.asarray(encoded.indices, dtype=np.int32)
        signs = np.asarray(encoded.signs, dtype=np.int8)
        norms = np.asarray(encoded.residual_norms, dtype=np.float32)

        was_1d = indices.ndim == 1
        if was_1d:
            indices = indices[None, :]
            signs = signs[None, :]
            norms = norms.reshape(1)

        mse_term = np.sum(self.mse_quantizer.codebook[indices] * query_rot[None, :], axis=1, dtype=np.float32)
        residual_term = self.qjl_scale * norms * (signs @ proj_query)
        scores = mse_term + residual_term.astype(np.float32, copy=False)
        return np.asarray(float(scores[0]), dtype=np.float32) if was_1d else scores.astype(np.float32, copy=False)


def exact_topk(
    query: ArrayLike,
    bank: ArrayLike,
    top_k: int,
    ids: Iterable[int] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    bank_array = np.asarray(bank, dtype=np.float32)
    query_array = np.asarray(query, dtype=np.float32)
    scores = bank_array @ query_array
    top_k = min(top_k, bank_array.shape[0])
    order = np.argpartition(-scores, kth=top_k - 1)[:top_k]
    order = order[np.argsort(-scores[order])]
    if ids is None:
        return order.astype(np.int32), scores[order].astype(np.float32)
    ids_array = np.asarray(list(ids), dtype=np.int32)
    return ids_array[order], scores[order].astype(np.float32)
