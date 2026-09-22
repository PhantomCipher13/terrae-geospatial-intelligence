# Competitor Analysis — SIH26227
**Date:** 2026-09-19

---

## Methodology

Searched GitHub and the public web for:
- "SIH 2026 satellite imagery semantic retrieval"
- "SIH26227 GitHub"
- "MR-ROGUE01/SIH-2026"
- "SlockAhuja/SIH_2026"
- "AETHER-EO satellite"

All findings are based on publicly available information as of 2026-09-19.

---

## MR-ROGUE01/SIH-2026

| Field | Finding |
|-------|---------|
| Repository | Not publicly indexed |
| Status | UNKNOWN — private or not yet pushed |
| Implemented | UNKNOWN |
| Claimed | UNKNOWN |
| Dataset | UNKNOWN |
| Architecture | UNKNOWN |

**Assessment:** Cannot assess. No analysis possible.

---

## SlockAhuja/SIH_2026 / AETHER-EO

| Field | Finding |
|-------|---------|
| Repository | Not publicly indexed |
| Status | UNKNOWN — private or different naming |
| Implemented | UNKNOWN |
| Claimed | UNKNOWN |
| Dataset | UNKNOWN |
| Architecture | UNKNOWN |

**Assessment:** Cannot assess. No analysis possible.

---

## General SIH 2026 Satellite/Remote Sensing Submissions (Observed Patterns)

Based on adjacent SIH submissions (different problem IDs but similar domain), the observed pattern is:

### Commonly Implemented
- Single-image classification using pretrained ResNet/EfficientNet
- Gradio or Streamlit frontend with demo image upload
- HuggingFace Spaces deployment

### Commonly Claimed but Not Verified
- "Multi-temporal change detection" — often single image pair with simple threshold
- "Semantic retrieval" — often keyword matching or basic cosine similarity on generic ResNet features
- "Offline operation" — rarely verified; HuggingFace API calls often present

### Common Weaknesses
1. No co-registration before change analysis → high false alarm rate
2. No sensor-aware band handling → discards spectral information
3. No provenance → cannot trace result to source data
4. No evaluation on held-out data → benchmark numbers typed, not measured
5. Cloud API dependencies → not truly offline
6. Single monolithic script → not extensible

### Our Differentiation Points
1. Sensor-aware adapter system (optical / SAR / generic)
2. Verified offline operation (TRANSFORMERS_OFFLINE=1 tested)
3. FAISS-backed retrieval with persisted index
4. Machine-measured benchmarks (no manual numbers)
5. Provenance schema on every result
6. Evidence-based change detection with ABSTAIN path
7. SQLite metadata DB separate from vector index

---

## Competitive Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Competitor ships polished UI before us | HIGH | Focus on working pipeline first; minimal UI later |
| Competitor claims RemoteCLIP retrieval | MEDIUM | We benchmark actual latency; they may not |
| Competitor uses cloud API | MEDIUM | We test offline; this is a judging criterion |
| Organiser dataset is unusual (SAR, hyperspectral) | MEDIUM | Our adapter system handles this |
| Competitor has better change detection | LOW (Phase 7) | Spectral baseline is honest and verifiable |
