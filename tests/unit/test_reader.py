"""tests/unit/test_reader.py — Tests for raster metadata reader."""
import pytest
import datetime


def test_reads_all_spatial_metadata(valid_geotiff):
    from terrae.ingest.reader import read_metadata
    meta = read_metadata(valid_geotiff)
    assert meta.crs_wkt is not None, "CRS WKT should be populated"
    assert meta.affine_transform is not None, "Affine transform should be populated"
    assert meta.bounds_native is not None
    assert meta.bounds_wgs84 is not None
    assert meta.width_px == 64
    assert meta.height_px == 64
    assert meta.band_count == 3


def test_reads_band_names(valid_geotiff):
    from terrae.ingest.reader import read_metadata
    meta = read_metadata(valid_geotiff)
    assert len(meta.bands) == 3
    names = [b.name for b in meta.bands]
    assert "Red" in names or "red" in [n.lower() for n in names if n]


def test_reads_acquisition_date(valid_geotiff):
    from terrae.ingest.reader import read_metadata
    meta = read_metadata(valid_geotiff)
    assert meta.acquisition_date == datetime.date(2024, 6, 15)


def test_missing_crs_is_none(no_crs_geotiff):
    """Missing CRS -> crs_wkt=None, never fabricated."""
    from terrae.ingest.reader import read_metadata
    meta = read_metadata(no_crs_geotiff)
    assert meta.crs_wkt is None
    assert meta.bounds_wgs84 is None  # cannot compute without CRS


def test_missing_date_is_none(no_date_geotiff):
    """Missing date tag -> acquisition_date=None, never fabricated."""
    from terrae.ingest.reader import read_metadata
    meta = read_metadata(no_date_geotiff)
    assert meta.acquisition_date is None
    assert meta.acquisition_datetime is None


def test_multispectral_band_count(multispectral_geotiff):
    from terrae.ingest.reader import read_metadata
    meta = read_metadata(multispectral_geotiff)
    assert meta.band_count == 4
    assert meta.dtype == "uint16"


def test_metadata_completeness_score(valid_geotiff):
    from terrae.ingest.reader import read_metadata
    meta = read_metadata(valid_geotiff)
    assert meta.metadata_completeness is not None
    assert 0.0 <= meta.metadata_completeness <= 1.0


def test_missing_fields_with_no_crs(no_crs_geotiff):
    from terrae.ingest.reader import read_metadata
    meta = read_metadata(no_crs_geotiff)
    missing = meta.missing_fields()
    assert "crs_wkt" in missing


def test_file_hash_populated(valid_geotiff):
    from terrae.ingest.reader import read_metadata
    meta = read_metadata(valid_geotiff)
    assert meta.file_hash_sha256 is not None
    assert len(meta.file_hash_sha256) == 64  # SHA-256 hex
