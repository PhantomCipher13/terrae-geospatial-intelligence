"""
terrae/app_factory.py
Dependency-injection factory — builds all application components from config.
"""
from __future__ import annotations
import logging
import os
from pathlib import Path
from typing import Optional, Tuple
import yaml

logger = logging.getLogger(__name__)


def _load_config(config_path: Optional[str] = None) -> dict:
    if config_path is None:
        config_path = os.environ.get("TERRAE_CONFIG", "configs/config.yaml")
    p = Path(config_path)
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {p.resolve()}")
    with open(p, encoding="utf-8-sig") as f:
        return yaml.safe_load(f)


def build_embedding_provider(cfg: dict):
    emb_cfg = cfg.get("embedding", {})
    provider_name = emb_cfg.get("provider", "").strip().lower()

    if provider_name == "mock":
        from terrae.providers.embeddings.mock_provider import MockEmbeddingProvider
        return MockEmbeddingProvider()

    elif provider_name == "remoteclip":
        from terrae.providers.embeddings.remoteclip_provider import RemoteCLIPProvider
        rc_cfg = emb_cfg.get("remoteclip", {})
        model_name = rc_cfg.get("model", "ViT-B-32")

        ckpt = rc_cfg.get("checkpoint")
        if ckpt:
            weights_path = Path(ckpt)
        else:
            models_dir = Path(cfg.get("storage", {}).get("models_dir", "models/local"))
            weights_path = models_dir / f"RemoteCLIP-{model_name}.pt"

        device = rc_cfg.get("device", "cpu")
        return RemoteCLIPProvider(
            model_name=model_name,
            weights_path=weights_path,
            device=device,
        )
    elif not provider_name:
        raise ValueError("embedding.provider is not set in configs/config.yaml.")
    else:
        raise ValueError(f"Unknown embedding provider: '{provider_name}'.")


def build_index_backend(cfg: dict) -> Tuple:
    backend_name = cfg.get("index", {}).get("backend", "faiss_flat")
    dim = cfg.get("index", {}).get("embedding_dim", 512)
    index_dir = cfg.get("storage", {}).get("index_dir", "data/faiss_index")

    if backend_name == "faiss_flat":
        from terrae.providers.index.faiss_flat import FaissFlat
        idx = FaissFlat(embedding_dim=dim)
        idx_path = Path(index_dir)
        if (idx_path / "faiss_flat.index").exists():
            idx.load(index_dir)
            logger.info(f"Loaded existing index: {idx.total_vectors} vectors")
        return idx, index_dir
    else:
        raise ValueError(f"Unknown index backend: '{backend_name}'")


def build_metadata_db(cfg: dict):
    from terrae.db.metadata_db import MetadataDB
    db_path = Path(cfg.get("storage", {}).get("db_path", "data/terrae_metadata.db"))
    return MetadataDB(db_path)


def build_quality_assessor(cfg: dict):
    name = cfg.get("quality", {}).get("assessor", "basic")
    if name == "basic":
        from terrae.providers.quality.basic import BasicQualityAssessor
        return BasicQualityAssessor(
            nodata_fail_threshold=cfg.get("quality", {}).get("nodata_fail_threshold", 0.9),
            nodata_warn_threshold=cfg.get("quality", {}).get("nodata_warn_threshold", 0.5),
        )
    return None


def build_ingest_pipeline(cfg: dict | None = None, config_path: str | None = None):
    if cfg is None:
        cfg = _load_config(config_path)
    from terrae.ingest.pipeline import IngestPipeline
    embedder = build_embedding_provider(cfg)
    idx, index_dir = build_index_backend(cfg)
    db = build_metadata_db(cfg)
    quality = build_quality_assessor(cfg)
    pipeline = IngestPipeline(
        embedding_provider=embedder,
        index_backend=idx,
        metadata_db=db,
        quality_assessor=quality,
        tile_size=cfg.get("ingest", {}).get("tile_size", 256),
        tile_overlap=cfg.get("ingest", {}).get("tile_overlap", 0),
        nodata_threshold=cfg.get("ingest", {}).get("nodata_threshold", 0.9),
        quality_fail_action=cfg.get("ingest", {}).get("quality_fail_action", "skip"),
    )
    return pipeline, idx, db, index_dir


def build_retrieval_engine(cfg: dict | None = None, config_path: str | None = None):
    if cfg is None:
        cfg = _load_config(config_path)
    from terrae.retrieval.engine import RetrievalEngine
    embedder = build_embedding_provider(cfg)
    idx, index_dir = build_index_backend(cfg)
    db = build_metadata_db(cfg)
    return RetrievalEngine(embedder, idx, db), idx, db

def build_temporal_workflow(cfg: dict | None = None, config_path: str | None = None):
    if cfg is None:
        cfg = _load_config(config_path)
    db = build_metadata_db(cfg)
    from terrae.providers.change.spectral_detector import SpectralChangeDetector
    from terrae.temporal.workflow import TemporalAnalysisWorkflow
    change_detector = SpectralChangeDetector()
    return TemporalAnalysisWorkflow(db, change_detector), db
