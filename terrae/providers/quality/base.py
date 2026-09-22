"""
terrae/providers/quality/base.py
Abstract interface for image quality assessment.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np
from terrae.core.result import QualityReport
from terrae.core.raster_metadata import RasterMetadata


class QualityAssessor(ABC):
    """
    Abstract quality assessor.

    Evaluates a raster/tile and returns an honest QualityReport.
    NEVER fabricate quality scores — use None for metrics that cannot be computed.
    """

    @property
    @abstractmethod
    def assessor_id(self) -> str:
        """Stable identifier, e.g. 'basic-nodata-v1', 'sentinel2-cloud-v1'."""

    @abstractmethod
    def assess(
        self,
        array: np.ndarray,
        metadata: RasterMetadata | None = None,
    ) -> QualityReport:
        """
        Assess quality of a raster array.

        Args:
            array: float32 array (C, H, W).
            metadata: optional RasterMetadata for completeness checks.

        Returns:
            QualityReport with honest status.
            Use None for any metric that cannot be calculated.
        """
