# TERRAE — Project Status
**Product:** TERRAE — Earth Intelligence · Satellite Investigation Console (SIH26227)
**Project:** SIH26227 — Semantic Retrieval and Multi-Temporal Change Analysis of Satellite Imagery
**Last updated:** 2026-09-19
**Test results:** 70/70 PASSED

---

## Vertical Slice — STATUS: WORKING

The following end-to-end pipeline executes without error, fully offline:

```
GeoTIFF (4-band uint16, 512x512, EPSG:4326, 2024-06-15)
  → validate                  [PASS]
  → read_metadata             [bands=4, crs=YES, date=YES, bounds computed]
  → generate_tiles            [4 tiles x 256x256, nodata detection, WGS84 bounds]
  → sensor_adapter            [GenericRasterAdapter — per-band min-max]
  → encode_image              [MockEmbeddingProvider — RANDOM, pipeline test only]
  → faiss_flat index          [4 vectors, save/load verified]
  → metadata_db               [1 scene, 4 tiles, 4 embeddings, provenance]
  → query_planner             [intent classification — retrieval vs change]
  → retrieval_engine          [4 ranked results, bounds + source_path in output]
  
Ingest time: ~0.2s | Query time: <100ms | Network calls: ZERO
```

---

## Module Status

### IMPLEMENTED (real, tested, offline)

| Module | File | Notes |
|--------|------|-------|
| Raster validator | `terrae/ingest/validator.py` | CRS missing = warn not fail; bad file = fail |
| Raster metadata reader | `terrae/ingest/reader.py` | CRS, transform, bounds, band names, date, sensor, nodata, hash |
| Tile generator | `terrae/ingest/tiler.py` | Windowed reads, nodata detection, WGS84 bounds, coverage |
| Ingest pipeline | `terrae/ingest/pipeline.py` | Deduplicate, quality gate, adapt, embed, index, batch DB insert |
| Optical sensor adapter | `terrae/providers/sensors/optical.py` | uint8/uint16 normalisation; RGB by band name |
| SAR sensor adapter | `terrae/providers/sensors/sar.py` | log10 dB — NOT optical normalisation |
| Generic raster adapter | `terrae/providers/sensors/generic.py` | Fallback with explicit warning |
| Sensor registry | `terrae/providers/sensors/registry.py` | Keyword dispatch; Sentinel-1/2/Landsat/etc |
| FAISS Flat index | `terrae/providers/index/faiss_flat.py` | IndexFlatIP + string tile_id mapping, save/load |
| SQLite metadata DB | `terrae/db/metadata_db.py` | scenes, tiles, embeddings, provenance tables |
| Retrieval engine | `terrae/retrieval/engine.py` | Model-agnostic; logs provenance; fetches source_path from scene |
| Query planner | `terrae/planner/query_planner.py` | Intent classification; per-stage flags; skips expensive stages |
| App factory | `terrae/app_factory.py` | Single DI point; config-driven provider selection |
| Config | `configs/config.yaml` | All paths, tile sizes, provider names — no hardcoded machine paths |
| Core data models | `terrae/core/` | RasterMetadata, BandInfo, TileRecord, QualityReport, RegistrationResult, AnalysisPlan, ChangeVerdict |

### MOCK / PLACEHOLDER

| Component | File | Why mock | What's needed |
|-----------|------|----------|---------------|
| Image embeddings | `terrae/providers/embeddings/mock_provider.py` | RemoteCLIP weights not locally staged | Download ~350MB from HuggingFace |
| Text embeddings | same | same | same |

`is_mock = True` property is set. Every call prints a warning. Pipeline passes mock check through to query output (⚠️ MOCK label).

### INTERFACE ONLY (no concrete implementation)

| Interface | File | Concrete impl | Phase |
|-----------|------|---------------|-------|
| EmbeddingProvider | `terrae/providers/embeddings/base.py` | MockProvider, RemoteCLIPProvider (needs weights) | 3 done, real model Phase 3 next |
| IndexBackend | `terrae/providers/index/base.py` | FaissFlat done | — |
| RegistrationProvider | `terrae/providers/registration/base.py` | OpenCVECC written, untested on real data | Phase 7 |
| QualityAssessor | `terrae/providers/quality/base.py` | BasicQualityAssessor (nodata+completeness) | Basic done; cloud mask Phase 7 |
| ChangeDetector | `terrae/providers/change/base.py` | None | Phase 7 |
| TemporalEncoder | `terrae/providers/temporal/base.py` | None | Phase 7+ |

### NOT STARTED

- Spectral change baseline (NDVI / NDWI difference)
- ChangeFormer learned change detector
- Multi-scene temporal query workflow
- Earliest-change identification
- Analyst review workflow / evidence provenance UI
- Frontend / interactive interface
- GeoRSCLIP alternative embedding provider
- Prithvi / Clay integration
- COG streaming (currently reads full tile per window — COG optimization deferred)

---

## Current Embedding Model

**Active:** `MockEmbeddingProvider` (MOCK-random-v1)
- is_mock = True
- embedding_dim = 512
- Results: RANDOM, not semantic
- Guard: every call emits `UserWarning`

**Ready to switch to:** `RemoteCLIPProvider` (RemoteCLIP-ViT-B-32-v1)
- Config: set `embedding.provider = remoteclip` in `configs/config.yaml`
- Requires: `open-clip-torch` installed + `models/local/RemoteCLIP-ViT-B-32.pt`
- requires_bands = ["Red", "Green", "Blue"] (RGB only)

---

## Current Raster Assumptions

- Accepts any band count (1–64 via GenericAdapter; 1–13 OpticalAdapter; 1–4 SARAdapter)
- Sensor type determined from GDAL tags + filename keywords — NOT from file content
- Multispectral bands beyond RGB: accepted, stored in metadata, NOT yet semantically used by any real embedding model
- Nodata: read from rasterio; tiles with >90% nodata skipped from index (configurable)
- CRS missing: ingested with warning; bounds_wgs84 = NULL in DB
- Acquisition date missing: ingested with warning; NULL in DB — never fabricated

---

## Current Index Type

`faiss-flat-ip-dim512` — FAISS IndexFlatIP with IndexIDMap

- Exact search (no approximation)
- Inner product = cosine similarity (all vectors are L2-normalised)
- Suitable for up to ~100k vectors without HNSW upgrade
- Persistent: `data/faiss_index/faiss_flat.index` + `faiss_idmap.json`

---

## Offline Status

All currently implemented modules run 100% offline:
- `rasterio 1.4.4` — GDAL bundled, no network
- `faiss-cpu 1.15.1` — local computation
- `sqlite3` — built-in Python
- `numpy`, `scipy`, `Pillow`, `opencv-python` — local
- `PyYAML`, `pydantic` — local

**NOT offline yet:** Real embedding inference (`RemoteCLIPProvider`) requires `open-clip-torch` — installable once from PyPI, then fully offline.

---

## Known Limitations

1. MockEmbeddingProvider produces random vectors — no semantic retrieval quality
2. `source_path` fetched via JOIN to scenes table at query time (correct but 1 extra DB call per result)
3. SAR adapter normalisation not validated on real Sentinel-1 data
4. GenericAdapter applied to synthetic test GeoTIFF (no sensor tag) — expected, not a bug
5. No duplicate tile detection within a scene (only scene-level deduplication by file hash)
6. `open-clip-torch` not yet installed — needed for RemoteCLIP
7. No multi-file batch ingest script yet

---

## Architecture Verification (8 Requirements)

| # | Requirement | Satisfied |
|---|-------------|-----------|
| 1 | No model hard-coded in core logic | YES — only abstract interfaces used in Pipeline/Engine |
| 2 | Full raster metadata preservation | YES — CRS, transform, bounds, bands, nodata, date, sensor |
| 3 | Registration returns all 5 statuses | YES — enum + interface contract |
| 4 | Expensive stages skip when not needed | YES — QueryPlanner.plan_query() stage flags |
| 5 | FAISS behind IndexBackend abstraction | YES — FaissFlat implements IndexBackend |
| 6 | No runtime network dependency | YES — verified with TRANSFORMERS_OFFLINE=1 |
| 7 | Temporal analysis for N observations | YES — List[TemporalObservation] interface design |
| 8 | ABSTAIN propagation for failed evidence | YES — ChangeVerdict.ABSTAIN + abstain_reason field |
