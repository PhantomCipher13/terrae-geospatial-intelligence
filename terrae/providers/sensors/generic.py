"""
terrae/providers/sensors/generic.py
Generic raster adapter — used when sensor type is unknown.
Applies conservative normalisation. Explicitly warns about assumptions.
"""
from __future__ import annotations
import logging
from typing import Optional, List, Tuple
import numpy as np
from terrae.providers.sensors.base import SensorAdapter

logger = logging.getLogger(__name__)


class GenericRasterAdapter(SensorAdapter):
    """
    Fallback adapter for unknown sensor types.
    Performs min-max normalisation per-band with a warning.
    """

    @property
    def sensor_type(self) -> str:
        return "generic"

    @property
    def adapter_id(self) -> str:
        return "generic-raster-adapter-v1"

    @property
    def supported_band_count_range(self) -> Tuple[int, int]:
        return (1, 64)

    def _normalize(self, array: np.ndarray) -> np.ndarray:
        logger.warning(
            "GenericRasterAdapter: sensor type unknown. Applying per-band min-max "
            "normalisation. Verify this is appropriate for your data."
        )
        arr = array.astype(np.float32)
        out = np.zeros_like(arr)
        for c in range(arr.shape[0]):
            band = arr[c]
            lo, hi = band.min(), band.max()
            if hi > lo:
                out[c] = (band - lo) / (hi - lo)
            else:
                out[c] = 0.0
        return out

    def get_rgb_preview(
        self,
        array: np.ndarray,
        band_names: Optional[List[str]] = None,
    ) -> np.ndarray:
        norm = self._normalize(array)
        C = norm.shape[0]
        if C >= 3:
            rgb = norm[:3]
        elif C == 1:
            rgb = np.concatenate([norm, norm, norm], axis=0)
        else:
            pad = np.zeros((3 - C, *norm.shape[1:]), dtype=np.float32)
            rgb = np.concatenate([norm, pad], axis=0)
        return (rgb * 255).astype(np.uint8)

    def extract_quality_hints(self, array: np.ndarray) -> dict:
        return {}
