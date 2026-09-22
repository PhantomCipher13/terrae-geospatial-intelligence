"""
tests/unit/test_attribution.py
Tests for evidence-based change attribution, spectral indices, spatial coherence,
and evidence chain generation.
"""
import numpy as np
import pytest
from geoai.change.attribution import (
    AttributionClass,
    attribute_change,
    compute_ndvi,
    compute_ndwi,
    compute_spatial_coherence,
    DISCLAIMER_TEXT,
)
from geoai.core.result import ChangeVerdict


def test_ndvi_calculation():
    """Test 1: Known synthetic values produce expected NDVI."""
    # Healthy vegetation: high NIR (0.8), low Red (0.1)
    nir = np.array([0.8], dtype=np.float32)
    red = np.array([0.1], dtype=np.float32)
    ndvi = compute_ndvi(nir, red)
    expected = (0.8 - 0.1) / (0.8 + 0.1)
    assert np.isclose(ndvi[0], expected, atol=1e-3)

    # Water / negative NDVI: low NIR (0.05), higher Red (0.15)
    nir_w = np.array([0.05], dtype=np.float32)
    red_w = np.array([0.15], dtype=np.float32)
    ndvi_w = compute_ndvi(nir_w, red_w)
    assert ndvi_w[0] < 0.0

    # Zero values safe from div by zero
    ndvi_z = compute_ndvi(np.array([0.0]), np.array([0.0]))
    assert not np.isnan(ndvi_z[0])
    assert not np.isinf(ndvi_z[0])


def test_ndwi_calculation():
    """Test 2: Known synthetic values produce expected NDWI."""
    # Water: high Green (0.3), low NIR (0.05)
    green = np.array([0.3], dtype=np.float32)
    nir = np.array([0.05], dtype=np.float32)
    ndwi = compute_ndwi(green, nir)
    expected = (0.3 - 0.05) / (0.3 + 0.05)
    assert np.isclose(ndwi[0], expected, atol=1e-3)
    assert ndwi[0] > 0.5

    # Dense vegetation: Green (0.1), high NIR (0.7) -> negative NDWI
    ndwi_veg = compute_ndwi(np.array([0.1]), np.array([0.7]))
    assert ndwi_veg[0] < 0.0


def test_construction_signature():
    """Test 3: NIR decrease + Red increase + NDVI decrease favors BUILT_SURFACE."""
    # 4 bands: Blue, Green, Red, NIR. Shape: (4, 32, 32)
    t0 = np.zeros((4, 32, 32), dtype=np.float32)
    t1 = np.zeros((4, 32, 32), dtype=np.float32)

    # T0: Vegetation in changed area
    # Blue=0.03, Green=0.07, Red=0.04, NIR=0.35
    t0[0] = 0.03
    t0[1] = 0.07
    t0[2] = 0.04
    t0[3] = 0.35

    # T1: Built surface / concrete
    # Blue=0.20, Green=0.20, Red=0.25, NIR=0.22
    t1[0] = 0.20
    t1[1] = 0.20
    t1[2] = 0.25
    t1[3] = 0.22

    # Mask: 16x16 center block changed
    mask = np.zeros((32, 32), dtype=bool)
    mask[8:24, 8:24] = True

    res = attribute_change(t0, t1, mask, query_text="urban development", verdict="SUPPORTED")
    assert res.dominant_interpretation == AttributionClass.BUILT_SURFACE.value
    assert res.support[AttributionClass.BUILT_SURFACE.value] > 0.50
    assert res.metrics["delta_red_mean"] > 0.15
    assert res.metrics["delta_ndvi_mean"] < -0.30
    assert res.evidence_chain is not None
    assert res.evidence_chain.verdict == "SUPPORTED"
    assert "built-surface" in res.interpretation_text.lower()


def test_vegetation_growth():
    """Test 4: NIR increase + Red decrease + NDVI increase favors VEGETATION_CHANGE."""
    t0 = np.zeros((4, 32, 32), dtype=np.float32)
    t1 = np.zeros((4, 32, 32), dtype=np.float32)

    # T0: Barren soil / cleared ground
    # Red=0.22, NIR=0.10
    t0[0] = 0.10
    t0[1] = 0.10
    t0[2] = 0.22
    t0[3] = 0.10

    # T1: Re-greened / flourishing vegetation
    # Red=0.04, NIR=0.38
    t1[0] = 0.04
    t1[1] = 0.15
    t1[2] = 0.04
    t1[3] = 0.38

    mask = np.zeros((32, 32), dtype=bool)
    mask[8:24, 8:24] = True

    res = attribute_change(t0, t1, mask, verdict="REVIEW")
    assert res.dominant_interpretation == AttributionClass.VEGETATION_CHANGE.value
    assert res.support[AttributionClass.VEGETATION_CHANGE.value] > 0.50
    assert res.metrics["delta_ndvi_mean"] > 0.30
    assert "vegetation" in res.interpretation_text.lower()


def test_water_appearance():
    """Test 5: NIR decrease + NDWI increase + low end NIR/Red favors WATER_CHANGE."""
    t0 = np.zeros((4, 32, 32), dtype=np.float32)
    t1 = np.zeros((4, 32, 32), dtype=np.float32)

    # T0: Dry ground
    t0[0] = 0.08
    t0[1] = 0.10
    t0[2] = 0.12
    t0[3] = 0.30

    # T1: Flooding / reservoir fill (very low NIR, high green/blue relative to NIR)
    t1[0] = 0.08
    t1[1] = 0.12
    t1[2] = 0.04
    t1[3] = 0.02

    mask = np.zeros((32, 32), dtype=bool)
    mask[8:24, 8:24] = True

    res = attribute_change(t0, t1, mask)
    assert res.dominant_interpretation == AttributionClass.WATER_CHANGE.value
    assert res.support[AttributionClass.WATER_CHANGE.value] > 0.50
    assert "water" in res.interpretation_text.lower()


def test_no_changed_pixels():
    """Test 6: Empty mask returns UNCERTAIN, zero metrics, no crash."""
    t0 = np.zeros((4, 32, 32), dtype=np.float32)
    t1 = np.zeros((4, 32, 32), dtype=np.float32)
    mask = np.zeros((32, 32), dtype=bool)

    res = attribute_change(t0, t1, mask)
    assert res.dominant_interpretation == AttributionClass.UNCERTAIN.value
    assert res.support[AttributionClass.UNCERTAIN.value] == 1.0
    assert res.metrics["changed_pixel_count"] == 0
    assert res.metrics["change_fraction"] == 0.0
    assert res.metrics["spatial_coherence"] == 0.0
    assert res.evidence_chain is not None


def test_spatial_coherence():
    """Test 7: Single large connected component has higher coherence than scattered pixels."""
    # Clustered mask: 100 pixels in one contiguous 10x10 block
    clustered = np.zeros((32, 32), dtype=bool)
    clustered[5:15, 5:15] = True
    stats_clustered = compute_spatial_coherence(clustered)

    # Scattered mask: 100 isolated pixels
    scattered = np.zeros((32, 32), dtype=bool)
    scattered[::3, ::3] = True
    scattered = scattered[:32, :32]
    stats_scattered = compute_spatial_coherence(scattered)

    assert stats_clustered["coherence"] == 1.0
    assert stats_clustered["component_count"] == 1
    assert stats_scattered["component_count"] > 10
    assert stats_scattered["coherence"] < stats_clustered["coherence"]


def test_existing_workflow_regression():
    """Test 8: Integration regression test with MetadataDB and TemporalAnalysisWorkflow."""
    from geoai.app_factory import _load_config, build_metadata_db, build_temporal_workflow

    cfg = _load_config("configs/config.yaml")
    db = build_metadata_db(cfg)
    temporal, _ = build_temporal_workflow(cfg)

    # Check if DB has scenes
    stats = db.stats()
    if stats["scenes"] < 2:
        pytest.skip("Not enough scenes in DB for temporal test")

    with db._conn as conn:
        c = conn.cursor()
        c.execute("SELECT tile_id FROM tiles WHERE scene_id IN (SELECT scene_id FROM scenes WHERE source_path LIKE '%scene_T0%')")
        tiles = c.fetchall()

    if not tiles:
        pytest.skip("No T0 tiles in DB")

    found_supported = False
    for row in tiles:
        tid = row[0]
        res = temporal.run_analysis(tid, query_text="construction activity")
        assert res.verdict in [ChangeVerdict.SUPPORTED, ChangeVerdict.REVIEW, ChangeVerdict.ABSTAIN]
        assert res.attribution is not None
        if res.verdict == ChangeVerdict.SUPPORTED:
            found_supported = True
            assert res.attribution.dominant_interpretation == AttributionClass.BUILT_SURFACE.value
            assert res.attribution.evidence_chain is not None
            assert res.attribution.evidence_chain.verdict == "SUPPORTED"

    assert found_supported, "Expected at least one tile with SUPPORTED construction verdict."


def test_nan_invalid_input():
    """Test 9: Attribution handles NaN and Inf values gracefully without crashing."""
    t0 = np.full((4, 16, 16), np.nan, dtype=np.float32)
    t1 = np.full((4, 16, 16), np.inf, dtype=np.float32)
    t0[2, 0:5, 0:5] = 0.1
    t1[2, 0:5, 0:5] = 0.5
    mask = np.zeros((16, 16), dtype=bool)
    mask[0:5, 0:5] = True

    # Should not raise exception
    res = attribute_change(t0, t1, mask)
    assert res is not None
    assert not np.isnan(res.support[AttributionClass.UNCERTAIN.value])


def test_offline_integrity(monkeypatch):
    """Test 10: Attribution performs zero network calls."""
    import socket

    def guarded_socket(*args, **kwargs):
        raise RuntimeError("Network access attempted during offline attribution test!")

    monkeypatch.setattr(socket, "socket", guarded_socket)

    t0 = np.zeros((4, 16, 16), dtype=np.float32)
    t1 = np.zeros((4, 16, 16), dtype=np.float32)
    t0[:, 2:8, 2:8] = 0.2
    t1[:, 2:8, 2:8] = 0.5
    mask = np.zeros((16, 16), dtype=bool)
    mask[2:8, 2:8] = True

    res = attribute_change(t0, t1, mask, query_text="test query")
    assert res.evidence_chain is not None
    assert res.evidence_chain.disclaimer == DISCLAIMER_TEXT
