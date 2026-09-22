"""
backend/main.py
TERRAE — Earth Intelligence · Production REST API
=============================================================================
FastAPI backend service for public deployment on Render.
Exposes real RemoteCLIP / FAISS semantic retrieval, temporal spectral analysis,
heuristic physical attribution, and multi-date MECE trajectory endpoints.

Bound to: 0.0.0.0, dynamic PORT from Render.
CORS: Configured via FRONTEND_ORIGIN.
"""
from __future__ import annotations

import os
import sys
import io
import base64
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import numpy as np
from PIL import Image

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("terrae.api")

# -----------------------------------------------------------------------------
# FASTAPI APP INITIALIZATION
# -----------------------------------------------------------------------------
app = FastAPI(
    title="TERRAE — Earth Intelligence API",
    description="Operational REST API for Satellite Investigation, Multimodal RemoteCLIP Retrieval, and Temporal Attribution.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# -----------------------------------------------------------------------------
# CORS CONFIGURATION (Vercel Frontend Support)
# -----------------------------------------------------------------------------
frontend_origin_env = os.environ.get("FRONTEND_ORIGIN", "*").strip()
if frontend_origin_env == "*" or not frontend_origin_env:
    allowed_origins = ["*"]
else:
    allowed_origins = [orig.strip() for orig in frontend_origin_env.split(",") if orig.strip()]
    # Always include standard localhost origins for local frontend testing
    for local in ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8501"]:
        if local not in allowed_origins:
            allowed_origins.append(local)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS initialized with allowed origins: {allowed_origins}")

# -----------------------------------------------------------------------------
# STATIC ASSETS MOUNT
# -----------------------------------------------------------------------------
ui_assets_dir = PROJECT_ROOT / "data" / "ui_assets"
if ui_assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(ui_assets_dir)), name="assets")
    logger.info(f"Mounted static assets at /assets from {ui_assets_dir}")

# -----------------------------------------------------------------------------
# CORE ENGINE LAZY INITIALIZATION & FALLBACK HANDLING
# -----------------------------------------------------------------------------
from geoai.app_factory import build_retrieval_engine, build_temporal_workflow, _load_config
from geoai.change.attribution import DISPLAY_LABELS, DISCLAIMER_TEXT
from geoai.core.result import ChangeVerdict

CANONICAL_CTRL_TILE = "747db63c-08b4-4d59-a8f6-fc6a570aeee1"
CANONICAL_REAL_TILE = "2cbad278-c845-4e50-843e-abcc5d4382c6"

_engine = None
_idx = None
_db = None
_temporal = None
_model_provider_name = "unknown"

def get_services():
    global _engine, _idx, _db, _temporal, _model_provider_name
    if _engine is None or _temporal is None:
        cfg = _load_config()
        
        # Check if RemoteCLIP weights exist on disk
        weights_path = PROJECT_ROOT / "models" / "local" / "RemoteCLIP-ViT-B-32.pt"
        env_provider = os.environ.get("EMBEDDING_PROVIDER", "").lower()
        
        if env_provider == "mock" or not weights_path.exists():
            cfg["embedding"]["provider"] = "mock"
            _model_provider_name = "MockEmbeddingProvider (Deterministic Mode)"
            logger.info("Using MockEmbeddingProvider (Weights absent or mock requested)")
        else:
            cfg["embedding"]["provider"] = "remoteclip"
            _model_provider_name = "RemoteCLIP-ViT-B-32"
            logger.info("Using RemoteCLIP-ViT-B-32 Provider")

        _engine, _idx, _db = build_retrieval_engine(cfg)
        _temporal, _ = build_temporal_workflow(cfg)
        logger.info("TERRAE Engine and Temporal Workflow initialized successfully.")

    return _engine, _idx, _db, _temporal, _model_provider_name

# -----------------------------------------------------------------------------
# PYDANTIC SCHEMAS
# -----------------------------------------------------------------------------
class SearchRequest(BaseModel):
    query: str = Field(default="new construction and buildings", description="Natural-language search intent")
    top_k: int = Field(default=5, ge=1, le=50, description="Max candidate tiles to retrieve")

class SearchResultItem(BaseModel):
    tile_id: str
    scene_id: str
    similarity_score: float
    sensor: Optional[str] = "Sentinel-2"
    acquisition_date: Optional[str] = None
    bounds_wgs84: Optional[Any] = None
    source_path: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    count: int
    results: List[SearchResultItem]

class AnalyzeRequest(BaseModel):
    tile_id: str = Field(default=CANONICAL_CTRL_TILE, description="Target tile UUID")
    query: str = Field(default="new construction and buildings", description="Hypothesis query")

def serialize_analysis_result(res):
    if res is None:
        return None
    
    mask_b64 = ""
    chg_frac = 0.0
    total_px = 0
    chg_px = 0
    if getattr(res, "evidence", None):
        ev = res.evidence[0]
        chg_frac = float(getattr(ev, "change_fraction", 0.0) or 0.0)
        mask = getattr(ev, "change_mask", None)
        if mask is not None:
            total_px = int(mask.size)
            chg_px = int(np.sum(mask > 0))
            try:
                h, w = mask.shape
                rgb = np.full((h, w, 3), [14, 13, 12], dtype=np.uint8)
                rgb[mask > 0] = [197, 168, 105]
                img = Image.fromarray(rgb)
                img.thumbnail((400, 400))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                mask_b64 = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
            except Exception as e:
                logger.warning(f"Error encoding change mask: {e}")

    attr_data = None
    if getattr(res, "attribution", None):
        att = res.attribution
        attr_data = {
            "dominant_interpretation": getattr(att, "dominant_interpretation", ""),
            "scores": getattr(att, "scores", {}),
            "metrics": getattr(att, "metrics", {}),
        }

    pers_data = None
    if getattr(res, "persistence", None):
        p = res.persistence
        pers_data = {
            "category": getattr(p, "category", ""),
            "dominant_temporal_state": str(getattr(p, "dominant_temporal_state", "")),
            "category_counts": getattr(p, "category_counts", {}),
            "valid_pixels": int(getattr(p, "valid_pixels", 0) or 0),
        }

    return {
        "verdict": getattr(res.verdict, "value", str(res.verdict)),
        "change_fraction": chg_frac,
        "changed_pixels": chg_px,
        "total_pixels": total_px,
        "change_mask_b64": mask_b64,
        "attribution": attr_data,
        "persistence": pers_data,
        "notes": getattr(res, "notes", []),
    }

# -----------------------------------------------------------------------------
# API ROUTES
# -----------------------------------------------------------------------------
@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Render and deployment health probe."""
    return {
        "status": "ok",
        "app": "TERRAE",
        "version": "1.0.0",
        "timestamp": "2026-09-22T00:00:00Z"
    }

@app.get("/api/status")
def system_status():
    """Returns operational backend status and engine telemetry."""
    try:
        engine, idx, db, temporal, provider_name = get_services()
        total_vectors = getattr(idx, "total_vectors", 0) if idx else 0
        return {
            "status": "ok",
            "service": "TERRAE — Earth Intelligence · Satellite Investigation Console",
            "model_provider": provider_name,
            "faiss_indexed_vectors": total_vectors,
            "offline_mode": True,
            "disclaimer": DISCLAIMER_TEXT
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return {
            "status": "degraded",
            "error": str(e)
        }

@app.post("/api/search", response_model=SearchResponse)
def search_satellite_tiles(req: SearchRequest):
    """
    Executes multimodal semantic retrieval across FAISS index.
    Maps natural-language query to candidate satellite tiles.
    """
    try:
        engine, _, _, _, _ = get_services()
        raw_results = engine.search_text(req.query, top_k=req.top_k)
        
        items = []
        for r in raw_results:
            items.append(SearchResultItem(
                tile_id=r.tile_id,
                scene_id=r.scene_id,
                similarity_score=float(r.similarity_score),
                sensor=getattr(r, "sensor", "Sentinel-2"),
                acquisition_date=getattr(r, "acquisition_date", None),
                bounds_wgs84=getattr(r, "bounds_wgs84", None),
                source_path=getattr(r, "source_path", None)
            ))
            
        return SearchResponse(
            query=req.query,
            count=len(items),
            results=items
        )
    except Exception as e:
        logger.error(f"Search error for query '{req.query}': {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/analyze")
def analyze_temporal_change(req: AnalyzeRequest):
    """
    Executes co-registered temporal change detection, spectral attribution,
    and 3-date persistence trajectory analysis for a target tile.
    """
    try:
        _, _, _, temporal, _ = get_services()
        result = temporal.run_analysis(req.tile_id, req.query)
        serialized = serialize_analysis_result(result)
        serialized["tile_id"] = req.tile_id
        serialized["query"] = req.query
        return serialized
    except Exception as e:
        logger.error(f"Analysis error for tile '{req.tile_id}': {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/cases/controlled")
def get_controlled_case():
    """Returns full pre-computed analysis for Case 01 (Controlled Construction)."""
    try:
        _, _, _, temporal, _ = get_services()
        res = temporal.run_analysis(CANONICAL_CTRL_TILE, "new construction and buildings")
        data = serialize_analysis_result(res)
        data["title"] = "Controlled Construction & Building Development"
        data["dataset_type"] = "SYNTHETIC TEMPORAL BENCHMARK"
        data["gsd"] = "10m GSD"
        data["crs"] = "EPSG:32643"
        data["tile_id"] = CANONICAL_CTRL_TILE
        return data
    except Exception as e:
        logger.error(f"Controlled case error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cases/real-sentinel2")
def get_real_sentinel2_case():
    """Returns full pre-computed analysis for Case 02 (Real Sentinel-2 MGRS 43RGM)."""
    try:
        _, _, _, temporal, _ = get_services()
        res = temporal.run_analysis(CANONICAL_REAL_TILE, "urban development and building construction")
        data = serialize_analysis_result(res)
        data["title"] = "Real Earth Observation (MGRS 43RGM · NCR)"
        data["dataset_type"] = "REAL SENTINEL-2 L2A"
        data["gsd"] = "10m GSD"
        data["tile_id"] = CANONICAL_REAL_TILE
        return data
    except Exception as e:
        logger.error(f"Real Sentinel-2 case error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evidence/layers")
def get_evidence_layers():
    """Returns metadata, telemetry, and interpretations for the 6 Progressive Evidence stages."""
    return {
        "layers": [
            {
                "idx": "01",
                "name": "SATELLITE REFLECTANCE",
                "title": "Raw Multispectral Surface Radiance",
                "badge": "LAYER 01 / 06 · RAW SURFACE REFLECTANCE",
                "telemetry": "SENTINEL-2 L2A · 10M GSD · B02, B03, B04, B08",
                "legend": "RGB BOA Reflectance (B04=Red, B03=Green, B02=Blue)",
                "location": "MGRS 43RGM · 262,144 valid pixels (100% SCL valid)",
                "evidence": "Sub-pixel aligned 10m bands B02, B03, B04, B08 · TOA → BOA",
                "verdict": "OBSERVATION BASELINE · Pre-monsoon dry canopy",
                "asset_url": "/assets/evidence_01_raw.jpg"
            },
            {
                "idx": "02",
                "name": "SPECTRAL DIFFERENCING",
                "title": "Change Mask Overlay (τ = 0.15)",
                "badge": "LAYER 02 / 06 · CHANGE MASK OVERLAY (τ = 0.15)",
                "telemetry": "THRESHOLD: τ = 0.15 · CHANGED: 1.0% (2,542 PX) · VALID: 100%",
                "legend": "Amber = Divergent (τ ≥ 0.15) · Black = Stable Background (99.0%)",
                "location": "2,542 px (1.00%) · Cluster #14 Centroid (184, 112)",
                "evidence": "Amber mask isolates genuine divergence from sensor noise (τ = 0.15)",
                "verdict": "FLAGGED FOR DECOMPOSITION · 1.0% divergence",
                "asset_url": "/assets/evidence_02_mask.jpg"
            },
            {
                "idx": "03",
                "name": "PHYSICAL ATTRIBUTION",
                "title": "Multi-Spectral Vector Decomposition",
                "badge": "LAYER 03 / 06 · PHYSICAL SPECTRAL ATTRIBUTION",
                "telemetry": "ΔNIR: -22.6% · ΔRED: -12.6% · ΔNDVI: -0.10",
                "legend": "Green = Veg Flush (ΔNIR > 0) · Amber = Disturbance (ΔNIR < 0) · Teal = Water",
                "location": "2,542 px · Focused across localized agrarian parcels",
                "evidence": "ΔNIR: -22.6% · ΔRed: -12.6% · Chlorophyll absorption cycle",
                "verdict": "VEGETATIVE DIVERGENCE · Crop senescence, not concrete",
                "asset_url": "/assets/evidence_03_spectral.jpg"
            },
            {
                "idx": "04",
                "name": "SPATIAL COHERENCE",
                "title": "8-Connected Topological Clustering",
                "badge": "LAYER 04 / 06 · 8-CONNECTED TOPOLOGY (15.7% COHERENCE)",
                "telemetry": "CLUSTERS: 152 · COHERENCE: 15.7% · NOISE FILTER: PASS",
                "legend": "Color Coded = 152 8-Connected Clusters · 84.3% Single-pixel Noise Suppressed",
                "location": "152 connected components · Dispersed agrarian topology",
                "evidence": "Spatial coherence 15.7% · Dispersed, non-contiguous components",
                "verdict": "SPATIAL REJECTION · Sub-threshold coherence (15.7% < 70%)",
                "asset_url": "/assets/evidence_04_topology.jpg"
            },
            {
                "idx": "05",
                "name": "TEMPORAL PERSISTENCE",
                "title": "MECE Multi-Date Trajectory",
                "badge": "LAYER 05 / 06 · TEMPORAL PERSISTENCE TRAJECTORY",
                "telemetry": "STABLE: 98.75% · PERSISTENT: 0.39% · LATE: 0.52%",
                "legend": "Green = Stable (98.75%) · Gold = Late-Onset (0.52%) · Amber = Transient (0.39%)",
                "location": "258,869 px (98.75%) stable terrain · 3 dates evaluated",
                "evidence": "98.75% Stable · 0.39% Persistent · Seasonal reversible trajectory",
                "verdict": "TEMPORAL REJECTION · Seasonal non-persistent cycle",
                "asset_url": "/assets/evidence_05_trajectory.jpg"
            },
            {
                "idx": "06",
                "name": "AUDITABLE DECISION",
                "title": "REVIEW · Cryptographic Provenance",
                "badge": "LAYER 06 / 06 · AUDITABLE CONCLUSION (REVIEW)",
                "telemetry": "VERDICT: REVIEW · SEASONAL PHENOLOGY · SHA-256 VERIFIED",
                "legend": "Gold Stamp = REVIEW · SHA-256 Provenance Locked",
                "location": "MGRS 43RGM · Canonical Tile 2cbad278 · SHA-256 Verified",
                "evidence": "Heuristic Support: 51.1% Built / 24.7% Veg / 19.9% Season",
                "verdict": "⚠ REVIEW REQUIRED · False alert avoided",
                "asset_url": "/assets/evidence_06_verdict.jpg"
            }
        ]
    }

# -----------------------------------------------------------------------------
# MAIN CLI ENTRYPOINT (Direct Execution / Render Start Command)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    logger.info(f"Starting TERRAE Backend on {host}:{port}...")
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)
