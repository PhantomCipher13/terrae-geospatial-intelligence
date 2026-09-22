"""
tests/unit/test_real_sentinel.py
Unit tests for real Sentinel-2 Level-2A data validation, band mapping,
reflectance normalization, quality/cloud masking, and attribution compatibility.
"""
from pathlib import Path
import numpy as np
import pytest
import rasterio

from geoai.ingest.reader import read_metadata
from geoai.providers.sensors.registry import get_adapter
from geoai.providers.sensors.optical import OpticalAdapter
from geoai.change.attribution import (
    attribute_change,
    compute_ndvi,
    compute_ndwi,
    AttributionClass,
)
from geoai.core.result import ChangeVerdict

DATA_DIR = Path("data/real/sentinel2")
T0_PATH = DATA_DIR / "real_T0_20230519.tif"
T1_PATH = DATA_DIR / "real_T1_20231205.tif"
SCL0_PATH = DATA_DIR / "scl_T0_20230519.tif"
SCL1_PATH = DATA_DIR / "scl_T1_20231205.tif"


def test_real_sentinel_band_mapping():
    """Test A: Real Sentinel-2 band mapping resolves B02->Blue, B03->Green, B04->Red, B08->NIR."""
    if not T0_PATH.exists():
        pytest.skip("Real Sentinel-2 test data not staged.")

    meta = read_metadata(T0_PATH)
    assert meta.sensor in ["Sentinel-2", "Sentinel-2A"]
    assert meta.sensor_type == "optical"
    assert meta.band_count == 4

    band_names = [b.name for b in meta.bands]
    assert band_names == ["Blue", "Green", "Red", "NIR"]

    adapter = get_adapter(meta)
    assert isinstance(adapter, OpticalAdapter)

    # Verify OpticalAdapter correctly maps RGB channels
    dummy_arr = np.zeros((4, 64, 64), dtype=np.uint16)
    dummy_arr[2] = 2000  # Red
    dummy_arr[1] = 1500  # Green
    dummy_arr[0] = 1000  # Blue
    rgb = adapter.get_rgb_preview(dummy_arr, band_names)
    assert rgb.shape == (64, 64, 3)
    # Channel 0 of preview should correspond to Red (highest)
    assert rgb[:, :, 0].mean() > rgb[:, :, 1].mean() > rgb[:, :, 2].mean()


def test_real_data_normalization_range():
    """Test B: Real-data normalization produces valid reflectance ranges in [0, 1]."""
    if not T0_PATH.exists() or not T1_PATH.exists():
        pytest.skip("Real Sentinel-2 test data not staged.")

    with rasterio.open(T0_PATH) as ds0, rasterio.open(T1_PATH) as ds1:
        raw0 = ds0.read()
        raw1 = ds1.read()

    # Sentinel-2 standard scaling: raw / 10000.0
    norm0 = np.clip(raw0.astype(np.float32) / 10000.0, 0.0, 1.0)
    norm1 = np.clip(raw1.astype(np.float32) / 10000.0, 0.0, 1.0)

    assert norm0.min() >= 0.0 and norm0.max() <= 1.0
    assert norm1.min() >= 0.0 and norm1.max() <= 1.0

    # Typical Earth surface reflectance mean is between 0.05 and 0.40
    assert 0.03 < norm0.mean() < 0.50
    assert 0.03 < norm1.mean() < 0.50


def test_real_temporal_pair_metadata_alignment():
    """Test C: Real temporal pair contains matching geographic/tile metadata."""
    if not T0_PATH.exists() or not T1_PATH.exists():
        pytest.skip("Real Sentinel-2 test data not staged.")

    meta0 = read_metadata(T0_PATH)
    meta1 = read_metadata(T1_PATH)

    # Identical CRS, dimensions, and spatial transform
    assert meta0.crs_epsg == meta1.crs_epsg == 32643
    assert meta0.width_px == meta1.width_px == 512
    assert meta0.height_px == meta1.height_px == 512
    assert meta0.affine_transform == meta1.affine_transform
    assert meta0.bounds_native == meta1.bounds_native

    # Different acquisition dates
    assert meta0.acquisition_date is not None
    assert meta1.acquisition_date is not None
    assert meta0.acquisition_date != meta1.acquisition_date


def test_quality_cloud_masking():
    """Test D: Invalid/cloud pixels are excluded when a valid quality mask exists."""
    # Synthetic observation with 100 changed pixels
    t0 = np.full((4, 32, 32), 0.1, dtype=np.float32)
    t1 = np.full((4, 32, 32), 0.1, dtype=np.float32)
    t1[:, 0:10, 0:10] = 0.4  # 100 changed pixels

    change_mask = np.zeros((32, 32), dtype=bool)
    change_mask[0:10, 0:10] = True

    # Case 1: All pixels valid
    valid_all = np.ones((32, 32), dtype=bool)
    res_clean = attribute_change(t0, t1, change_mask, valid_mask=valid_all)
    assert res_clean.metrics["changed_pixel_count"] == 100
    assert res_clean.metrics["valid_pixels"] == 1024
    assert res_clean.metrics["invalid_pixels_fraction"] == 0.0

    # Case 2: 50 changed pixels contaminated by cloud shadow
    valid_cloud = np.ones((32, 32), dtype=bool)
    valid_cloud[0:5, 0:10] = False  # top half of changed area is cloud-contaminated
    res_cloud = attribute_change(t0, t1, change_mask, valid_mask=valid_cloud)
    # Only 50 valid changed pixels should remain
    assert res_cloud.metrics["changed_pixel_count"] == 50
    assert res_cloud.metrics["valid_pixels"] == 1024 - 50
    assert res_cloud.metrics["invalid_pixels_fraction"] == pytest.approx(50 / 1024, abs=1e-3)


def test_attribution_accepts_real_four_band_data():
    """Test E: Attribution function accepts real four-band Sentinel-2 arrays."""
    if not T0_PATH.exists() or not T1_PATH.exists():
        pytest.skip("Real Sentinel-2 test data not staged.")

    with rasterio.open(T0_PATH) as ds0, rasterio.open(T1_PATH) as ds1:
        obs0 = np.clip(ds0.read() / 10000.0, 0.0, 1.0).astype(np.float32)
        obs1 = np.clip(ds1.read() / 10000.0, 0.0, 1.0).astype(np.float32)

    diff = np.abs(obs1 - obs0)
    change_mask = np.mean(diff, axis=0) > 0.15

    res = attribute_change(
        obs_t0=obs0,
        obs_t1=obs1,
        change_mask=change_mask,
        band_names=["Blue", "Green", "Red", "NIR"],
        query_text="real validation",
    )

    assert res.dominant_interpretation in [c.value for c in AttributionClass]
    assert len(res.support) == 6
    assert np.isclose(sum(res.support.values()), 1.0, atol=1e-2)
    assert res.evidence_chain is not None
    assert "delta_nir" in res.evidence_chain.spectral_evidence


def test_real_three_date_persistence():
    """Test F: Three-date real Sentinel-2 temporal persistence produces MECE distribution."""
    tmid_path = DATA_DIR / "real_Tmid_20231006.tif"
    if not (T0_PATH.exists() and tmid_path.exists() and T1_PATH.exists()):
        pytest.skip("Three-date real Sentinel-2 data not staged.")

    from geoai.temporal.persistence import analyze_temporal_persistence

    with rasterio.open(T0_PATH) as ds0, rasterio.open(tmid_path) as ds_mid, rasterio.open(T1_PATH) as ds1:
        obs0 = np.clip(ds0.read() / 10000.0, 0.0, 1.0).astype(np.float32)
        obs_mid = np.clip(ds_mid.read() / 10000.0, 0.0, 1.0).astype(np.float32)
        obs1 = np.clip(ds1.read() / 10000.0, 0.0, 1.0).astype(np.float32)

    res = analyze_temporal_persistence(
        observations=[obs0, obs_mid, obs1],
        timestamps=["2023-05-19", "2023-10-06", "2023-12-05"],
        threshold=0.15,
        band_names=["Blue", "Green", "Red", "NIR"],
    )

    td = res.trajectory_distribution
    total_frac = (
        td["stable_fraction"]
        + td["persistent_fraction"]
        + td["transient_fraction"]
        + td["late_fraction"]
        + td["reversible_fraction"]
    )
    assert total_frac == pytest.approx(1.0, abs=1e-4)
    assert res.valid_pixels == 262144
    assert td["stable_fraction"] > 0.95
    assert res.category == "STABLE"

    # Verify counts match valid pixels
    counts = res.category_counts
    assert sum(counts.values()) == 262144
    assert counts["STABLE"] == 258869

    # Verify spectral trajectory is populated
    assert len(res.spectral_trajectory["NDVI"]) == 3
    assert len(res.spectral_trajectory["NIR"]) == 3
