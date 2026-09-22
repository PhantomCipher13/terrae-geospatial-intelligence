"""
geoai/providers/sensors/optical.py
Optical (passive, reflectance/radiance) sensor adapter.
Handles: Sentinel-2, Landsat, Planet, PlanetScope, aerial RGB, generic optical.
"""
from __future__ import annotations
import logging
from typing import Optional, List, Tuple
import numpy as np
from geoai.providers.sensors.base import SensorAdapter, BandCompatibilityError

logger = logging.getLogger(__name__)

# Sentinel-2 band name aliases -> canonical names
_S2_ALIASES = {
    "B01":"Coastal","B02":"Blue","B03":"Green","B04":"Red",
    "B05":"RedEdge1","B06":"RedEdge2","B07":"RedEdge3","B08":"NIR",
    "B8A":"NarrowNIR","B09":"WaterVapour","B10":"Cirrus",
    "B11":"SWIR1","B12":"SWIR2",
}
# Generic names for RGB selection fallback
_RGB_NAMES = {"red","r","band3","b04","b4"}
_GREEN_NAMES = {"green","g","band2","b03","b3"}
_BLUE_NAMES = {"blue","b","band1","b02","b2"}


class OpticalAdapter(SensorAdapter):
    """
    Optical sensor adapter.

    Normalisation strategy:
    - If array dtype is uint16 (typical S2 L2A): divide by 10000.0 (reflectance scale).
    - If array dtype is uint8: divide by 255.0.
    - If already float in [0,1]: pass through.
    - Clips to [0, 1] after normalisation.
    - Per-band percentile stretch for preview only (does not alter embeddings).
    """

    @property
    def sensor_type(self) -> str:
        return "optical"

    @property
    def adapter_id(self) -> str:
        return "optical-adapter-v1"

    @property
    def supported_band_count_range(self) -> Tuple[int, int]:
        return (1, 13)   # 1-band panchromatic to 13-band Sentinel-2

    def _normalize(self, array: np.ndarray) -> np.ndarray:
        """Normalise to float32 [0, 1]."""
        arr = array.astype(np.float32)
        # Detect scale from dtype of original
        if array.dtype == np.uint16:
            arr = arr / 10000.0
        elif array.dtype == np.uint8:
            arr = arr / 255.0
        elif arr.max() > 1.0:
            # Unknown integer scale — normalise by actual max, warn
            amax = arr.max()
            if amax > 0:
                arr = arr / amax
                logger.warning(
                    f"OpticalAdapter: unknown dtype {array.dtype} with max={amax:.1f}. "
                    "Normalised by array max. Verify band scaling is correct."
                )
        return np.clip(arr, 0.0, 1.0)

    def get_rgb_preview(
        self,
        array: np.ndarray,
        band_names: Optional[List[str]] = None,
    ) -> np.ndarray:
        """
        Produce uint8 (H, W, 3) RGB preview.
        Attempts to find R/G/B channels by name; falls back to bands 0,1,2 or greyscale.
        """
        norm = self._normalize(array)

        rgb = self._find_rgb_bands(norm, band_names)  # (3, H, W) float32

        # 2% percentile contrast stretch for display
        lo, hi = np.percentile(rgb, [2, 98])
        if hi > lo:
            rgb = np.clip((rgb - lo) / (hi - lo), 0, 1)
        # Transpose to (H, W, 3) for display/PIL compatibility
        return (rgb.transpose(1, 2, 0) * 255).astype(np.uint8)

    def _find_rgb_bands(self, norm: np.ndarray, band_names: Optional[List[str]]) -> np.ndarray:
        C = norm.shape[0]
        if band_names is not None:
            names_lower = [n.lower() for n in band_names]
            r_idx = next((i for i, n in enumerate(names_lower) if n in _RGB_NAMES), None)
            g_idx = next((i for i, n in enumerate(names_lower) if n in _GREEN_NAMES), None)
            b_idx = next((i for i, n in enumerate(names_lower) if n in _BLUE_NAMES), None)
            if r_idx is not None and g_idx is not None and b_idx is not None:
                return np.stack([norm[r_idx], norm[g_idx], norm[b_idx]], axis=0)
            logger.warning(
                f"OpticalAdapter: could not identify R/G/B from band_names={band_names}. "
                "Falling back to first 3 bands."
            )
        if C >= 3:
            return norm[:3]
        elif C == 1:
            return np.concatenate([norm, norm, norm], axis=0)
        else:
            # 2-band: pad with zeros
            pad = np.zeros((1, *norm.shape[1:]), dtype=np.float32)
            return np.concatenate([norm, pad], axis=0)[:3]

    def extract_quality_hints(self, array: np.ndarray) -> dict:
        norm = self._normalize(array)
        total_px = array.shape[1] * array.shape[2]
        # Approximate saturated pixels (>0.99 across all bands)
        saturated = float(np.mean(np.all(norm > 0.99, axis=0)))
        # Approximate dark pixels (<0.01 across all bands — possible shadow or nodata)
        dark = float(np.mean(np.all(norm < 0.01, axis=0)))
        return {
            "saturated_fraction": saturated,
            "dark_fraction": dark,
        }
