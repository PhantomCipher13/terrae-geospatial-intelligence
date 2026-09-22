"""
scripts/download_models.py
One-time model weight staging script.
Run BEFORE going offline. Requires network access.

Usage:
    C:\Python311\python.exe scripts\download_models.py --model remoteclip-vitb32
    C:\Python311\python.exe scripts\download_models.py --model all
"""
import argparse
import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

MODELS = {
    "remoteclip-vitb32": {
        "repo_id": "chendelong/RemoteCLIP",
        "filename": "RemoteCLIP-ViT-B-32.pt",
        "license": "CC BY 4.0",
        "source": "https://huggingface.co/chendelong/RemoteCLIP",
        "approx_size_mb": 605,
    },
    "remoteclip-vitl14": {
        "repo_id": "chendelong/RemoteCLIP",
        "filename": "RemoteCLIP-ViT-L-14.pt",
        "license": "CC BY 4.0",
        "source": "https://huggingface.co/chendelong/RemoteCLIP",
        "approx_size_mb": 890,
    },
}


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def download_model(model_key: str, output_dir: Path) -> Path:
    cfg = MODELS[model_key]
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / cfg["filename"]

    if dest.exists():
        size_mb = dest.stat().st_size / (1024 ** 2)
        print(f"[EXISTS] {dest} ({size_mb:.1f} MB) - skipping download")
        sha = sha256_file(dest)
        print(f"  SHA-256: {sha}")
        return dest

    print(f"[DOWNLOAD] {cfg['filename']} from {cfg['repo_id']}")
    print(f"  License: {cfg['license']}")
    print(f"  Approx size: {cfg['approx_size_mb']} MB")
    print(f"  Destination: {dest}")

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("ERROR: huggingface_hub not installed.")
        sys.exit(1)

    import time
    t0 = time.time()
    path = hf_hub_download(
        repo_id=cfg["repo_id"],
        filename=cfg["filename"],
        local_dir=str(output_dir),
        force_download=False,
    )
    elapsed = time.time() - t0
    size_mb = Path(path).stat().st_size / (1024 ** 2)
    sha = sha256_file(Path(path))

    print(f"\n[OK] Downloaded in {elapsed:.1f}s")
    print(f"  Path:    {path}")
    print(f"  Size:    {size_mb:.1f} MB")
    print(f"  SHA-256: {sha}")
    print(f"  License: {cfg['license']}")
    print(f"  Source:  {cfg['source']}")

    # Write provenance record
    import json, datetime
    record = {
        "model_key": model_key,
        "repo_id": cfg["repo_id"],
        "filename": cfg["filename"],
        "local_path": str(path),
        "size_bytes": Path(path).stat().st_size,
        "sha256": sha,
        "license": cfg["license"],
        "source": cfg["source"],
        "download_date": datetime.datetime.utcnow().isoformat() + "Z",
    }
    prov_path = output_dir / f"{cfg['filename']}.provenance.json"
    with open(prov_path, "w") as f:
        json.dump(record, f, indent=2)
    print(f"  Provenance: {prov_path}")
    return Path(path)


def main():
    parser = argparse.ArgumentParser(description="Download and stage model weights offline.")
    parser.add_argument("--model", required=True,
                        choices=list(MODELS) + ["all"],
                        help="Model key to download, or 'all'")
    parser.add_argument("--output-dir", default="models/local",
                        help="Local directory to store weights.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    keys = list(MODELS) if args.model == "all" else [args.model]
    for k in keys:
        download_model(k, output_dir)


if __name__ == "__main__":
    main()
