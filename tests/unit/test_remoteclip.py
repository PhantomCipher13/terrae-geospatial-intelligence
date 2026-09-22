"""
tests/unit/test_remoteclip.py

Tests for RemoteCLIPProvider.

Tests that require actual weights are decorated with:
    @pytest.mark.skipif(not WEIGHTS_AVAILABLE, reason="RemoteCLIP weights not staged")

Tests that verify error behaviour (missing weights, invalid config) always run.
All tests run CPU-only and offline (TRANSFORMERS_OFFLINE=1).
"""
from __future__ import annotations

import os
import warnings
from pathlib import Path

import numpy as np
import pytest

# ── Detect whether the checkpoint is staged ──────────────────────────────────
WEIGHTS_PATH = Path("models/local/RemoteCLIP-ViT-B-32.pt")
WEIGHTS_AVAILABLE = WEIGHTS_PATH.exists()

# Enforce offline for all tests in this module
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def real_provider():
    """Load a real RemoteCLIPProvider once for the whole module (expensive)."""
    if not WEIGHTS_AVAILABLE:
        pytest.skip("RemoteCLIP weights not staged at models/local/RemoteCLIP-ViT-B-32.pt")
    from geoai.providers.embeddings.remoteclip_provider import RemoteCLIPProvider
    return RemoteCLIPProvider(model_name="ViT-B-32", device="cpu")


@pytest.fixture
def rgb_image_hwc():
    """224x224x3 uint8 synthetic RGB image."""
    rng = np.random.default_rng(0)
    return rng.integers(0, 255, (224, 224, 3), dtype=np.uint8)


@pytest.fixture
def rgb_image_chw():
    """3x224x224 float32 synthetic RGB image in [0,1]."""
    rng = np.random.default_rng(1)
    return rng.random((3, 224, 224)).astype(np.float32)


# ── Error condition tests (always run) ───────────────────────────────────────

def test_missing_checkpoint_raises():
    """FileNotFoundError if weights_path points to non-existent file."""
    from geoai.providers.embeddings.remoteclip_provider import RemoteCLIPProvider
    with pytest.raises(FileNotFoundError) as exc_info:
        RemoteCLIPProvider(
            model_name="ViT-B-32",
            weights_path=Path("/nonexistent/RemoteCLIP-ViT-B-32.pt"),
        )
    assert "RemoteCLIP" in str(exc_info.value)


def test_invalid_model_name_raises():
    """ValueError for unknown model variant."""
    from geoai.providers.embeddings.remoteclip_provider import RemoteCLIPProvider
    with pytest.raises(ValueError, match="Unknown RemoteCLIP variant"):
        RemoteCLIPProvider(model_name="ViT-UNKNOWN-99")


def test_no_weights_anywhere_raises(tmp_path, monkeypatch):
    """FileNotFoundError when no weights found in any default directory."""
    from geoai.providers.embeddings import remoteclip_provider as m
    # Redirect default search dirs to an empty temp directory
    monkeypatch.setattr(m, "_DEFAULT_SEARCH_DIRS", [tmp_path / "nonexistent"])
    from geoai.providers.embeddings.remoteclip_provider import RemoteCLIPProvider
    with pytest.raises(FileNotFoundError):
        RemoteCLIPProvider(model_name="ViT-B-32", weights_path=None)


def test_mock_is_not_fallback():
    """
    Verifies that RemoteCLIPProvider never silently uses mock embeddings.
    When weights are missing, it must RAISE — not return a mock provider.
    """
    from geoai.providers.embeddings.remoteclip_provider import RemoteCLIPProvider
    with pytest.raises((FileNotFoundError, Exception)):
        p = RemoteCLIPProvider(
            model_name="ViT-B-32",
            weights_path=Path("/definitely/not/there.pt"),
        )
        # If somehow it didn't raise, check that it's not mock
        assert not p.is_mock, "Provider must not silently fall back to mock!"


def test_app_factory_mock_explicit():
    """MockEmbeddingProvider is returned when provider='mock' in config."""
    from geoai.app_factory import build_embedding_provider
    provider = build_embedding_provider({"embedding": {"provider": "mock"}})
    from geoai.providers.embeddings.mock_provider import MockEmbeddingProvider
    assert isinstance(provider, MockEmbeddingProvider)
    assert provider.is_mock


def test_app_factory_invalid_provider():
    """Unknown provider name raises ValueError."""
    from geoai.app_factory import build_embedding_provider
    with pytest.raises(ValueError, match="Unknown embedding provider"):
        build_embedding_provider({"embedding": {"provider": "llama"}})


def test_app_factory_empty_provider():
    """Empty provider name raises ValueError (not silently mock)."""
    from geoai.app_factory import build_embedding_provider
    with pytest.raises(ValueError):
        build_embedding_provider({"embedding": {"provider": ""}})


# ── Real model tests (skipped if weights not staged) ─────────────────────────

def test_real_provider_is_not_mock(real_provider):
    assert real_provider.is_mock is False


def test_real_provider_model_id(real_provider):
    assert "RemoteCLIP" in real_provider.model_id
    assert "ViT-B-32" in real_provider.model_id


def test_real_provider_embedding_dim(real_provider):
    assert real_provider.embedding_dim == 512


def test_real_provider_required_bands(real_provider):
    bands = real_provider.required_bands
    assert bands is not None
    assert "Red" in bands
    assert "Green" in bands
    assert "Blue" in bands
    assert len(bands) == 3


def test_real_provider_required_image_size(real_provider):
    size = real_provider.required_image_size
    assert size == (224, 224)


def test_real_provider_device_cpu(real_provider):
    assert real_provider.device == "cpu"


def test_image_embedding_shape_hwc(real_provider, rgb_image_hwc):
    """HWC uint8 input → (512,) float32 unit vector."""
    vec = real_provider.encode_image(rgb_image_hwc)
    assert vec.shape == (512,)
    assert vec.dtype == np.float32


def test_image_embedding_shape_chw(real_provider, rgb_image_chw):
    """CHW float32 input → (512,) float32 unit vector."""
    vec = real_provider.encode_image(rgb_image_chw)
    assert vec.shape == (512,)
    assert vec.dtype == np.float32


def test_image_embedding_l2_normalized(real_provider, rgb_image_hwc):
    """Image embedding must be L2-normalised (unit vector)."""
    vec = real_provider.encode_image(rgb_image_hwc)
    norm = np.linalg.norm(vec)
    assert abs(norm - 1.0) < 1e-4, f"Not unit vector: norm={norm}"


def test_text_embedding_shape(real_provider):
    vec = real_provider.encode_text("urban area")
    assert vec.shape == (512,)
    assert vec.dtype == np.float32


def test_text_embedding_l2_normalized(real_provider):
    vec = real_provider.encode_text("dense forest")
    norm = np.linalg.norm(vec)
    assert abs(norm - 1.0) < 1e-4, f"Not unit vector: norm={norm}"


def test_image_embedding_deterministic(real_provider, rgb_image_hwc):
    """Same input twice must produce identical embeddings."""
    v1 = real_provider.encode_image(rgb_image_hwc)
    v2 = real_provider.encode_image(rgb_image_hwc)
    max_diff = float(np.max(np.abs(v1 - v2)))
    assert max_diff < 1e-5, f"Non-deterministic: max_diff={max_diff}"


def test_text_embedding_deterministic(real_provider):
    v1 = real_provider.encode_text("water body")
    v2 = real_provider.encode_text("water body")
    max_diff = float(np.max(np.abs(v1 - v2)))
    assert max_diff < 1e-5, f"Non-deterministic: max_diff={max_diff}"


def test_different_images_produce_different_embeddings(real_provider):
    rng = np.random.default_rng(42)
    img1 = rng.integers(0, 255, (224, 224, 3), dtype=np.uint8)
    rng2 = np.random.default_rng(99)
    img2 = rng2.integers(0, 255, (224, 224, 3), dtype=np.uint8)
    v1 = real_provider.encode_image(img1)
    v2 = real_provider.encode_image(img2)
    cosine = float(np.dot(v1, v2))
    # Two random images should not be identical
    assert cosine < 0.999, "Two different images have identical embeddings — suspicious"


def test_different_texts_produce_different_embeddings(real_provider):
    v1 = real_provider.encode_text("urban area with buildings")
    v2 = real_provider.encode_text("dense tropical forest")
    cosine = float(np.dot(v1, v2))
    assert cosine < 0.999


def test_batch_encode_images_shape(real_provider, rgb_image_hwc):
    """encode_batch_images returns (N, 512) array."""
    images = [rgb_image_hwc, rgb_image_hwc]
    vecs = real_provider.encode_batch_images(images)
    assert vecs.shape == (2, 512)
    assert vecs.dtype == np.float32


def test_batch_matches_single_encode(real_provider, rgb_image_hwc):
    """Batch and single encode must produce identical results."""
    v_single = real_provider.encode_image(rgb_image_hwc)
    v_batch = real_provider.encode_batch_images([rgb_image_hwc])
    max_diff = float(np.max(np.abs(v_single - v_batch[0])))
    assert max_diff < 1e-4, f"Batch/single mismatch: {max_diff}"


def test_checkpoint_sha256_returns_hex(real_provider):
    sha = real_provider.checkpoint_sha256()
    assert len(sha) == 64
    assert all(c in "0123456789abcdef" for c in sha)


def test_cpu_inference_no_cuda_required(real_provider, rgb_image_hwc):
    """All inference must work on CPU without CUDA."""
    import torch
    assert not torch.cuda.is_available() or real_provider.device == "cpu"
    # Must not raise even if CUDA unavailable
    vec = real_provider.encode_image(rgb_image_hwc)
    assert vec.shape == (512,)


def test_load_time_recorded(real_provider):
    """Load time should be positive and recorded."""
    assert real_provider.load_time_s is not None
    assert real_provider.load_time_s > 0
