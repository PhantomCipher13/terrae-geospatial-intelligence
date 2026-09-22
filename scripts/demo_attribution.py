"""
scripts/demo_attribution.py
Demonstrate Evidence-Based Change Attribution on:
1. Real synthetic construction scene from DB (Case A)
2. Vegetation regrowth scenario (Case B)
3. Ambiguous / no change scenario (Case C)
"""
import sys
from pathlib import Path

# Safe Unicode output for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import numpy as np
from terrae.app_factory import _load_config, build_metadata_db, build_temporal_workflow
from terrae.change.attribution import attribute_change, DISPLAY_LABELS

def main():
    print("=" * 70)
    print("  SIH26227 — Evidence-Based Change Attribution Demonstration")
    print("=" * 70)
    
    cfg = _load_config("configs/config.yaml")
    db = build_metadata_db(cfg)
    temporal, _ = build_temporal_workflow(cfg)

    # -------------------------------------------------------------
    # CASE A: Real synthetic construction scene in database
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("  CASE A: Construction / Built-Surface Signature (Database Ingest)")
    print("-" * 70)

    with db._conn as conn:
        c = conn.cursor()
        c.execute("SELECT tile_id FROM tiles WHERE scene_id IN (SELECT scene_id FROM scenes WHERE source_path LIKE '%scene_T0%')")
        tiles = c.fetchall()

    target_tile_id = None
    target_res = None
    t0_time = time.perf_counter()
    for row in tiles:
        tid = row[0]
        res = temporal.run_analysis(tid, query_text="new construction and buildings")
        if res.verdict.name == "SUPPORTED":
            target_tile_id = tid
            target_res = res
            break
    elapsed_ms = (time.perf_counter() - t0_time) * 1000

    if target_res:
        attr = target_res.attribution
        chain = attr.evidence_chain
        print(f"Tile ID:                 {target_tile_id}")
        print(f"Verdict:                 {target_res.verdict.name}")
        print(f"Changed Fraction:        {attr.metrics['change_fraction']*100:.1f}%")
        print(f"Primary Interpretation:  {DISPLAY_LABELS.get(attr.dominant_interpretation, attr.dominant_interpretation)}")
        print(f"Interpretation Text:\n  '{attr.interpretation_text}'")
        print("\nSpectral Evidence:")
        for k, v in chain.spectral_evidence.items():
            print(f"  {k:15s}: {v}")
        print("\nSpatial Evidence:")
        for k, v in chain.spatial_evidence.items():
            print(f"  {k:15s}: {v}")
        print("\nAttribution Support Scores (Heuristic Signature Matching):")
        for k, v in attr.support.items():
            bar = "█" * int(round(v * 25))
            print(f"  {DISPLAY_LABELS.get(k, k):25s}: {v*100:5.1f}%  {bar}")

        if target_res.persistence:
            p = target_res.persistence
            print(f"\nTemporal Persistence Analysis:")
            print(f"  Dominant State:        {p.dominant_temporal_state}")
            print(f"  Interpretation:        '{p.interpretation_text}'")
            print(f"  Intervals:             T0->Tmid: {p.intervals['t0_tmid']:.1%}, Tmid->T1: {p.intervals['tmid_t1']:.1%}, T0->T1: {p.intervals['t0_t1']:.1%}")
            td = p.trajectory_distribution
            print(f"  Trajectory Dist:       Persistent={td['persistent_fraction']:.1%}, Late={td['late_fraction']:.1%}, Stable={td['stable_fraction']:.1%}")

        print(f"\nExecution Latency:       {elapsed_ms:.1f} ms (includes DB reads, 3-scene stack, differencing & attribution)")

    # -------------------------------------------------------------
    # CASE B: Vegetation growth / greening signature
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("  CASE B: Vegetation Dynamics / Greening Signature")
    print("-" * 70)
    
    # 4 bands: B, G, R, NIR. 64x64
    t0_veg = np.zeros((4, 64, 64), dtype=np.float32)
    t1_veg = np.zeros((4, 64, 64), dtype=np.float32)
    # T0: Cleared / barren soil
    t0_veg[0] = 0.08
    t0_veg[1] = 0.10
    t0_veg[2] = 0.18
    t0_veg[3] = 0.12
    # T1: Regrown vegetation
    t1_veg[0] = 0.04
    t1_veg[1] = 0.12
    t1_veg[2] = 0.05
    t1_veg[3] = 0.36
    mask_veg = np.zeros((64, 64), dtype=bool)
    mask_veg[16:48, 16:48] = True  # 25% change

    attr_veg = attribute_change(t0_veg, t1_veg, mask_veg, query_text="forest growth", verdict="REVIEW")
    print(f"Verdict:                 REVIEW (Significant spectral change, but non-construction)")
    print(f"Changed Fraction:        {attr_veg.metrics['change_fraction']*100:.1f}%")
    print(f"Primary Interpretation:  {DISPLAY_LABELS.get(attr_veg.dominant_interpretation, attr_veg.dominant_interpretation)}")
    print(f"Interpretation Text:\n  '{attr_veg.interpretation_text}'")
    print("\nSpectral Evidence:")
    for k, v in attr_veg.evidence_chain.spectral_evidence.items():
        print(f"  {k:15s}: {v}")
    print("\nAttribution Support Scores:")
    for k, v in attr_veg.support.items():
        bar = "█" * int(round(v * 25))
        print(f"  {DISPLAY_LABELS.get(k, k):25s}: {v*100:5.1f}%  {bar}")

    # -------------------------------------------------------------
    # CASE C: Ambiguous / no change scenario
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("  CASE C: Unchanged / Ambiguous Background Scenario")
    print("-" * 70)
    t0_bg = np.full((4, 64, 64), 0.15, dtype=np.float32)
    t1_bg = np.full((4, 64, 64), 0.15, dtype=np.float32)
    mask_bg = np.zeros((64, 64), dtype=bool)

    attr_bg = attribute_change(t0_bg, t1_bg, mask_bg, query_text="any change", verdict="REVIEW")
    print(f"Verdict:                 REVIEW")
    print(f"Changed Fraction:        {attr_bg.metrics['change_fraction']*100:.1f}%")
    print(f"Primary Interpretation:  {DISPLAY_LABELS.get(attr_bg.dominant_interpretation, attr_bg.dominant_interpretation)}")
    print(f"Interpretation Text:\n  '{attr_bg.interpretation_text}'")
    print("\nAttribution Support Scores:")
    for k, v in attr_bg.support.items():
        bar = "█" * int(round(v * 25))
        print(f"  {DISPLAY_LABELS.get(k, k):25s}: {v*100:5.1f}%  {bar}")

    print("\n" + "=" * 70)
    print("  DISCLAIMER:")
    print(f"  {attr.evidence_chain.disclaimer}")
    print("=" * 70)

if __name__ == "__main__":
    main()
