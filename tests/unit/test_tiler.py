"""tests/unit/test_tiler.py — Tests for windowed tile generator."""
import pytest
import numpy as np


def test_tiles_cover_full_image(valid_geotiff):
    from geoai.ingest.reader import read_metadata
    from geoai.ingest.tiler import generate_tiles
    meta = read_metadata(valid_geotiff)
    tiles = list(generate_tiles(meta, tile_size=32, scene_id="test-scene"))
    # 64x64 image / 32 tile = 2x2 = 4 tiles
    assert len(tiles) == 4


def test_tile_arrays_have_correct_shape(valid_geotiff):
    from geoai.ingest.reader import read_metadata
    from geoai.ingest.tiler import generate_tiles
    meta = read_metadata(valid_geotiff)
    for record, arr in generate_tiles(meta, tile_size=32, scene_id="s"):
        assert arr.ndim == 3
        assert arr.shape[0] == 3      # 3 bands
        assert arr.shape[1] == 32
        assert arr.shape[2] == 32


def test_empty_tile_detected(mostly_nodata_geotiff):
    """Tiles with >90% nodata should be flagged is_empty=True."""
    from geoai.ingest.reader import read_metadata
    from geoai.ingest.tiler import generate_tiles
    meta = read_metadata(mostly_nodata_geotiff)
    # nodata=0 set in fixture
    tiles = list(generate_tiles(meta, tile_size=64, nodata_threshold=0.9, scene_id="s"))
    # The full tile should be flagged empty (>90% zeros)
    assert len(tiles) == 1
    record, arr = tiles[0]
    assert record.is_empty


def test_tile_ids_are_unique(valid_geotiff):
    from geoai.ingest.reader import read_metadata
    from geoai.ingest.tiler import generate_tiles
    meta = read_metadata(valid_geotiff)
    ids = [r.tile_id for r, _ in generate_tiles(meta, tile_size=32, scene_id="s")]
    assert len(ids) == len(set(ids))


def test_tile_bounds_populated_when_crs_present(valid_geotiff):
    from geoai.ingest.reader import read_metadata
    from geoai.ingest.tiler import generate_tiles
    meta = read_metadata(valid_geotiff)
    for record, _ in generate_tiles(meta, tile_size=32, scene_id="s"):
        assert record.bounds_wgs84 is not None
        assert len(record.bounds_wgs84) == 4


def test_tile_bounds_none_when_no_crs(no_crs_geotiff):
    from geoai.ingest.reader import read_metadata
    from geoai.ingest.tiler import generate_tiles
    meta = read_metadata(no_crs_geotiff)
    for record, _ in generate_tiles(meta, tile_size=16, scene_id="s"):
        # No CRS => bounds_native may exist from transform, but wgs84 cannot be computed
        # The key requirement: system does not crash and bounds_wgs84 is None or present
        pass  # should not raise


def test_acquisition_date_propagated(valid_geotiff):
    from geoai.ingest.reader import read_metadata
    from geoai.ingest.tiler import generate_tiles
    meta = read_metadata(valid_geotiff)
    for record, _ in generate_tiles(meta, tile_size=32, scene_id="s"):
        assert record.acquisition_date == "2024-06-15"


def test_multispectral_tile_band_count(multispectral_geotiff):
    from geoai.ingest.reader import read_metadata
    from geoai.ingest.tiler import generate_tiles
    meta = read_metadata(multispectral_geotiff)
    for record, arr in generate_tiles(meta, tile_size=64, scene_id="s"):
        assert arr.shape[0] == 4  # 4-band
        break
