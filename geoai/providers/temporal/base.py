"""
geoai/providers/temporal/base.py
Abstract interface for temporal encoding providers.
Temporal encoders produce embeddings that are aware of acquisition time,
enabling time-series retrieval and ordering across observations.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List
import numpy as np


@dataclass
class TemporalObservation:
    """
    A single observation in a temporal stack.
    """
    array: np.ndarray             # (C, H, W) float32
    timestamp: Optional[str]      # ISO 8601 date/datetime string or None
    sensor: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class TemporalEncoder(ABC):
    """
    Abstract temporal encoder.

    Takes an ordered sequence of raster observations and produces
    a temporal-aware representation for retrieval or change analysis.

    Designed from the start for N >= 2 observations (not only before/after pairs).
    """

    @property
    @abstractmethod
    def encoder_id(self) -> str:
        """Stable identifier for provenance."""

    @property
    @abstractmethod
    def embedding_dim(self) -> int:
        """Dimension of the temporal embedding output."""

    @property
    def min_observations(self) -> int:
        return 2

    @abstractmethod
    def encode_sequence(
        self,
        observations: List[TemporalObservation],
    ) -> np.ndarray:
        """
        Encode an ordered temporal sequence of observations.

        Args:
            observations: Ordered list (oldest first) of TemporalObservation.
                          Missing timestamps must be preserved as None — do not fabricate.
                          len(observations) >= min_observations.

        Returns:
            float32 numpy array of shape (embedding_dim,), L2-normalised.
        """
