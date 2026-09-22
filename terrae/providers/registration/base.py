"""
terrae/providers/registration/base.py
Abstract interface for co-registration providers.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np
from terrae.core.result import RegistrationResult, RegistrationStatus


class RegistrationProvider(ABC):
    """
    Abstract co-registration provider.

    Takes two raster arrays (reference, target) and attempts to align them.
    MUST return a RegistrationResult with an honest status — never fabricate
    a GOOD result when quality is borderline or unknown.

    If implementation is unavailable/not installed, return status=UNAVAILABLE.
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Stable identifier for provenance, e.g. 'opencv-ecc-v1', 'arosics-local-v1'."""

    @abstractmethod
    def register(
        self,
        reference: np.ndarray,
        target: np.ndarray,
        reference_meta: dict | None = None,
        target_meta: dict | None = None,
    ) -> RegistrationResult:
        """
        Align target to reference.

        Args:
            reference: float32 array (C, H, W) or (H, W) — reference image.
            target:    float32 array same shape — image to warp.
            reference_meta: optional dict with CRS/transform info.
            target_meta:    optional dict with CRS/transform info.

        Returns:
            RegistrationResult with honest status and quality metrics.
            If quality cannot be assessed, use status=UNAVAILABLE, not GOOD.
        """

    def can_register(self) -> bool:
        """Return True if this provider's dependencies are installed and usable."""
        return True
