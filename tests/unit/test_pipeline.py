"""tests/unit/test_pipeline.py — Integration tests for the ingest pipeline."""
import warnings
import pytest
import numpy as np


def _make_pipeline(tmp_path, tile_size=32):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from geoai.providers.embeddings.mock_provider import MockEmbeddingProvider
    from geoai.providers.index.faiss_flat import FaissFlat
    from geoai.db.metadata_db import MetadataDB
    from geoai.ingest.pipeline import IngestPipeline
    embedder = MockEmbeddingProvider()
    idx = FaissFlat(512)
    db = MetadataDB(tmp_path / "test.db")
    pipeline = IngestPipeline(
        embedding_provider=embedder,
        index_backend=idx,
        metadata_db=db,
        tile_size=tile_size,
    )
    return pipeline, idx, db


def test_full_pipeline_rgb(valid_geotiff, tmp_path):
    pipeline, idx, db = _make_pipeline(tmp_path, tile_size=32)
    report = pipeline.ingest(valid_geotiff)
    assert report.success
    assert not report.skipped
    assert report.tiles_generated == 4  # 64x64 / 32 = 2x2
    assert report.tiles_indexed > 0
    assert idx.total_vectors == report.tiles_indexed
    stats = db.stats()
    assert stats["scenes"] == 1
    assert stats["tiles"] == 4
    assert stats["embedded"] == report.tiles_indexed


def test_full_pipeline_multispectral(multispectral_geotiff, tmp_path):
    pipeline, idx, db = _make_pipeline(tmp_path, tile_size=64)
    report = pipeline.ingest(multispectral_geotiff)
    assert report.success
    assert report.tiles_generated >= 1


def test_duplicate_ingestion_skipped(valid_geotiff, tmp_path):
    pipeline, idx, db = _make_pipeline(tmp_path, tile_size=32)
    report1 = pipeline.ingest(valid_geotiff)
    assert report1.success and not report1.skipped
    report2 = pipeline.ingest(valid_geotiff)
    assert report2.skipped
    assert report2.success
    # Index should not grow
    assert idx.total_vectors == report1.tiles_indexed


def test_no_crs_ingested_without_crash(no_crs_geotiff, tmp_path):
    """Files without CRS should ingest successfully with warnings."""
    pipeline, idx, db = _make_pipeline(tmp_path, tile_size=16)
    report = pipeline.ingest(no_crs_geotiff)
    assert report.success
    assert any("CRS" in w or "crs" in w.lower() for w in report.warnings)


def test_no_date_ingested_without_crash(no_date_geotiff, tmp_path):
    pipeline, idx, db = _make_pipeline(tmp_path, tile_size=16)
    report = pipeline.ingest(no_date_geotiff)
    assert report.success
    # Check that acquisition_date is None (not fabricated) in DB
    tiles = db.get_tiles_for_scene(report.scene_id)
    for t in tiles:
        assert t["acquisition_date"] is None


def test_mostly_nodata_tiles_skipped(mostly_nodata_geotiff, tmp_path):
    pipeline, idx, db = _make_pipeline(tmp_path, tile_size=64)
    report = pipeline.ingest(mostly_nodata_geotiff)
    assert report.success
    assert report.tiles_skipped_empty > 0
    assert report.tiles_indexed == 0  # all tiles are empty


def test_missing_file_fails_gracefully(tmp_path):
    pipeline, idx, db = _make_pipeline(tmp_path)
    from pathlib import Path
    report = pipeline.ingest(Path("/nonexistent/scene.tif"))
    assert not report.success
    # Validator reports file-not-found; it may appear in warnings or errors
    all_messages = report.errors + report.warnings
    assert len(all_messages) > 0
    assert any("not exist" in m or "not found" in m or "nonexistent" in m.lower() for m in all_messages)


def test_index_vectors_retrievable_after_ingest(valid_geotiff, tmp_path):
    pipeline, idx, db = _make_pipeline(tmp_path, tile_size=32)
    report = pipeline.ingest(valid_geotiff)
    assert report.tiles_indexed > 0
    import numpy as np
    rng = np.random.default_rng(42)
    q = rng.standard_normal(512).astype(np.float32)
    q /= np.linalg.norm(q)
    results = idx.search(q, top_k=10)
    assert len(results) == report.tiles_indexed
