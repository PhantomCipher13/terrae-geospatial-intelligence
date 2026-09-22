"""
geoai/providers/embeddings/mock_provider.py

⚠️  MOCK EMBEDDING PROVIDER — FOR PIPELINE TESTING ONLY ⚠️

This provider generates DETERMINISTIC RANDOM embeddings seeded by a hash
of the input. Results are completely meaningless for retrieval quality.

USE ONLY when real model weights are not locally staged.
NEVER use for benchmarks, demos, or any result presented to users.

is_mock == True guards against accidental use in evaluation code.
"""
from __future__ import annotations
import hashlib
import numpy as np
from geoai.providers.embeddings.base import EmbeddingProvider


class MockEmbeddingProvider(EmbeddingProvider):
    """
    Deterministic random embedding provider.
    Seeds RNG from input bytes so the same input always returns the same vector.
    This makes pipeline tests reproducible without a real model.
    """
    _DIM = 512

    def __init__(self) -> None:
        import warnings
        warnings.warn(
            "\n⚠️  MockEmbeddingProvider is active. "
            "Embeddings are RANDOM and SEMANTICALLY MEANINGLESS. "
            "Do not use for retrieval evaluation or demos. "
            "Download RemoteCLIP weights and use RemoteCLIPProvider instead.",
            stacklevel=2,
        )

    @property
    def model_id(self) -> str:
        return "MOCK-random-v1"

    @property
    def embedding_dim(self) -> int:
        return self._DIM

    @property
    def is_mock(self) -> bool:
        return True

    def _seed_from_bytes(self, data: bytes) -> int:
        digest = hashlib.sha256(data).hexdigest()
        return int(digest[:8], 16)  # use first 32 bits as seed

    def encode_image(self, image_array: np.ndarray) -> np.ndarray:
        seed = self._seed_from_bytes(image_array.tobytes()[:4096])
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self._DIM).astype(np.float32)
        return vec / (np.linalg.norm(vec) + 1e-12)

    def encode_text(self, text: str) -> np.ndarray:
        seed = self._seed_from_bytes(text.encode("utf-8"))
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self._DIM).astype(np.float32)
        return vec / (np.linalg.norm(vec) + 1e-12)
