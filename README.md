# TERRAE — Earth Intelligence
**SIH26227 — Satellite Investigation Console**

> **Satellite investigation system, not merely a change detector.**

---

## 1. Executive Summary
**TERRAE** is a self-contained, air-gapped Earth Intelligence platform that moves remote sensing analysis beyond opaque binary change masks. Built on multimodal GeoAI engineering, the system integrates natural-language query discovery with co-registered temporal satellite stacks, multi-spectral physical attribution, three-date trajectory partitioning, and an auditable decision layer.

```text
  ASK          →  Natural-language query (e.g., "new construction and buildings")
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

## 2. Key Documentation
- **[docs/MILESTONE_REPORT.md](docs/MILESTONE_REPORT.md)**: Full milestone report detailing system architecture, real Sentinel-2 validation, OSCD 5-pair validation subset, limitations, and verification profiles.
- **[docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md)**: Concise presenter runbook with step-by-step instructions for Demo Case A (Controlled Construction) and Demo Case B (Real Sentinel-2 Stack).
- **[docs/JUDGE_QA.md](docs/JUDGE_QA.md)**: Definitive Q&A guide preparing technically defensible, scientifically conservative answers for judge/panel review.

---

## 3. Quick Start Commands

### Launch Analyst UI (Streamlit)
```powershell
C:\Python311\python.exe -m streamlit run ui/app.py
```

### Run Full Unit Test Suite (135 tests passing)
```powershell
C:\Python311\python.exe -m pytest tests\ -q
```

### Run Standalone Evidence Attribution Demo
```powershell
C:\Python311\python.exe scripts/demo_attribution.py
```

### Run Real Sentinel-2 Validation (MGRS 43RGM 3-Date Stack)
```powershell
C:\Python311\python.exe scripts/validate_real_sentinel.py
```

### Run OSCD 5-Pair Benchmark Evaluation
```powershell
C:\Python311\python.exe scripts/benchmark_oscd.py
```

### Air-Gapped Offline Verification (Zero Outbound Network Calls)
```powershell
$env:HF_HUB_OFFLINE="1"; $env:TRANSFORMERS_OFFLINE="1"; C:\Python311\python.exe scripts/offline_test.py
```

---

## 4. Current Status & Verification
- **Semantic Retrieval:** PASS (Local RemoteCLIP ViT-B-32 + FAISS Flat L2)
- **Temporal Spectral Change:** PASS (4-band differencing, $\tau = 0.15$)
- **Evidence-Based Attribution:** PASS (Heuristic physical signature matching)
- **Three-Date Trajectory Analysis:** PASS (MECE 5-category partition across valid pixels)
- **Real Sentinel-2 Validation:** PASS (MGRS Tile 43RGM, 3 dates, SCL cloud masked, Decision: REVIEW)
- **OSCD Validation:** COMPLETE (5-pair validation subset from train-labels release)
- **Offline Runtime:** PASS (Zero outbound network calls verified)
- **Test Suite:** PASS (135 / 135 unit tests passing)

---

## 5. Scientific Honesty & Terminology Disclaimer
> **Attribution scores represent heuristic support for candidate change signatures, not calibrated probabilities or causal estimates.**  
> **Temporal categories represent trajectory classifications across discrete observations, not causal proofs.**  
> **The system provides structured evidence to assist human analyst investigation; it does not make automated legal or administrative decisions.**
