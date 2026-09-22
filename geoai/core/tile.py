"""
geoai/core/tile.py
Internal representation of a raster tile extracted from a scene.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple
from pathlib import Path
import numpy as np


@dataclass
class TileRecord:
    """
    A tile extracted from a raster scene.
    The array is NOT stored here (memory) — only metadata + path to array on disk.
    """
    tile_id: str                                    # UUID — stable identifier
    scene_id: str                                   # Parent scene UUID
    source_path: Path                               # Originating GeoTIFF path
    tile_row: int                                   # Grid row (0-based)
    tile_col: int                                   # Grid column (0-based)
    pixel_window: Tuple[int, int, int, int]         # (col_off, row_off, width, height)
    bounds_native: Optional[Tuple[float, float, float, float]] = None  # (W,S,E,N) native CRS
    bounds_wgs84: Optional[Tuple[float, float, float, float]] = None   # (W,S,E,N) WGS84
    crs_epsg: Optional[int] = None
    band_count: Optional[int] = None
    dtype: Optional[str] = None
    nodata_fraction: Optional[float] = None         # Fraction of nodata pixels in tile
    is_empty: bool = False                          # True if >nodata_threshold fraction
    array_path: Optional[Path] = None              # Path to saved .npy file (if cached)
    acquisition_date: Optional[str] = None         # ISO date string from parent scene
    sensor: Optional[str] = None
    sensor_type: Optional[str] = None              # 'optical', 'sar', 'unknown'


@dataclass
class EmbeddedTile(TileRecord):
    """A TileRecord that has been embedded."""
    embedding: Optional[np.ndarray] = None         # shape (dim,) float32
    embedding_model: Optional[str] = None
    embedding_version: Optional[str] = None
    preprocessing_version: Optional[str] = None
