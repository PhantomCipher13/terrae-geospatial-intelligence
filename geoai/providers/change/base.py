"""
geoai/providers/change/base.py
Abstract interface for change detection providers.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Any
import numpy as np
from geoai.core.result import ChangeVerdict, RegistrationResult


@dataclass
class ChangeEvidence:
    """
    Evidence from a single change detection method for a single image pair.
    Missing values must be None — never fabricated.
    """
    method: str                             # e.g. 'spectral-diff-ndvi', 'changeformer-v1'
    change_mask: Optional[np.ndarray] = None  # bool (H, W) — True = changed pixel
    change_probability: Optional[np.ndarray] = None  # float32 (H, W) in [0,1]
    change_fraction: Optional[float] = None   # fraction of pixels flagged as changed
    confidence: Optional[float] = None        # 0.0–1.0 overall method confidence
    notes: List[str] = field(default_factory=list)


@dataclass
class TemporalChangeResult:
    """
    Full result of multi-temporal change analysis across N observations.
    Designed for ≥2 observations, not just a before/after pair.
    """
    verdict: ChangeVerdict
    # Ordered list of observation timestamps (ISO strings or None)
    observation_timestamps: List[Optional[str]] = field(default_factory=list)
    # Evidence from each method
    evidence: List[ChangeEvidence] = field(default_factory=list)
    # Registration result applied before analysis
    registration: Optional[RegistrationResult] = None
    # Change type classification (if available)
    change_type: Optional[str] = None        # 'construction', 'clearance', 'water', 'road', None
    change_type_confidence: Optional[float] = None
    # Earliest confirmed change (index into observation_timestamps)
    earliest_change_idx: Optional[int] = None
    # Reason for ABSTAIN verdict
    abstain_reason: Optional[str] = None
    # Evidence-based change attribution result
    attribution: Optional[Any] = None
    # Multi-temporal trajectory persistence result (>= 3 dates)
    persistence: Optional[Any] = None
    notes: List[str] = field(default_factory=list)


class ChangeDetector(ABC):
    """
    Abstract change detector.

    Designed for multi-temporal stacks (N observations, N >= 2).
    Must propagate uncertainty: if evidence is insufficient, return ABSTAIN.
    Never return SUPPORTED with fabricated confidence.
    """

    @property
    @abstractmethod
    def detector_id(self) -> str:
        """Stable identifier for provenance."""

    @property
    def required_bands(self) -> Optional[List[str]]:
        """Band names required, in order. None = accepts any bands."""
        return None

    @property
    def min_observations(self) -> int:
        """Minimum number of temporal observations required."""
        return 2

    @abstractmethod
    def detect(
        self,
        observations: List[np.ndarray],
        timestamps: List[Optional[str]] | None = None,
        registration_result: RegistrationResult | None = None,
    ) -> TemporalChangeResult:
        """
        Detect changes across multiple temporal observations.

        Args:
            observations: List of float32 arrays (C, H, W), each is one time step.
                          Length >= min_observations.
            timestamps:   Optional ISO date strings, one per observation.
            registration_result: Result of prior registration step.

        Returns:
            TemporalChangeResult. If registration failed or evidence is
            insufficient, verdict MUST be ABSTAIN with abstain_reason set.
        """
