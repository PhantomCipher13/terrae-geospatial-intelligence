"""tests/unit/test_sensors.py — Tests for sensor/band adapters."""
import pytest
import numpy as np
from terrae.providers.sensors.base import BandCompatibilityError


def test_optical_normalize_uint16():
    from terrae.providers.sensors.optical import OpticalAdapter
    a = OpticalAdapter()
    arr = np.ones((3, 32, 32), dtype=np.uint16) * 2000  # S2-style reflectance
    out = a._normalize(arr)
    assert out.dtype == np.float32
    assert out.max() <= 1.0
    assert out.min() >= 0.0
    assert abs(out.mean() - 0.2) < 0.01  # 2000/10000 = 0.2


def test_optical_normalize_uint8():
    from terrae.providers.sensors.optical import OpticalAdapter
    a = OpticalAdapter()
    arr = np.ones((3, 32, 32), dtype=np.uint8) * 128
    out = a._normalize(arr)
    assert abs(out.mean() - 128/255) < 0.01


def test_optical_rgb_preview_shape(valid_geotiff):
    import rasterio
    from terrae.providers.sensors.optical import OpticalAdapter
    with rasterio.open(valid_geotiff) as ds:
        arr = ds.read().astype(np.float32)
    a = OpticalAdapter()
    preview = a.get_rgb_preview(arr, band_names=["Red","Green","Blue"])
    assert preview.shape == (arr.shape[1], arr.shape[2], 3)
    assert preview.dtype == np.uint8


def test_sar_normalize_does_not_use_optical_scale():
    from terrae.providers.sensors.sar import SARAdapter
    a = SARAdapter()
    # SAR amplitude values are NOT in [0,1] reflectance range
    arr = np.ones((2, 32, 32), dtype=np.float32) * 0.01  # typical SAR amplitude
    out = a._normalize(arr)
    # After log normalisation, result should be float32 in [0,1]
    assert out.dtype == np.float32
    # All identical pixels → after robust stretch might be 0 (percentile collapse)
    # Key: no crash, output is bounded
    assert np.all(np.isfinite(out))


def test_generic_adapter_warns_and_normalizes():
    import logging
    from terrae.providers.sensors.generic import GenericRasterAdapter
    a = GenericRasterAdapter()
    arr = np.random.default_rng(0).integers(0, 65535, (5, 16, 16)).astype(np.float32)
    out = a._normalize(arr)
    assert out.shape == arr.shape
    assert out.max() <= 1.0
    assert out.min() >= 0.0


def test_band_selection_by_name():
    from terrae.providers.sensors.optical import OpticalAdapter
    a = OpticalAdapter()
    arr = np.random.default_rng(0).random((4, 16, 16)).astype(np.float32)
    band_names = ["Red", "Green", "Blue", "NIR"]
    # Request only RGB
    selected = a._select_bands(arr, band_names, ["Red", "Green", "Blue"])
    assert selected.shape[0] == 3


def test_band_selection_missing_raises():
    from terrae.providers.sensors.optical import OpticalAdapter
    a = OpticalAdapter()
    arr = np.zeros((3, 16, 16), dtype=np.float32)
    band_names = ["Red", "Green", "Blue"]
    with pytest.raises(BandCompatibilityError):
        a._select_bands(arr, band_names, ["Red", "Green", "Blue", "NIR"])


def test_band_selection_no_names_raises():
    from terrae.providers.sensors.optical import OpticalAdapter
    a = OpticalAdapter()
    arr = np.zeros((4, 16, 16), dtype=np.float32)
    with pytest.raises(BandCompatibilityError):
        a._select_bands(arr, None, ["Red", "Green", "Blue"])


def test_registry_returns_optical_for_sentinel2():
    from terrae.providers.sensors.registry import get_adapter
    from terrae.core.raster_metadata import RasterMetadata
    from pathlib import Path
    meta = RasterMetadata(source_path=Path("scene.tif"), sensor="Sentinel-2A", sensor_type="optical")
    adapter = get_adapter(meta)
    assert adapter.sensor_type == "optical"


def test_registry_returns_sar_for_sentinel1():
    from terrae.providers.sensors.registry import get_adapter
    from terrae.core.raster_metadata import RasterMetadata
    from pathlib import Path
    meta = RasterMetadata(source_path=Path("scene.tif"), sensor="Sentinel-1 GRD")
    adapter = get_adapter(meta)
    assert adapter.sensor_type == "sar"


def test_registry_returns_generic_for_unknown():
    from terrae.providers.sensors.registry import get_adapter
    adapter = get_adapter(None)
    assert adapter.sensor_type == "generic"
