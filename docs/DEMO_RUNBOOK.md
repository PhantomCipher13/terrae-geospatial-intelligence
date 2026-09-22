# TERRAE — Demo Runbook
**Project:** SIH26227 — Satellite Investigation Console  
**Audience:** Judges, Evaluators, and Technical Presenters

---

## 1. Demo Objective
The **TERRAE** Earth Intelligence platform demonstrates a self-contained, air-gapped satellite investigation workflow. Rather than returning an uncalibrated binary change mask, the system connects natural-language query discovery to temporal co-registered observations, multi-spectral physical attribution, three-date trajectory partitioning, and an auditable decision layer with conservative `SUPPORTED / REVIEW / ABSTAIN` states.

---

## 2. Demo 1 — Controlled Construction (Case A)
Demonstrates the complete affirmative evidence chain under known ground-truth physical conditions.

### Steps to Execute
1. Launch UI:
   ```powershell
   C:\Python311\python.exe -m streamlit run ui/app.py
   ```
2. Navigate to **Tab "1 & 2. Retrieval & Discovery"**.
3. Under **"Quick Load Preset Demonstrations"**, click:
   `[Load Case A: Controlled Construction (Synthetic)]`
   *(Alternatively: type `"new construction and buildings"` in the query box and click Search).*
4. Switch to **Tab "3–9. Temporal Analysis & Evidence Chain"**.
5. Click **"Run End-to-End Temporal Investigation"**.

### Expected Outputs
- **Dataset Mode Badge:** `🧪 Dataset Mode: SYNTHETIC VALIDATION`
- **Change Evidence:** Changed pixel fraction: **11.5%** with dense, clustered change mask.
- **Attribution Support:** Built-surface support **97.1%**, Unresolved $1.3\%$ (driven by $\Delta \text{NIR} = -1.5\%$, $\Delta \text{Red} = +21.5\%$, $\Delta \text{NDVI} = -0.75$).
- **Spatial Coherence:** **99.7%** across 24 connected components.
- **Temporal Trajectory:** `LATE_ONSET_CHANGE — 11.5% of valid pixels` (Stable across $T_0 \to T_{mid}$, land conversion emerging at $T_1$).
- **Final Decision:** `Decision: SUPPORTED` (Change fraction $\ge 5.0\%$ with dominant built-surface attribution).

---

## 3. Demo 2 — Real Sentinel-2 Three-Date Stack (Case B)
Demonstrates that the system avoids forcing a false positive when real-world change is sparse and seasonally confounded.

### Steps to Execute
1. In the Streamlit UI, navigate to **Tab "1 & 2. Retrieval & Discovery"**.
2. Under **"Quick Load Preset Demonstrations"**, click:
   `[Load Case B: Real Sentinel-2 Stack (NCR 43RGM)]`
3. Switch to **Tab "3–9. Temporal Analysis & Evidence Chain"**.
4. Click **"Run End-to-End Temporal Investigation"**.

### Expected Outputs
- **Dataset Mode Badge:** `🛰️ Dataset Mode: REAL SENTINEL-2 VALIDATION` (ESA Copernicus Level-2A BOA Surface Reflectance).
- **Temporal Stack:** 3 observations across 2023 ($T_0$: May 19, $T_{mid}$: Oct 6, $T_1$: Dec 5).
- **Quality Masking:** SCL quality mask: 0 masked/invalid pixels in the analyzed 512×512 window.
- **Change Evidence:** Changed fraction: **0.84%** across $T_0 \to T_1$ (diffuse agricultural and seasonal reflectance shift).
- **MECE Trajectory Distribution:**
  - `STABLE`: **98.85%** of valid pixels.
  - `LATE_ONSET_CHANGE`: 0.44%
  - `PERSISTENT_CHANGE`: 0.39%
  - `TRANSIENT_CHANGE`: 0.22%
  - `REVERSIBLE_CHANGE`: 0.10%
- **Final Decision:** `Decision: REVIEW`

### What This Demonstrates to Judges
- `REVIEW` indicates that the available evidence does not cross the configured threshold (5.0%) for an automatic affirmative decision and should be inspected by an analyst.
- Demonstrates conservative system restraint: when a real satellite scene is 98.8% stable, the system refuses to force an unjustified `SUPPORTED` claim.

---

## 4. CLI Verification & Demo Commands

### Interactive Streamlit Analyst UI
```powershell
C:\Python311\python.exe -m streamlit run ui/app.py
```

### Standalone Evidence-Based Attribution Demo (Cases A, B, C)
```powershell
C:\Python311\python.exe scripts/demo_attribution.py
```

### Standalone Real Sentinel-2 Three-Date Verification
```powershell
C:\Python311\python.exe scripts/validate_real_sentinel.py
```

### Standalone External OSCD Benchmark Validation
```powershell
C:\Python311\python.exe scripts/benchmark_oscd.py
```

### Full Unit Test Suite (135 tests)
```powershell
C:\Python311\python.exe -m pytest tests\ -q
```

### Air-Gapped Offline Verification (Zero Network Calls)
```powershell
$env:HF_HUB_OFFLINE="1"; $env:TRANSFORMERS_OFFLINE="1"; C:\Python311\python.exe scripts/offline_test.py
```

---

## 5. Emergency Recovery

| Issue | Symptom | Immediate Fix |
| :--- | :--- | :--- |
| **Missing Model Checkpoint** | `FileNotFoundError: RemoteCLIP checkpoint not found` | Verify file exists at `models/local/RemoteCLIP-ViT-B-32.pt` (605 MB). Run from project root. |
| **Wrong Working Directory** | `ModuleNotFoundError: No module named 'terrae'` | Ensure CWD is `c:\Users\Admin\Downloads\Internal hackathon\terrae` and run with `PYTHONPATH=.`. |
| **Empty Vector Index** | `Search returned 0 hits` | Check `data/faiss_index/index.faiss`. Run `C:\Python311\python.exe scripts/prepare_real_sentinel.py` to restore index. |
| **Missing Staged Raster** | `FileNotFoundError: Required file not found: ...` | Verify `data/sample/temporal/` and `data/real/sentinel2/` directories exist with `.tif` files. |
| **Streamlit Port Conflict** | `Address already in use` | Run with alternative port: `C:\Python311\python.exe -m streamlit run ui/app.py --server.port 8502`. |
