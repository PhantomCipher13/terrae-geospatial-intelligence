"""
terrae/providers/sensors/sar.py
SAR (Synthetic Aperture Radar) sensor adapter.
Handles: Sentinel-1 GRD/SLC VV/VH, ERS, ALOS-2, etc.

CRITICAL: SAR data must NOT be normalised like optical data.
SAR amplitude/intensity values have completely different statistics.
This adapter applies log-ratio normalisation appropriate for SAR intensity.
"""
from __future__ import annotations
import logging
from typing import Optional, List, Tuple
import numpy as np
from terrae.providers.sensors.base import SensorAdapter

logger = logging.getLogger(__name__)


class SARAdapter(SensorAdapter):
    """
    SAR sensor adapter.

    Normalisation strategy:
    - Assumes input is SAR amplitude or intensity (linear scale).
    - If dtype is float and values span several orders of magnitude → log10 normalisation.
    - Clips to [mean - 3*std, mean + 3*std] in log space before final [0,1] scale.
    - Do NOT pass SAR data through an optical [0,1] reflectance normalisation.

    Warning: If sensor_type cannot be confirmed as SAR, use GenericAdapter instead.
    """

    @property
    def sensor_type(self) -> str:
        return "sar"

    @property
    def adapter_id(self) -> str:
        return "sar-adapter-v1"

    @property
    def supported_band_count_range(self) -> Tuple[int, int]:
        return (1, 4)  # VV, VH, HH, HV

    def _normalize(self, array: np.ndarray) -> np.ndarray:
        """
        Normalise SAR amplitude/intensity to float32 [0, 1].
        Uses log10 compression with robust clipping.
        """
        arr = array.astype(np.float32)
        # Replace non-positive values (invalid SAR pixels) with NaN
        arr[arr <= 0] = np.nan
        # Convert to dB scale
        arr_db = 10.0 * np.log10(arr + 1e-12)
        # Per-band robust normalisation
        out = np.zeros_like(arr_db)
        for c in range(arr_db.shape[0]):
            band = arr_db[c]
            valid = band[~np.isnan(band)]
            if len(valid) == 0:
                logger.warning(f"SARAdapter: band {c} has no valid pixels.")
                out[c] = 0.0
                continue
            lo = np.percentile(valid, 2)
            hi = np.percentile(valid, 98)
            if hi == lo:
                out[c] = 0.0
            else:
                out[c] = np.clip((band - lo) / (hi - lo), 0.0, 1.0)
        # Replace NaN with 0 (nodata)
        out = np.nan_to_num(out, nan=0.0)
        return out.astype(np.float32)

    def get_rgb_preview(
        self,
        array: np.ndarray,
        band_names: Optional[List[str]] = None,
    ) -> np.ndarray:
        """
        RGB preview for SAR: VV→R, VH→G, VV/VH ratio→B if 2+ bands.
        Single-band: greyscale.
        """
        norm = self._normalize(array)
        C = norm.shape[0]
        if C >= 2:
            ratio = np.clip(norm[0] / (norm[1] + 1e-6), 0, 1)
            rgb = np.stack([norm[0], norm[1], ratio], axis=0)
        elif C == 1:
            rgb = np.concatenate([norm, norm, norm], axis=0)
        else:
            rgb = norm[:3]
        return (rgb * 255).astype(np.uint8)

    def extract_quality_hints(self, array: np.ndarray) -> dict:
        invalid = float(np.mean(array <= 0))
        return {"invalid_sar_pixel_fraction": invalid}
