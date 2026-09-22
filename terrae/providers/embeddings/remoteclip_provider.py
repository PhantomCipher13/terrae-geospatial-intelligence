"""
terrae/providers/embeddings/remoteclip_provider.py

RemoteCLIP ViT-B-32 embedding provider.

Source: https://huggingface.co/chendelong/RemoteCLIP
Paper:  Chen et al. "RemoteCLIP: A Vision-Language Foundation Model for Remote Sensing"
License: CC BY 4.0
Checkpoint: RemoteCLIP-ViT-B-32.pt (~605 MB)

LOADING STRATEGY (critical — prevents silent runtime downloads):
1. Create ViT-B-32 architecture with pretrained=None, load_weights=False
   → No network call, no OpenCLIP base weight download
2. torch.load() the local .pt checkpoint with map_location=device
3. Load state dict into the bare architecture
4. Call model.eval()

If the checkpoint file is missing: RAISE FileNotFoundError immediately.
NEVER fall back silently to mock embeddings — that would corrupt real pipelines.
Mock mode must be selected explicitly via config (embedding.provider: mock).
"""
from __future__ import annotations

import hashlib
import logging
import time
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

from terrae.providers.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

# Canonical variant registry
_VARIANTS: dict[str, dict] = {
    "ViT-B-32": {
        "hf_repo": "chendelong/RemoteCLIP",
        "filename": "RemoteCLIP-ViT-B-32.pt",
        "expected_dim": 512,
        "image_size": 224,
        "license": "CC BY 4.0",
    },
    "ViT-L-14": {
        "hf_repo": "chendelong/RemoteCLIP",
        "filename": "RemoteCLIP-ViT-L-14.pt",
        "expected_dim": 768,
        "image_size": 224,
        "license": "CC BY 4.0",
    },
    "ViT-H-14": {
        "hf_repo": "chendelong/RemoteCLIP",
        "filename": "RemoteCLIP-ViT-H-14.pt",
        "expected_dim": 1024,
        "image_size": 224,
        "license": "CC BY 4.0",
    },
}

# Default search directories (relative to cwd = project root)
_DEFAULT_SEARCH_DIRS: list[Path] = [
    Path("models") / "local",
    Path.home() / ".cache" / "terrae" / "models",
]


class RemoteCLIPProvider(EmbeddingProvider):
    """
    Real RemoteCLIP embedding provider. is_mock = False.

    Performs actual ViT-B-32 neural-network inference via open_clip.
    Requires locally staged checkpoint — no runtime network calls.

    Raises:
        FileNotFoundError: if checkpoint not found at expected paths.
        ImportError: if open_clip_torch not installed.
        RuntimeError: if checkpoint cannot be loaded or dim mismatch.
    """

    def __init__(
        self,
        model_name: str = "ViT-B-32",
        weights_path: Optional[Path] = None,
        device: str = "cpu",
    ) -> None:
        if model_name not in _VARIANTS:
            raise ValueError(
                f"Unknown RemoteCLIP variant '{model_name}'. "
                f"Valid options: {list(_VARIANTS)}"
            )

        self._variant = model_name
        self._variant_cfg = _VARIANTS[model_name]
        self._expected_dim: int = self._variant_cfg["expected_dim"]
        self._image_size: int = self._variant_cfg["image_size"]
        self._device_str = self._resolve_device(device)
        self._weights_path: Optional[Path] = None
        self._model = None
        self._preprocess = None
        self._tokenizer = None
        self._load_time_s: Optional[float] = None

        # Resolve and load
        resolved = self._find_weights(weights_path, model_name)
        self._weights_path = resolved
        self._load_checkpoint(resolved, model_name)

    # ------------------------------------------------------------------ #
    # EmbeddingProvider interface                                          #
    # ------------------------------------------------------------------ #

    @property
    def model_id(self) -> str:
        return f"RemoteCLIP-{self._variant}-v1"

    @property
    def model_version(self) -> str:
        return self._variant

    @property
    def embedding_dim(self) -> int:
        return self._expected_dim

    @property
    def is_mock(self) -> bool:
        return False

    @property
    def required_bands(self) -> Optional[List[str]]:
        """RemoteCLIP requires 3-channel RGB input in that order."""
        return ["Red", "Green", "Blue"]

    @property
    def required_image_size(self) -> Optional[Tuple[int, int]]:
        return (self._image_size, self._image_size)

    @property
    def device(self) -> str:
        return self._device_str

    @property
    def checkpoint_path(self) -> Optional[Path]:
        return self._weights_path

    @property
    def load_time_s(self) -> Optional[float]:
        return self._load_time_s

    # ------------------------------------------------------------------ #
    # Encoding                                                             #
    # ------------------------------------------------------------------ #

    def encode_image(self, image_array: np.ndarray) -> np.ndarray:
        """
        Encode an RGB image tile to a unit L2-normalised embedding.

        Args:
            image_array: float32 array (C, H, W) in [0,1] or (H, W, C) uint8.
                         Must have 3 channels (R, G, B in that order).

        Returns:
            float32 np.ndarray shape (512,), L2-normalised.
        """
        import torch
        from PIL import Image

        arr = image_array

        # Handle CHW → HWC
        if arr.ndim == 3 and arr.shape[0] == 3:
            arr = arr.transpose(1, 2, 0)  # (C,H,W) → (H,W,C)

        # Convert to uint8 [0,255] for PIL
        if arr.dtype != np.uint8:
            if arr.max() <= 1.0 + 1e-6:
                arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
            else:
                arr = np.clip(arr, 0, 255).astype(np.uint8)

        if arr.ndim != 3 or arr.shape[2] != 3:
            raise ValueError(
                f"encode_image expects 3-channel RGB array, got shape {image_array.shape}"
            )

        pil_img = Image.fromarray(arr, mode="RGB")
        tensor = self._preprocess(pil_img).unsqueeze(0)

        if self._device_str != "cpu":
            tensor = tensor.to(self._device_str)

        with torch.no_grad():
            features = self._model.encode_image(tensor)
            norm = features.norm(dim=-1, keepdim=True).clamp(min=1e-12)
            features = features / norm

        vec = features.squeeze(0).cpu().numpy().astype(np.float32)
        assert vec.shape == (self._expected_dim,), (
            f"Unexpected embedding dim {vec.shape}, expected ({self._expected_dim},)"
        )
        return vec

    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode a text query to a unit L2-normalised embedding.

        Args:
            text: Query string (English).

        Returns:
            float32 np.ndarray shape (512,), L2-normalised.
        """
        import torch

        tokens = self._tokenizer([text])
        if self._device_str != "cpu":
            tokens = tokens.to(self._device_str)

        with torch.no_grad():
            features = self._model.encode_text(tokens)
            norm = features.norm(dim=-1, keepdim=True).clamp(min=1e-12)
            features = features / norm

        vec = features.squeeze(0).cpu().numpy().astype(np.float32)
        assert vec.shape == (self._expected_dim,), (
            f"Unexpected text embedding dim {vec.shape}"
        )
        return vec

    def encode_batch_images(self, images: List[np.ndarray]) -> np.ndarray:
        """Batch encode for efficiency — reduces per-image Python overhead."""
        import torch
        from PIL import Image

        tensors = []
        for img in images:
            arr = img
            if arr.ndim == 3 and arr.shape[0] == 3:
                arr = arr.transpose(1, 2, 0)
            if arr.dtype != np.uint8:
                arr = np.clip(arr * 255.0 if arr.max() <= 1.0 + 1e-6 else arr, 0, 255).astype(np.uint8)
            pil = Image.fromarray(arr, mode="RGB")
            tensors.append(self._preprocess(pil))

        batch = torch.stack(tensors, dim=0)
        if self._device_str != "cpu":
            batch = batch.to(self._device_str)

        with torch.no_grad():
            features = self._model.encode_image(batch)
            norm = features.norm(dim=-1, keepdim=True).clamp(min=1e-12)
            features = features / norm

        return features.cpu().numpy().astype(np.float32)

    # ------------------------------------------------------------------ #
    # Internal loading                                                     #
    # ------------------------------------------------------------------ #

    def _find_weights(self, weights_path: Optional[Path], model_name: str) -> Path:
        """Locate checkpoint file. FAIL if not found — never download at runtime."""
        filename = self._variant_cfg["filename"]

        if weights_path is not None:
            p = Path(weights_path)
            if not p.exists():
                raise FileNotFoundError(
                    f"RemoteCLIP checkpoint not found at specified path: '{p}'\n"
                    f"Stage it with: python scripts/download_models.py --model remoteclip-vitb32"
                )
            return p

        for d in _DEFAULT_SEARCH_DIRS:
            candidate = d / filename
            if candidate.exists():
                logger.info(f"Found RemoteCLIP weights at: {candidate}")
                return candidate

        searched = [str(d / filename) for d in _DEFAULT_SEARCH_DIRS]
        raise FileNotFoundError(
            f"RemoteCLIP checkpoint '{filename}' not found.\n"
            f"Searched:\n" + "\n".join(f"  {p}" for p in searched) + "\n"
            f"Stage it with:\n"
            f"  python scripts/download_models.py --model remoteclip-vitb32\n"
            f"To use random mock embeddings instead, set:\n"
            f"  embedding.provider: mock  (in configs/config.yaml)"
        )

    def _load_checkpoint(self, weights_path: Path, model_name: str) -> None:
        """
        Load RemoteCLIP weights without any network access.

        Strategy:
          1. open_clip.create_model_and_transforms(pretrained=None, load_weights=False)
             → builds ViT-B-32 architecture from scratch, NO download
          2. torch.load(weights_path, map_location=device)
             → loads the .pt checkpoint from local disk
          3. model.load_state_dict(checkpoint)
             → injects weights into the bare architecture
        """
        try:
            import open_clip
        except ImportError:
            raise ImportError(
                "open_clip_torch is required for RemoteCLIPProvider.\n"
                "Install: C:\\Python311\\python.exe -m pip install open-clip-torch"
            )
        import torch

        t0 = time.time()
        logger.info(f"Creating ViT-B-32 architecture (no download)...")
        model, _, preprocess = open_clip.create_model_and_transforms(
            model_name,
            pretrained=None,
            load_weights=False,
            device=self._device_str,
        )
        logger.info(f"Architecture created. Loading checkpoint from {weights_path} ...")

        # Load checkpoint — handles both raw state_dict and wrapped checkpoints
        ckpt = torch.load(str(weights_path), map_location=self._device_str, weights_only=False)

        # RemoteCLIP .pt files may be wrapped under 'state_dict' key
        if isinstance(ckpt, dict):
            state_dict = ckpt.get("state_dict", ckpt.get("model", ckpt))
        else:
            state_dict = ckpt

        # Strip 'module.' prefix if checkpoint was saved from DataParallel
        cleaned = {}
        for k, v in state_dict.items():
            cleaned[k.replace("module.", "", 1)] = v

        missing, unexpected = model.load_state_dict(cleaned, strict=False)
        if missing:
            logger.warning(f"Missing keys in checkpoint ({len(missing)}): {missing[:5]}")
        if unexpected:
            logger.warning(f"Unexpected keys in checkpoint ({len(unexpected)}): {unexpected[:5]}")

        model.eval()
        self._model = model
        self._preprocess = preprocess
        self._tokenizer = open_clip.get_tokenizer(model_name)
        self._load_time_s = time.time() - t0

        # Verify embedding dimension with a tiny forward pass
        self._verify_dim()
        logger.info(
            f"RemoteCLIP {model_name} loaded in {self._load_time_s:.2f}s. "
            f"Device: {self._device_str}. Dim: {self._expected_dim}."
        )

    def _verify_dim(self) -> None:
        """Run a tiny forward pass to confirm embedding dimension."""
        import torch
        dummy = torch.zeros(1, 3, self._image_size, self._image_size, device=self._device_str)
        with torch.no_grad():
            out = self._model.encode_image(dummy)
        actual_dim = out.shape[-1]
        if actual_dim != self._expected_dim:
            raise RuntimeError(
                f"RemoteCLIP checkpoint dimension mismatch: "
                f"expected {self._expected_dim}, got {actual_dim}. "
                f"Wrong checkpoint file?"
            )

    @staticmethod
    def _resolve_device(device: str) -> str:
        if device == "auto":
            import torch
            if torch.cuda.is_available():
                return "cuda"
            try:
                import torch_directml
                return "privateuseone"  # DirectML device
            except ImportError:
                pass
            return "cpu"
        return device

    # ------------------------------------------------------------------ #
    # Provenance helpers                                                   #
    # ------------------------------------------------------------------ #

    def checkpoint_sha256(self) -> str:
        """Compute SHA-256 of the checkpoint file (for provenance records)."""
        if self._weights_path is None:
            return "unknown"
        h = hashlib.sha256()
        with open(self._weights_path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
