"""
scripts/semantic_smoke_test.py
Manually curated semantic plausibility check for RemoteCLIP embeddings.

This is NOT a benchmark. It only verifies that text-image similarity is
semantically coherent using synthetic imagery categories.

We generate simple synthetic images representing rough categories and verify
that the correct text query gets the highest similarity score. With real
RemoteCLIP weights, correct ranking should occur for these obvious cases.

Run after: python scripts/ingest.py --file <real_or_synthetic_scene.tif>
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import warnings


def make_synthetic_category_image(category: str) -> np.ndarray:
    """
    Generate a 224x224 uint8 RGB image with rough visual characteristics.
    These are NOT real satellite images — they are colorimetric approximations
    used only to sanity-check that RemoteCLIP's text-image similarity is working.

    Real evaluation requires a labeled satellite dataset (e.g., RSICD, UCMerced).
    """
    rng = np.random.default_rng(hash(category) % (2 ** 32))
    base = np.zeros((224, 224, 3), dtype=np.uint8)

    if category == "water":
        # Blue dominant
        base[..., 0] = rng.integers(20, 60, (224, 224))
        base[..., 1] = rng.integers(60, 100, (224, 224))
        base[..., 2] = rng.integers(130, 200, (224, 224))
    elif category == "vegetation":
        # Green dominant
        base[..., 0] = rng.integers(20, 60, (224, 224))
        base[..., 1] = rng.integers(80, 150, (224, 224))
        base[..., 2] = rng.integers(20, 60, (224, 224))
    elif category == "urban":
        # Grey tones with variation
        g = rng.integers(100, 180, (224, 224))
        base[..., 0] = np.clip(g + rng.integers(-20, 20, (224, 224)), 0, 255)
        base[..., 1] = np.clip(g + rng.integers(-20, 20, (224, 224)), 0, 255)
        base[..., 2] = np.clip(g + rng.integers(-20, 20, (224, 224)), 0, 255)
    elif category == "bare_soil":
        # Brown / sandy
        base[..., 0] = rng.integers(130, 180, (224, 224))
        base[..., 1] = rng.integers(100, 140, (224, 224))
        base[..., 2] = rng.integers(60, 100, (224, 224))
    else:
        base = rng.integers(0, 255, (224, 224, 3), dtype=np.uint8)

    return base.astype(np.uint8)


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def run_smoke_test(embedder):
    CATEGORIES = {
        "water":      "water body or river",
        "vegetation": "dense forest or vegetation",
        "urban":      "urban area with buildings",
        "bare_soil":  "bare soil or agricultural fields",
    }

    QUERIES = [
        "water body or river",
        "dense forest or vegetation",
        "urban area with buildings",
        "bare soil or agricultural fields",
    ]

    print("\n" + "=" * 60)
    print("  Semantic Smoke Test (synthetic imagery)")
    print(f"  Model: {embedder.model_id} | is_mock={embedder.is_mock}")
    print("=" * 60)
    print("\nNOTE: Synthetic images are colorimetric approximations only.")
    print("      Real validation requires a labeled satellite dataset.\n")

    # Compute image embeddings
    cat_embeddings = {}
    for cat, _ in CATEGORIES.items():
        img = make_synthetic_category_image(cat)
        vec = embedder.encode_image(img)
        assert abs(np.linalg.norm(vec) - 1.0) < 0.01, "Image embedding not L2-normalised!"
        cat_embeddings[cat] = vec

    # Compute text embeddings
    query_embeddings = {}
    for q in QUERIES:
        vec = embedder.encode_text(q)
        assert abs(np.linalg.norm(vec) - 1.0) < 0.01, "Text embedding not L2-normalised!"
        query_embeddings[q] = vec

    # Similarity matrix
    print(f"{'Category':<22}  {'Best matching query':<40}  Score   Expected?")
    print("-" * 90)
    all_correct = True
    for cat, expected_query in CATEGORIES.items():
        img_vec = cat_embeddings[cat]
        scores = {q: cosine_sim(img_vec, query_embeddings[q]) for q in QUERIES}
        best_q = max(scores, key=scores.get)
        best_score = scores[best_q]
        correct = (best_q == expected_query)
        if not correct:
            all_correct = False
        status = "YES" if correct else "NO (plausibility check only)"
        print(f"  {cat:<20}  {best_q:<40}  {best_score:.4f}  {status}")

    print("\n[Determinism check] Running image embed twice, expecting identical output...")
    test_img = make_synthetic_category_image("water")
    v1 = embedder.encode_image(test_img)
    v2 = embedder.encode_image(test_img)
    max_diff = float(np.max(np.abs(v1 - v2)))
    print(f"  Max abs diff between runs: {max_diff:.2e}  "
          f"({'OK' if max_diff < 1e-5 else 'FAIL - non-deterministic!'})")

    print("\n[Summary]")
    if embedder.is_mock:
        print("  WARNING: MockEmbeddingProvider active — results are RANDOM.")
        print("  No semantic meaning. Switch to remoteclip for real evaluation.")
    else:
        if all_correct:
            print("  Semantic smoke test: PLAUSIBLE (all simple categories matched)")
        else:
            print("  Semantic smoke test: PARTIAL (some categories did not match)")
            print("  This may be expected — synthetic colorimetric images are not")
            print("  real satellite data. Evaluate with real imagery for conclusions.")
    print("=" * 60 + "\n")
    return all_correct


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()

    from terrae.app_factory import _load_config, build_embedding_provider
    cfg = _load_config(args.config)
    embedder = build_embedding_provider(cfg)
    run_smoke_test(embedder)


if __name__ == "__main__":
    main()
