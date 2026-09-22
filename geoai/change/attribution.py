"""
geoai/change/attribution.py
Evidence-Based Change Attribution & Evidence Chain.

Calculates spectral indices (NDVI, NDWI, delta bands), spatial coherence,
and heuristic attribution support across candidate change interpretations.

Terminology note:
Attribution scores represent heuristic support for candidate change signatures,
not calibrated probabilities or causal estimates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy.ndimage import label


class AttributionClass(str, Enum):
    BUILT_SURFACE = "BUILT_SURFACE"
    VEGETATION_CHANGE = "VEGETATION_CHANGE"
    WATER_CHANGE = "WATER_CHANGE"
    SEASONAL = "SEASONAL"
    ARTIFACT = "ARTIFACT"
    UNCERTAIN = "UNCERTAIN"


# Friendly display labels for UI and reports (never using "probability")
DISPLAY_LABELS: Dict[str, str] = {
    AttributionClass.BUILT_SURFACE.value: "Built-surface support",
    AttributionClass.VEGETATION_CHANGE.value: "Vegetation-change support",
    AttributionClass.WATER_CHANGE.value: "Water-change support",
    AttributionClass.SEASONAL.value: "Seasonal support",
    AttributionClass.ARTIFACT.value: "Artifact support",
    AttributionClass.UNCERTAIN.value: "Unresolved evidence",
}

DISCLAIMER_TEXT = (
    "Attribution scores represent heuristic support for candidate change "
    "signatures, not calibrated probabilities or causal estimates."
)


@dataclass
class EvidenceChain:
    """Step-by-step evidence chain explaining the change interpretation."""
    query_text: Optional[str] = None
    retrieval_summary: Optional[str] = None
    temporal_observation: Optional[str] = None
    spectral_evidence: Dict[str, str] = field(default_factory=dict)
    spatial_evidence: Dict[str, str] = field(default_factory=dict)
    attribution_support: Dict[str, float] = field(default_factory=dict)
    alternative_interpretations: List[Dict[str, Any]] = field(default_factory=list)
    primary_interpretation: str = AttributionClass.UNCERTAIN.value
    interpretation_text: str = ""
    verdict: str = "REVIEW"
    temporal_trajectory: Optional[Dict[str, Any]] = None
    disclaimer: str = DISCLAIMER_TEXT

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_text": self.query_text,
            "retrieval_summary": self.retrieval_summary,
            "temporal_observation": self.temporal_observation,
            "spectral_evidence": self.spectral_evidence,
            "spatial_evidence": self.spatial_evidence,
            "attribution_support": self.attribution_support,
            "alternative_interpretations": self.alternative_interpretations,
            "primary_interpretation": self.primary_interpretation,
            "interpretation_text": self.interpretation_text,
            "verdict": self.verdict,
            "temporal_trajectory": self.temporal_trajectory,
            "disclaimer": self.disclaimer,
        }


@dataclass
class AttributionResult:
    """Complete result of evidence-based change attribution."""
    dominant_interpretation: str
    support: Dict[str, float]
    metrics: Dict[str, Any]
    interpretation_text: str
    evidence_chain: Optional[EvidenceChain] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dominant_interpretation": self.dominant_interpretation,
            "support": self.support,
            "metrics": self.metrics,
            "interpretation_text": self.interpretation_text,
            "evidence_chain": self.evidence_chain.to_dict() if self.evidence_chain else None,
        }


def compute_ndvi(nir: np.ndarray, red: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """
    Compute Normalized Difference Vegetation Index:
    NDVI = (NIR - Red) / (NIR + Red + eps)
    Safe against division by zero and NaNs. Output clipped to [-1.0, 1.0].
    """
    denom = nir + red + eps
    ndvi = (nir - red) / denom
    ndvi = np.nan_to_num(ndvi, nan=0.0, posinf=1.0, neginf=-1.0)
    return np.clip(ndvi, -1.0, 1.0).astype(np.float32)


def compute_ndwi(green: np.ndarray, nir: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """
    Compute Normalized Difference Water Index (McFeeters):
    NDWI = (Green - NIR) / (Green + NIR + eps)
    Safe against division by zero and NaNs. Output clipped to [-1.0, 1.0].
    """
    denom = green + nir + eps
    ndwi = (green - nir) / denom
    ndwi = np.nan_to_num(ndwi, nan=0.0, posinf=1.0, neginf=-1.0)
    return np.clip(ndwi, -1.0, 1.0).astype(np.float32)


def compute_spatial_coherence(change_mask: np.ndarray) -> Dict[str, Any]:
    """
    Compute spatial coherence of changed pixels using connected component labeling.
    Coherence = largest_component_size / total_changed_pixels.
    Returns 0.0 when no pixels changed.
    """
    if change_mask is None or not np.any(change_mask):
        return {
            "coherence": 0.0,
            "component_count": 0,
            "largest_component_size": 0,
            "changed_pixel_count": 0,
        }

    mask_bool = change_mask.astype(bool)
    total_changed = int(np.sum(mask_bool))
    if total_changed == 0:
        return {
            "coherence": 0.0,
            "component_count": 0,
            "largest_component_size": 0,
            "changed_pixel_count": 0,
        }

    labeled, num_features = label(mask_bool)
    if num_features == 0:
        return {
            "coherence": 0.0,
            "component_count": 0,
            "largest_component_size": 0,
            "changed_pixel_count": total_changed,
        }

    # Bincount ignores background label 0
    counts = np.bincount(labeled.ravel())[1:]
    largest = int(np.max(counts)) if len(counts) > 0 else 0
    coherence = float(largest / total_changed) if total_changed > 0 else 0.0

    return {
        "coherence": float(np.clip(coherence, 0.0, 1.0)),
        "component_count": int(num_features),
        "largest_component_size": largest,
        "changed_pixel_count": total_changed,
    }


def generate_interpretation_text(dominant: str) -> str:
    """Deterministic explanation templates based on dominant signature."""
    templates = {
        AttributionClass.BUILT_SURFACE.value: (
            "The observed change shows a strong built-surface / vegetation-loss spectral signature, "
            "supported by decreased NIR, increased Red reflectance, reduced NDVI, and coherent spatial structure."
        ),
        AttributionClass.VEGETATION_CHANGE.value: (
            "The observed change is more consistent with vegetation dynamics than built-surface change, "
            "based on the NDVI response and weaker structural evidence."
        ),
        AttributionClass.WATER_CHANGE.value: (
            "The observed spectral pattern is consistent with a water-related change, "
            "supported by reduced NIR and an increase in NDWI."
        ),
        AttributionClass.SEASONAL.value: (
            "The observed change is consistent with seasonal vegetation variation, "
            "exhibiting moderate NDVI shift and diffuse spatial structure without strong structural transition."
        ),
        AttributionClass.ARTIFACT.value: (
            "The spectral shifts are abrupt and uniform across bands, suggesting possible "
            "imaging, cloud, or sensor artifacts rather than genuine ground-cover transition."
        ),
        AttributionClass.UNCERTAIN.value: (
            "The available spectral and spatial evidence is mixed, so the system does not "
            "assign a dominant interpretation."
        ),
    }
    return templates.get(dominant, templates[AttributionClass.UNCERTAIN.value])


def attribute_change(
    obs_t0: np.ndarray,
    obs_t1: np.ndarray,
    change_mask: np.ndarray,
    band_names: Optional[List[str]] = None,
    query_text: Optional[str] = None,
    verdict: str = "REVIEW",
    valid_mask: Optional[np.ndarray] = None,
) -> AttributionResult:
    """
    Perform evidence-based change attribution across T0 and T1 observations.

    Args:
        obs_t0: float32 array (C, H, W) normalized in [0, 1].
        obs_t1: float32 array (C, H, W) normalized in [0, 1].
        change_mask: boolean or uint8 array (H, W) where True/1 indicates changed pixel.
        band_names: Optional list of band names, e.g. ["Blue", "Green", "Red", "NIR"].
        query_text: User query string if available.
        verdict: Existing verdict string ("SUPPORTED", "REVIEW", "ABSTAIN").
        valid_mask: Optional boolean array (H, W) where True = valid, False = cloud/invalid.

    Returns:
        AttributionResult containing support scores, metrics, and evidence chain.
    """
    # Safeguard input arrays against NaN / Inf
    t0 = np.nan_to_num(obs_t0.astype(np.float32), nan=0.0, posinf=1.0, neginf=0.0)
    t1 = np.nan_to_num(obs_t1.astype(np.float32), nan=0.0, posinf=1.0, neginf=0.0)
    mask = np.nan_to_num(change_mask, nan=0).astype(bool)

    # Validate reflectance range consistency (expected [0, 1] range)
    if np.mean(t0 > 0.99) > 0.5 or np.mean(t1 > 0.99) > 0.5:
        import logging
        logging.getLogger(__name__).warning(
            "Inconsistent reflectance scale detected: >50% of values near/above 1.0. "
            "Verify that input uint16 data was normalized by 10000.0."
        )

    # Apply valid mask (e.g. SCL cloud/shadow filtering) if provided
    total_pixels = mask.size
    if valid_mask is not None:
        v_mask = valid_mask.astype(bool)
        mask = mask & v_mask
        total_valid = int(np.sum(v_mask))
        invalid_fraction = float(1.0 - (total_valid / total_pixels)) if total_pixels > 0 else 0.0
    else:
        total_valid = total_pixels
        invalid_fraction = 0.0

    # Resolve band indices (Default: 0=Blue, 1=Green, 2=Red, 3=NIR)
    b_idx, g_idx, r_idx, nir_idx = 0, 1, 2, 3
    if band_names:
        names_lower = [str(b).lower() for b in band_names]
        for i, n in enumerate(names_lower):
            if "blue" in n: b_idx = i
            elif "green" in n: g_idx = i
            elif "red" in n and "edge" not in n: r_idx = i
            elif "nir" in n or "near" in n: nir_idx = i

    max_b = max(b_idx, g_idx, r_idx, nir_idx)
    if t0.shape[0] <= max_b or t1.shape[0] <= max_b:
        raise ValueError(
            f"Expected at least {max_b + 1} bands for attribution (Blue, Green, Red, NIR), "
            f"got {min(t0.shape[0], t1.shape[0])} bands."
        )

    # Compute bands & spectral indices
    b_t0, b_t1 = t0[b_idx], t1[b_idx]
    g_t0, g_t1 = t0[g_idx], t1[g_idx]
    r_t0, r_t1 = t0[r_idx], t1[r_idx]
    nir_t0, nir_t1 = t0[nir_idx], t1[nir_idx]

    ndvi_t0 = compute_ndvi(nir_t0, r_t0)
    ndvi_t1 = compute_ndvi(nir_t1, r_t1)
    ndwi_t0 = compute_ndwi(g_t0, nir_t0)
    ndwi_t1 = compute_ndwi(g_t1, nir_t1)

    delta_b = b_t1 - b_t0
    delta_g = g_t1 - g_t0
    delta_red = r_t1 - r_t0
    delta_nir = nir_t1 - nir_t0
    delta_ndvi = ndvi_t1 - ndvi_t0
    delta_ndwi = ndwi_t1 - ndwi_t0

    # Spatial coherence
    spatial_stats = compute_spatial_coherence(mask)
    changed_count = spatial_stats["changed_pixel_count"]
    coherence = spatial_stats["coherence"]
    component_count = spatial_stats["component_count"]
    change_fraction = float(changed_count / total_valid) if total_valid > 0 else 0.0

    # Case: No changed pixels
    if changed_count == 0:
        empty_support = {
            AttributionClass.BUILT_SURFACE.value: 0.0,
            AttributionClass.VEGETATION_CHANGE.value: 0.0,
            AttributionClass.WATER_CHANGE.value: 0.0,
            AttributionClass.SEASONAL.value: 0.0,
            AttributionClass.ARTIFACT.value: 0.0,
            AttributionClass.UNCERTAIN.value: 1.0,
        }
        empty_metrics = {
            "delta_nir_mean": 0.0,
            "delta_red_mean": 0.0,
            "delta_green_mean": 0.0,
            "delta_blue_mean": 0.0,
            "delta_ndvi_mean": 0.0,
            "delta_ndwi_mean": 0.0,
            "change_fraction": 0.0,
            "spatial_coherence": 0.0,
            "component_count": 0,
            "changed_pixel_count": 0,
            "valid_pixels": total_valid,
            "invalid_pixels_fraction": float(np.round(invalid_fraction, 4)),
        }
        text = generate_interpretation_text(AttributionClass.UNCERTAIN.value)
        chain = EvidenceChain(
            query_text=query_text,
            retrieval_summary="No significant change region detected.",
            temporal_observation="0.0% of pixels changed",
            spectral_evidence={"delta_nir": "0.0%", "delta_red": "0.0%", "delta_ndvi": "0.00", "delta_ndwi": "0.00"},
            spatial_evidence={"coherence": "0%", "components": "0"},
            attribution_support=empty_support,
            primary_interpretation=AttributionClass.UNCERTAIN.value,
            interpretation_text=text,
            verdict=verdict,
        )
        return AttributionResult(
            dominant_interpretation=AttributionClass.UNCERTAIN.value,
            support=empty_support,
            metrics=empty_metrics,
            interpretation_text=text,
            evidence_chain=chain,
        )

    # Aggregated metrics over changed pixels
    m_dnir = float(np.mean(delta_nir[mask]))
    m_dred = float(np.mean(delta_red[mask]))
    m_dgreen = float(np.mean(delta_g[mask]))
    m_dblue = float(np.mean(delta_b[mask]))
    m_dndvi = float(np.mean(delta_ndvi[mask]))
    m_dndwi = float(np.mean(delta_ndwi[mask]))

    # --- Rule-Based Evidence Evaluation (Heuristic Support Points) ---
    scores: Dict[str, float] = {
        AttributionClass.BUILT_SURFACE.value: 0.02,
        AttributionClass.VEGETATION_CHANGE.value: 0.02,
        AttributionClass.WATER_CHANGE.value: 0.01,
        AttributionClass.SEASONAL.value: 0.02,
        AttributionClass.ARTIFACT.value: 0.01,
        AttributionClass.UNCERTAIN.value: 0.05,
    }

    # 1. BUILT_SURFACE signature:
    # NIR decreases or stays lower relative to visible; Red increases noticeably;
    # NDVI decreases significantly (vegetation loss / impervious surface gain); high spatial coherence.
    if m_dred > 0.04:
        scores[AttributionClass.BUILT_SURFACE.value] += min(m_dred * 5.0, 1.5)
    if m_dndvi < -0.08:
        scores[AttributionClass.BUILT_SURFACE.value] += min(abs(m_dndvi) * 4.0, 1.5)
    if m_dnir < 0.02 and m_dred > 0.05:
        scores[AttributionClass.BUILT_SURFACE.value] += 0.5
    if m_dnir < -0.05:
        scores[AttributionClass.BUILT_SURFACE.value] += 0.4
    if coherence > 0.5:
        scores[AttributionClass.BUILT_SURFACE.value] += coherence * 0.6

    # 2. VEGETATION_CHANGE signature (Greening / Regeneration):
    # NIR increases, Red decreases, NDVI increases.
    if m_dndvi > 0.08:
        scores[AttributionClass.VEGETATION_CHANGE.value] += min(m_dndvi * 4.0, 1.2)
    if m_dnir > 0.05:
        scores[AttributionClass.VEGETATION_CHANGE.value] += min(m_dnir * 3.0, 0.8)
    if m_dred < -0.02:
        scores[AttributionClass.VEGETATION_CHANGE.value] += min(abs(m_dred) * 3.0, 0.6)

    # 3. WATER_CHANGE signature:
    # Water strongly absorbs NIR and Red. End-state NIR and Red must be low.
    mean_nir_t1 = float(np.mean(nir_t1[mask]))
    mean_red_t1 = float(np.mean(r_t1[mask]))
    mean_ndwi_t1 = float(np.mean(ndwi_t1[mask]))

    if m_dndwi > 0.10 and m_dred < 0.03 and mean_nir_t1 < 0.18:
        scores[AttributionClass.WATER_CHANGE.value] += min(m_dndwi * 4.0, 1.5)
    if m_dnir < -0.12 and mean_nir_t1 < 0.15 and mean_red_t1 < 0.15:
        scores[AttributionClass.WATER_CHANGE.value] += min(abs(m_dnir) * 3.0, 1.0)
    if mean_ndwi_t1 > 0.05 and mean_red_t1 < 0.12 and mean_nir_t1 < 0.15:
        scores[AttributionClass.WATER_CHANGE.value] += 0.8

    # 4. SEASONAL signature:
    # Moderate NDVI shift without severe structural/reflectance disruption (low delta_red).
    if 0.03 <= abs(m_dndvi) <= 0.25 and abs(m_dred) < 0.08:
        scores[AttributionClass.SEASONAL.value] += 0.6
    if abs(m_dred) < 0.05 and abs(m_dnir) < 0.10:
        scores[AttributionClass.SEASONAL.value] += 0.4
    if coherence < 0.5:
        scores[AttributionClass.SEASONAL.value] += 0.3

    # 5. ARTIFACT signature:
    # All visible & NIR bands jump simultaneously in lockstep without spectral divergence.
    band_deltas = np.array([m_dblue, m_dgreen, m_dred, m_dnir])
    band_std = float(np.std(band_deltas))
    band_mean = float(np.mean(np.abs(band_deltas)))
    if band_mean > 0.20 and band_std < 0.04:
        # Uniform shift across all bands indicates cloud/sensor/illumination artifact
        scores[AttributionClass.ARTIFACT.value] += 1.5

    # Normalize scores to sum to 1.0
    total_score = sum(scores.values())
    if total_score <= 0.1:
        normalized_support = {k: 0.0 for k in scores}
        normalized_support[AttributionClass.UNCERTAIN.value] = 1.0
        dominant = AttributionClass.UNCERTAIN.value
    else:
        normalized_support = {
            k: float(np.round(v / total_score, 3)) for k, v in scores.items()
        }
        # Re-ensure exact sum to 1.0 due to rounding
        diff = 1.0 - sum(normalized_support.values())
        top_k = max(normalized_support, key=normalized_support.get)
        normalized_support[top_k] = float(np.round(normalized_support[top_k] + diff, 3))

        # Dominant interpretation (highest support excluding UNCERTAIN if others > 0.2)
        candidates = {k: v for k, v in normalized_support.items() if k != AttributionClass.UNCERTAIN.value}
        best_candidate = max(candidates, key=candidates.get)
        if candidates[best_candidate] >= 0.30:
            dominant = best_candidate
        else:
            dominant = AttributionClass.UNCERTAIN.value

    interpretation_text = generate_interpretation_text(dominant)

    metrics = {
        "delta_nir_mean": float(np.round(m_dnir, 4)),
        "delta_red_mean": float(np.round(m_dred, 4)),
        "delta_green_mean": float(np.round(m_dgreen, 4)),
        "delta_blue_mean": float(np.round(m_dblue, 4)),
        "delta_ndvi_mean": float(np.round(m_dndvi, 4)),
        "delta_ndwi_mean": float(np.round(m_dndwi, 4)),
        "change_fraction": float(np.round(change_fraction, 4)),
        "spatial_coherence": float(np.round(coherence, 4)),
        "component_count": int(component_count),
        "changed_pixel_count": int(changed_count),
        "valid_pixels": int(total_valid),
        "invalid_pixels_fraction": float(np.round(invalid_fraction, 4)),
    }

    # Format evidence chain strings
    def _pct(v: float) -> str:
        sign = "+" if v > 0 else ""
        return f"{sign}{v*100:.1f}%"

    def _val(v: float) -> str:
        sign = "+" if v > 0 else ""
        return f"{sign}{v:.2f}"

    spectral_ev = {
        "delta_nir": _pct(m_dnir),
        "delta_red": _pct(m_dred),
        "delta_ndvi": _val(m_dndvi),
        "delta_ndwi": _val(m_dndwi),
    }

    spatial_ev = {
        "coherence": f"{coherence * 100:.1f}%",
        "components": str(component_count),
        "changed_pixels": str(changed_count),
    }

    # Categorize support levels for alternative interpretations
    alternatives = []
    for cls_name, score in normalized_support.items():
        if cls_name == AttributionClass.UNCERTAIN.value:
            continue
        level = "STRONG" if score >= 0.50 else ("MODERATE" if score >= 0.20 else "LOW")
        alternatives.append({
            "interpretation": cls_name,
            "display_name": DISPLAY_LABELS.get(cls_name, cls_name),
            "support_score": score,
            "level": level,
        })
    alternatives.sort(key=lambda x: x["support_score"], reverse=True)

    chain = EvidenceChain(
        query_text=query_text,
        retrieval_summary="Relevant satellite tile retrieved via semantic search.",
        temporal_observation=f"{change_fraction * 100:.1f}% of valid pixels changed",
        spectral_evidence=spectral_ev,
        spatial_evidence=spatial_ev,
        attribution_support=normalized_support,
        alternative_interpretations=alternatives,
        primary_interpretation=dominant,
        interpretation_text=interpretation_text,
        verdict=verdict,
        disclaimer=DISCLAIMER_TEXT,
    )

    return AttributionResult(
        dominant_interpretation=dominant,
        support=normalized_support,
        metrics=metrics,
        interpretation_text=interpretation_text,
        evidence_chain=chain,
    )
