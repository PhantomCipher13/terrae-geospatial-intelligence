# System Architecture — SIH26227 TERRAE Workstation
**Version:** 0.1 (Phase 3 MVP)  
**Last Updated:** 2026-09-19

---

## 1. Guiding Principles

1. **Correctness first** — no fake results, no invented benchmarks
2. **Offline-first** — zero runtime network calls after models are staged
3. **Sensor-agnostic** — never assume RGB; handle multispectral and SAR
4. **Modular** — each component has a clean interface; swap implementations freely
5. **Provenance** — every result is traceable to source data + model version
6. **Coarse-to-fine** — expensive operations only run on justified candidates

---

## 2. High-Level Pipeline

```
USER (text query or image query)
         │
         ▼
┌─────────────────────────┐
│   QUERY UNDERSTANDING   │  Parse intent, detect modality (text/image)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  METADATA PRE-FILTER    │  Date range, sensor type, geographic bounds
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  RS SEMANTIC RETRIEVAL  │  RemoteCLIP / GeoRSCLIP → FAISS search
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    TOP-K CANDIDATES     │  Ranked by cosine similarity
└────────────┬────────────┘
             │  (optional deeper analysis)
             ▼
┌─────────────────────────┐
│  EO RERANKING           │  Band-aware feature reranking
└────────────┬────────────┘
             │  (if temporal analysis requested)
             ▼
┌─────────────────────────┐
│ TEMPORAL CANDIDATE SEL. │  Find before/after scene pairs
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  IMAGE QUALITY GATE     │  Cloud fraction, nodata fraction, SNR
└────────────┬────────────┘
             │  PASS or ABSTAIN("insufficient quality")
             ▼
┌─────────────────────────┐
│ REGISTRATION QUALITY    │  Co-register, compute NCC/MI quality score
└────────────┬────────────┘
             │  PASS or ABSTAIN("registration inadequate")
             ▼
┌─────────────────────────┐
│   SPECTRAL EVIDENCE     │  NDVI diff, NDWI diff, NBR diff, MAD
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  LEARNED CHANGE MODEL   │  ChangeFormer / BIT-CD (Phase 7+)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  TEMPORAL PERSISTENCE   │  Change present across ≥2 dates?
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   EVIDENCE FUSION       │  Combine spectral + learned + temporal
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  VERDICT: SUPPORTED / REVIEW / ABSTAIN│
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────┐
│  PROVENANCE + AUDIT     │  Full trace: scene→tile→model→version→time
└─────────────────────────┘
```

---

## 3. Storage Architecture

```
GeoTIFF / COG files (on-disk, organized by scene)
              │
              ▼
    ┌─────────────────────────────────────────────┐
    │            INGEST PIPELINE                  │
    │  validate → read metadata → tile → embed    │
    └──────────┬──────────────────────────────────┘
               │
     ┌─────────┼──────────────────────────────────────┐
     │         │                                      │
     ▼         ▼                                      ▼
┌─────────┐ ┌───────────────────┐          ┌─────────────────┐
│  Tile   │ │   SQLite DB       │          │  FAISS Index    │
│  Store  │ │  (metadata_db)    │          │  (.faiss file)  │
│ (disk)  │ │                   │          │                 │
│         │ │ scenes table      │          │  vectors        │
│ PNG/NPY │ │ tiles table       │◄────────►│  (normalized)   │
│ arrays  │ │ embeddings table  │          │                 │
└─────────┘ │ provenance table  │          └─────────────────┘
            └───────────────────┘
                     │
                     ▼ (stable tile_id links all three)
```

### Key Design Decision: Separate Vector Index from Metadata DB
- FAISS index holds ONLY float32 vectors + integer IDs
- SQLite holds human-readable metadata + provenance
- A tile_id (UUID) is the stable bridge between both
- If FAISS index is rebuilt, metadata is preserved

---

## 4. Module Structure

```
terrae/
├── terrae/
│   ├── __init__.py
│   ├── adapters/              # Sensor/band adapters
│   │   ├── base.py            # Abstract BandAdapter
│   │   ├── optical.py         # OpticalAdapter (RGB + multispectral)
│   │   ├── sar.py             # SARAdapter (SAR amplitude/phase)
│   │   ├── generic.py         # GenericRasterAdapter (fallback)
│   │   └── registry.py        # Auto-detect sensor, dispatch adapter
│   ├── ingest/                # Ingestion pipeline
│   │   ├── validator.py       # Raster validation
│   │   ├── reader.py          # Metadata extraction
│   │   ├── tiler.py           # Memory-safe windowed tiling
│   │   └── pipeline.py        # Orchestrate full ingest
│   ├── embeddings/            # Embedding models
│   │   ├── base.py            # Abstract EmbeddingEncoder
│   │   ├── mock_encoder.py    # MOCK: deterministic random (labeled)
│   │   └── remoteclip_encoder.py  # RemoteCLIP (real, needs weights)
│   ├── index/                 # Vector index
│   │   └── faiss_index.py     # FAISS wrapper (Flat→HNSW)
│   ├── db/                    # Local metadata DB
│   │   └── metadata_db.py     # SQLite schema + CRUD
│   ├── retrieval/             # Query handling
│   │   └── query.py           # Text/image → ranked tile results
│   ├── provenance/            # Provenance tracking
│   │   └── schema.py          # Pydantic provenance models
│   └── change/                # (Phase 7) Change detection
│       ├── quality.py         # Image quality gate
│       ├── registration.py    # Co-registration wrapper
│       ├── spectral.py        # Spectral indices + difference
│       ├── learned.py         # Learned change model adapter
│       └── fusion.py          # Evidence fusion + verdict
├── configs/
│   └── config.yaml            # All tunable parameters
├── scripts/
│   ├── ingest.py              # CLI: ingest a GeoTIFF
│   ├── query.py               # CLI: text query
│   └── download_models.py     # CLI: pre-stage model weights
├── tests/
│   ├── conftest.py
│   └── unit/
│       ├── test_validator.py
│       ├── test_tiler.py
│       ├── test_db.py
│       ├── test_index.py
│       └── test_query.py
├── evaluation/
│   ├── retrieval/             # Recall@K, MRR, nDCG scripts
│   ├── change/                # F1, IoU, FPR scripts
│   ├── robustness/            # Stress tests
│   └── system/                # Latency, memory, storage
└── docs/
    ├── PROJECT_STATUS.md
    ├── OFFLINE_REQUIREMENTS.md
    ├── architecture/
    │   └── ARCHITECTURE.md    # This file
    ├── research/
    │   ├── RESEARCH_LOG.md
    │   ├── COMPETITOR_ANALYSIS.md
    │   └── MODEL_CANDIDATES.md
    ├── benchmarks/            # Machine-readable JSON results
    └── decisions/             # Architecture decision records
```

---

## 5. Sensor Adapter Design

```python
class BandAdapter(ABC):
    @property
    def sensor_type(self) -> str: ...
    @property
    def supported_bands(self) -> List[str]: ...
    def normalize(self, array: np.ndarray) -> np.ndarray: ...
    def preprocess_for_embedding(self, array: np.ndarray) -> np.ndarray: ...
    def extract_quality_info(self, array: np.ndarray) -> dict: ...
    def get_rgb_preview(self, array: np.ndarray) -> np.ndarray: ...
```

Dispatch logic: `registry.py` inspects band count + metadata to select adapter.

---

## 6. Embedding Adapter Design

```python
class EmbeddingEncoder(ABC):
    @property
    def is_mock(self) -> bool: ...         # Must be True for MOCK adapters
    @property
    def embedding_dim(self) -> int: ...
    @property
    def model_version(self) -> str: ...
    def encode_image(self, image: np.ndarray) -> np.ndarray: ...  # float32 (dim,)
    def encode_text(self, text: str) -> np.ndarray: ...           # float32 (dim,)
```

All embeddings are L2-normalized before storage and search.

---

## 7. Performance Tiers

| Tier | Hardware | Index Type | Model | Expected Query Latency |
|------|---------|------------|-------|----------------------|
| CPU-only | Any machine | FlatIP | RemoteCLIP ViT-B-32 | ~500ms-2s |
| Modest GPU | 4GB VRAM | HNSW | RemoteCLIP ViT-B-32 | ~100-300ms |
| Full GPU | 8GB+ VRAM | HNSW | GeoRSCLIP ViT-H-14 | ~50-150ms |

**IMPORTANT: These are estimates only. Real benchmarks in `evaluation/system/`.**

---

## 8. Provenance Schema (Summary)

Every tile result includes:
- `tile_id`: UUID stable identifier
- `scene_id`: Parent scene UUID
- `source_file`: Absolute path + SHA256 hash
- `acquisition_date`: ISO 8601 if available in metadata
- `sensor`: Detected or declared sensor type
- `crs`: Coordinate reference system EPSG code
- `bounds`: Lon/lat bounding box of tile
- `embedding_model`: Model name + version used
- `embedding_version`: Hash of model weights (first 8 chars of sha256)
- `preprocessing_version`: Adapter name + version
- `ingest_timestamp`: When tile was indexed
- `analysis_timestamp`: When query/analysis was run
- `similarity_score`: Float cosine similarity to query
