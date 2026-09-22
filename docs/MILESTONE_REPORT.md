# TERRAE — Earth Intelligence (SIH26227 Milestone Report)
**Date:** 2026-09-20  
**Project:** TERRAE — Satellite Investigation Console (SIH26227)

---

## 1. Prototype Overview
**TERRAE** is a self-contained, offline Earth Intelligence and satellite investigation platform designed to move remote sensing workflows beyond uncalibrated binary change detection toward an auditable, multimodal evidence chain. Built upon multimodal GeoAI foundations, it operationalizes open-vocabulary semantic discovery with co-registered temporal observation stacks.

### Core Verified Capabilities
- **Multimodal Semantic Retrieval:** Natural language text-to-imagery discovery executed locally via staged RemoteCLIP (ViT-B-32) and FAISS Flat L2 indexing, requiring zero external APIs.
- **Offline Integrity:** Rigorously verified with `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`. Zero outbound network connections during inference.
- **Temporal Change Workflow:** Geographic bounds matching and exact spatial intersection of temporal observation stacks, evaluating calibrated spectral surface reflectance against configurable decision thresholds.
- **Evidence-Based Change Attribution:** Multi-spectral delta analysis (Blue, Green, Red, NIR, NDVI, NDWI) and spatial coherence clustering to evaluate heuristic attribution support across candidate signatures (`BUILT_SURFACE`, `VEGETATION_CHANGE`, `WATER_CHANGE`, `SEASONAL`, `ARTIFACT`, `UNCERTAIN`).
- **Multi-Date Temporal Trajectory Analysis:** 3-date mutually exclusive & collectively exhaustive (MECE) trajectory partitioning (`STABLE`, `PERSISTENT_CHANGE`, `TRANSIENT_CHANGE`, `LATE_ONSET_CHANGE`, `REVERSIBLE_CHANGE`).
- **Real Sentinel-2 Validation:** Evaluated on real Sentinel-2A Level-2A surface reflectance (MGRS Tile `43RGM`, Greater Noida / NCR) with Scene Classification Layer (SCL) quality masking.
- **External OSCD Quantitative Benchmark:** Reproducible validation harness on the external, labeled OSCD dataset across 5 diverse global cities (3,025,938 valid pixels) evaluated with production parameters.
- **Analyst UI:** Interactive Streamlit interface (`ui/app.py`) following a strict 9-step judge-visible investigation workflow with real vs synthetic dataset badging.
- **Test Suite:** 135 / 135 unit tests passing with zero regressions.

---

## 2. Working Architecture

The system identity is a **satellite investigation system, not merely a change detector**. It implements a six-stage cognitive pipeline:

```text
  ASK          →  Natural language analyst prompt (e.g. "new construction and buildings")
   ↓
  DISCOVER     →  Multimodal semantic retrieval (RemoteCLIP ViT-B-32 + FAISS Flat L2)
   ↓
  COMPARE      →  Temporal spectral change differencing on co-registered observation stacks
   ↓
  EXPLAIN      →  Evidence-Based Change Attribution (spectral deltas, NDVI/NDWI, spatial coherence)
   ↓
  CHALLENGE    →  Temporal trajectory evidence (3-date MECE categories) and competing hypotheses
   ↓
  DECIDE       →  Decision Layer (SUPPORTED / REVIEW / ABSTAIN with complete provenance audit chain)
```

---

## 3. Evidence-Based Change Attribution

Traditional change detectors issue binary flags without scientific explanation. GeoAI implements **Evidence-Based Change Attribution**, generating structured evidence to explain candidate interpretations.

### Methodology
1. **Multi-Spectral Deltas:** Computes mean pixel differences across all 10m bands: $\Delta \text{Blue}$, $\Delta \text{Green}$, $\Delta \text{Red}$, $\Delta \text{NIR}$, $\Delta \text{NDVI}$, and $\Delta \text{NDWI}$.
2. **Spatial Coherence:** Measures connected component clustering, size of the largest connected region, and the ratio of clustered to isolated changed pixels.
3. **Signature Matching:** Compares observed metrics against canonical remote sensing physical profiles:
   - `BUILT_SURFACE`: $\Delta \text{NIR} < 0$, $\Delta \text{Red} > 0$, $\Delta \text{NDVI} < 0$, high spatial coherence.
   - `VEGETATION_CHANGE`: $\Delta \text{NIR} < 0$, $\Delta \text{Red} > 0$, $\Delta \text{NDVI} \ll 0$, moderate-to-high spatial coherence.
   - `SEASONAL`: Cyclic vegetation shifts, diffuse spatial coherence (< 30%), moderate spectral fluctuations.
   - `WATER_CHANGE`: Significant $\Delta \text{NDWI}$ shifts, low Red reflectance.
   - `ARTIFACT`: Isolated single-pixel noise, zero spatial coherence (< 10%).
   - `UNCERTAIN`: Conflicting or sub-threshold evidence.

> **Scientific Disclaimer:** Attribution scores represent heuristic support across candidate signatures (normalized to 100%), not calibrated probabilities or causal proofs.

---

## 4. Temporal Trajectory Analysis

Two-date comparisons are inherently sensitive to seasonal, illumination, and phenological shifts. GeoAI integrates a **three-date temporal trajectory engine** evaluating interval dynamics across $T_0$, $T_{mid}$, and $T_1$.

### MECE Category Definitions
Pixel transitions across the stack are partitioned into 5 mutually exclusive and collectively exhaustive categories over all valid pixels:
- `STABLE`: $|T_{mid} - T_0| \le \tau$ AND $|T_1 - T_0| \le \tau$ (Temporally stable baseline).
- `PERSISTENT_CHANGE`: $|T_{mid} - T_0| > \tau$ AND $|T_1 - T_{mid}| \le \tau$ (Early change that persists through $T_1$).
- `TRANSIENT_CHANGE`: $|T_{mid} - T_0| > \tau$ AND $|T_1 - T_{mid}| > \tau$ AND $|T_1 - T_0| > \tau$ (Fluctuating state).
- `LATE_ONSET_CHANGE`: $|T_{mid} - T_0| \le \tau$ AND $|T_1 - T_0| > \tau$ (Stable initially, change emerged at $T_1$).
- `REVERSIBLE_CHANGE`: $|T_{mid} - T_0| > \tau$ AND $|T_1 - T_0| \le \tau$ (Temporary disturbance that returned to baseline).

---

## 5. Real Sentinel-2 Validation

Validated on real Sentinel-2A Level-2A Bottom-of-Atmosphere (BOA) surface reflectance imagery from AWS Open Data / Copernicus.

### Stack Configuration
- **MGRS Tile:** `43RGM` (Greater Noida / NCR, India; `EPSG:32643`, UTM Zone 43N, 10m GSD).
- **Window Extent:** 512 × 512 pixels (`col_off=4000, row_off=4000`, 262,144 pixels).
- **Observations:**
  1. $T_0$: `2023-05-19` (Dry summer pre-monsoon, high solar angle)
  2. $T_{mid}$: `2023-10-06` (Post-monsoon greening peak, clear sky)
  3. $T_1$: `2023-12-05` (Winter post-harvest dormancy, lower solar angle)
- **Quality / Cloud Mask:** SCL quality mask: 0 masked/invalid pixels in the analyzed 512×512 three-date intersection (262,144 / 262,144 valid pixels, 100.0%).
- **Registration:** `REGISTRATION_NOT_REQUIRED` (Identical ESA Copernicus MGRS UTM 10m fixed grid).

### Three-Date Persistence Results
- **Interval Changes:**
  - $T_0 \to T_{mid}$: $0.7\%$ (1,820 pixels > 0.15 threshold)
  - $T_{mid} \to T_1$: $0.2\%$ (619 pixels > 0.15 threshold)
  - $T_0 \to T_1$: $1.0\%$ (2,542 pixels > 0.15 threshold)
- **MECE Pixel Trajectory Distribution:**
  - `STABLE`: 258,869 pixels (**98.75%**)
  - `LATE_ONSET_CHANGE`: 1,373 pixels (**0.52%**)
  - `PERSISTENT_CHANGE`: 1,028 pixels (**0.39%**)
  - `TRANSIENT_CHANGE`: 624 pixels (**0.24%**)
  - `REVERSIBLE_CHANGE`: 250 pixels (**0.10%**)
  - Total Valid Pixels: 262,144 (100.0%)
- **Region-Average Spectral Trajectory (Changed Region):**
  - $\text{NDVI}: +0.192 \to +0.112 \to +0.092$
  - $\text{NDWI}: -0.215 \to -0.116 \to -0.095$
  - $\text{NIR}: 0.480 \to 0.279 \to 0.254$
  - $\text{Red}: 0.350 \to 0.245 \to 0.224$
- **Attribution Support:** Built-surface $51.1\%$, Vegetation-change $24.7\%$, Seasonal $19.9\%$, Unresolved $3.1\%$, Water/Artifact $0.6\%$ each.
- **Final Decision:** `REVIEW` (site-wide change across $T_0 \to T_1$ is $1.0\% < 5.0\%$; `REVIEW` indicates that the available evidence does not cross the configured threshold for an automatic affirmative decision and should be inspected by an analyst).
- **Processing Time:** $135.0\text{ ms}$ (100% offline).
- **Diagnostic Artifact:** `data/real/sentinel2/diagnostic_validation.png` (2048 × 512, 1x4 inspection layout).

> **Important Boundary:** *Real Sentinel-2 validation ≠ benchmark accuracy. This real-world case evaluates temporal trajectory partitioning and seasonal filtering on exploratory data.*

---

## 6. Synthetic Construction Demonstration

To verify the end-to-end evidence chain under fully known, controlled physical conditions, synthetic multi-spectral scenes were generated with controlled land conversions.

### Controlled Construction Stack
- **Search Query:** *"new construction and buildings"* $\to$ Tile `747db63c...` retrieved via RemoteCLIP.
- **Detected Change:** $11.5\%$ of valid pixels ($7,549$ changed pixels).
- **Attribution Support:** Built-surface support **97.1%**, Unresolved $1.3\%$.
- **Spatial Coherence:** **99.7%** (24 connected components).
- **Temporal Trajectory:** `LATE_ONSET_CHANGE` ($11.5\%$ late onset, $88.5\%$ stable).
- **Final Decision:** `SUPPORTED` (exceeds $5.0\%$ threshold with dominant built-surface attribution).

### Controlled Vegetation Stack
- **Detected Change:** $25.0\%$ change $\to$ Vegetation-change support $76.7\% \to$ Decision: `REVIEW`.

> **Important Boundary:** *Synthetic demonstration ≠ benchmark accuracy. Synthetic experiments confirm that the pipeline logic executes correctly under ground-truth conditions.*

---

## 7. External OSCD Validation

The change-detection component was quantitatively evaluated against the external, independent **OSCD (Onera Satellite Change Detection)** benchmark dataset.

### Subset Specification
- **Dataset:** Official OSCD dataset.
- **Scope:** **Fixed 5-pair OSCD validation subset, not the full OSCD benchmark.**
- **Label Subset Source:** OSCD training-label release (`Onera Satellite Change Detection dataset - Train Labels.zip`).
- **Pairs Evaluated:** 5 diverse global contexts:
  1. `aguasclaras` (Brazil — suburban expansion & savannah fringe)
  2. `beirut` (Lebanon — dense Mediterranean coastal port)
  3. `bordeaux` (France — European riverine city)
  4. `cupertino` (USA — Silicon Valley suburban development)
  5. `mumbai` (India — dense South Asian metropolitan center)
- **Spectral Bands:** 4 production 10m bands: B02 (Blue), B03 (Green), B04 (Red), B08 (NIR).
- **Detector Configuration:** Existing production `SpectralChangeDetector(threshold=0.15)`.
- **Benchmark-Driven Tuning:** **NONE** (evaluated strictly as-is).
- **Masking Discipline:** Evaluated strictly over valid pixels (`valid_mask`). Any 0/unlabelled pixels are excluded from all denominators and numerators.

### Quantitative Results

#### Per-Pair Breakdown
| Pair | Geographic Context | Valid Pixels | GT Change % | Precision | Recall | F1 Score | IoU | Accuracy |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **aguasclaras** | South America (Brazil) | 247,275 | 1.64% | 17.36% | 5.57% | 0.0844 | 0.0440 | 98.02% |
| **beirut** | Middle East (Lebanon) | 1,262,600 | 2.69% | 77.10% | 11.05% | 0.1933 | 0.1070 | 97.52% |
| **bordeaux** | Western Europe (France) | 238,337 | 1.00% | 21.14% | 7.35% | 0.1091 | 0.0577 | 98.80% |
| **cupertino** | North America (USA) | 799,820 | 2.37% | 53.84% | 13.99% | 0.2221 | 0.1249 | 97.68% |
| **mumbai** | South Asia (India) | 477,906 | 2.56% | 91.67% | 1.26% | 0.0248 | 0.0126 | 97.47% |

#### Micro-Aggregate Metrics (Pooled over 3,025,938 valid pixels)
- **Total Valid Pixels:** 3,025,938
- **Total GT Changed Pixels:** 71,540 (2.36%)
- **Confusion Matrix:** TP: 6,952 | TN: 2,949,270 | FP: 5,128 | FN: 64,588
- **Precision:** **57.55%**
- **Recall:** **9.72%**
- **F1 Score:** **0.1663**
- **IoU:** **0.0907**
- **Accuracy:** **97.70%**

#### Macro-Average Metrics Across 5 Pairs (Unweighted mean across geographies)
- **Macro Precision:** **52.22%**
- **Macro Recall:** **7.84%**
- **Macro F1 Score:** **0.1267**
- **Macro IoU:** **0.0692**
- **Macro Accuracy:** **97.90%**

> **Note on Accuracy & Class Imbalance:** The 97.70% overall accuracy is strongly influenced by extreme class imbalance in pixel-level change detection (only 2.36% of pixels are changed in ground truth). A trivial baseline predicting 100% unchanged would achieve 97.64% accuracy. Therefore, 97.70% accuracy must NOT be interpreted as evidence of strong change detection. The informative headline metrics are Precision (57.55%), Recall (9.72%), F1 (0.1663), and IoU (0.0907).

> **Important Boundary:** *OSCD validation ≠ production performance. This benchmark measures the sensitivity of the standalone spectral differencing threshold on external labeled satellite pairs.*

---

## 8. Benchmark Interpretation ("What This Means")

The fixed four-band spectral detector is conservative on this OSCD validation subset. It detects a relatively small portion of the ground-truth change, resulting in low recall, while maintaining moderate precision.

This indicates that the current detector is better interpreted as **an evidence-generating change candidate detector than as a complete high-recall semantic change detector**.

The limitation is expected from the current design: the detector uses only Blue, Green, Red, and NIR and a fixed spectral-distance threshold. Subtle urban changes may not produce sufficient spectral separation to cross that threshold.

On the evaluated OSCD subset, the fixed 0.15 threshold produced higher precision than recall, indicating conservative change triggering under this benchmark configuration. This should not be interpreted as generalized false-alarm performance.

---

## 9. Offline Execution

The workstation is built for air-gapped deployment, requiring zero outbound network access during all phases of operation.

### Verification Protocol
- Environment flags: `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`.
- Socket audit: Zero external HTTP/HTTPS requests or socket calls.

### Latency Profile (Local Hardware)
| Operation | Latency | Provenance |
| :--- | :---: | :--- |
| **Model Startup (RemoteCLIP ViT-B-32)** | ~4.8 s | Local PyTorch checkpoint (`models/local/`) |
| **Text Query Embedding** | ~45 ms | Local tokenization + visual-semantic projection |
| **Image Tile Embedding** | ~80 ms | Local ViT forward pass |
| **FAISS Flat L2 Search** | ~1 ms | In-memory 512-dim vector index |
| **End-to-End Search Query** | ~60 ms | Full query planner + FAISS + SQLite metadata |
| **Temporal Change + Attribution** | ~135 ms | Full 4-band spectral differencing + coherence |

---

## 10. Test Status

- **Total Tests:** **135 / 135 PASSED** (100% pass rate in 8.70s).
- **Test Modules:**
  - `test_reader.py`: GeoTIFF raster parsing & CRS extraction (9 tests)
  - `test_validator.py`: Raster boundary & band count verification (6 tests)
  - `test_tiler.py`: Windowed tile generation & metadata tagging (8 tests)
  - `test_sensors.py`: Optical, SAR, Generic sensor adapters (11 tests)
  - `test_db.py`: SQLite metadata CRUD & spatial queries (8 tests)
  - `test_index.py`: FAISS Flat indexing & similarity search (11 tests)
  - `test_remoteclip.py`: RemoteCLIP model loading & embedding shapes (27 tests)
  - `test_retrieval.py`: Retrieval engine end-to-end integration (9 tests)
  - `test_change.py`: SpectralChangeDetector baseline (2 tests)
  - `test_attribution.py`: Evidence-Based Attribution & Evidence Chain (10 tests)
  - `test_real_sentinel.py`: Sentinel-2 ingestion, SCL masking, 2-date pair (6 tests)
  - `test_persistence.py`: 3-date temporal trajectory & MECE distribution (11 tests)
  - `test_pipeline.py`: Full ingestion pipeline integration (8 tests)
  - `test_benchmark_oscd.py`: OSCD metrics correctness, masks, determinism, macro metrics (9 tests)

---

## 11. Current Limitations

1. **Heuristic Attribution Nature:** Attribution scores indicate heuristic alignment with known physical remote sensing signatures; they are not calibrated probabilities or causal proofs.
2. **10m 4-Band Spectral Scope:** Current processing utilizes 10m Sentinel-2 bands (Blue, Green, Red, NIR). SWIR bands (B11, B12) at 20m are omitted, so NDBI cannot yet be calculated for additional urban impervious surface confirmation.
3. **Discrete Temporal Sampling:** Three-date trajectories capture dominant interval dynamics but cannot reconstruct high-frequency phenological curves without dense time-series modeling.
4. **Spectral Change Recall on Subtle Disturbance:** As demonstrated in the OSCD benchmark, the conservative 0.15 threshold yields high precision (~58%) but modest recall (~10%) on subtle urban land changes.

---

## 12. SIH Demo Workflow

### Final Judge-Facing Claim
> **"The prototype is not designed to declare that every detected spectral difference represents a real-world semantic change. Instead, it builds an auditable evidence chain from retrieval through temporal comparison, candidate attribution, trajectory analysis, and a conservative final decision.**
> 
> **The current external benchmark shows a conservative change detector with limited recall on subtle OSCD changes. This is documented as a current model limitation rather than hidden through benchmark-specific tuning."**

### Two Complementary Demonstration Cases
The demo deliberately contrasts two distinct scenarios to showcase system judgment:

- **Case A — Controlled Construction (Synthetic):**
  - Query: *"new construction and buildings"*
  - Result: 11.5% change, 97.1% built-surface support, 99.7% spatial coherence, late-onset trajectory.
  - Final Decision: **SUPPORTED**
  - *Demonstrates the complete evidence chain triggering affirmative verification under clear conditions.*

- **Case B — Real Sentinel-2 Three-Date Stack (NCR / Greater Noida):**
  - Stack: May 19, Oct 6, Dec 5, 2023.
  - Result: 98.75% STABLE, 0.39% PERSISTENT_CHANGE, 1.0% overall change.
  - Final Decision: **REVIEW**
  - *Demonstrates that the system resists forcing a false positive when temporal evidence is weak or seasonally confounded.*

### Verification Commands
```powershell
# 1. Run full test suite (135 unit tests)
C:\Python311\python.exe -m pytest tests\ -q

# 2. Run OSCD Quantitative Benchmark
C:\Python311\python.exe scripts/benchmark_oscd.py

# 3. Run Real Sentinel-2 Three-Date Validation
C:\Python311\python.exe scripts/validate_real_sentinel.py

# 4. Run Offline Zero-Network Verification
$env:HF_HUB_OFFLINE="1"; $env:TRANSFORMERS_OFFLINE="1"; C:\Python311\python.exe scripts/offline_test.py

# 5. Launch Streamlit Analyst UI
C:\Python311\python.exe -m streamlit run ui/app.py
```
