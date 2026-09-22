"""
geoai/retrieval/engine.py
Semantic retrieval engine.
- Accepts text or image query
- Generates embedding via EmbeddingProvider (no hardcoded model)
- Searches IndexBackend (no hardcoded FAISS calls)
- Fetches tile metadata from MetadataDB
- Returns List[RetrievalResult] with provenance
"""
from __future__ import annotations
import json
import logging
import time
from pathlib import Path
from typing import List, Optional
import numpy as np

from geoai.core.result import RetrievalResult, AnalysisPlan
from geoai.providers.embeddings.base import EmbeddingProvider
from geoai.providers.index.base import IndexBackend
from geoai.db.metadata_db import MetadataDB

logger = logging.getLogger(__name__)


class RetrievalEngine:
    """
    Model-agnostic semantic retrieval engine.
    Depends only on abstract interfaces — never imports concrete models directly.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        index_backend: IndexBackend,
        metadata_db: MetadataDB,
    ) -> None:
        self._embedder = embedding_provider
        self._index = index_backend
        self._db = metadata_db

    def search_text(
        self,
        query_text: str,
        top_k: int = 10,
        plan: Optional[AnalysisPlan] = None,
    ) -> List[RetrievalResult]:
        """
        Embed query_text and search the index.
        Returns up to top_k RetrievalResult objects ranked by similarity.
        """
        if self._embedder.is_mock:
            logger.warning(
                "⚠️  RetrievalEngine: MockEmbeddingProvider active. "
                "Results are SEMANTICALLY MEANINGLESS."
            )

        if self._index.total_vectors == 0:
            logger.warning("Index is empty — no results possible. Have you ingested any imagery?")
            return []

        t0 = time.time()
        query_vec = self._embedder.encode_text(query_text)
        embed_time = time.time() - t0

        t1 = time.time()
        raw_results = self._index.search(query_vec, top_k)
        search_time = time.time() - t1

        logger.info(
            f"Query: '{query_text}' | "
            f"embed={embed_time*1000:.1f}ms | "
            f"search={search_time*1000:.1f}ms | "
            f"hits={len(raw_results)}"
        )

        results = []
        for rank, (tile_id, score) in enumerate(raw_results, start=1):
            tile_meta = self._db.get_tile(tile_id)
            if tile_meta is None:
                logger.warning(f"tile_id '{tile_id}' found in index but not in DB — skipping.")
                continue

            # Parse bounds from JSON string if stored that way
            bounds = tile_meta.get("bounds_wgs84")
            if isinstance(bounds, str):
                try:
                    bounds = json.loads(bounds)
                except Exception:
                    bounds = None

            # source_path is stored in scenes table, not tiles
            source_path = tile_meta.get("source_path")
            if source_path is None:
                scene = self._db.get_scene(tile_meta.get("scene_id", ""))
                source_path = scene.get("source_path") if scene else None

            result = RetrievalResult(
                tile_id=tile_id,
                scene_id=tile_meta.get("scene_id", ""),
                similarity_score=score,
                rank=rank,
                bounds_wgs84=tuple(bounds) if bounds else None,
                acquisition_date=tile_meta.get("acquisition_date"),
                sensor=tile_meta.get("sensor"),
                sensor_type=tile_meta.get("sensor_type"),
                source_path=source_path,
                embedding_model=tile_meta.get("embedding_model") or self._embedder.model_id,
                metadata=tile_meta,
            )
            results.append(result)

            # Log provenance
            try:
                self._db.log_provenance(tile_id, "query", {
                    "query_text": query_text,
                    "similarity_score": score,
                    "embedding_model": self._embedder.model_id,
                    "embedding_version": getattr(self._embedder, 'model_version', None),
                    "rank": rank,
                })
            except Exception as e:
                logger.warning(f"Could not log provenance for tile {tile_id}: {e}")

        return results

    def search_image(
        self,
        image_array: np.ndarray,
        top_k: int = 10,
    ) -> List[RetrievalResult]:
        """Image-to-image retrieval (uses encode_image instead of encode_text)."""
        if self._embedder.is_mock:
            logger.warning("⚠️  MockEmbeddingProvider: image-to-image results are meaningless.")
        if self._index.total_vectors == 0:
            return []

        query_vec = self._embedder.encode_image(image_array)
        raw_results = self._index.search(query_vec, top_k)

        results = []
        for rank, (tile_id, score) in enumerate(raw_results, start=1):
            tile_meta = self._db.get_tile(tile_id) or {}
            bounds = tile_meta.get("bounds_wgs84")
            if isinstance(bounds, str):
                try:
                    bounds = json.loads(bounds)
                except Exception:
                    bounds = None
            results.append(RetrievalResult(
                tile_id=tile_id,
                scene_id=tile_meta.get("scene_id", ""),
                similarity_score=score,
                rank=rank,
                bounds_wgs84=tuple(bounds) if bounds else None,
                acquisition_date=tile_meta.get("acquisition_date"),
                sensor=tile_meta.get("sensor"),
                source_path=tile_meta.get("source_path"),
                embedding_model=self._embedder.model_id,
                metadata=tile_meta,
            ))
        return results
