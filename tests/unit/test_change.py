"""
tests/unit/test_change.py
Tests for change detection logic.
"""
import numpy as np
from geoai.providers.change.spectral_detector import SpectralChangeDetector
from geoai.core.result import ChangeVerdict

def test_spectral_change_detector():
    detector = SpectralChangeDetector(threshold=0.15, min_change_fraction=0.05)
    assert detector.min_observations == 2
    
    # Create mock observations
    # Obs 1: all zeros
    obs1 = np.zeros((4, 64, 64), dtype=np.float32)
    # Obs 2: all zeros except a 10x10 square that is 0.5 (above 0.15 threshold)
    obs2 = np.zeros((4, 64, 64), dtype=np.float32)
    obs2[:, 10:20, 10:20] = 0.5
    
    result = detector.detect([obs1, obs2], ["2024-01-01", "2024-02-01"])
    
    # Check verdict
    # 10x10 = 100 pixels out of 4096 = ~0.024 (< 0.05 min fraction)
    # Wait, the threshold is 0.05. 0.024 < 0.05, so it should be REVIEW.
    assert result.verdict == ChangeVerdict.REVIEW
    assert result.evidence[0].change_fraction == 100.0 / 4096.0
    
    # Increase change area to 20x20 = 400 pixels (~0.097 > 0.05)
    obs2[:, 10:30, 10:30] = 0.5
    result2 = detector.detect([obs1, obs2], ["2024-01-01", "2024-02-01"])
    assert result2.verdict == ChangeVerdict.SUPPORTED
    
def test_spectral_change_insufficient_obs():
    detector = SpectralChangeDetector()
    obs1 = np.zeros((4, 64, 64), dtype=np.float32)
    result = detector.detect([obs1])
    assert result.verdict == ChangeVerdict.ABSTAIN
    assert "Insufficient" in result.abstain_reason
