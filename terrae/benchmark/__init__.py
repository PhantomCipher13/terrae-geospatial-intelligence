"""
terrae/benchmark/__init__.py
Validation harnesses and benchmark adapters for TERRAE.
"""
from terrae.benchmark.oscd import (
    OSCDMetrics,
    OSCDMacroMetrics,
    OSCDPair,
    OSCDBenchmarkReport,
    compute_binary_metrics,
    load_oscd_pair,
    evaluate_oscd_pair,
    run_oscd_benchmark,
)

__all__ = [
    "OSCDMetrics",
    "OSCDMacroMetrics",
    "OSCDPair",
    "OSCDBenchmarkReport",
    "compute_binary_metrics",
    "load_oscd_pair",
    "evaluate_oscd_pair",
    "run_oscd_benchmark",
]
