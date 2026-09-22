"""
geoai/providers/sensors/base.py
Abstract sensor/band adapter interface.

Sensor adapters are responsible for:
1. Declaring which bands they can handle.
2. Normalising raw raster data for embedding model input.
3. Selecting/reordering bands to match a model's required_bands contract.
4. Extracting quality hints from the raw data.
5. Generating an RGB preview for visualisation.

Rules:
- NEVER silently discard bands — raise or warn explicitly.
- NEVER silently reorder bands unless the mapping is explicitly declared.
- NEVER apply optical normalisation to SAR data or vice versa.
- If model requires bands this adapter cannot provide, raise BandCompatibilityError.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
import numpy as np


class BandCompatibilityError(ValueError):
    """Raised when the sensor adapter cannot satisfy a model's required_bands."""
    pass


class SensorAdapter(ABC):
    """
    Abstract sensor/band adapter.
    """

    @property
    @abstractmethod
    def sensor_type(self) -> str:
        """'optical', 'sar', 'hyperspectral', or 'generic'."""

    @property
    @abstractmethod
    def adapter_id(self) -> str:
        """Stable identifier for provenance."""

    @property
    @abstractmethod
    def supported_band_count_range(self) -> Tuple[int, int]:
        """(min_bands, max_bands) this adapter accepts."""

    def preprocess_for_embedding(
        self,
        array: np.ndarray,
        band_names: Optional[List[str]] = None,
        required_bands: Optional[List[str]] = None,
    ) -> np.ndarray:
        """
        Prepare a raw raster tile for an embedding model.

        Args:
            array: float32 (C, H, W) raw raster data.
            band_names: names of each band in array, in order. May be None.
            required_bands: list of band names the embedding model requires.
                            If provided, adapter must select + reorder.
                            If adapter cannot satisfy this, raise BandCompatibilityError.

        Returns:
            float32 (C', H, W) preprocessed array ready for the model.
            C' matches len(required_bands) if required_bands is set.
        """
        if required_bands is not None:
            array = self._select_bands(array, band_names, required_bands)
        return self._normalize(array)

    @abstractmethod
    def _normalize(self, array: np.ndarray) -> np.ndarray:
        """Apply sensor-appropriate normalisation to array (C, H, W)."""

    def _select_bands(
        self,
        array: np.ndarray,
        band_names: Optional[List[str]],
        required_bands: List[str],
    ) -> np.ndarray:
        """
        Select and reorder bands to match required_bands.
        Raises BandCompatibilityError if required_bands cannot be satisfied.
        """
        if band_names is None:
            raise BandCompatibilityError(
                f"Model requires bands {required_bands} but array has no band names. "
                "Cannot safely select bands without explicit band metadata."
            )
        name_to_idx = {n: i for i, n in enumerate(band_names)}
        selected = []
        missing = []
        for req in required_bands:
            if req in name_to_idx:
                selected.append(name_to_idx[req])
            else:
                missing.append(req)
        if missing:
            raise BandCompatibilityError(
                f"Required bands {missing} not found in available bands {band_names}."
            )
        return array[selected]

    @abstractmethod
    def get_rgb_preview(
        self,
        array: np.ndarray,
        band_names: Optional[List[str]] = None,
    ) -> np.ndarray:
        """
        Produce an 8-bit uint8 (H, W, 3) RGB array for visualisation.
        Must not silently map wrong bands to RGB.
        Returns a grey-scale repeat if RGB cannot be determined.
        """

    @abstractmethod
    def extract_quality_hints(self, array: np.ndarray) -> dict:
        """
        Extract sensor-specific quality information from raw array.
        Returns dict with available keys only (no fabricated values).
        """
