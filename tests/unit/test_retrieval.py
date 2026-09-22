"""tests/unit/test_retrieval.py — Tests for retrieval engine and query planner."""
import warnings
import pytest
import numpy as np


def _build_engine(tmp_path):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from geoai.providers.embeddings.mock_provider import MockEmbeddingProvider
    from geoai.providers.index.faiss_flat import FaissFlat
    from geoai.db.metadata_db import MetadataDB
    from geoai.retrieval.engine import RetrievalEngine
    embedder = MockEmbeddingProvider()
    idx = FaissFlat(512)
    db = MetadataDB(tmp_path / "ret.db")
    return RetrievalEngine(embedder, idx, db), idx, db


def _seed_db_and_index(idx, db, n=5):
    db.insert_scene("sc-ret", {"source_path": "/ret.tif", "file_hash": "hret"})
    for i in range(n):
        tid = f"ret-tile-{i:03d}"
        rng = np.random.default_rng(i)
        v = rng.standard_normal(512).astype(np.float32)
        v /= np.linalg.norm(v)
        idx.add(tid, v)
        db.insert_tile({"tile_id": tid, "scene_id": "sc-ret", "is_empty": False,
                        "acquisition_date": "2024-01-01", "sensor": "test"})
        db.insert_embedding(tid, {"embedding_model": "MOCK-random-v1", "is_mock": True})


def test_empty_index_returns_empty(tmp_path):
    engine, _, _ = _build_engine(tmp_path)
    results = engine.search_text("urban area", top_k=5)
    assert results == []


def test_retrieval_returns_results(tmp_path):
    engine, idx, db = _build_engine(tmp_path)
    _seed_db_and_index(idx, db, n=5)
    results = engine.search_text("forest", top_k=3)
    assert len(results) == 3


def test_results_sorted_by_score_descending(tmp_path):
    engine, idx, db = _build_engine(tmp_path)
    _seed_db_and_index(idx, db, n=10)
    results = engine.search_text("water body", top_k=10)
    scores = [r.similarity_score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_result_has_provenance_fields(tmp_path):
    engine, idx, db = _build_engine(tmp_path)
    _seed_db_and_index(idx, db, n=3)
    results = engine.search_text("construction", top_k=1)
    r = results[0]
    assert r.tile_id.startswith("ret-tile-")
    assert r.scene_id == "sc-ret"
    assert r.rank == 1
    assert r.acquisition_date == "2024-01-01"


def test_top_k_respected(tmp_path):
    engine, idx, db = _build_engine(tmp_path)
    _seed_db_and_index(idx, db, n=20)
    for k in [1, 5, 10, 15]:
        results = engine.search_text("test", top_k=k)
        assert len(results) <= k


# ── Query Planner tests ──────────────────────────────────────────────────────

def test_planner_retrieval_intent():
    from geoai.planner.query_planner import plan_query
    plan = plan_query("Find urban areas in northern region")
    assert plan.intent == "semantic_retrieval"
    assert plan.requires_retrieval
    assert not plan.requires_registration
    assert not plan.requires_learned_change


def test_planner_change_intent():
    from geoai.planner.query_planner import plan_query
    plan = plan_query("Where did construction increase between 2022 and 2024?")
    assert plan.intent == "change_detection"
    assert plan.requires_registration
    assert plan.requires_temporal_selection
    assert plan.requires_spectral_analysis


def test_planner_empty_query():
    from geoai.planner.query_planner import plan_query
    plan = plan_query(None, None)
    assert plan.intent == "empty"
    assert not plan.requires_retrieval


def test_planner_top_k_passed():
    from geoai.planner.query_planner import plan_query
    plan = plan_query("find forests", top_k=25)
    assert plan.top_k == 25
