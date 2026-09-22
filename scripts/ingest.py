"""
scripts/ingest.py
CLI: ingest a GeoTIFF/COG into the local index.

Usage:
    C:\Python311\python.exe scripts\ingest.py --file path\to\scene.tif
    C:\Python311\python.exe scripts\ingest.py --file path\to\scene.tif --config configs\config.yaml
"""
import argparse
import logging
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    parser = argparse.ArgumentParser(description="Ingest a GeoTIFF into the GeoAI index.")
    parser.add_argument("--file", required=True, help="Path to GeoTIFF or COG.")
    parser.add_argument("--config", default="configs/config.yaml", help="Config YAML path.")
    args = parser.parse_args()

    from geoai.app_factory import build_ingest_pipeline, _load_config
    cfg = _load_config(args.config)
    pipeline, index, db, index_dir = build_ingest_pipeline(cfg)

    print(f"\n📂 Ingesting: {args.file}")
    report = pipeline.ingest(Path(args.file))

    print("\n─── Ingest Report ───────────────────────────────────")
    print(f"  Scene ID:         {report.scene_id}")
    print(f"  Success:          {report.success}")
    if report.skipped:
        print(f"  Skipped:          YES — {report.skip_reason}")
    print(f"  Tiles generated:  {report.tiles_generated}")
    print(f"  Tiles indexed:    {report.tiles_indexed}")
    print(f"  Empty skipped:    {report.tiles_skipped_empty}")
    print(f"  Quality skipped:  {report.tiles_skipped_quality}")
    print(f"  Failed:           {report.tiles_failed}")
    print(f"  Elapsed:          {report.elapsed_s:.2f}s")
    if report.metadata_summary:
        print(f"  Metadata:         {report.metadata_summary}")
    if report.warnings:
        print(f"  Warnings ({len(report.warnings)}):")
        for w in report.warnings:
            print(f"    ⚠️  {w}")
    if report.errors:
        print(f"  Errors ({len(report.errors)}):")
        for e in report.errors:
            print(f"    ❌ {e}")
    print("────────────────────────────────────────────────────\n")

    if report.success and not report.skipped and report.tiles_indexed > 0:
        # Save index
        index.save(index_dir)
        print(f"✅ Index saved to '{index_dir}' ({index.total_vectors} total vectors)")

    stats = db.stats()
    print(f"📊 DB: {stats['scenes']} scenes | {stats['tiles']} tiles | {stats['embedded']} embedded")

    sys.exit(0 if report.success else 1)


if __name__ == "__main__":
    main()
