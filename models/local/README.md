# Model Weights Directory

This directory stores offline Foundation Model weights.
Per GitHub guidelines, large binary model files (>100 MB) are not tracked in git.

## Download Weights
To download and verify RemoteCLIP weights:

```powershell
python scripts/download_models.py --model remoteclip-vitb32
```

The script automatically downloads `RemoteCLIP-ViT-B-32.pt` (approx 605 MB) from Hugging Face (`chendelong/RemoteCLIP`), verifies its SHA-256 hash (`60014e39...`), and generates the provenance record.

## Mock / Fallback Mode
If weights are not present, the system automatically falls back to `MockEmbeddingProvider` for testing and deterministic validation.
