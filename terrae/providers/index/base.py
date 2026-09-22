"""
terrae/providers/index/base.py
Abstract interface for all vector index backends.
Application logic must not import concrete implementations (FAISS etc.) directly.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import numpy as np


class IndexBackend(ABC):
    """
    Abstract vector index backend.

    Contract:
    - Vectors stored are float32, L2-normalised (inner product == cosine similarity).
    - Each vector is associated with a stable string tile_id.
    - Internal integer IDs are managed by the backend; callers use tile_ids only.
    - index_id identifies the index configuration for provenance.
    """

    @property
    @abstractmethod
    def index_id(self) -> str:
        """Human-readable identifier for provenance, e.g. 'faiss-flat-ip-dim512'."""

    @property
    @abstractmethod
    def embedding_dim(self) -> int:
        """Dimension this index was built for."""

    @property
    @abstractmethod
    def total_vectors(self) -> int:
        """Number of vectors currently stored."""

    @abstractmethod
    def add(self, tile_id: str, vector: np.ndarray) -> None:
        """
        Add a single L2-normalised float32 vector with its tile_id.
        Raises ValueError if tile_id already exists (duplicate guard).
        """

    @abstractmethod
    def add_batch(self, tile_ids: List[str], vectors: np.ndarray) -> None:
        """
        Add a batch of vectors. vectors shape: (N, dim).
        Raises ValueError if any tile_id already exists.
        """

    @abstractmethod
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int,
    ) -> List[Tuple[str, float]]:
        """
        Search for top_k nearest neighbours.
        Returns list of (tile_id, similarity_score) sorted by score descending.
        Returns empty list if index is empty.
        """

    @abstractmethod
    def contains(self, tile_id: str) -> bool:
        """Return True if tile_id is already indexed."""

    @abstractmethod
    def save(self, path: str) -> None:
        """Persist index to disk. path is a directory or file prefix."""

    @abstractmethod
    def load(self, path: str) -> None:
        """Load index from disk."""

    @abstractmethod
    def is_trained(self) -> bool:
        """For IVF-style indexes that need a training step. Flat indexes always return True."""
