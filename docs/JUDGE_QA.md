# TERRAE — Judge Q&A Document
**Project:** SIH26227 — Satellite Investigation Console  
**Purpose:** Direct, technically defensible, and scientifically honest responses to panel questions.

---

### Q1. What is actually novel here?
**Answer:**  
The novelty is NOT in isolation claiming that natural-language retrieval or pixel differencing is new. Rather, the novelty is the **architectural integration of open-vocabulary semantic discovery with an auditable physical evidence chain**:
$$\text{ASK} \to \text{DISCOVER} \to \text{COMPARE} \to \text{EXPLAIN} \to \text{CHALLENGE} \to \text{DECIDE}$$
Instead of handing an analyst an opaque binary change map, the system connects semantic retrieval directly to temporal observation stacks, computes multi-spectral indices (NDVI/NDWI/deltas) and spatial coherence, challenges candidate explanations against three-date temporal trajectories, and delivers an auditable decision with conservative fallback states.

---

### Q2. Why not just use a standard change detector?
**Answer:**  
Standard change detectors (e.g., standard pixel differencing or black-box deep learning change masks) stop at answering *"Did something change?"*. They provide:
- No semantic entry point (cannot search by concept such as *"new construction and buildings"*).
- No explanation of physical land-cover mechanisms (cannot distinguish built-surface conversion from agricultural greening or water shifts).
- No defense against temporal/seasonal confounding (a two-epoch drop in reflectance is blindly flagged as change).
- No audit provenance for human-in-the-loop validation.

TERRAE is a **satellite investigation system**, providing multi-spectral attribution, trajectory verification across multiple dates, and clear decision confidence states.

---

### Q3. Why use heuristics rather than deep learning for change attribution?
**Answer:**  
In a small, offline, defensible prototype, heuristic signature matching based on well-established physical remote sensing principles ($\Delta \text{NIR}$, $\Delta \text{Red}$, $\Delta \text{NDVI}$, $\Delta \text{NDWI}$, and spatial connected-component coherence) is **fully interpretable, deterministic, and scientifically auditable**. It avoids hallucinated explanations common to ungrounded vision-language models and does not require massive labeled training corpora that may not generalize across global biomes.

---

### Q4. Why is the OSCD benchmark F1 score relatively low (0.1663)?
**Answer:**  
We evaluated our existing production spectral change detector ($\tau = 0.15$) strictly **as-is** on the OSCD 5-pair validation subset without benchmark-specific fine-tuning or threshold hunting:
1. **Conservative Threshold:** The fixed $\tau = 0.15$ requires a substantial 15% spectral reflectance shift across all 4 bands to trigger, intentionally designed to suppress atmospheric and seasonal noise.
2. **Subtle Urban Changes:** In the OSCD ground truth, urban changes include fine-grained ground preparation, minor road repaving, and interior building renovations that produce subtle spectral shifts below 0.15.
3. **Spectral Band Scope:** The 4-band pathway utilizes Blue, Green, Red, and NIR. It lacks 20m SWIR bands (B11/B12) to compute NDBI for impervious surface isolation.

When the detector triggers, it achieves high precision (e.g., **91.67%** in Mumbai, **77.10%** in Beirut, aggregate **57.55%**), but exhibits conservative recall (**9.72%**). We chose to report this limitation honestly rather than overfitting our threshold to the benchmark.

---

### Q5. Why is overall accuracy 97.70% if F1 is 0.1663?
**Answer:**  
This is a textbook example of **extreme class imbalance** in remote sensing:
- Across the 3,025,938 valid pixels evaluated in the OSCD subset, only **71,540 pixels (2.36%)** represent true ground-truth change; the remaining **97.64%** of the scene is unchanged.
- A trivial dummy baseline that predicts "no change" everywhere would achieve **97.64% accuracy** while having an F1 score of 0.0.
- Therefore, **97.70% accuracy is NOT presented as evidence of strong change detection**. The true headline metrics are Precision (57.55%), Recall (9.72%), F1 (0.1663), and IoU (0.0907).

---

### Q6. Why does the real Sentinel-2 case result in a REVIEW decision?
**Answer:**  
In our real-world Greater Noida / NCR 3-date stack (MGRS Tile `43RGM`):
- Overall change across $T_0 \to T_1$ is only **1.0%** (2,542 of 262,144 pixels), which is well below the system's 5.0% threshold for an automatic affirmative `SUPPORTED` decision.
- The 3-date MECE trajectory analysis reveals that **98.75% of the analyzed tile is temporally STABLE**, with persistent conversion accounting for only 0.39%.
- Furthermore, the spectral trajectory reveals competing seasonal agricultural dynamics (dry summer pre-monsoon vs winter post-harvest).
- Therefore, the system issues a conservative `Decision: REVIEW`. `REVIEW` indicates that the available evidence does not cross the configured threshold for an automatic affirmative decision and should be inspected by an analyst. It is an intentional safety feature, not an algorithm failure.

---

### Q7. Is the attribution causal?
**Answer:**  
**No.** We explicitly do NOT claim causal inference. Attribution scores represent **heuristic support for candidate physical signatures** based on multi-spectral delta alignment and spatial morphology. They provide structured hypotheses to guide an analyst's investigation; they do not prove causality.

---

### Q8. Does the system truly operate completely offline?
**Answer:**  
**Yes.** Verified via our automated offline test suite (`scripts/offline_test.py`) with environment variables:
`HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`.
- Model weights: Pre-staged local PyTorch checkpoint (`models/local/RemoteCLIP-ViT-B-32.pt`, 605 MB).
- Embeddings: Local CPU/GPU forward pass via `open-clip-torch`.
- Index: Local FAISS Flat L2 index (`data/faiss_index/`).
- Metadata: Local SQLite database (`data/geoai_metadata.db`).
- Imagery: Local GeoTIFF rasters with windowed reads via Rasterio.
- Runtime network calls: **Zero.**

---

### Q9. What is on the roadmap for a full production system?
**Answer:**  
Our current vertical slice was intentionally frozen to prove the core concept. The technical roadmap includes:
1. **Multi-Resolution Sensor Pipelines:** Incorporating 20m SWIR bands (B11, B12) to compute NDBI for impervious surface confirmation.
2. **Learned Change Detection:** Integrating pre-trained foundation change models (e.g. ChangeFormer / BIT) fine-tuned on multi-sensor datasets for higher recall on subtle urban modifications.
3. **Dense Time-Series Modeling:** Harmonic regression and Kalman filtering across dense temporal observations to reconstruct continuous phenological curves.
4. **Conformal Prediction:** Producing statistically rigorous confidence intervals on change predictions rather than purely heuristic thresholds.
5. **On-Premise GPU Containerization:** Packaging as an air-gapped Docker container with TensorRT-optimized embeddings.

---

### Q10. Can this system replace a human analyst?
**Answer:**  
**No, and that is not its purpose.** TERRAE is designed as an Earth Intelligence **decision-support tool** that accelerates human analyst workflows. By translating natural-language queries into localized, co-registered temporal evidence chains, it filters out millions of irrelevant pixels and highlights candidates. When evidence is ambiguous or sub-threshold, the system explicitly routes the case to `REVIEW` or `ABSTAIN`, ensuring human oversight on all high-stakes decisions.
