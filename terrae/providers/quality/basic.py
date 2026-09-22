"""
terrae/providers/quality/basic.py
Basic quality assessor — computes nodata fraction and metadata completeness.
Does NOT fabricate cloud fraction or metrics it cannot compute.
"""
from __future__ import annotations
import numpy as np
from terrae.core.result import QualityReport, QualityStatus
from terrae.core.raster_metadata import RasterMetadata
from terrae.providers.quality.base import QualityAssessor


class BasicQualityAssessor(QualityAssessor):
    """
    Assessor that computes:
    - nodata_fraction from the array
    - metadata completeness from RasterMetadata.missing_fields()
    - has_crs, has_geotransform, has_acquisition_date from metadata

    Does NOT compute:
    - cloud_fraction (requires sensor-specific cloud mask)
    - invalid_pixel_fraction beyond nodata check

    Thresholds (configurable):
    - nodata > 0.9 → FAIL
    - nodata > 0.5 → WARNING
    - metadata_completeness < 0.5 → WARNING
    """

    def __init__(
        self,
        nodata_fail_threshold: float = 0.9,
        nodata_warn_threshold: float = 0.5,
    ) -> None:
        self._fail_th = nodata_fail_threshold
        self._warn_th = nodata_warn_threshold

    @property
    def assessor_id(self) -> str:
        return "basic-nodata-v1"

    def assess(
        self,
        array: np.ndarray,
        metadata: RasterMetadata | None = None,
        nodata_value: float | None = None,
    ) -> QualityReport:
        notes = []
        report = QualityReport(status=QualityStatus.PASS)

        # --- Nodata fraction ---
        if nodata_value is not None:
            nd_frac = float(np.mean(array == nodata_value))
        elif np.issubdtype(array.dtype, np.floating):
            nd_frac = float(np.mean(np.isnan(array)))
        else:
            nd_frac = None  # Cannot determine without knowing nodata value

        report.nodata_fraction = nd_frac

        if nd_frac is not None:
            if nd_frac > self._fail_th:
                report.status = QualityStatus.FAIL
                notes.append(f"Nodata fraction {nd_frac:.2%} exceeds fail threshold {self._fail_th:.0%}.")
            elif nd_frac > self._warn_th:
                report.status = QualityStatus.WARNING
                notes.append(f"Nodata fraction {nd_frac:.2%} exceeds warning threshold {self._warn_th:.0%}.")

        # --- Metadata completeness ---
        if metadata is not None:
            missing = metadata.missing_fields()
            completeness = metadata.metadata_completeness
            report.metadata_completeness = completeness
            report.has_crs = metadata.crs_wkt is not None
            report.has_geotransform = metadata.affine_transform is not None
            report.has_acquisition_date = metadata.has_temporal_info()
            if completeness is not None and completeness < 0.5:
                if report.status == QualityStatus.PASS:
                    report.status = QualityStatus.WARNING
                notes.append(f"Low metadata completeness ({completeness:.0%}). Missing: {missing}")

        # cloud_fraction: deliberately None — requires sensor-specific cloud mask
        report.cloud_fraction = None
        report.notes = notes
        return report
