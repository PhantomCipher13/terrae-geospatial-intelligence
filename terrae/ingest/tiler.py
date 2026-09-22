"""
terrae/ingest/tiler.py
Memory-safe windowed tile extractor using rasterio.

Design:
- Uses rasterio windowed reads — never loads full raster into RAM.
- Skips tiles where nodata fraction exceeds threshold.
- Returns TileRecord objects (no array stored in memory after yield).
- Caller is responsible for what to do with each yielded tile.
"""
from __future__ import annotations
import logging
import uuid
from pathlib import Path
from typing import Iterator, Optional, Tuple
import numpy as np

from terrae.core.raster_metadata import RasterMetadata
from terrae.core.tile import TileRecord

logger = logging.getLogger(__name__)


def generate_tiles(
    metadata: RasterMetadata,
    tile_size: int = 256,
    overlap: int = 0,
    nodata_threshold: float = 0.9,
    scene_id: Optional[str] = None,
) -> Iterator[Tuple[TileRecord, np.ndarray]]:
    """
    Generate tiles from a raster using memory-safe windowed reads.

    Yields (TileRecord, array) pairs where:
    - array is float32 (C, H, W) raw raster data (NOT normalised — adapter handles that)
    - TileRecord.is_empty == True if nodata fraction > nodata_threshold (array still yielded)

    Args:
        metadata: RasterMetadata for the source file.
        tile_size: Square tile side length in pixels.
        overlap: Pixel overlap between adjacent tiles (0 = no overlap).
        nodata_threshold: Tiles with nodata_fraction > this are marked is_empty.
        scene_id: Parent scene UUID. Auto-generated if None.
    """
    try:
        import rasterio
        from rasterio.windows import Window
    except ImportError:
        raise ImportError("rasterio is required: pip install rasterio")

    if scene_id is None:
        scene_id = str(uuid.uuid4())

    path = metadata.source_path
    stride = tile_size - overlap

    with rasterio.open(path) as ds:
        W, H = ds.width, ds.height
        nodata = ds.nodata

        row_idx = 0
        for row_off in range(0, H, stride):
            col_idx = 0
            for col_off in range(0, W, stride):
                # Actual tile dimensions (may be smaller at edges)
                actual_w = min(tile_size, W - col_off)
                actual_h = min(tile_size, H - row_off)
                if actual_w <= 0 or actual_h <= 0:
                    col_idx += 1
                    continue

                window = Window(col_off, row_off, actual_w, actual_h)
                tile_id = str(uuid.uuid4())

                # Read all bands
                try:
                    arr = ds.read(window=window).astype(np.float32)  # (C, h, w)
                except Exception as e:
                    logger.warning(f"Failed to read window {window} from {path.name}: {e}")
                    col_idx += 1
                    continue

                # Compute nodata fraction
                nodata_fraction: Optional[float] = None
                if nodata is not None:
                    nodata_fraction = float(np.mean(arr == nodata))
                elif np.isnan(arr).any():
                    nodata_fraction = float(np.mean(np.isnan(arr)))
                is_empty = (nodata_fraction is not None and nodata_fraction > nodata_threshold)

                # Compute tile geographic bounds
                bounds_native = None
                bounds_wgs84 = None
                if ds.transform is not None:
                    from rasterio.windows import bounds as window_bounds
                    wb = window_bounds(window, ds.transform)
                    # rasterio 1.4: bounds() returns plain tuple (left, bottom, right, top)
                    left, bottom, right, top = wb[0], wb[1], wb[2], wb[3]
                    bounds_native = (left, bottom, right, top)
                    if ds.crs is not None:
                        try:
                            from rasterio.warp import transform_bounds
                            bounds_wgs84 = transform_bounds(
                                ds.crs, "EPSG:4326",
                                left, bottom, right, top
                            )
                        except Exception:
                            pass

                acq_date_str = None
                if metadata.acquisition_date is not None:
                    acq_date_str = metadata.acquisition_date.isoformat()
                elif metadata.acquisition_datetime is not None:
                    acq_date_str = metadata.acquisition_datetime.date().isoformat()

                record = TileRecord(
                    tile_id=tile_id,
                    scene_id=scene_id,
                    source_path=path,
                    tile_row=row_idx,
                    tile_col=col_idx,
                    pixel_window=(col_off, row_off, actual_w, actual_h),
                    bounds_native=bounds_native,
                    bounds_wgs84=bounds_wgs84,
                    crs_epsg=metadata.crs_epsg,
                    band_count=ds.count,
                    dtype=str(arr.dtype),
                    nodata_fraction=nodata_fraction,
                    is_empty=is_empty,
                    acquisition_date=acq_date_str,
                    sensor=metadata.sensor,
                    sensor_type=metadata.sensor_type,
                )
                yield record, arr
                col_idx += 1
            row_idx += 1
