"""
scripts/query.py
CLI: text or image query against the local index.

Usage:
    C:\Python311\python.exe scripts\query.py --text "urban construction area"
    C:\Python311\python.exe scripts\query.py --text "flooded farmland" --top-k 5
    C:\Python311\python.exe scripts\query.py --config configs\config.yaml --text "dense forest"
"""
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.WARNING,  # quiet for CLI — only show results
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    parser = argparse.ArgumentParser(description="Query the GeoAI semantic index.")
    parser.add_argument("--text", default=None, help="Text query string.")
    parser.add_argument("--top-k", type=int, default=10, help="Number of results to return.")
    parser.add_argument("--config", default="configs/config.yaml", help="Config YAML path.")
    args = parser.parse_args()

    if not args.text:
        parser.print_help()
        sys.exit(1)

    from geoai.app_factory import build_retrieval_engine, _load_config
    from geoai.planner.query_planner import plan_query

    cfg = _load_config(args.config)
    engine, index, db = build_retrieval_engine(cfg)

    # Plan the query
    plan = plan_query(query_text=args.text, top_k=args.top_k)
    print(f"\n🔍 Query:  '{args.text}'")
    print(f"   Intent: {plan.intent}")
    for note in plan.notes:
        print(f"   📋 {note}")

    if index.total_vectors == 0:
        print("\n⚠️  Index is empty. Run: python scripts/ingest.py --file <path/to/scene.tif>")
        sys.exit(0)

    print(f"\n   Index:  {index.total_vectors} vectors ({index.index_id})")

    results = engine.search_text(args.text, top_k=args.top_k, plan=plan)

    if not results:
        print("\n   No results found.")
        sys.exit(0)

    print(f"\n{'─'*60}")
    print(f"  Top-{len(results)} Results")
    print(f"{'─'*60}")
    for r in results:
        mock_warn = ""
        if r.embedding_model and "MOCK" in r.embedding_model.upper():
            mock_warn = " ⚠️ MOCK"
        print(f"\n  Rank #{r.rank}{mock_warn}")
        print(f"  Tile ID:    {r.tile_id}")
        print(f"  Score:      {r.similarity_score:.4f}")
        print(f"  Sensor:     {r.sensor or 'UNKNOWN'} ({r.sensor_type or 'UNKNOWN'})")
        print(f"  Date:       {r.acquisition_date or 'UNKNOWN'}")
        if r.bounds_wgs84:
            b = r.bounds_wgs84
            print(f"  Bounds:     W={b[0]:.4f} S={b[1]:.4f} E={b[2]:.4f} N={b[3]:.4f}")
        else:
            print(f"  Bounds:     UNAVAILABLE (no CRS/transform in source)")
        print(f"  Source:     {r.source_path}")
    print(f"{'─'*60}\n")

    stats = db.stats()
    print(f"📊 DB: {stats['scenes']} scenes | {stats['tiles']} tiles | {stats['embedded']} embedded\n")


if __name__ == "__main__":
    main()
