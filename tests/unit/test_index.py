"""tests/unit/test_index.py — Tests for FAISS FlatIP index backend."""
import pytest
import numpy as np
import warnings


def _rand_unit(dim=512, seed=None):
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(dim).astype(np.float32)
    return v / np.linalg.norm(v)


def test_empty_index_returns_no_results(faiss_index):
    q = _rand_unit(512, seed=0)
    results = faiss_index.search(q, top_k=5)
    assert results == []


def test_add_and_search(faiss_index):
    v1 = _rand_unit(512, seed=1)
    faiss_index.add("tile-001", v1)
    results = faiss_index.search(v1, top_k=1)
    assert len(results) == 1
    tile_id, score = results[0]
    assert tile_id == "tile-001"
    assert abs(score - 1.0) < 1e-4  # self-similarity ~= 1.0


def test_top_k_ordering(faiss_index):
    target = _rand_unit(512, seed=99)
    for i in range(10):
        faiss_index.add(f"tile-{i:03d}", _rand_unit(512, seed=i))
    faiss_index.add("tile-target", target)
    results = faiss_index.search(target, top_k=3)
    assert len(results) == 3
    scores = [s for _, s in results]
    assert scores == sorted(scores, reverse=True)
    assert results[0][0] == "tile-target"


def test_duplicate_raises(faiss_index):
    v = _rand_unit(512, seed=5)
    faiss_index.add("tile-dup", v)
    with pytest.raises(ValueError, match="Duplicate"):
        faiss_index.add("tile-dup", v)


def test_contains(faiss_index):
    v = _rand_unit(512, seed=6)
    assert not faiss_index.contains("tile-xyz")
    faiss_index.add("tile-xyz", v)
    assert faiss_index.contains("tile-xyz")


def test_total_vectors(faiss_index):
    assert faiss_index.total_vectors == 0
    for i in range(5):
        faiss_index.add(f"t{i}", _rand_unit(512, seed=i))
    assert faiss_index.total_vectors == 5


def test_save_and_load(faiss_index, tmp_dir):
    vecs = {f"tile-{i}": _rand_unit(512, seed=i) for i in range(10)}
    for tid, v in vecs.items():
        faiss_index.add(tid, v)
    save_path = str(tmp_dir / "index")
    faiss_index.save(save_path)

    from geoai.providers.index.faiss_flat import FaissFlat
    new_idx = FaissFlat(512)
    new_idx.load(save_path)
    assert new_idx.total_vectors == 10
    for tid in vecs:
        assert new_idx.contains(tid)


def test_load_missing_raises(tmp_dir):
    from geoai.providers.index.faiss_flat import FaissFlat
    idx = FaissFlat(512)
    with pytest.raises(FileNotFoundError):
        idx.load(str(tmp_dir / "nonexistent_index"))


def test_zero_norm_vector_raises(faiss_index):
    zero = np.zeros(512, dtype=np.float32)
    with pytest.raises(ValueError):
        faiss_index.add("tile-zero", zero)


def test_wrong_dimension_raises(faiss_index):
    wrong = _rand_unit(256, seed=7)
    with pytest.raises(ValueError):
        faiss_index.add("tile-wrong-dim", wrong)


def test_batch_add(faiss_index):
    ids = [f"batch-{i}" for i in range(20)]
    vecs = np.stack([_rand_unit(512, seed=i) for i in range(20)])
    faiss_index.add_batch(ids, vecs)
    assert faiss_index.total_vectors == 20
