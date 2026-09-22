"""
scripts/benchmark.py
Measure real inference and retrieval performance.
Reports: model load time, image embed time, text embed time, FAISS search time,
         end-to-end time, peak RAM, device, vector count.

Usage:
    C:\Python311\python.exe scripts\benchmark.py
    C:\Python311\python.exe scripts\benchmark.py --config configs\config.yaml --n-images 20 --top-k 10
"""
import argparse
import gc
import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np


def get_ram_mb() -> float:
    try:
        import psutil
        return psutil.Process().memory_info().rss / (1024 ** 2)
    except ImportError:
        return -1.0


def benchmark_embedding_provider(embedder, n_images: int = 10):
    """Time image and text embedding with warm + cold passes."""
    import numpy as np
    rng = np.random.default_rng(42)

    # Generate synthetic RGB images (HWC uint8)
    images = [
        (rng.integers(0, 255, (224, 224, 3), dtype=np.uint8))
        for _ in range(n_images)
    ]

    # ── Cold image embed (first call, model may be JIT-ing)
    _ = embedder.encode_image(images[0])

    # ── Warm image embed (N times)
    t0 = time.perf_counter()
    for img in images:
        embedder.encode_image(img)
    img_time_total = time.perf_counter() - t0
    img_time_per = img_time_total / n_images

    # ── Text embed
    texts = [
        "urban area", "dense forest", "water body",
        "agricultural fields", "roads and built-up area",
        "barren land", "snow and ice", "industrial area",
    ]
    t0 = time.perf_counter()
    for text in texts:
        embedder.encode_text(text)
    txt_time_total = time.perf_counter() - t0
    txt_time_per = txt_time_total / len(texts)

    return {
        "n_images": n_images,
        "n_texts": len(texts),
        "img_time_total_s": img_time_total,
        "img_time_per_s": img_time_per,
        "txt_time_total_s": txt_time_total,
        "txt_time_per_s": txt_time_per,
    }


def benchmark_faiss(index, n_queries: int = 20, top_k: int = 10):
    """Time FAISS search on the loaded index."""
    if index.total_vectors == 0:
        return {"skipped": True, "reason": "Index is empty"}

    rng = np.random.default_rng(99)
    queries = []
    for _ in range(n_queries):
        v = rng.standard_normal(index.embedding_dim).astype(np.float32)
        v /= np.linalg.norm(v)
        queries.append(v)

    # Cold
    _ = index.search(queries[0], top_k)

    # Warm
    t0 = time.perf_counter()
    for q in queries:
        index.search(q, top_k)
    total = time.perf_counter() - t0

    return {
        "n_queries": n_queries,
        "top_k": top_k,
        "total_s": total,
        "per_query_ms": (total / n_queries) * 1000,
        "indexed_vectors": index.total_vectors,
    }


def main():
    parser = argparse.ArgumentParser(description="Benchmark RemoteCLIP + FAISS performance.")
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--n-images", type=int, default=10)
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  TERRAE Workstation — Performance Benchmark")
    print("=" * 60)

    # System info
    print(f"\n[System]")
    print(f"  OS:       {platform.system()} {platform.release()}")
    print(f"  Python:   {sys.version.split()[0]}")
    try:
        import torch
        print(f"  PyTorch:  {torch.__version__}")
        print(f"  CUDA:     {'YES' if torch.cuda.is_available() else 'NO'}")
    except Exception:
        pass

    ram_start = get_ram_mb()
    print(f"  RAM at start: {ram_start:.1f} MB")

    # Load components
    print(f"\n[Loading components from {args.config}]")
    from terrae.app_factory import _load_config, build_embedding_provider, build_index_backend

    cfg = _load_config(args.config)
    provider_name = cfg.get("embedding", {}).get("provider", "unknown")
    print(f"  Embedding provider: {provider_name}")

    t_load_start = time.perf_counter()
    embedder = build_embedding_provider(cfg)
    load_time = time.perf_counter() - t_load_start

    ram_after_load = get_ram_mb()
    print(f"  Model load time:  {load_time:.2f}s")
    print(f"  RAM after load:   {ram_after_load:.1f} MB (+{ram_after_load - ram_start:.1f} MB)")
    print(f"  Model ID:         {embedder.model_id}")
    print(f"  Is mock:          {embedder.is_mock}")
    print(f"  Embedding dim:    {embedder.embedding_dim}")
    if hasattr(embedder, 'device'):
        print(f"  Device:           {embedder.device}")
    if hasattr(embedder, 'checkpoint_path') and embedder.checkpoint_path:
        size_mb = embedder.checkpoint_path.stat().st_size / (1024 ** 2)
        print(f"  Checkpoint size:  {size_mb:.1f} MB")

    # Embedding benchmark
    print(f"\n[Embedding Benchmark] n_images={args.n_images}")
    emb_results = benchmark_embedding_provider(embedder, n_images=args.n_images)
    print(f"  Image embed:  {emb_results['img_time_per_s']*1000:.1f} ms/image  "
          f"(total {emb_results['img_time_total_s']:.2f}s for {args.n_images} images)")
    print(f"  Text embed:   {emb_results['txt_time_per_s']*1000:.1f} ms/query  "
          f"(total {emb_results['txt_time_total_s']:.2f}s for {emb_results['n_texts']} queries)")

    # FAISS benchmark
    print(f"\n[FAISS Search Benchmark] top_k={args.top_k}")
    idx, _ = build_index_backend(cfg)
    faiss_results = benchmark_faiss(idx, top_k=args.top_k)
    if faiss_results.get("skipped"):
        print(f"  SKIPPED: {faiss_results['reason']}")
        print(f"  (Ingest some imagery first to populate the index)")
    else:
        print(f"  Indexed vectors:  {faiss_results['indexed_vectors']}")
        print(f"  Search time:      {faiss_results['per_query_ms']:.3f} ms/query")

    # End-to-end retrieval
    print(f"\n[End-to-End Retrieval]")
    from terrae.db.metadata_db import MetadataDB
    from terrae.retrieval.engine import RetrievalEngine
    from terrae.planner.query_planner import plan_query

    db = MetadataDB(Path(cfg.get("storage", {}).get("db_path", "data/terrae_metadata.db")))
    engine = RetrievalEngine(embedder, idx, db)
    test_queries = ["urban area", "dense forest", "water body"]
    e2e_times = []
    for q in test_queries:
        t0 = time.perf_counter()
        plan = plan_query(q, top_k=args.top_k)
        results = engine.search_text(q, top_k=args.top_k, plan=plan)
        e2e_ms = (time.perf_counter() - t0) * 1000
        e2e_times.append(e2e_ms)
        print(f"  '{q}': {e2e_ms:.1f} ms → {len(results)} results")

    avg_e2e = sum(e2e_times) / len(e2e_times)
    print(f"  Average e2e:  {avg_e2e:.1f} ms")

    ram_end = get_ram_mb()
    print(f"\n[Memory]")
    print(f"  Peak RAM:  {ram_end:.1f} MB")
    print(f"  Delta:     +{ram_end - ram_start:.1f} MB")

    print(f"\n[Summary]")
    print(f"  Model load:     {load_time:.2f}s")
    print(f"  Image embed:    {emb_results['img_time_per_s']*1000:.1f} ms/image")
    print(f"  Text embed:     {emb_results['txt_time_per_s']*1000:.1f} ms/query")
    if not faiss_results.get("skipped"):
        print(f"  FAISS search:   {faiss_results['per_query_ms']:.3f} ms/query  ({faiss_results['indexed_vectors']} vectors)")
    print(f"  E2E retrieval:  {avg_e2e:.1f} ms average")
    print(f"  RAM delta:      +{ram_end - ram_start:.1f} MB")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
