# Model Candidates — SIH26227 GeoAI Workstation
**Date:** 2026-09-19

Selection criteria: accuracy × latency × memory × storage × offline feasibility × implementation complexity

---

## RETRIEVAL MODELS (Text-to-Image / Image-to-Image)

### 1. RemoteCLIP ViT-B-32 ⭐ SELECTED (Phase 3 PRIMARY)

| Field | Value |
|-------|-------|
| Purpose | Text-image and image-image retrieval for remote sensing |
| Architecture | CLIP ViT-B-32 fine-tuned on RS image-text pairs |
| Input modality | Image (any RGB-convertible) + Text |
| Supported bands | RGB (3-band input required; we handle band selection in adapter) |
| Parameter count | ~151M (standard ViT-B-32) |
| Model size on disk | ~350MB |
| Local inference | YES — weights downloaded once |
| CPU feasibility | YES — ~200-500ms per image on modern CPU |
| GPU requirement | None required (CPU works) |
| License | CC BY 4.0 |
| Source | github.com/ChenDelong1999/RemoteCLIP, huggingface.co/chendelong/RemoteCLIP |
| HuggingFace ID | chendelong/RemoteCLIP |
| Load method | open_clip.create_model_and_transforms('ViT-B-32', ...) |
| Role in system | Primary embedding model: image tiles + text queries → embeddings |
| Limitations | RGB only input; text encoder is English-only |
| ONNX available | Not officially — can export manually |

**Rationale:** Best balance of RS-specific training, manageable size, open license,
offline-compatible loading via open_clip. Outperforms vanilla CLIP on RS retrieval.

---

### 2. GeoRSCLIP ViT-B-32 (Phase 3 ALTERNATIVE / BENCHMARK)

| Field | Value |
|-------|-------|
| Purpose | RS image-text retrieval, zero-shot classification |
| Architecture | CLIP + PEFT fine-tuned on RS5M (5M RS image-text pairs) |
| Input modality | Image (RGB) + Text |
| Parameter count | ~151M |
| Model size | ~350MB |
| Local inference | YES |
| CPU feasibility | YES |
| License | Unspecified in search results — VERIFY before use |
| Source | huggingface.co/Zilun/GeoRSCLIP |
| Role in system | Benchmark comparison vs RemoteCLIP |
| Limitations | License unclear; RS5M may have noisy labels |

**Rationale:** Larger training corpus (5M vs RemoteCLIP's approach), but license
unclear. Use only after verifying license. ViT-H-14 variant too large for CPU-primary.

---

### 3. GeoRSCLIP ViT-H-14 (DEFERRED)

| Field | Value |
|-------|-------|
| Model size | ~4x ViT-B-32 (~1.5GB) |
| CPU feasibility | POOR — too slow for interactive use |
| Role | Benchmark only on GPU machine |

---

## CHANGE DETECTION MODELS

### 4. Spectral Difference Baseline ⭐ SELECTED (Phase 7 First Implementation)

| Field | Value |
|-------|-------|
| Purpose | Change detection via spectral index differences |
| Indices | NDVI (vegetation), NDWI (water), NBR (burn), MAD (multivariate) |
| Input | Before + after registered multispectral tiles |
| Model size | 0 — no learned model |
| CPU feasibility | EXCELLENT |
| Dependencies | numpy, scipy only |
| Limitations | High false alarm rate without co-registration |
| Role | Spectral evidence layer in evidence fusion |

**Rationale:** Start here. No weight dependency. Measurably correct results.
Establishes baseline before adding learned model.

---

### 5. ChangeFormer (Phase 7 Learned Layer)

| Field | Value |
|-------|-------|
| Purpose | Binary change detection (building-level) |
| Architecture | Siamese Transformer + MLP decoder |
| Input | RGB before + after patches (256x256) |
| Parameter count | ~41M |
| Model size | ~160MB |
| Pretrained on | LEVIR-CD, S2Looking |
| F1 on LEVIR-CD | ~0.90 (reported, not verified by us) |
| CPU inference | ~5-15s per 256x256 patch — SLOW |
| License | MIT (justchenhao/ChangeFormer) |
| Source | github.com/justchenhao/ChangeFormer |
| Role | Learned change evidence; run only after spectral gate passes |
| Limitations | RGB only; slow on CPU; LEVIR-CD optimized |

**Rationale:** Add as second evidence layer in Phase 7. Only invoked after
spectral evidence + registration quality pass — coarse-to-fine strategy.

---

## DENSE EMBEDDING / BACKBONE MODELS

### 6. Prithvi-EO-2.0-300M (Phase 7+ POTENTIAL)

| Field | Value |
|-------|-------|
| Purpose | Multi-spectral EO backbone for dense tasks |
| Architecture | ViT-based MAE + HLS dataset pre-training |
| Supported bands | 6-band HLS (Blue, Green, Red, Narrow NIR, SWIR1, SWIR2) |
| Parameter count | 300M |
| Model size | ~1.2GB |
| Local inference | YES (Apache 2.0) |
| CPU feasibility | POOR for dense inference; feasible for global embeddings |
| License | Apache 2.0 |
| Source | huggingface.co/ibm-nasa-geospatial/Prithvi-EO-2.0-300M |
| Role | Change detection backbone (if fine-tuned on organiser data) |
| Limitations | HLS bands only; not for text retrieval; large |

**Rationale:** Deferred. Too large for Phase 3. Relevant if organiser dataset
is HLS/Sentinel-2 and we need dense segmentation. Revisit in Phase 7.

---

### 7. Clay Foundation Model (Phase 7+ POTENTIAL)

| Field | Value |
|-------|-------|
| Purpose | Multi-sensor EO dense embeddings |
| Architecture | MAE ViT, patch-based |
| Supported sensors | Sentinel-1, Sentinel-2, Landsat, NAIP |
| Model size | ~500MB-1GB depending on variant |
| Local inference | YES (Apache 2.0) |
| License | Apache 2.0 |
| Source | clay-foundation/model HuggingFace |
| Role | Image-to-image retrieval when sensor matches |
| Limitations | No text encoder; complex multi-sensor input handling |

**Rationale:** Interesting for image-to-image similarity across sensors.
Deferred to Phase 7+ after retrieval baseline is established.

---

## MOCK ENCODER (Development Only)

### 8. MockEncoder ⚠️ CLEARLY LABELED MOCK

| Field | Value |
|-------|-------|
| Purpose | Development + testing without real model weights |
| Embedding | Deterministic random (seeded by image content hash) |
| Quality | Meaningless for real retrieval — for testing pipeline only |
| CPU feasibility | INSTANT |
| Label in output | Always prints "WARNING: MockEncoder active — results are meaningless" |

**Use only when:** Real model weights not available locally.
**Never use for:** Benchmarks, demos, evaluations, or any real result.

---

## Selection Summary

| Phase | Retrieval Model | Change Model | Rationale |
|-------|----------------|--------------|-----------|
| Phase 3 (MVP) | MockEncoder → RemoteCLIP ViT-B-32 | None | Pipeline validation |
| Phase 7 | RemoteCLIP ViT-B-32 | Spectral baseline + ChangeFormer | End-to-end |
| Phase 7+ | GeoRSCLIP for benchmark | Prithvi/Clay if dataset fits | Accuracy push |
