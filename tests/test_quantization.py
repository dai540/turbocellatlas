import numpy as np

from tca.quantization import TurboQuantMSE, TurboQuantProd


def test_mse_quantizer_roundtrip_shape():
    rng = np.random.default_rng(1)
    data = rng.normal(size=(16, 32)).astype(np.float32)
    quantizer = TurboQuantMSE(dimension=32, bit_width=2, seed=3, monte_carlo_samples=5000)
    encoded = quantizer.encode(data)
    decoded = quantizer.decode(encoded)

    assert decoded.shape == data.shape
    assert np.isfinite(decoded).all()


def test_prod_quantizer_scores_are_finite():
    rng = np.random.default_rng(5)
    data = rng.normal(size=(20, 24)).astype(np.float32)
    query = rng.normal(size=24).astype(np.float32)
    quantizer = TurboQuantProd(dimension=24, bit_width=3, seed=7, monte_carlo_samples=5000)
    encoded = quantizer.encode(data)
    scores = quantizer.approximate_inner_products(query, encoded)

    assert scores.shape == (20,)
    assert np.isfinite(scores).all()
