"""
geoai/providers/embeddings/base.py
Abstract interface for all embedding providers.
APPLICATION LOGIC MUST NOT IMPORT CONCRETE PROVIDERS DIRECTLY.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
import numpy as np


class EmbeddingProvider(ABC):
    """
    Abstract base for all embedding models.

    Contract:
      - encode_image returns a float32 numpy array of shape (embedding_dim,)
      - encode_text returns a float32 numpy array of shape (embedding_dim,)
      - All outputs are L2-normalised (unit vectors) so cosine sim == dot product
      - is_mock MUST be True for any placeholder/random implementation
      - model_id is a stable string identifier used in provenance records
    """

    @property
    @abstractmethod
    def model_id(self) -> str:
        """Stable string identifier for provenance. e.g. 'RemoteCLIP-ViT-B-32-v1'"""

    @property
    @abstractmethod
    def embedding_dim(self) -> int:
        """Dimension of output embedding vector."""

    @property
    @abstractmethod
    def is_mock(self) -> bool:
        """
        True only if this provider generates RANDOM / NON-SEMANTIC embeddings.
        Used to prevent mock results from polluting real benchmarks.
        """

    @property
    def required_bands(self) -> Optional[List[str]]:
        """
        If not None, list of band names this model requires in order.
        e.g. ['Red', 'Green', 'Blue']  or  ['B04', 'B03', 'B02']
        The sensor adapter uses this to select/reorder bands before inference.
        None means the provider handles band negotiation internally.
        """
        return None

    @property
    def required_image_size(self) -> Optional[tuple]:
        """
        (H, W) that this model expects. None = flexible.
        """
        return None

    @abstractmethod
    def encode_image(self, image_array: np.ndarray) -> np.ndarray:
        """
        Encode a preprocessed image tile to a unit embedding vector.

        Args:
            image_array: float32 numpy array.
                         Shape: (C, H, W) or (H, W, C) — document your convention.
                         Values: model-specific range (adapter must handle normalisation).

        Returns:
            float32 numpy array of shape (embedding_dim,), L2-normalised.
        """

    @abstractmethod
    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode a text query to a unit embedding vector.

        Args:
            text: Query string (English, no length limit enforced here).

        Returns:
            float32 numpy array of shape (embedding_dim,), L2-normalised.
        """

    def encode_batch_images(self, images: List[np.ndarray]) -> np.ndarray:
        """
        Default batch implementation — override for efficiency.

        Returns:
            float32 array of shape (N, embedding_dim).
        """
        return np.stack([self.encode_image(img) for img in images], axis=0)
