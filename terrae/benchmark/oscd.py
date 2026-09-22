"""
terrae/benchmark/oscd.py
OSCD (Onera Satellite Change Detection) Benchmark Validation Harness.

Provides reproducible, quantitative validation for the existing change-detection component
against the external, labeled OSCD dataset without detector retraining or tuning.
"""
from __future__ import annotations

import logging
import os
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import rasterio
from rasterio.errors import NotGeoreferencedWarning

from terrae.providers.change.base import ChangeDetector, TemporalChangeResult
from terrae.providers.change.spectral_detector import SpectralChangeDetector

logger = logging.getLogger(__name__)

# Suppress rasterio warnings about unreferenced coordinate systems on local crops
warnings.filterwarnings("ignore", category=NotGeoreferencedWarning)


@dataclass(frozen=True)
class OSCDMetrics:
    """Quantitative binary change detection metrics."""
    tp: int
    tn: int
    fp: int
    fn: int
    precision: float
    recall: float
    f1: float
    iou: float
    accuracy: float
    valid_pixels: int
    excluded_pixels: int
    gt_changed_pixels: int
    gt_change_pct: float


@dataclass
class OSCDPair:
    """Represents a single co-registered OSCD image pair with ground truth."""
    city: str
    obs1: np.ndarray  # Shape: (C, H, W), float32 in [0, 1]
    obs2: np.ndarray  # Shape: (C, H, W), float32 in [0, 1]
    gt_mask: np.ndarray  # Shape: (H, W), boolean
    valid_mask: np.ndarray  # Shape: (H, W), boolean
    dates: Optional[Tuple[str, str]] = None


@dataclass(frozen=True)
class OSCDMacroMetrics:
    """Unweighted macro-averaged metrics across evaluated pairs."""
    precision: float
    recall: float
    f1: float
    iou: float
    accuracy: float


@dataclass
class OSCDBenchmarkReport:
    """Full benchmark evaluation report across multiple OSCD pairs."""
    pair_metrics: Dict[str, OSCDMetrics]
    aggregate_metrics: OSCDMetrics
    macro_metrics: OSCDMacroMetrics
    detector_id: str
    pairs_evaluated: int
    evaluation_time_sec: float


def compute_binary_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    valid_mask: Optional[np.ndarray] = None,
) -> OSCDMetrics:
    """
    Compute binary change detection metrics strictly over valid pixels.

    Args:
        y_true: Ground truth boolean or integer array (changed = True / >0)
        y_pred: Predicted change mask boolean or integer array
        valid_mask: Optional boolean mask where True indicates valid pixels.
                    If None, all pixels are treated as valid.

    Returns:
        OSCDMetrics dataclass with TP, TN, FP, FN, Precision, Recall, F1, IoU, Accuracy.

    Raises:
        ValueError: If y_true and y_pred shapes do not match, or if valid_mask shape mismatches.
    """
    if y_true.shape != y_pred.shape:
        raise ValueError(
            f"Shape mismatch between y_true {y_true.shape} and y_pred {y_pred.shape}"
        )

    yt = y_true.astype(bool)
    yp = y_pred.astype(bool)

    if valid_mask is not None:
        if valid_mask.shape != y_true.shape:
            raise ValueError(
                f"Shape mismatch between valid_mask {valid_mask.shape} and y_true {y_true.shape}"
            )
        vm = valid_mask.astype(bool)
        yt_eval = yt[vm]
        yp_eval = yp[vm]
        valid_pixels = int(np.sum(vm))
        excluded_pixels = int(y_true.size - valid_pixels)
    else:
        yt_eval = yt.ravel()
        yp_eval = yp.ravel()
        valid_pixels = int(y_true.size)
        excluded_pixels = 0

    tp = int(np.sum(yp_eval & yt_eval))
    tn = int(np.sum(~yp_eval & ~yt_eval))
    fp = int(np.sum(yp_eval & ~yt_eval))
    fn = int(np.sum(~yp_eval & yt_eval))

    gt_changed = tp + fn
    gt_change_pct = (gt_changed / valid_pixels * 100.0) if valid_pixels > 0 else 0.0

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2.0 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    iou = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0.0
    accuracy = (tp + tn) / valid_pixels if valid_pixels > 0 else 0.0

    return OSCDMetrics(
        tp=tp,
        tn=tn,
        fp=fp,
        fn=fn,
        precision=precision,
        recall=recall,
        f1=f1,
        iou=iou,
        accuracy=accuracy,
        valid_pixels=valid_pixels,
        excluded_pixels=excluded_pixels,
        gt_changed_pixels=gt_changed,
        gt_change_pct=gt_change_pct,
    )


def load_oscd_pair(
    city_dir: Union[str, Path],
    city_name: Optional[str] = None,
    bands: Optional[List[str]] = None,
) -> OSCDPair:
    """
    Load an OSCD image pair, 4 compatible spectral bands, and ground-truth change mask.

    Expected directory structure:
        <city_dir>/
            imgs_1_rect/  (B02.tif, B03.tif, B04.tif, B08.tif)
            imgs_2_rect/  (B02.tif, B03.tif, B04.tif, B08.tif)
            cm/           (<city_name>-cm.tif or cm.png)
            dates.txt     (optional: date_1: YYYYMMDD, date_2: YYYYMMDD)

    Normalisation:
        Sentinel-2 surface reflectance: raw uint16 / 10000.0 clipped to [0.0, 1.0].
    """
    path = Path(city_dir)
    name = city_name or path.name

    if bands is None:
        bands = ["B02", "B03", "B04", "B08"]

    def _read_band(t_dir: Path, band_name: str) -> np.ndarray:
        target = t_dir / f"{band_name}.tif"
        if not target.exists():
            # Try case-insensitive lookup
            candidates = list(t_dir.glob(f"*{band_name}*.tif"))
            if candidates:
                target = candidates[0]
            else:
                raise FileNotFoundError(f"Band file not found for {band_name} in {t_dir}")
        with rasterio.open(target) as src:
            arr = src.read(1)
        if arr.dtype == np.uint16:
            arr = arr.astype(np.float32) / 10000.0
        elif arr.dtype == np.uint8:
            arr = arr.astype(np.float32) / 255.0
        else:
            arr = arr.astype(np.float32)
        return np.clip(arr, 0.0, 1.0)

    dir_1 = path / "imgs_1_rect"
    dir_2 = path / "imgs_2_rect"

    if not dir_1.exists() or not dir_2.exists():
        raise FileNotFoundError(f"Missing imgs_1_rect or imgs_2_rect in {city_dir}")

    b1_list = [_read_band(dir_1, b) for b in bands]
    b2_list = [_read_band(dir_2, b) for b in bands]

    obs1 = np.stack(b1_list, axis=0)  # (C, H, W)
    obs2 = np.stack(b2_list, axis=0)  # (C, H, W)

    if obs1.shape != obs2.shape:
        raise ValueError(
            f"Dimension mismatch between observation 1 {obs1.shape} and observation 2 {obs2.shape} for {name}"
        )

    # Load Ground Truth Change Mask
    cm_dir = path / "cm"
    gt_tif = cm_dir / f"{name}-cm.tif"
    if not gt_tif.exists():
        # Fallback to any cm.tif or cm.png
        tifs = list(cm_dir.glob("*-cm.tif")) + list(cm_dir.glob("cm.tif"))
        if tifs:
            gt_tif = tifs[0]
        else:
            pngs = list(cm_dir.glob("*.png"))
            if pngs:
                gt_tif = pngs[0]
            else:
                raise FileNotFoundError(f"No ground truth change mask found in {cm_dir}")

    with rasterio.open(gt_tif) as src:
        gt_raw = src.read(1)

    if gt_raw.shape != obs1.shape[1:]:
        raise ValueError(
            f"Shape mismatch: ground truth {gt_raw.shape} does not match image raster {obs1.shape[1:]} for {name}"
        )

    # Interpret OSCD label encoding:
    # Standard OSCD tif labels: 1 = unchanged, 2 = changed, 0 = unlabelled / nodata
    # Standard OSCD png labels: 0 = unchanged, 255 = changed
    unique_vals = set(np.unique(gt_raw))
    if 2 in unique_vals:
        gt_mask = (gt_raw == 2)
        valid_mask = (gt_raw != 0)
    elif 255 in unique_vals:
        gt_mask = (gt_raw == 255)
        valid_mask = np.ones_like(gt_mask, dtype=bool)
    else:
        gt_mask = (gt_raw > 0)
        valid_mask = np.ones_like(gt_mask, dtype=bool)

    # Exclude non-finite / corrupt values if any
    valid_finite = (
        ~np.isnan(obs1).any(axis=0)
        & ~np.isnan(obs2).any(axis=0)
        & ~np.isinf(obs1).any(axis=0)
        & ~np.isinf(obs2).any(axis=0)
    )
    valid_mask = valid_mask & valid_finite

    # Dates parsing
    dates = None
    dates_file = path / "dates.txt"
    if dates_file.exists():
        try:
            content = dates_file.read_text(encoding="utf-8")
            d1, d2 = None, None
            for line in content.splitlines():
                if "date_1" in line:
                    d1 = line.split(":")[-1].strip()
                elif "date_2" in line:
                    d2 = line.split(":")[-1].strip()
            if d1 and d2:
                dates = (d1, d2)
        except Exception as e:
            logger.debug("Failed parsing dates.txt for %s: %s", name, e)

    return OSCDPair(
        city=name,
        obs1=obs1,
        obs2=obs2,
        gt_mask=gt_mask,
        valid_mask=valid_mask,
        dates=dates,
    )


def evaluate_oscd_pair(
    detector: ChangeDetector,
    pair: OSCDPair,
) -> Tuple[TemporalChangeResult, OSCDMetrics]:
    """
    Evaluate the change detector on a single OSCD pair.

    Args:
        detector: Any ChangeDetector adhering to the terrae interface.
        pair: An OSCDPair instance.

    Returns:
        Tuple of (TemporalChangeResult, OSCDMetrics).
    """
    timestamps = list(pair.dates) if pair.dates else [None, None]
    result = detector.detect(
        observations=[pair.obs1, pair.obs2],
        timestamps=timestamps,
    )

    if not result.evidence or result.evidence[0].change_mask is None:
        raise RuntimeError(f"Detector {detector.detector_id} returned no change mask evidence")

    pred_mask = result.evidence[0].change_mask

    if pred_mask.shape != pair.gt_mask.shape:
        raise ValueError(
            f"Prediction mask shape {pred_mask.shape} does not match GT mask shape {pair.gt_mask.shape}"
        )

    metrics = compute_binary_metrics(
        y_true=pair.gt_mask,
        y_pred=pred_mask,
        valid_mask=pair.valid_mask,
    )

    return result, metrics


def run_oscd_benchmark(
    benchmark_dir: Union[str, Path],
    detector: Optional[ChangeDetector] = None,
    city_subset: Optional[List[str]] = None,
) -> OSCDBenchmarkReport:
    """
    Run evaluation across all (or subset of) staged OSCD benchmark pairs.

    Computes both per-pair metrics and true micro-averaged aggregate metrics.
    """
    t_start = time.perf_counter()
    b_path = Path(benchmark_dir)

    if detector is None:
        detector = SpectralChangeDetector(threshold=0.15)

    if city_subset is not None:
        cities = sorted(city_subset)
    else:
        cities = sorted([d.name for d in b_path.iterdir() if d.is_dir()])

    pair_metrics: Dict[str, OSCDMetrics] = {}

    total_tp = 0
    total_tn = 0
    total_fp = 0
    total_fn = 0
    total_valid = 0
    total_excluded = 0
    total_gt_changed = 0

    for city in cities:
        city_dir = b_path / city
        if not city_dir.is_dir():
            logger.warning("City directory %s not found in %s, skipping", city, benchmark_dir)
            continue

        pair = load_oscd_pair(city_dir, city_name=city)
        _, m = evaluate_oscd_pair(detector, pair)
        pair_metrics[city] = m

        total_tp += m.tp
        total_tn += m.tn
        total_fp += m.fp
        total_fn += m.fn
        total_valid += m.valid_pixels
        total_excluded += m.excluded_pixels
        total_gt_changed += m.gt_changed_pixels

    # Compute micro-averaged aggregate metrics
    agg_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    agg_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    agg_f1 = (
        (2.0 * agg_precision * agg_recall) / (agg_precision + agg_recall)
        if (agg_precision + agg_recall) > 0
        else 0.0
    )
    agg_iou = (
        total_tp / (total_tp + total_fp + total_fn)
        if (total_tp + total_fp + total_fn) > 0
        else 0.0
    )
    agg_acc = (total_tp + total_tn) / total_valid if total_valid > 0 else 0.0
    agg_gt_change_pct = (
        (total_gt_changed / total_valid * 100.0) if total_valid > 0 else 0.0
    )

    agg_metrics = OSCDMetrics(
        tp=total_tp,
        tn=total_tn,
        fp=total_fp,
        fn=total_fn,
        precision=agg_precision,
        recall=agg_recall,
        f1=agg_f1,
        iou=agg_iou,
        accuracy=agg_acc,
        valid_pixels=total_valid,
        excluded_pixels=total_excluded,
        gt_changed_pixels=total_gt_changed,
        gt_change_pct=agg_gt_change_pct,
    )

    # Compute unweighted macro-averaged metrics across pairs
    n_pairs = len(pair_metrics)
    if n_pairs > 0:
        macro_metrics = OSCDMacroMetrics(
            precision=sum(m.precision for m in pair_metrics.values()) / n_pairs,
            recall=sum(m.recall for m in pair_metrics.values()) / n_pairs,
            f1=sum(m.f1 for m in pair_metrics.values()) / n_pairs,
            iou=sum(m.iou for m in pair_metrics.values()) / n_pairs,
            accuracy=sum(m.accuracy for m in pair_metrics.values()) / n_pairs,
        )
    else:
        macro_metrics = OSCDMacroMetrics(0.0, 0.0, 0.0, 0.0, 0.0)

    t_elapsed = time.perf_counter() - t_start

    return OSCDBenchmarkReport(
        pair_metrics=pair_metrics,
        aggregate_metrics=agg_metrics,
        macro_metrics=macro_metrics,
        detector_id=detector.detector_id,
        pairs_evaluated=len(pair_metrics),
        evaluation_time_sec=t_elapsed,
    )
