"""
terrae/providers/change/spectral_detector.py
Concrete implementation of ChangeDetector using spectral differencing.
"""
from __future__ import annotations
import numpy as np
from typing import List, Optional

from terrae.providers.change.base import ChangeDetector, TemporalChangeResult, ChangeEvidence
from terrae.core.result import ChangeVerdict, RegistrationResult, RegistrationStatus

class SpectralChangeDetector(ChangeDetector):
    """
    Detects change using simple absolute spectral difference and/or NDVI difference.
    """
    def __init__(self, threshold: float = 0.15, min_change_fraction: float = 0.05):
        self._threshold = threshold
        self._min_change_fraction = min_change_fraction

    @property
    def detector_id(self) -> str:
        return f"spectral-diff-v1(t={self._threshold})"

    @property
    def required_bands(self) -> Optional[List[str]]:
        # This implementation requires Red and NIR for NDVI, but we'll accept any 4-band if not strict.
        return ["Blue", "Green", "Red", "NIR"]

    def detect(
        self,
        observations: List[np.ndarray],
        timestamps: List[Optional[str]] | None = None,
        registration_result: RegistrationResult | None = None,
    ) -> TemporalChangeResult:
        if timestamps is None:
            timestamps = [None] * len(observations)
            
        # 1. Quality gate
        if registration_result and registration_result.status == RegistrationStatus.FAILED:
            return TemporalChangeResult(
                verdict=ChangeVerdict.ABSTAIN,
                observation_timestamps=timestamps,
                registration=registration_result,
                abstain_reason="Registration FAILED, cannot perform pixel-wise comparison"
            )
            
        if len(observations) < self.min_observations:
            return TemporalChangeResult(
                verdict=ChangeVerdict.ABSTAIN,
                observation_timestamps=timestamps,
                registration=registration_result,
                abstain_reason=f"Insufficient observations (need {self.min_observations}, got {len(observations)})"
            )
            
        # 2. Compute change between first and last observation
        obs1 = observations[0]
        obs2 = observations[-1]
        
        # Simple absolute difference across all available bands
        diff = np.abs(obs2 - obs1)
        mean_diff = np.mean(diff, axis=0) # Average across bands
        
        # Normalise to 0-1 for probability proxy (assuming inputs are already normalised or raw uint16)
        # If max is > 1.0, assume they are raw and divide by typical max (e.g., 10000)
        # If <= 1.0, use as is. We'll normalise by max difference in scene to highlight relative change,
        # or use fixed scaling. For simplicity:
        max_val = np.max(mean_diff) if np.max(mean_diff) > 1e-6 else 1.0
        prob = (mean_diff / max_val).astype(np.float32)
        
        # Apply fixed logical threshold based on input scale
        # Assume input arrays are float32 [0,1] or float32 derived from uint16 [0, 65535]
        # Our sensor adapters (OpticalAdapter) output float32 [0,1]! So obs1, obs2 are in [0,1].
        change_mask = mean_diff > self._threshold
        change_fraction = float(np.mean(change_mask))
        
        evidence = ChangeEvidence(
            method="spectral-diff",
            change_mask=change_mask,
            change_probability=prob,
            change_fraction=change_fraction,
            confidence=0.8 if change_fraction > self._min_change_fraction else 0.4
        )
        
        # 3. Verdict
        if change_fraction > self._min_change_fraction:
            verdict = ChangeVerdict.SUPPORTED
            notes = [f"Significant change detected ({change_fraction:.1%} of pixels > {self._threshold} threshold)"]
        else:
            verdict = ChangeVerdict.REVIEW
            notes = [f"Minimal change detected ({change_fraction:.1%} of pixels)"]
            
        return TemporalChangeResult(
            verdict=verdict,
            observation_timestamps=timestamps,
            evidence=[evidence],
            registration=registration_result,
            earliest_change_idx=1 if verdict == ChangeVerdict.SUPPORTED else None,
            notes=notes
        )
