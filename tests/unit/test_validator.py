"""tests/unit/test_validator.py — Tests for raster validator."""
import pytest
import numpy as np
from pathlib import Path


def test_valid_rgb_passes(valid_geotiff):
    from terrae.ingest.validator import validate_raster
    ok, errors = validate_raster(valid_geotiff)
    assert ok, f"Expected valid, got errors: {errors}"


def test_missing_file_fails():
    from terrae.ingest.validator import validate_raster
    ok, errors = validate_raster(Path("/nonexistent/path/scene.tif"))
    assert not ok
    assert any("not exist" in e or "not found" in e for e in errors)


def test_no_crs_warns_but_passes(no_crs_geotiff):
    """Missing CRS is a warning, not a fatal error — file can still be ingested."""
    from terrae.ingest.validator import validate_raster
    ok, errors = validate_raster(no_crs_geotiff)
    assert ok
    assert any("CRS" in e or "crs" in e.lower() for e in errors)


def test_multispectral_passes(multispectral_geotiff):
    from terrae.ingest.validator import validate_raster
    ok, errors = validate_raster(multispectral_geotiff)
    assert ok


def test_empty_file_fails(tmp_path):
    empty = tmp_path / "empty.tif"
    empty.write_bytes(b"")
    from terrae.ingest.validator import validate_raster
    ok, errors = validate_raster(empty)
    assert not ok


def test_invalid_bytes_fails(tmp_path):
    bad = tmp_path / "corrupt.tif"
    bad.write_bytes(b"NOT A GEOTIFF AT ALL")
    from terrae.ingest.validator import validate_raster
    ok, errors = validate_raster(bad)
    assert not ok
