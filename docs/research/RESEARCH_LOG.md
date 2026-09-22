# Research Log — SIH26227 GeoAI Workstation
**Last Updated:** 2026-09-19

Each entry follows the format:
SOURCE | DATE | WHAT IT PROVES | HOW IT AFFECTS DESIGN

---

## SECTION A — COMPETITOR ANALYSIS

### A1. MR-ROGUE01/SIH-2026
**SOURCE:** GitHub search, web search  
**DATE:** 2026-09-19  
**WHAT IT PROVES:** No publicly indexed repository found under this exact name for the satellite/GeoAI problem. May be private or submitted under different name.  
**HOW IT AFFECTS DESIGN:** Cannot assess. We design independently.

### A2. SlockAhuja/SIH_2026 / AETHER-EO
**SOURCE:** Web search  
**DATE:** 2026-09-19  
**WHAT IT PROVES:** No public repository found. "AETHER-EO" appears in search results as a project name but no open-source codebase indexed.  
**HOW IT AFFECTS DESIGN:** We cannot reverse-engineer competitor choices. We focus on correctness over claiming features.

### A3. General SIH26227 Landscape
**SOURCE:** Web search results, SIH portal references  
**DATE:** 2026-09-19  
**WHAT IT PROVES:** Most SIH satellite-imagery submissions appear to use: (a) a CLIP-family model for retrieval, (b) a UNet or transformer for change detection, (c) a Flask/Gradio UI as frontend. Very few document offline operation or provenance.  
**HOW IT AFFECTS DESIGN:**  
- Opportunity: Strong provenance + offline guarantee differentiates us  
- Opportunity: Sensor-aware band handling is often ignored by competitors  
- Risk: Judges may expect polished UI — keep a minimal but functional interface  

---

## SECTION B — MODEL RESEARCH

### B1. RemoteCLIP
**SOURCE:** ChenDelong/RemoteCLIP GitHub, HuggingFace chendelong/RemoteCLIP, IEEE TGRS 2024  
**DATE:** 2026-09-19  
**WHAT IT PROVES:**  
- Three variants: RN50, ViT-B-32, ViT-L-14  
- OpenCLIP-compatible weights — can load with `open_clip.create_model_and_transforms`  
- License: CC BY 4.0  
- Trained on RS-specific image-text pairs (Box-to-Caption + Mask-to-Box augmentation)  
- Outperforms vanilla CLIP on RS zero-shot classification and retrieval  
- ViT-B-32 is ~350MB, feasible for offline staging  
**HOW IT AFFECTS DESIGN:**  
- PRIMARY RETRIEVAL MODEL choice: RemoteCLIP ViT-B-32  
- Load via open_clip — no Transformers dependency for image encoder  
- Text encoder same architecture as CLIP — offline tokenizer available  
- Must download weights once and store in `models/local/`  

### B2. GeoRSCLIP
**SOURCE:** Zilun/GeoRSCLIP HuggingFace, om-ai-lab/RS5M GitHub, IEEE TGRS 2024  
**DATE:** 2026-09-19  
**WHAT IT PROVES:**  
- Based on CLIP + PEFT (LoRA-style fine-tuning) on RS5M dataset (5M RS image-text pairs)  
- RS5M is largest RS image-text dataset used for CLIP fine-tuning as of 2024  
- Variants: ViT-B-32, ViT-H-14  
- Performance gain: 3-20% on zero-shot classification vs vanilla CLIP, 3-6% on retrieval  
- Loads via standard transformers / open_clip  
**HOW IT AFFECTS DESIGN:**  
- SECONDARY / ALTERNATIVE RETRIEVAL MODEL  
- ViT-H-14 is ~4x larger than B-32 — skip for CPU-primary setup  
- ViT-B-32 is a fair comparison baseline against RemoteCLIP  
- Both can be tested and benchmarked in evaluation phase  

### B3. Prithvi-EO-2.0
**SOURCE:** ibm-nasa-geospatial HuggingFace, IBM/NASA announcements, TerraTorch repo  
**DATE:** 2026-09-19  
**WHAT IT PROVES:**  
- Sizes: 300M and 600M (also Tiny/Small for edge)  
- Trained on 6-band HLS data (Blue, Green, Red, Narrow NIR, SWIR1, SWIR2)  
- License: Apache 2.0  
- TerraTorch framework for fine-tuning and inference  
- Supports offline inference after download  
- NOT a retrieval/text model — it is a segmentation/dense prediction backbone  
**HOW IT AFFECTS DESIGN:**  
- NOT for retrieval in Phase 3 — wrong task type  
- POTENTIAL ROLE: Change detection backbone (Phase 7+) if we fine-tune on LEVIR-CD  
- 300M model feasible on CPU, slower than CLIP-family  
- TerraTorch dependency adds complexity — evaluate carefully  

### B4. Clay Foundation Model
**SOURCE:** clay-foundation/model GitHub, HuggingFace  
**DATE:** 2026-09-19  
**WHAT IT PROVES:**  
- Multi-modal EO foundation model supporting Sentinel-1, Sentinel-2, Landsat  
- Patch-based MAE pre-training  
- License: Apache 2.0  
- Generates dense spatial embeddings rather than CLIP-style global embeddings  
- Designed for time-series and multi-sensor inputs  
**HOW IT AFFECTS DESIGN:**  
- POSSIBLE ROLE: Scene-level embedding for similarity search  
- More complex to use for text-query retrieval (no text encoder)  
- Better suited for image-to-image retrieval (Phase 3 extension)  
- Deferred to Phase 7+ unless organiser dataset confirms multi-sensor need  

### B5. Change Detection Models
**SOURCE:** GitHub survey (open-mmlab/mmsegmentation, justchenhao/ChangeFormer, BIT-CD repo)  
**DATE:** 2026-09-19  
**WHAT IT PROVES:**  
- ChangeFormer (Transformer-based CD): trained on LEVIR-CD, S2Looking  
- BIT-CD (Binary change detection Transformer): strong LEVIR-CD results  
- Both available as pretrained weights on GitHub releases  
- F1 > 0.87 on LEVIR-CD for both  
- CPU inference is slow (~5-15 seconds per 256x256 patch)  
**HOW IT AFFECTS DESIGN:**  
- Start with spectral difference baseline (no learned model dependency)  
- Add ChangeFormer as learned evidence layer in Phase 7  
- Must benchmark actual inference time before claiming suitability  

### B6. FAISS
**SOURCE:** PyPI faiss-cpu, Facebook Research, pip dry-run test  
**DATE:** 2026-09-19  
**WHAT IT PROVES:**  
- faiss-cpu 1.15.1 has prebuilt wheel for Windows cp311 (confirmed by pip dry-run)  
- Supports: IndexFlatL2, IndexFlatIP, IndexHNSWFlat, IndexIVFFlat, IndexIVFPQ  
- IndexFlatIP = exact cosine similarity (after L2 normalization)  
- HNSW: approximate, fast, no training, good for <1M vectors  
- IVF: needs training (kmeans), better for >100k vectors  
- Incremental add supported for all index types  
- Save/load via `faiss.write_index` / `faiss.read_index`  
**HOW IT AFFECTS DESIGN:**  
- Phase 3 MVP: IndexFlatIP (exact, small collection)  
- Phase 5+: Switch to HNSW when tile count > 10k  
- Always normalize embeddings before adding to IP index  

---

## SECTION C — DATASET RESEARCH

### C1. Sentinel-2 (ESA Copernicus)
**SOURCE:** ESA Copernicus Open Access Hub, Sentinel-2 user guide  
**DATE:** 2026-09-19  
**WHAT IT PROVES:**  
- 13 bands: B1(443nm)..B12(2190nm)  
- 10m resolution (B2,B3,B4,B8), 20m (B5,B6,B7,B8A,B11,B12), 60m (B1,B9,B10)  
- 5-day revisit at equator  
- Level-2A = surface reflectance (atmospherically corrected)  
- Format: GeoTIFF per-band or JP2  
- Free, open access  
**HOW IT AFFECTS DESIGN:**  
- Band adapter must handle 13-band S2 without discarding non-RGB bands  
- B4/B3/B2 for RGB visualization, B8 for NIR  
- NDVI = (B8-B4)/(B8+B4) for vegetation change detection  
- Do NOT assume organiser uses S2 without verification  

### C2. LEVIR-CD
**SOURCE:** justchenhao.github.io/LEVIR, Kaggle mirror  
**DATE:** 2026-09-19  
**WHAT IT PROVES:**  
- 637 before-after pairs, 1024x1024 px, 0.5m resolution (Google Earth)  
- Building change detection — binary labels  
- Standard split: train/val/test  
- RGB only (3 bands)  
- License: academic use  
**HOW IT AFFECTS DESIGN:**  
- PRIMARY development dataset for change detection module  
- RGB-only so we test optical adapter first  
- Not the organiser dataset — do not over-optimize for LEVIR-CD distribution  

### C3. S2Looking
**SOURCE:** S2Looking GitHub repo  
**DATE:** 2026-09-19  
**WHAT IT PROVES:**  
- 5000 pairs, 1024x1024, 0.5-0.8m resolution, side-looking satellite  
- Rural building change detection  
- More varied viewing angles = good registration challenge  
**HOW IT AFFECTS DESIGN:**  
- Use for testing registration/false-alarm suppression  
- Side-looking geometry highlights importance of co-registration  

### C4. OSCD (Onera Satellite Change Detection)
**SOURCE:** IEEE DataPort, HuggingFace blanchon/OSCD_MSI  
**DATE:** 2026-09-19  
**WHAT IT PROVES:**  
- 24 pairs of Sentinel-2 multispectral scenes  
- Urban change detection  
- Full 13-band + RGB label maps  
- Available on HuggingFace — can load via datasets library  
**HOW IT AFFECTS DESIGN:**  
- Best dataset for testing multi-band (non-RGB) change detection pipeline  
- Validates our sensor-aware band adapter for Sentinel-2  
- Small enough for rapid iteration  

### C5. Organiser Dataset
**SOURCE:** SIH26227 problem statement  
**DATE:** 2026-09-19  
**WHAT IT PROVES:** UNKNOWN — not yet obtained  
**HOW IT AFFECTS DESIGN:**  
- HIGHEST PRIORITY to obtain  
- Do NOT assume: sensor, resolution, bands, format, labels, temporal structure  
- Design system to be sensor-agnostic from day 1  

---

## SECTION D — GEO/RASTER LIBRARIES

### D1. Rasterio
**SOURCE:** rasterio readthedocs, pip dry-run (rasterio-1.4.4-cp311-cp311-win_amd64.whl available)  
**DATE:** 2026-09-19  
**WHAT IT PROVES:**  
- Binary wheel available for Windows Python 3.11 on PyPI  
- Provides: CRS, affine transform, windowed reads, nodata, band count  
- `rasterio.open()` returns a DatasetReader with full metadata  
- Windowed reads = memory-safe tile extraction  
**HOW IT AFFECTS DESIGN:**  
- PRIMARY raster I/O library  
- `pip install rasterio` works on target machine  
- GDAL is bundled inside the wheel — no separate GDAL install needed  

### D2. FAISS Indexing Strategy
**SOURCE:** FAISS GitHub wiki, Facebook Research papers  
**DATE:** 2026-09-19  
**WHAT IT PROVES:**  
- For <10k vectors: IndexFlatIP (exact) — no overhead  
- For 10k-1M vectors: IndexHNSWFlat — good recall, fast, no training  
- For >1M vectors: IndexIVFPQ — compressed, fast, slightly lossy  
- Incremental add: `index.add(vectors)` — all index types support this  
- ID mapping: faiss.IndexIDMap wraps any index to maintain custom IDs  
**HOW IT AFFECTS DESIGN:**  
- Phase 3 MVP: IndexIDMap(IndexFlatIP) for simplicity + exact results  
- Index metadata (tile_id → vector mapping) stored separately in SQLite  
- Save/load on every add to persist state  

---

## SECTION E — REGISTRATION / FALSE CHANGE

### E1. Co-Registration Approaches
**SOURCE:** AROSICS GitHub, OpenCV ECC docs, academic survey  
**DATE:** 2026-09-19  
**WHAT IT PROVES:**  
- Sub-pixel misalignment is a PRIMARY source of false change detections  
- AROSICS: Python library for automatic sub-pixel co-registration of satellite imagery  
- OpenCV ECC (Enhanced Correlation Coefficient): works for rigid + affine transforms  
- AROSICS handles non-rigid (polynomial) warping — better for satellite  
- AROSICS Windows install: UNKNOWN — needs test (`pip install arosics`)  
**HOW IT AFFECTS DESIGN:**  
- Phase 7: Co-registration is not optional — must run before change analysis  
- If registration quality < threshold: return "Insufficient evidence"  
- Do not convert uncertain co-registration into confident "no change"  
- Implement registration quality metric (NCC or mutual information)  

### E2. Seasonal / Illumination False Alarms
**SOURCE:** RS literature, OSCD dataset notes  
**DATE:** 2026-09-19  
**WHAT IT PROVES:**  
- Seasonal vegetation changes (green→brown, snow cover) produce large spectral differences  
- Shadow movement between acquisitions causes local radiometric differences  
- Cloud/haze: must detect and mask before comparison  
**HOW IT AFFECTS DESIGN:**  
- Phase 7: Image quality gate must check cloud fraction before analysis  
- Use cloud masks from Sentinel-2 SCL band or simple threshold  
- Design temporal persistence check: single-date "change" that disappears = false alarm  
- Never claim "same season eliminates false alarms" — test explicitly  
