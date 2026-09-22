"""
geoai/providers/index/faiss_flat.py
Concrete IndexBackend: FAISS IndexFlatIP with IDMap for string tile_ids.

- IndexFlatIP = exact inner-product search (== cosine similarity on unit vectors)
- IndexIDMap wraps it to use 64-bit int internal IDs
- tile_id <-> int mapping maintained in self._id_map (dict, not FAISS)
- index + id_map saved to separate files for portability

Phase 3: FlatIP (exact, any size).
Future: swap to HNSW or IVF-PQ via IndexBackend swap — no caller changes needed.
"""
from __future__ import annotations
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from geoai.providers.index.base import IndexBackend

logger = logging.getLogger(__name__)


class FaissFlat(IndexBackend):
    """
    FAISS IndexFlatIP wrapped with string tile_id mapping.
    Thread-safety: not guaranteed — single-writer assumed for MVP.
    """

    def __init__(self, embedding_dim: int) -> None:
        try:
            import faiss
            self._faiss = faiss
        except ImportError:
            raise ImportError(
                "faiss-cpu is required. Install with: pip install faiss-cpu"
            )

        self._dim = embedding_dim
        self._index = self._faiss.IndexIDMap(
            self._faiss.IndexFlatIP(embedding_dim)
        )
        # tile_id (str) -> internal int64 id
        self._str_to_int: Dict[str, int] = {}
        # internal int64 -> tile_id (str)
        self._int_to_str: Dict[int, str] = {}
        self._next_id: int = 0

    # ------------------------------------------------------------------ #
    # Properties                                                           #
    # ------------------------------------------------------------------ #

    @property
    def index_id(self) -> str:
        return f"faiss-flat-ip-dim{self._dim}"

    @property
    def embedding_dim(self) -> int:
        return self._dim

    @property
    def total_vectors(self) -> int:
        return self._index.ntotal

    # ------------------------------------------------------------------ #
    # Mutation                                                             #
    # ------------------------------------------------------------------ #

    def add(self, tile_id: str, vector: np.ndarray) -> None:
        if self.contains(tile_id):
            raise ValueError(f"Duplicate tile_id '{tile_id}' — already indexed.")
        vec = self._validate_vector(vector)
        int_id = self._next_id
        self._index.add_with_ids(vec.reshape(1, -1), np.array([int_id], dtype=np.int64))
        self._str_to_int[tile_id] = int_id
        self._int_to_str[int_id] = tile_id
        self._next_id += 1

    def add_batch(self, tile_ids: List[str], vectors: np.ndarray) -> None:
        if len(tile_ids) != vectors.shape[0]:
            raise ValueError("tile_ids and vectors length mismatch.")
        duplicates = [t for t in tile_ids if self.contains(t)]
        if duplicates:
            raise ValueError(f"Duplicate tile_ids detected: {duplicates[:5]}")

        vecs = vectors.astype(np.float32)
        int_ids = np.arange(
            self._next_id, self._next_id + len(tile_ids), dtype=np.int64
        )
        self._index.add_with_ids(vecs, int_ids)
        for tile_id, int_id in zip(tile_ids, int_ids.tolist()):
            self._str_to_int[tile_id] = int_id
            self._int_to_str[int_id] = tile_id
        self._next_id += len(tile_ids)

    # ------------------------------------------------------------------ #
    # Search                                                               #
    # ------------------------------------------------------------------ #

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int,
    ) -> List[Tuple[str, float]]:
        if self.total_vectors == 0:
            return []
        k = min(top_k, self.total_vectors)
        vec = self._validate_vector(query_vector).reshape(1, -1)
        scores, int_ids = self._index.search(vec, k)
        results = []
        for score, iid in zip(scores[0], int_ids[0]):
            if iid < 0:       # FAISS returns -1 for unfilled slots
                continue
            tile_id = self._int_to_str.get(int(iid))
            if tile_id is not None:
                results.append((tile_id, float(score)))
        return results

    # ------------------------------------------------------------------ #
    # Utilities                                                            #
    # ------------------------------------------------------------------ #

    def contains(self, tile_id: str) -> bool:
        return tile_id in self._str_to_int

    def is_trained(self) -> bool:
        return True   # FlatIP needs no training

    # ------------------------------------------------------------------ #
    # Persistence                                                          #
    # ------------------------------------------------------------------ #

    def save(self, path: str) -> None:
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        index_file = p / "faiss_flat.index"
        idmap_file = p / "faiss_idmap.json"
        self._faiss.write_index(self._index, str(index_file))
        with open(idmap_file, "w") as f:
            json.dump({
                "str_to_int": self._str_to_int,
                "int_to_str": {str(k): v for k, v in self._int_to_str.items()},
                "next_id": self._next_id,
                "embedding_dim": self._dim,
            }, f)
        logger.info(f"Index saved: {self.total_vectors} vectors → {p}")

    def load(self, path: str) -> None:
        p = Path(path)
        index_file = p / "faiss_flat.index"
        idmap_file = p / "faiss_idmap.json"
        if not index_file.exists() or not idmap_file.exists():
            raise FileNotFoundError(f"Index files not found in '{p}'.")
        self._index = self._faiss.read_index(str(index_file))
        with open(idmap_file) as f:
            data = json.load(f)
        self._str_to_int = data["str_to_int"]
        self._int_to_str = {int(k): v for k, v in data["int_to_str"].items()}
        self._next_id = data["next_id"]
        logger.info(f"Index loaded: {self.total_vectors} vectors from {p}")

    # ------------------------------------------------------------------ #
    # Internal                                                             #
    # ------------------------------------------------------------------ #

    def _validate_vector(self, vec: np.ndarray) -> np.ndarray:
        vec = np.asarray(vec, dtype=np.float32)
        if vec.ndim != 1 or vec.shape[0] != self._dim:
            raise ValueError(
                f"Expected 1D vector of length {self._dim}, got shape {vec.shape}."
            )
        norm = np.linalg.norm(vec)
        if norm < 1e-10:
            raise ValueError("Zero-norm vector cannot be added to inner-product index.")
        return vec
