"""
tests/unit/test_benchmark_oscd.py
Unit tests for the OSCD quantitative benchmark validation harness.
"""
import numpy as np
import pytest
from pathlib import Path

from geoai.benchmark.oscd import (
    OSCDMetrics,
    OSCDPair,
    compute_binary_metrics,
    evaluate_oscd_pair,
    load_oscd_pair,
    run_oscd_benchmark,
)
from geoai.providers.change.spectral_detector import SpectralChangeDetector


class TestMetricCorrectness:
    """Validate binary classification metrics against hand-calculated ground truth."""

    def test_known_toy_arrays(self):
        # 10 pixels:
        # y_true: [T, T, T, T, F, F, F, F, F, F] (4 positive, 6 negative)
        # y_pred: [T, T, T, F, T, T, F, F, F, F] (5 positive, 5 negative)
        # TP = 3, FP = 2, FN = 1, TN = 4
        y_true = np.array([1, 1, 1, 1, 0, 0, 0, 0, 0, 0], dtype=bool)
        y_pred = np.array([1, 1, 1, 0, 1, 1, 0, 0, 0, 0], dtype=bool)

        m = compute_binary_metrics(y_true, y_pred)

        assert m.tp == 3
        assert m.fp == 2
        assert m.fn == 1
        assert m.tn == 4
        assert m.valid_pixels == 10
        assert m.excluded_pixels == 0
        assert m.gt_changed_pixels == 4
        assert pytest.approx(m.gt_change_pct) == 40.0

        # Precision = 3 / (3 + 2) = 0.6
        assert pytest.approx(m.precision) == 0.6
        # Recall = 3 / (3 + 1) = 0.75
        assert pytest.approx(m.recall) == 0.75
        # F1 = 2 * 0.6 * 0.75 / (0.6 + 0.75) = 0.9 / 1.35 = 2/3
        assert pytest.approx(m.f1) == 2.0 / 3.0
        # IoU = 3 / (3 + 2 + 1) = 0.5
        assert pytest.approx(m.iou) == 0.5
        # Accuracy = (3 + 4) / 10 = 0.7
        assert pytest.approx(m.accuracy) == 0.7

    def test_all_negative(self):
        y_true = np.zeros((4, 4), dtype=bool)
        y_pred = np.zeros((4, 4), dtype=bool)

        m = compute_binary_metrics(y_true, y_pred)

        assert m.tp == 0
        assert m.tn == 16
        assert m.fp == 0
        assert m.fn == 0
        assert m.precision == 0.0
        assert m.recall == 0.0
        assert m.f1 == 0.0
        assert m.iou == 0.0
        assert m.accuracy == 1.0

    def test_all_positive(self):
        y_true = np.ones((4, 4), dtype=bool)
        y_pred = np.ones((4, 4), dtype=bool)

        m = compute_binary_metrics(y_true, y_pred)

        assert m.tp == 16
        assert m.tn == 0
        assert m.fp == 0
        assert m.fn == 0
        assert m.precision == 1.0
        assert m.recall == 1.0
        assert m.f1 == 1.0
        assert m.iou == 1.0
        assert m.accuracy == 1.0


class TestShapeMismatchHandling:
    """Verify that shape mismatches trigger clear ValueError exceptions."""

    def test_prediction_truth_shape_mismatch(self):
        y_true = np.zeros((10, 10), dtype=bool)
        y_pred = np.zeros((10, 12), dtype=bool)

        with pytest.raises(ValueError, match="Shape mismatch between y_true"):
            compute_binary_metrics(y_true, y_pred)

    def test_valid_mask_shape_mismatch(self):
        y_true = np.zeros((10, 10), dtype=bool)
        y_pred = np.zeros((10, 10), dtype=bool)
        valid_mask = np.ones((10, 15), dtype=bool)

        with pytest.raises(ValueError, match="Shape mismatch between valid_mask"):
            compute_binary_metrics(y_true, y_pred, valid_mask=valid_mask)


class TestMaskHandling:
    """Verify that masked pixels are strictly excluded from all metric calculations."""

    def test_masked_pixels_excluded_from_confusion_matrix(self):
        # 10 pixels:
        # y_true:     [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        # y_pred:     [1, 1, 1, 0, 1, 1, 0, 0, 0, 0]
        # Without mask: TP=3, FP=2, FN=1, TN=4
        # Mask out indices 3 (FN) and 4 (FP)
        valid_mask = np.array([1, 1, 1, 0, 0, 1, 1, 1, 1, 1], dtype=bool)
        y_true = np.array([1, 1, 1, 1, 0, 0, 0, 0, 0, 0], dtype=bool)
        y_pred = np.array([1, 1, 1, 0, 1, 1, 0, 0, 0, 0], dtype=bool)

        m = compute_binary_metrics(y_true, y_pred, valid_mask=valid_mask)

        # After masking:
        # Evaluated true: [1, 1, 1, 0, 0, 0, 0, 0] (3 pos, 5 neg)
        # Evaluated pred: [1, 1, 1, 1, 0, 0, 0, 0] (4 pos, 4 neg)
        # TP = 3, FP = 1, FN = 0, TN = 4
        assert m.tp == 3
        assert m.fp == 1
        assert m.fn == 0
        assert m.tn == 4
        assert m.valid_pixels == 8
        assert m.excluded_pixels == 2
        assert m.gt_changed_pixels == 3
        assert pytest.approx(m.precision) == 0.75
        assert pytest.approx(m.recall) == 1.0
        assert pytest.approx(m.accuracy) == 7.0 / 8.0


class TestBinaryConversion:
    """Verify correct interpretation of OSCD label encodings."""

    def test_oscd_tif_encoding(self, tmp_path):
        import rasterio

        # 1 = unchanged, 2 = changed, 0 = nodata
        gt_data = np.array([[0, 1], [2, 1]], dtype=np.uint8)
        img_data = np.ones((4, 2, 2), dtype=np.float32) * 0.2

        city_dir = tmp_path / "test_city"
        (city_dir / "imgs_1_rect").mkdir(parents=True)
        (city_dir / "imgs_2_rect").mkdir(parents=True)
        (city_dir / "cm").mkdir(parents=True)

        for b in ["B02", "B03", "B04", "B08"]:
            for t in [1, 2]:
                t_dir = city_dir / f"imgs_{t}_rect"
                with rasterio.open(
                    t_dir / f"{b}.tif", "w", driver="GTiff", width=2, height=2, count=1, dtype="uint16"
                ) as dst:
                    dst.write(np.full((2, 2), 2000, dtype=np.uint16), 1)

        with rasterio.open(
            city_dir / "cm" / "test_city-cm.tif", "w", driver="GTiff", width=2, height=2, count=1, dtype="uint8"
        ) as dst:
            dst.write(gt_data, 1)

        pair = load_oscd_pair(city_dir)

        # gt_mask: only pixel (1, 0) is changed
        assert pair.gt_mask[0, 0] == False  # was 0 (nodata)
        assert pair.gt_mask[0, 1] == False  # was 1 (unchanged)
        assert pair.gt_mask[1, 0] == True   # was 2 (changed)
        assert pair.gt_mask[1, 1] == False  # was 1 (unchanged)

        # valid_mask: (0, 0) was 0 -> False, others True
        assert pair.valid_mask[0, 0] == False
        assert pair.valid_mask[0, 1] == True
        assert pair.valid_mask[1, 0] == True
        assert pair.valid_mask[1, 1] == True


class TestBenchmarkDeterminism:
    """Verify that multiple benchmark runs produce identical results."""

    def test_determinism_on_staged_data(self):
        benchmark_dir = Path("data/benchmark/oscd")
        if not benchmark_dir.exists():
            pytest.skip("Benchmark data not staged")

        detector1 = SpectralChangeDetector(threshold=0.15)
        report1 = run_oscd_benchmark(benchmark_dir, detector=detector1, city_subset=["bordeaux"])

        detector2 = SpectralChangeDetector(threshold=0.15)
        report2 = run_oscd_benchmark(benchmark_dir, detector=detector2, city_subset=["bordeaux"])

        m1 = report1.pair_metrics["bordeaux"]
        m2 = report2.pair_metrics["bordeaux"]

        assert m1.tp == m2.tp
        assert m1.tn == m2.tn
        assert m1.fp == m2.fp
        assert m1.fn == m2.fn
        assert m1.precision == m2.precision
        assert m1.recall == m2.recall
        assert m1.f1 == m2.f1
        assert m1.iou == m2.iou
        assert m1.accuracy == m2.accuracy

    def test_macro_metrics_calculation(self):
        benchmark_dir = Path("data/benchmark/oscd")
        if not benchmark_dir.exists():
            pytest.skip("Benchmark data not staged")

        detector = SpectralChangeDetector(threshold=0.15)
        cities = ["bordeaux", "aguasclaras"]
        report = run_oscd_benchmark(benchmark_dir, detector=detector, city_subset=cities)

        expected_macro_prec = sum(m.precision for m in report.pair_metrics.values()) / 2.0
        expected_macro_rec = sum(m.recall for m in report.pair_metrics.values()) / 2.0
        expected_macro_f1 = sum(m.f1 for m in report.pair_metrics.values()) / 2.0

        assert pytest.approx(report.macro_metrics.precision) == expected_macro_prec
        assert pytest.approx(report.macro_metrics.recall) == expected_macro_rec
        assert pytest.approx(report.macro_metrics.f1) == expected_macro_f1
