"""
terrae/ingest/pipeline.py
Full ingest pipeline: GeoTIFF -> tiles -> embeddings -> FAISS index -> SQLite DB.

Design rules:
- Duplicate scenes (same file hash) are detected and skipped.
- Empty tiles (nodata > threshold) are stored in DB but NOT indexed in FAISS.
- All components injected via constructor — no hardcoded models or paths.
- No network calls.
"""
from __future__ import annotations
import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import numpy as np

from terrae.core.raster_metadata import RasterMetadata
from terrae.core.result import QualityStatus
from terrae.db.metadata_db import MetadataDB
from terrae.ingest.reader import read_metadata
from terrae.ingest.tiler import generate_tiles
from terrae.ingest.validator import validate_raster
from terrae.providers.embeddings.base import EmbeddingProvider
from terrae.providers.index.base import IndexBackend
from terrae.providers.quality.base import QualityAssessor
from terrae.providers.sensors.base import SensorAdapter, BandCompatibilityError
from terrae.providers.sensors.registry import get_adapter

logger = logging.getLogger(__name__)


@dataclass
class IngestReport:
    """Result summary of a single scene ingest."""
    scene_id: str
    source_path: str
    success: bool
    skipped: bool = False
    skip_reason: Optional[str] = None
    tiles_generated: int = 0
    tiles_indexed: int = 0
    tiles_skipped_empty: int = 0
    tiles_skipped_quality: int = 0
    tiles_failed: int = 0
    elapsed_s: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata_summary: Optional[str] = None


class IngestPipeline:
    """
    Orchestrates the full ingest flow.
    Injected dependencies — never imports concrete models internally.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        index_backend: IndexBackend,
        metadata_db: MetadataDB,
        quality_assessor: Optional[QualityAssessor] = None,
        tile_size: int = 256,
        tile_overlap: int = 0,
        nodata_threshold: float = 0.9,
        quality_fail_action: str = "skip",  # 'skip' | 'warn_and_index'
    ) -> None:
        self._embedder = embedding_provider
        self._index = index_backend
        self._db = metadata_db
        self._quality = quality_assessor
        self._tile_size = tile_size
        self._tile_overlap = tile_overlap
        self._nodata_threshold = nodata_threshold
        self._quality_fail_action = quality_fail_action

        if embedding_provider.is_mock:
            logger.warning(
                "⚠️  IngestPipeline: MockEmbeddingProvider active. "
                "Indexed embeddings are RANDOM and have no retrieval meaning."
            )

    def ingest(self, path: Path) -> IngestReport:
        """
        Ingest a single GeoTIFF/COG file.
        Returns IngestReport with full accounting of what happened.
        """
        path = Path(path)
        t0 = time.time()
        report = IngestReport(
            scene_id="",
            source_path=str(path),
            success=False,
        )

        # Step 1: Validate
        is_valid, validation_errors = validate_raster(path)
        for e in validation_errors:
            if e.startswith("ERROR"):
                report.errors.append(e)
            else:
                report.warnings.append(e)
        if not is_valid:
            report.elapsed_s = time.time() - t0
            return report

        # Step 2: Read metadata
        try:
            metadata = read_metadata(path)
        except Exception as e:
            report.errors.append(f"Metadata read failed: {e}")
            report.elapsed_s = time.time() - t0
            return report

        report.metadata_summary = metadata.summary()

        # Step 3: Duplicate detection
        if metadata.file_hash_sha256:
            existing_scene_id = self._db.scene_exists(metadata.file_hash_sha256)
            if existing_scene_id:
                report.skipped = True
                report.skip_reason = f"Duplicate: file already ingested as scene_id={existing_scene_id}"
                report.scene_id = existing_scene_id
                report.success = True
                report.elapsed_s = time.time() - t0
                logger.info(f"Skipping duplicate: {path.name} (scene_id={existing_scene_id})")
                return report

        # Step 4: Scene record
        scene_id = str(uuid.uuid4())
        report.scene_id = scene_id
        self._db.insert_scene(scene_id, {
            "source_path": str(path),
            "file_hash": metadata.file_hash_sha256,
            "band_count": metadata.band_count,
            "dtype": metadata.dtype,
            "width_px": metadata.width_px,
            "height_px": metadata.height_px,
            "crs_epsg": metadata.crs_epsg,
            "bounds_wgs84": list(metadata.bounds_wgs84) if metadata.bounds_wgs84 else None,
            "acquisition_date": metadata.acquisition_date.isoformat() if metadata.acquisition_date else None,
            "sensor": metadata.sensor,
            "sensor_type": metadata.sensor_type,
            "processing_level": metadata.processing_level,
            "metadata_completeness": metadata.metadata_completeness,
            "tags": metadata.tags,
        })

        # Step 5: Get sensor adapter
        adapter: SensorAdapter = get_adapter(metadata)
        band_names = [b.name for b in metadata.bands] if metadata.bands else None

        # Step 6: Tile, embed, index
        tile_batch_db = []
        tile_batch_ids = []
        tile_batch_vecs = []

        for tile_record, raw_array in generate_tiles(
            metadata=metadata,
            tile_size=self._tile_size,
            overlap=self._tile_overlap,
            nodata_threshold=self._nodata_threshold,
            scene_id=scene_id,
        ):
            report.tiles_generated += 1

            tile_dict = {
                "tile_id": tile_record.tile_id,
                "scene_id": tile_record.scene_id,
                "tile_row": tile_record.tile_row,
                "tile_col": tile_record.tile_col,
                "pixel_window": list(tile_record.pixel_window),
                "bounds_wgs84": list(tile_record.bounds_wgs84) if tile_record.bounds_wgs84 else None,
                "crs_epsg": tile_record.crs_epsg,
                "band_count": tile_record.band_count,
                "dtype": tile_record.dtype,
                "nodata_fraction": tile_record.nodata_fraction,
                "is_empty": tile_record.is_empty,
                "acquisition_date": tile_record.acquisition_date,
                "sensor": tile_record.sensor,
                "sensor_type": tile_record.sensor_type,
            }
            tile_batch_db.append(tile_dict)

            if tile_record.is_empty:
                report.tiles_skipped_empty += 1
                continue

            # Quality gate
            if self._quality is not None:
                qr = self._quality.assess(
                    raw_array, metadata, nodata_value=metadata.nodata
                )
                if qr.status == QualityStatus.FAIL:
                    if self._quality_fail_action == "skip":
                        report.tiles_skipped_quality += 1
                        continue
                    else:
                        report.warnings.append(
                            f"Tile {tile_record.tile_id} quality FAIL — indexed anyway (warn_and_index mode)"
                        )

            # Preprocess for embedding
            try:
                required_bands = self._embedder.required_bands
                preprocessed = adapter.preprocess_for_embedding(
                    raw_array, band_names=band_names, required_bands=required_bands
                )
            except BandCompatibilityError as e:
                report.tiles_failed += 1
                report.warnings.append(f"Band compatibility error (tile {tile_record.tile_id}): {e}")
                continue
            except Exception as e:
                report.tiles_failed += 1
                report.warnings.append(f"Preprocessing failed (tile {tile_record.tile_id}): {e}")
                continue

            # Resize to model expected size if needed
            expected_size = self._embedder.required_image_size
            if expected_size is not None:
                preprocessed = self._resize_for_model(preprocessed, expected_size)

            # Generate embedding
            try:
                vec = self._embedder.encode_image(preprocessed)
            except Exception as e:
                report.tiles_failed += 1
                report.warnings.append(f"Embedding failed (tile {tile_record.tile_id}): {e}")
                continue

            tile_batch_ids.append(tile_record.tile_id)
            tile_batch_vecs.append(vec)

        # Flush tile records to DB
        if tile_batch_db:
            self._db.insert_tiles_batch(tile_batch_db)

        # Batch-add to FAISS index
        if tile_batch_ids:
            vecs_array = np.stack(tile_batch_vecs, axis=0)
            try:
                self._index.add_batch(tile_batch_ids, vecs_array)
                report.tiles_indexed = len(tile_batch_ids)
            except Exception as e:
                report.errors.append(f"FAISS batch add failed: {e}")

            # Record embedding metadata
            for tid in tile_batch_ids:
                self._db.insert_embedding(tid, {
                    "embedding_model": self._embedder.model_id,
                    "embedding_dim": self._embedder.embedding_dim,
                    "is_mock": self._embedder.is_mock,
                    "index_backend": self._index.index_id,
                })

        report.success = True
        report.elapsed_s = time.time() - t0
        logger.info(
            f"Ingest complete: {path.name} | "
            f"tiles={report.tiles_generated} | "
            f"indexed={report.tiles_indexed} | "
            f"empty_skipped={report.tiles_skipped_empty} | "
            f"quality_skipped={report.tiles_skipped_quality} | "
            f"failed={report.tiles_failed} | "
            f"time={report.elapsed_s:.1f}s"
        )
        return report

    @staticmethod
    def _resize_for_model(array: np.ndarray, size: tuple) -> np.ndarray:
        """Resize (C, H, W) to (C, size[0], size[1]) using PIL."""
        import PIL.Image
        target_h, target_w = size
        C = array.shape[0]
        channels = []
        for c in range(C):
            band = array[c]
            pil = PIL.Image.fromarray((band * 255).clip(0, 255).astype(np.uint8))
            pil = pil.resize((target_w, target_h), PIL.Image.BILINEAR)
            channels.append(np.array(pil).astype(np.float32) / 255.0)
        return np.stack(channels, axis=0)
