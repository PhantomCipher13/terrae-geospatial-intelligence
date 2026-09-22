"""
geoai/providers/registration/opencv_ecc.py
OpenCV ECC-based co-registration provider.
Handles rigid/affine registration for overlapping single-band images.

Status: REAL implementation — uses OpenCV ECC algorithm.
Limitation: Works best for small shifts (<50px), rigid transforms only.
For sub-pixel accuracy on satellite imagery, AROSICS is preferred (Phase 7+).
"""
from __future__ import annotations
import logging
import time
from typing import Optional
import numpy as np

from geoai.core.result import RegistrationResult, RegistrationStatus
from geoai.providers.registration.base import RegistrationProvider

logger = logging.getLogger(__name__)


class OpenCVECCProvider(RegistrationProvider):
    """
    ECC (Enhanced Correlation Coefficient) co-registration via OpenCV.
    Uses the first band of each input array for alignment.
    """

    def __init__(
        self,
        warp_mode: str = "translation",   # 'translation' | 'euclidean' | 'affine'
        max_iter: int = 500,
        epsilon: float = 1e-6,
        ncc_threshold_good: float = 0.95,
        ncc_threshold_borderline: float = 0.80,
    ) -> None:
        self._warp_mode = warp_mode
        self._max_iter = max_iter
        self._eps = epsilon
        self._good_th = ncc_threshold_good
        self._border_th = ncc_threshold_borderline

    @property
    def provider_id(self) -> str:
        return f"opencv-ecc-{self._warp_mode}-v1"

    def can_register(self) -> bool:
        try:
            import cv2
            return True
        except ImportError:
            return False

    def register(
        self,
        reference: np.ndarray,
        target: np.ndarray,
        reference_meta: dict | None = None,
        target_meta: dict | None = None,
    ) -> RegistrationResult:
        if not self.can_register():
            return RegistrationResult(
                status=RegistrationStatus.UNAVAILABLE,
                method=self.provider_id,
                notes=["opencv-python not installed."],
            )

        import cv2
        t0 = time.time()

        # Use first band, convert to float32
        ref = self._extract_band(reference)
        tgt = self._extract_band(target)

        if ref.shape != tgt.shape:
            return RegistrationResult(
                status=RegistrationStatus.FAILED,
                method=self.provider_id,
                processing_time_s=time.time() - t0,
                notes=[f"Shape mismatch: ref={ref.shape} tgt={tgt.shape}. Cannot register."],
            )

        # ECC warp mode
        mode_map = {
            "translation": cv2.MOTION_TRANSLATION,
            "euclidean": cv2.MOTION_EUCLIDEAN,
            "affine": cv2.MOTION_AFFINE,
        }
        warp_mode_cv = mode_map.get(self._warp_mode, cv2.MOTION_TRANSLATION)

        if self._warp_mode in ("translation", "euclidean"):
            warp_matrix = np.eye(2, 3, dtype=np.float32)
        else:
            warp_matrix = np.eye(2, 3, dtype=np.float32)

        try:
            criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                        self._max_iter, self._eps)
            cc, warp_matrix = cv2.findTransformECC(
                ref, tgt, warp_matrix, warp_mode_cv, criteria
            )
        except cv2.error as e:
            return RegistrationResult(
                status=RegistrationStatus.FAILED,
                method=self.provider_id,
                processing_time_s=time.time() - t0,
                notes=[f"ECC failed to converge: {e}"],
            )

        # Extract shift
        shift_x = float(warp_matrix[0, 2])
        shift_y = float(warp_matrix[1, 2])

        # Determine status from ECC correlation coefficient
        if cc >= self._good_th:
            status = RegistrationStatus.GOOD
        elif cc >= self._border_th:
            status = RegistrationStatus.BORDERLINE
        else:
            status = RegistrationStatus.FAILED

        elapsed = time.time() - t0
        return RegistrationResult(
            status=status,
            method=self.provider_id,
            shift_x_px=shift_x,
            shift_y_px=shift_y,
            quality_metric=float(cc),
            confidence=float(cc),
            processing_time_s=elapsed,
            notes=[
                f"ECC correlation coefficient: {cc:.4f}",
                f"Shift: ({shift_x:.2f}, {shift_y:.2f}) px",
            ],
        )

    def _extract_band(self, array: np.ndarray) -> np.ndarray:
        if array.ndim == 3:
            band = array[0].astype(np.float32)
        else:
            band = array.astype(np.float32)
        # Normalise to [0,1] for ECC
        lo, hi = band.min(), band.max()
        if hi > lo:
            return (band - lo) / (hi - lo)
        return band
