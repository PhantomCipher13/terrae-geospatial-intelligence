"""
geoai/providers/sensors/registry.py
Dispatch logic: given raster metadata, return the appropriate SensorAdapter.
"""
from __future__ import annotations
import logging
from typing import Optional
from geoai.core.raster_metadata import RasterMetadata
from geoai.providers.sensors.base import SensorAdapter
from geoai.providers.sensors.optical import OpticalAdapter
from geoai.providers.sensors.sar import SARAdapter
from geoai.providers.sensors.generic import GenericRasterAdapter

logger = logging.getLogger(__name__)

_SAR_KEYWORDS = {"sentinel-1", "sar", "grd", "slc", "ers", "alos", "radarsat", "palsar"}
_OPTICAL_KEYWORDS = {
    "sentinel-2", "landsat", "modis", "spot", "planet", "pleiades",
    "worldview", "geoeye", "maxar", "aerial", "drone",
}


def get_adapter(metadata: Optional[RasterMetadata] = None,
                sensor_hint: Optional[str] = None) -> SensorAdapter:
    """
    Return the most appropriate SensorAdapter for the given raster metadata.

    Logic:
    1. Check explicit sensor_hint (override).
    2. Check metadata.sensor_type if already set.
    3. Check metadata.sensor string against known keywords.
    4. Fallback to GenericRasterAdapter with a warning.
    """
    # 1. Explicit override
    if sensor_hint is not None:
        h = sensor_hint.lower()
        if h == "optical":
            return OpticalAdapter()
        if h == "sar":
            return SARAdapter()
        if h == "generic":
            return GenericRasterAdapter()
        logger.warning(f"Unknown sensor_hint='{sensor_hint}'. Falling back to GenericRasterAdapter.")
        return GenericRasterAdapter()

    if metadata is None:
        logger.warning("No metadata provided to adapter registry. Using GenericRasterAdapter.")
        return GenericRasterAdapter()

    # 2. Explicit sensor_type field
    if metadata.sensor_type is not None:
        st = metadata.sensor_type.lower()
        if st == "optical":
            return OpticalAdapter()
        if st == "sar":
            return SARAdapter()
        if st == "generic" or st == "unknown":
            return GenericRasterAdapter()

    # 3. Keyword match on sensor string
    if metadata.sensor is not None:
        s = metadata.sensor.lower()
        for kw in _SAR_KEYWORDS:
            if kw in s:
                logger.info(f"SAR keyword '{kw}' matched in sensor='{metadata.sensor}'. Using SARAdapter.")
                return SARAdapter()
        for kw in _OPTICAL_KEYWORDS:
            if kw in s:
                logger.info(f"Optical keyword '{kw}' matched in sensor='{metadata.sensor}'. Using OpticalAdapter.")
                return OpticalAdapter()

    logger.warning(
        f"Cannot determine sensor type from metadata "
        f"(sensor='{metadata.sensor}', sensor_type='{metadata.sensor_type}'). "
        "Using GenericRasterAdapter. Verify band interpretation is correct."
    )
    return GenericRasterAdapter()
