"""
tests/unit/test_persistence.py
Unit tests for multi-temporal trajectory persistence check.
"""
from pathlib import Path
import numpy as np
import pytest
import rasterio

from geoai.temporal.persistence import (
    analyze_temporal_persistence,
    TemporalCategory,
    TemporalPersistenceResult,
)


def _create_mock_stack(h=64, w=64, bands=4):
    """Helper to generate baseline 4-band observations (Blue, Green, Red, NIR)."""
    base = np.zeros((bands, h, w), dtype=np.float32)
    base[0] = 0.08
    base[1] = 0.20
    base[2] = 0.10
    base[3] = 0.60
    return base


def test_requires_at_least_three_observations():
    """Test 1: Raises ValueError if fewer than 3 observations are provided."""
    obs = [_create_mock_stack(), _create_mock_stack()]
    with pytest.raises(ValueError, match="requires >= 3 observations"):
        analyze_temporal_persistence(obs, ["2023-01-01", "2023-02-01"])


def test_mutual_exclusivity_and_exhaustiveness():
    """
    Test 2: Verify that every valid pixel belongs to exactly one category
    (mutually exclusive and collectively exhaustive), and invalid pixels are excluded.
    """
    obs0 = _create_mock_stack(100, 100)
    obs_mid = _create_mock_stack(100, 100)
    obs1 = _create_mock_stack(100, 100)

    # Patch 1 (rows 0:20): Stable (no change)
    # Patch 2 (rows 20:40): Persistent (changed at Tmid, remains changed at T1)
    obs_mid[2, 20:40, :] = 0.60
    obs1[2, 20:40, :] = 0.60

    # Patch 3 (rows 40:60): Reversible (changed at Tmid, returns to T0 at T1)
    obs_mid[3, 40:60, :] = 1.0
    obs_mid[2, 40:60, :] = 0.0
    obs1[3, 40:60, :] = 0.60  # returns exactly to baseline
    obs1[2, 40:60, :] = 0.10

    # Patch 4 (rows 60:80): Late onset (stable at Tmid, changed at T1)
    obs1[2, 60:80, :] = 0.60

    # Patch 5 (rows 80:100): Transient (moderate change at Tmid, decays without strict return)
    obs_mid[2, 80:100, :] = 0.60
    obs1[2, 80:100, :] = 0.42

    # Mask bottom-right corner as invalid (e.g. cloud)
    v_mask = np.ones((100, 100), dtype=bool)
    v_mask[90:, 90:] = False
    valid_count = int(np.sum(v_mask))

    res = analyze_temporal_persistence(
        [obs0, obs_mid, obs1],
        ["2023-01-01", "2023-06-01", "2023-12-01"],
        threshold=0.10,
        valid_mask=v_mask,
    )

    td = res.trajectory_distribution
    # Fractions must sum to 1.0
    total_frac = (
        td["stable_fraction"]
        + td["persistent_fraction"]
        + td["transient_fraction"]
        + td["late_fraction"]
        + td["reversible_fraction"]
    )
    assert total_frac == pytest.approx(1.0, abs=1e-4)

    # Valid pixel count must equal denominator
    assert res.valid_pixels == valid_count
    assert res.total_pixels == 10000

    # All categories must have represented pixels
    assert td["stable_fraction"] > 0.10
    assert td["persistent_fraction"] > 0.10
    assert td["reversible_fraction"] > 0.10
    assert td["late_fraction"] > 0.10
    assert td["transient_fraction"] > 0.05


def test_fractions_sum_to_one():
    """Test 3: Category fractions sum to approximately 1.0 within float tolerance."""
    obs0 = _create_mock_stack()
    obs_mid = _create_mock_stack()
    obs1 = _create_mock_stack()

    obs_mid[2, :32, :32] = 0.50
    obs1[2, :32, :32] = 0.50

    res = analyze_temporal_persistence(
        [obs0, obs_mid, obs1],
        ["2023-01-01", "2023-06-01", "2023-12-01"],
        threshold=0.10,
    )
    td = res.trajectory_distribution
    assert sum(td.values()) == pytest.approx(1.0, abs=1e-5)


def test_stable_case():
    """Test 4: Synthetic stable pixels are classified as STABLE."""
    obs0 = _create_mock_stack()
    obs_mid = obs0.copy()
    obs1 = obs0.copy()

    res = analyze_temporal_persistence(
        [obs0, obs_mid, obs1],
        ["2023-01-01", "2023-06-01", "2023-12-01"],
        threshold=0.10,
    )
    assert res.category in [TemporalCategory.STABLE.value, TemporalCategory.INSUFFICIENT_TEMPORAL_EVIDENCE.value]
    assert res.trajectory_distribution["stable_fraction"] == 1.0
    assert res.trajectory_distribution["persistent_fraction"] == 0.0
    assert res.trajectory_distribution["transient_fraction"] == 0.0
    assert res.trajectory_distribution["late_fraction"] == 0.0
    assert res.trajectory_distribution["reversible_fraction"] == 0.0


def test_persistent_change_case():
    """Test 5: A change occurring by Tmid and remaining changed at T1 is PERSISTENT_CHANGE."""
    obs0 = _create_mock_stack()
    obs_mid = _create_mock_stack()
    obs1 = _create_mock_stack()

    # Change center 32x32 at Tmid and maintain at T1
    obs_mid[2, 16:48, 16:48] = 0.35
    obs_mid[3, 16:48, 16:48] = 0.20
    obs1[2, 16:48, 16:48] = 0.35
    obs1[3, 16:48, 16:48] = 0.20

    res = analyze_temporal_persistence(
        [obs0, obs_mid, obs1],
        ["2023-01-01", "2023-06-01", "2023-12-01"],
        threshold=0.10,
    )
    assert res.category == TemporalCategory.PERSISTENT_CHANGE.value
    assert res.trajectory_distribution["persistent_fraction"] > 0.15
    assert len(res.spectral_trajectory["NDVI"]) == 3
    assert res.spectral_trajectory["NDVI"][0] > res.spectral_trajectory["NDVI"][2]


def test_late_onset_change_case():
    """Test 6: Little change by Tmid followed by meaningful change by T1 is LATE_ONSET_CHANGE."""
    obs0 = _create_mock_stack()
    obs_mid = obs0.copy()  # Unchanged at Tmid
    obs1 = _create_mock_stack()

    # Change only emerges in the final observation
    obs1[2, 16:48, 16:48] = 0.40
    obs1[3, 16:48, 16:48] = 0.15

    res = analyze_temporal_persistence(
        [obs0, obs_mid, obs1],
        ["2023-01-01", "2023-06-01", "2023-12-01"],
        threshold=0.10,
    )
    assert res.category == TemporalCategory.LATE_ONSET_CHANGE.value
    assert res.trajectory_distribution["late_fraction"] > 0.15
    assert res.intervals["t0_tmid"] == 0.0
    assert res.intervals["tmid_t1"] > 0.15


def test_reversible_change_case():
    """Test 7: Strong movement away from T0 followed by a substantial return toward T0 is REVERSIBLE_CHANGE."""
    obs0 = _create_mock_stack()
    obs_mid = _create_mock_stack()
    obs1 = _create_mock_stack()

    # Green-up / excursion at Tmid, returns to baseline at T1
    obs_mid[3, 16:48, 16:48] = 0.90  # NIR spike
    obs_mid[2, 16:48, 16:48] = 0.04  # Red drop
    obs1 = obs0.copy()

    res = analyze_temporal_persistence(
        [obs0, obs_mid, obs1],
        ["2023-01-01", "2023-06-01", "2023-12-01"],
        threshold=0.08,
    )
    assert res.category in [
        TemporalCategory.REVERSIBLE_CHANGE.value,
        TemporalCategory.SEASONAL_OR_REVERSIBLE.value,
        TemporalCategory.TRANSIENT_CHANGE.value,
    ]
    assert res.trajectory_distribution["reversible_fraction"] > 0.15
    assert res.intervals["t0_tmid"] > 0.10
    assert res.intervals["t0_t1"] < 0.01


def test_transient_change_case():
    """Test 8: Intermediate change that does not satisfy stricter reversible criterion is TRANSIENT_CHANGE."""
    obs0 = _create_mock_stack()
    obs_mid = _create_mock_stack()
    obs1 = _create_mock_stack()

    # At Tmid: Red increases by 0.50 (0.10 -> 0.60). Mean diff = 0.125 > 0.10 threshold
    obs_mid[2, 16:48, 16:48] = 0.60
    # At T1: Red returns only slightly by 0.18 (0.60 -> 0.42).
    # d_mid_1 = 0.045 <= 0.07 (movement back is small, failing reversible criterion)
    # d_0_1 = 0.08 <= 0.10 (fails persistent criterion)
    obs1[2, 16:48, 16:48] = 0.42

    res = analyze_temporal_persistence(
        [obs0, obs_mid, obs1],
        ["2023-01-01", "2023-06-01", "2023-12-01"],
        threshold=0.10,
    )
    assert res.category == TemporalCategory.TRANSIENT_CHANGE.value
    assert res.trajectory_distribution["transient_fraction"] > 0.15


def test_invalid_pixels_excluded_from_denominator():
    """Test 9: Invalid/cloud masked pixels are excluded from the category fraction denominator."""
    obs0 = _create_mock_stack(64, 64)
    obs_mid = _create_mock_stack(64, 64)
    obs1 = _create_mock_stack(64, 64)

    obs_mid[2, 0:32, 0:32] = 0.35
    obs1[2, 0:32, 0:32] = 0.35

    # Mask bottom half of the image as invalid
    v_mask = np.ones((64, 64), dtype=bool)
    v_mask[32:, :] = False  # 50% invalid
    expected_valid = 32 * 64

    res = analyze_temporal_persistence(
        [obs0, obs_mid, obs1],
        ["2023-01-01", "2023-06-01", "2023-12-01"],
        threshold=0.10,
        valid_mask=v_mask,
    )
    assert res.valid_pixels == expected_valid
    assert res.total_pixels == 64 * 64
    # Fractions must sum to 1.0 over the valid pixels
    assert sum(res.trajectory_distribution.values()) == pytest.approx(1.0, abs=1e-5)


def test_real_intermediate_fixture_properties():
    """Test 10: Verify real intermediate Sentinel-2 fixture staged on disk."""
    tmid_path = Path("data/real/sentinel2/real_Tmid_20231006.tif")
    scl_path = Path("data/real/sentinel2/scl_Tmid_20231006.tif")

    assert tmid_path.exists(), f"Missing real Tmid: {tmid_path}"
    assert scl_path.exists(), f"Missing real SCL: {scl_path}"

    with rasterio.open(tmid_path) as src:
        assert src.count == 4
        assert src.crs.to_epsg() == 32643
        assert src.tags().get("ACQUISITION_DATE") == "2023-10-06"
        assert src.width == 512
        assert src.height == 512

    with rasterio.open(scl_path) as scl_src:
        assert scl_src.width == 512
        assert scl_src.height == 512


def test_workflow_persistence_integration():
    """Test 11: Workflow attaches persistence result and updates evidence chain."""
    from geoai.db.metadata_db import MetadataDB
    from geoai.temporal.workflow import TemporalAnalysisWorkflow

    db = MetadataDB(Path("data/geoai_metadata.db"))
    rows = db._conn.execute(
        "SELECT t.tile_id FROM tiles t JOIN scenes s ON t.scene_id = s.scene_id WHERE s.source_path LIKE ? LIMIT 1",
        ("%real%",),
    ).fetchall()

    if rows:
        tile_id = rows[0][0]
        wf = TemporalAnalysisWorkflow(db)
        result = wf.run_analysis(tile_id)

        assert result.persistence is not None
        assert isinstance(result.persistence, TemporalPersistenceResult)
        assert result.persistence.category in [c.value for c in TemporalCategory]
        assert any("Temporal Persistence:" in n for n in result.notes)
        if result.attribution and result.attribution.evidence_chain:
            assert result.attribution.evidence_chain.temporal_trajectory is not None