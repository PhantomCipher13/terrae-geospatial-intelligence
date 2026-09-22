"""tests/unit/test_db.py — Tests for SQLite metadata database."""
import pytest
import json


def test_insert_and_retrieve_scene(metadata_db):
    metadata_db.insert_scene("scene-001", {
        "source_path": "/data/scene.tif",
        "file_hash": "abc123",
        "band_count": 3,
        "sensor": "Sentinel-2",
    })
    scene = metadata_db.get_scene("scene-001")
    assert scene is not None
    assert scene["source_path"] == "/data/scene.tif"
    assert scene["sensor"] == "Sentinel-2"


def test_duplicate_scene_detection(metadata_db):
    metadata_db.insert_scene("s1", {"source_path": "/a.tif", "file_hash": "hash-xyz"})
    existing = metadata_db.scene_exists("hash-xyz")
    assert existing == "s1"
    missing = metadata_db.scene_exists("nonexistent-hash")
    assert missing is None


def test_insert_and_retrieve_tile(metadata_db):
    metadata_db.insert_scene("sc1", {"source_path": "/a.tif", "file_hash": "h1"})
    metadata_db.insert_tile({
        "tile_id": "tile-aaa",
        "scene_id": "sc1",
        "tile_row": 0, "tile_col": 0,
        "band_count": 4,
        "is_empty": False,
        "acquisition_date": "2024-01-01",
    })
    tile = metadata_db.get_tile("tile-aaa")
    assert tile is not None
    assert tile["scene_id"] == "sc1"
    assert tile["acquisition_date"] == "2024-01-01"


def test_tile_does_not_exist(metadata_db):
    tile = metadata_db.get_tile("nonexistent-tile")
    assert tile is None


def test_batch_tile_insert(metadata_db):
    metadata_db.insert_scene("sc2", {"source_path": "/b.tif", "file_hash": "h2"})
    tiles = [
        {"tile_id": f"t{i}", "scene_id": "sc2", "is_empty": False}
        for i in range(5)
    ]
    metadata_db.insert_tiles_batch(tiles)
    results = metadata_db.get_tiles_for_scene("sc2")
    assert len(results) == 5


def test_embedding_metadata_stored(metadata_db):
    metadata_db.insert_scene("sc3", {"source_path": "/c.tif", "file_hash": "h3"})
    metadata_db.insert_tile({"tile_id": "t-emb", "scene_id": "sc3", "is_empty": False})
    metadata_db.insert_embedding("t-emb", {
        "embedding_model": "MOCK-random-v1",
        "embedding_dim": 512,
        "is_mock": True,
    })
    tile = metadata_db.get_tile("t-emb")
    assert tile["embedding_model"] == "MOCK-random-v1"
    assert tile["is_mock"] == 1


def test_stats(metadata_db):
    s = metadata_db.stats()
    assert "scenes" in s and "tiles" in s and "embedded" in s
    assert all(isinstance(v, int) for v in s.values())


def test_provenance_log(metadata_db):
    metadata_db.insert_scene("sc4", {"source_path": "/d.tif", "file_hash": "h4"})
    metadata_db.insert_tile({"tile_id": "t-prov", "scene_id": "sc4", "is_empty": False})
    # Should not raise
    metadata_db.log_provenance("t-prov", "query", {
        "query_text": "urban area",
        "similarity_score": 0.85,
        "embedding_model": "MOCK-random-v1",
    })
