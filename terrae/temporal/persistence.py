"""
terrae/temporal/persistence.py
Multi-temporal trajectory persistence check for >= 3 observations.

Analyzes trajectory behavior across T0 -> Tmid -> T1:
- PERSISTENT_CHANGE: Transition appears in T0->Tmid and remains present at T1.
- TRANSIENT_CHANGE: Transition appears in T0->Tmid, but reverses by T1.
- SEASONAL_OR_REVERSIBLE: Trajectory exhibits seasonal fluctuation (e.g. dry -> lush -> dormant).
- LATE_ONSET_CHANGE: Minimal change T0->Tmid, clear change appears Tmid->T1.
- INSUFFICIENT_TEMPORAL_EVIDENCE: No meaningful change across sequence.

Terminology note:
These are temporal trajectory classifications, not causal proofs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import numpy as np

from terrae.change.attribution import compute_ndvi, compute_ndwi


class TemporalCategory(str, Enum):
    STABLE = "STABLE"
    PERSISTENT_CHANGE = "PERSISTENT_CHANGE"
    TRANSIENT_CHANGE = "TRANSIENT_CHANGE"
    LATE_ONSET_CHANGE = "LATE_ONSET_CHANGE"
    REVERSIBLE_CHANGE = "REVERSIBLE_CHANGE"
    SEASONAL_OR_REVERSIBLE = "SEASONAL_OR_REVERSIBLE"
    INSUFFICIENT_TEMPORAL_EVIDENCE = "INSUFFICIENT_TEMPORAL_EVIDENCE"


TEMPORAL_TEMPLATES: Dict[str, str] = {
    TemporalCategory.STABLE.value: (
        "Most of the valid scene remains temporally stable, while a small fraction "
        "contains localized persistent, transient, late-onset, or reversible trajectories."
    ),
    TemporalCategory.PERSISTENT_CHANGE.value: (
        "The dominant temporal trajectory exhibits early-emerging spectral departure that remains sustained "
        "across the sequence, providing trajectory evidence for persistent land-cover conversion."
    ),
    TemporalCategory.TRANSIENT_CHANGE.value: (
        "The dominant temporal trajectory exhibits an intermediate spectral departure that does not persist "
        "into the final observation, without satisfying the criteria for full trajectory reversal."
    ),
    TemporalCategory.LATE_ONSET_CHANGE.value: (
        "The dominant temporal trajectory remains stable through the intermediate date, with meaningful "
        "spectral change emerging primarily in the final interval."
    ),
    TemporalCategory.REVERSIBLE_CHANGE.value: (
        "The dominant temporal trajectory exhibits reversible temporal variation across the sequence: "
        "a meaningful departure is followed by a directed return toward the initial baseline state."
    ),
    TemporalCategory.SEASONAL_OR_REVERSIBLE.value: (
        "The dominant temporal trajectory exhibits reversible variation across the sequence "
        "(e.g. cyclical phenological fluctuation between dry and post-monsoon seasons), "
        "rather than permanent land-cover conversion."
    ),
    TemporalCategory.INSUFFICIENT_TEMPORAL_EVIDENCE.value: (
        "The observations show minimal spectral variation across intervals, providing insufficient temporal evidence "
        "for land-cover transition."
    ),
}


@dataclass
class TemporalPersistenceResult:
    """Result of temporal trajectory persistence analysis."""
    category: str
    interpretation_text: str
    intervals: Dict[str, float]                     # Interval changes: t0_tmid, tmid_t1, t0_t1
    trajectory_distribution: Dict[str, float]       # Mutually exclusive: stable_fraction, persistent_fraction, ...
    persistence_metrics: Dict[str, float]           # Alias / backward compatibility
    spectral_trajectory: Dict[str, List[float]]     # Region-average continuous measurements
    timestamps: List[str]
    valid_pixels: int
    total_pixels: int
    category_distribution: Dict[str, float] = field(default_factory=dict)
    category_counts: Dict[str, int] = field(default_factory=dict)
    interval_counts: Dict[str, int] = field(default_factory=dict)
    dominant_temporal_state: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "dominant_temporal_state": self.dominant_temporal_state,
            "interpretation_text": self.interpretation_text,
            "intervals": self.intervals,
            "interval_counts": self.interval_counts,
            "trajectory_distribution": self.trajectory_distribution,
            "persistence_metrics": self.persistence_metrics,
            "category_distribution": self.category_distribution,
            "category_counts": self.category_counts,
            "spectral_trajectory": self.spectral_trajectory,
            "timestamps": self.timestamps,
            "valid_pixels": self.valid_pixels,
            "total_pixels": self.total_pixels,
        }


def analyze_temporal_persistence(
    observations: List[np.ndarray],
    timestamps: List[str],
    threshold: float = 0.15,
    valid_mask: Optional[np.ndarray] = None,
    band_names: Optional[List[str]] = None,
) -> TemporalPersistenceResult:
    """
    Analyze temporal persistence across >= 3 observations.

    Pixel categories are mutually exclusive and collectively exhaustive over valid pixels:
    - STABLE: Below threshold across all 3 intervals.
    - PERSISTENT_CHANGE: Changed by Tmid, remains changed at T1 without return.
    - TRANSIENT_CHANGE: Intermediate change not persisting into T1 without meeting strict reversal.
    - LATE_ONSET_CHANGE: Little change by Tmid, meaningful change emerging at T1.
    - REVERSIBLE_CHANGE: Meaningful departure by Tmid, substantial return toward T0 at T1.

    Args:
        observations: List of float32 arrays (C, H, W) normalized to [0, 1].
        timestamps: List of acquisition dates (ISO strings).
        threshold: Spectral change threshold (default 0.15).
        valid_mask: Optional boolean array (H, W) masking cloud/invalid pixels across dates.
        band_names: List of band names (default ["Blue", "Green", "Red", "NIR"]).

    Returns:
        TemporalPersistenceResult with category, MECE trajectory distribution, interval changes,
        and region-average spectral trajectory.
    """
    n_obs = len(observations)
    if n_obs < 3:
        raise ValueError(f"Temporal persistence analysis requires >= 3 observations, got {n_obs}.")

    # Resolve band indices
    b_idx, g_idx, r_idx, nir_idx = 0, 1, 2, 3
    if band_names:
        names_lower = [str(b).lower() for b in band_names]
        for i, n in enumerate(names_lower):
            if "blue" in n: b_idx = i
            elif "green" in n: g_idx = i
            elif "red" in n and "edge" not in n: r_idx = i
            elif "nir" in n or "near" in n: nir_idx = i

    shape = observations[0].shape[1:]  # (H, W)
    total_pixels = shape[0] * shape[1]

    if valid_mask is not None:
        v_mask = valid_mask.astype(bool)
        total_valid = int(np.sum(v_mask))
    else:
        v_mask = np.ones(shape, dtype=bool)
        total_valid = total_pixels

    empty_dist = {
        "stable_fraction": 1.0,
        "persistent_fraction": 0.0,
        "transient_fraction": 0.0,
        "late_fraction": 0.0,
        "reversible_fraction": 0.0,
    }
    empty_cat_dist = {
        TemporalCategory.STABLE.value: 1.0,
        TemporalCategory.PERSISTENT_CHANGE.value: 0.0,
        TemporalCategory.TRANSIENT_CHANGE.value: 0.0,
        TemporalCategory.LATE_ONSET_CHANGE.value: 0.0,
        TemporalCategory.REVERSIBLE_CHANGE.value: 0.0,
    }

    if total_valid == 0:
        return TemporalPersistenceResult(
            category=TemporalCategory.STABLE.value,
            dominant_temporal_state=f"{TemporalCategory.STABLE.value} — 0.00% of valid pixels",
            interpretation_text="No valid pixels available for temporal persistence analysis.",
            intervals={"t0_tmid": 0.0, "tmid_t1": 0.0, "t0_t1": 0.0},
            interval_counts={"t0_tmid": 0, "tmid_t1": 0, "t0_t1": 0},
            trajectory_distribution=empty_dist,
            persistence_metrics={**empty_dist, "seasonal_reversal_fraction": 0.0},
            category_distribution=empty_cat_dist,
            category_counts={k: 0 for k in empty_cat_dist},
            spectral_trajectory={},
            timestamps=timestamps,
            valid_pixels=0,
            total_pixels=total_pixels,
        )

    # Consider first, middle, and last observation
    obs0 = observations[0]
    obs_mid = observations[n_obs // 2]
    obs1 = observations[-1]

    # Compute interval differences (mean absolute difference across bands)
    diff_0_mid = np.mean(np.abs(obs_mid - obs0), axis=0)
    diff_mid_1 = np.mean(np.abs(obs1 - obs_mid), axis=0)
    diff_0_1 = np.mean(np.abs(obs1 - obs0), axis=0)

    # Interval masks (exceeding threshold & valid)
    mask_0_mid = (diff_0_mid > threshold) & v_mask
    mask_mid_1 = (diff_mid_1 > threshold) & v_mask
    mask_0_1 = (diff_0_1 > threshold) & v_mask

    # Calculate change fractions per interval (kept strictly separate from trajectory distribution)
    frac_0_mid = float(np.sum(mask_0_mid) / total_valid)
    frac_mid_1 = float(np.sum(mask_mid_1) / total_valid)
    frac_0_1 = float(np.sum(mask_0_1) / total_valid)

    # -------------------------------------------------------------------------
    # Mutually Exclusive & Collectively Exhaustive (MECE) Pixel Classification
    # -------------------------------------------------------------------------

    # 1. STABLE: All 3 interval differences are below the meaningful threshold
    mask_stable = (diff_0_mid <= threshold) & (diff_mid_1 <= threshold) & (diff_0_1 <= threshold) & v_mask
    non_stable = v_mask & (~mask_stable)

    # 2. LATE_ONSET_CHANGE: T0 -> Tmid is below threshold, but change emerges at T1
    mask_late = non_stable & (diff_0_mid <= threshold) & (diff_0_1 > threshold)

    # Directional return vector and margin for strict reversal checking
    v_mid_to_1 = obs1 - obs_mid
    v_mid_to_0 = obs0 - obs_mid
    dot_return = np.sum(v_mid_to_1 * v_mid_to_0, axis=0)  # positive when moving back towards T0
    return_margin = max(0.03, threshold * 0.2)

    # 3. REVERSIBLE_CHANGE:
    # Requires:
    # - Meaningful movement away from T0 to Tmid
    # - Meaningful movement back from Tmid to T1
    # - Final state T1 substantially closer to T0 than Tmid was
    # - Return exceeds margin and is directed towards T0
    mask_reversible = (
        non_stable
        & (~mask_late)
        & (diff_0_mid > threshold)
        & (diff_mid_1 > threshold * 0.7)
        & (diff_0_1 < diff_0_mid - return_margin)
        & ((diff_0_1 <= threshold) | (diff_0_1 < 0.6 * diff_0_mid))
        & (dot_return > 0)
    )

    # 4. PERSISTENT_CHANGE:
    # Requires:
    # - Meaningful change by Tmid
    # - T0 -> T1 remains meaningfully different from T0
    # - No strong evidence that the state returned toward T0
    mask_persistent = (
        non_stable
        & (~mask_late)
        & (~mask_reversible)
        & (diff_0_mid > threshold)
        & (diff_0_1 > threshold)
        & (diff_0_1 >= diff_0_mid - return_margin)
    )

    # 5. TRANSIENT_CHANGE:
    # Temporary / intermediate change that does not persist at T1 and does not meet strict reversal
    mask_transient = non_stable & (~mask_late) & (~mask_reversible) & (~mask_persistent)

    # Actual pixel counts
    c_stable = int(np.sum(mask_stable))
    c_persist = int(np.sum(mask_persistent))
    c_transient = int(np.sum(mask_transient))
    c_late = int(np.sum(mask_late))
    c_rev = int(np.sum(mask_reversible))

    # Verify collective exhaustiveness over valid pixels
    assert c_stable + c_persist + c_transient + c_late + c_rev == total_valid

    # Mutually exclusive category fractions
    stable_fraction = float(c_stable / total_valid)
    persistent_fraction = float(c_persist / total_valid)
    transient_fraction = float(c_transient / total_valid)
    late_fraction = float(c_late / total_valid)
    reversible_fraction = float(c_rev / total_valid)

    trajectory_distribution = {
        "stable_fraction": float(np.round(stable_fraction, 4)),
        "persistent_fraction": float(np.round(persistent_fraction, 4)),
        "transient_fraction": float(np.round(transient_fraction, 4)),
        "late_fraction": float(np.round(late_fraction, 4)),
        "reversible_fraction": float(np.round(reversible_fraction, 4)),
    }

    # Ensure rounded distribution sums exactly to 1.0
    rounding_diff = 1.0 - sum(trajectory_distribution.values())
    if abs(rounding_diff) > 1e-6:
        dominant_key = max(trajectory_distribution, key=trajectory_distribution.get)
        trajectory_distribution[dominant_key] = float(np.round(trajectory_distribution[dominant_key] + rounding_diff, 4))

    category_distribution = {
        TemporalCategory.STABLE.value: trajectory_distribution["stable_fraction"],
        TemporalCategory.PERSISTENT_CHANGE.value: trajectory_distribution["persistent_fraction"],
        TemporalCategory.TRANSIENT_CHANGE.value: trajectory_distribution["transient_fraction"],
        TemporalCategory.LATE_ONSET_CHANGE.value: trajectory_distribution["late_fraction"],
        TemporalCategory.REVERSIBLE_CHANGE.value: trajectory_distribution["reversible_fraction"],
    }

    # Backward compatibility metrics dictionary
    persistence_metrics = {
        **trajectory_distribution,
        "seasonal_reversal_fraction": trajectory_distribution["reversible_fraction"],
    }

    # -------------------------------------------------------------------------
    # Region-Average Continuous Spectral Trajectory (Aggregates Across Stack)
    # -------------------------------------------------------------------------
    ndvi0 = compute_ndvi(obs0[nir_idx], obs0[r_idx])
    ndvi_mid = compute_ndvi(obs_mid[nir_idx], obs_mid[r_idx])
    ndvi1 = compute_ndvi(obs1[nir_idx], obs1[r_idx])

    sample_mask = mask_0_1 if np.sum(mask_0_1) > 0 else v_mask

    def _mean_val(arr, mask):
        return float(np.mean(arr[mask]))

    spectral_trajectory = {
        "NDVI": [
            float(np.round(_mean_val(ndvi0, sample_mask), 3)),
            float(np.round(_mean_val(ndvi_mid, sample_mask), 3)),
            float(np.round(_mean_val(ndvi1, sample_mask), 3)),
        ],
        "NDWI": [
            float(np.round(_mean_val(compute_ndwi(obs0[g_idx], obs0[nir_idx]), sample_mask), 3)),
            float(np.round(_mean_val(compute_ndwi(obs_mid[g_idx], obs_mid[nir_idx]), sample_mask), 3)),
            float(np.round(_mean_val(compute_ndwi(obs1[g_idx], obs1[nir_idx]), sample_mask), 3)),
        ],
        "NIR": [
            float(np.round(_mean_val(obs0[nir_idx], sample_mask), 3)),
            float(np.round(_mean_val(obs_mid[nir_idx], sample_mask), 3)),
            float(np.round(_mean_val(obs1[nir_idx], sample_mask), 3)),
        ],
        "Red": [
            float(np.round(_mean_val(obs0[r_idx], sample_mask), 3)),
            float(np.round(_mean_val(obs_mid[r_idx], sample_mask), 3)),
            float(np.round(_mean_val(obs1[r_idx], sample_mask), 3)),
        ],
    }

    # -------------------------------------------------------------------------
    # Dominant Temporal Trajectory Classification
    # -------------------------------------------------------------------------
    change_candidates = [
        (TemporalCategory.PERSISTENT_CHANGE.value, persistent_fraction),
        (TemporalCategory.REVERSIBLE_CHANGE.value, reversible_fraction),
        (TemporalCategory.TRANSIENT_CHANGE.value, transient_fraction),
        (TemporalCategory.LATE_ONSET_CHANGE.value, late_fraction),
    ]
    change_candidates.sort(key=lambda x: x[1], reverse=True)
    best_change_cat, best_change_val = change_candidates[0]

    if stable_fraction >= 0.95 or best_change_val < 0.01:
        category = TemporalCategory.STABLE.value
    else:
        category = best_change_cat

    category_counts = {
        TemporalCategory.STABLE.value: c_stable,
        TemporalCategory.PERSISTENT_CHANGE.value: c_persist,
        TemporalCategory.TRANSIENT_CHANGE.value: c_transient,
        TemporalCategory.LATE_ONSET_CHANGE.value: c_late,
        TemporalCategory.REVERSIBLE_CHANGE.value: c_rev,
    }
    interval_counts = {
        "t0_tmid": int(np.sum(mask_0_mid)),
        "tmid_t1": int(np.sum(mask_mid_1)),
        "t0_t1": int(np.sum(mask_0_1)),
    }

    if category == TemporalCategory.STABLE.value:
        dom_frac = stable_fraction
        if stable_fraction >= 0.9999:
            interp_text = "The spectral observations remain temporally stable across all intervals across valid pixels."
        else:
            interp_text = (
                f"Most of the valid scene remains temporally stable ({stable_fraction*100:.2f}%), "
                "while a small fraction contains localized persistent, transient, late-onset, or reversible trajectories."
            )
    else:
        dom_frac = category_distribution.get(category, 0.0)
        interp_text = TEMPORAL_TEMPLATES.get(category, TEMPORAL_TEMPLATES[TemporalCategory.STABLE.value])

    dom_state = f"{category} — {dom_frac*100:.2f}% of valid pixels"

    return TemporalPersistenceResult(
        category=category,
        dominant_temporal_state=dom_state,
        interpretation_text=interp_text,
        intervals={
            "t0_tmid": float(np.round(frac_0_mid, 4)),
            "tmid_t1": float(np.round(frac_mid_1, 4)),
            "t0_t1": float(np.round(frac_0_1, 4)),
        },
        interval_counts=interval_counts,
        trajectory_distribution=trajectory_distribution,
        persistence_metrics=persistence_metrics,
        category_distribution=category_distribution,
        category_counts=category_counts,
        spectral_trajectory=spectral_trajectory,
        timestamps=timestamps,
        valid_pixels=total_valid,
        total_pixels=total_pixels,
    )
