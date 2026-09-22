"""
terrae/core/raster_metadata.py
Normalized internal representation of raster metadata.
Never fabricate missing values — use None/unknown explicitly.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path
import datetime


@dataclass
class BandInfo:
    """Metadata for a single raster band."""
    index: int                          # 1-based (rasterio convention)
    name: Optional[str] = None          # e.g. 'B04', 'Red', 'VV'
    description: Optional[str] = None
    nodata: Optional[float] = None
    dtype: Optional[str] = None         # e.g. 'uint16', 'float32'
    units: Optional[str] = None         # e.g. 'reflectance', 'dB'
    wavelength_nm: Optional[float] = None  # centre wavelength if known


@dataclass
class RasterMetadata:
    """
    Canonical internal representation of raster metadata.
    All optional fields use None when unknown — never fabricated.
    """
    # --- Identity ---
    source_path: Path
    file_hash_sha256: Optional[str] = None   # populated during ingest

    # --- Spatial ---
    crs_wkt: Optional[str] = None            # WKT string of CRS
    crs_epsg: Optional[int] = None           # EPSG code if determinable
    affine_transform: Optional[Tuple[float, ...]] = None  # (a,b,c,d,e,f) row-major
    bounds_native: Optional[Tuple[float, float, float, float]] = None  # (W,S,E,N) native CRS
    bounds_wgs84: Optional[Tuple[float, float, float, float]] = None   # (W,S,E,N) EPSG:4326
    width_px: Optional[int] = None
    height_px: Optional[int] = None
    res_x: Optional[float] = None            # pixel width in native CRS units
    res_y: Optional[float] = None            # pixel height in native CRS units (positive)

    # --- Bands ---
    band_count: Optional[int] = None
    dtype: Optional[str] = None              # dominant dtype
    nodata: Optional[float] = None           # global nodata
    bands: List[BandInfo] = field(default_factory=list)

    # --- Temporal ---
    acquisition_date: Optional[datetime.date] = None
    acquisition_datetime: Optional[datetime.datetime] = None

    # --- Sensor / Platform ---
    sensor: Optional[str] = None            # e.g. 'Sentinel-2A', 'Landsat-8'
    platform: Optional[str] = None          # e.g. 'ESA', 'USGS'
    sensor_type: Optional[str] = None       # 'optical', 'sar', 'hyperspectral', 'unknown'
    processing_level: Optional[str] = None  # e.g. 'L2A', 'L1C'

    # --- Quality indicators (populated by QualityAssessor) ---
    nodata_fraction: Optional[float] = None
    metadata_completeness: Optional[float] = None  # 0.0–1.0 fraction of key fields present

    # --- Extra tags from GDAL/rasterio ---
    tags: Dict[str, Any] = field(default_factory=dict)

    def missing_fields(self) -> List[str]:
        """Return list of key fields that are None."""
        key_fields = [
            'crs_wkt', 'affine_transform', 'bounds_native',
            'width_px', 'height_px', 'band_count', 'acquisition_date', 'sensor',
        ]
        return [f for f in key_fields if getattr(self, f) is None]

    def has_spatial_ref(self) -> bool:
        return self.crs_wkt is not None and self.affine_transform is not None

    def has_temporal_info(self) -> bool:
        return self.acquisition_date is not None or self.acquisition_datetime is not None

    def summary(self) -> str:
        missing = self.missing_fields()
        return (
            f"RasterMetadata({self.source_path.name} | "
            f"bands={self.band_count} | dtype={self.dtype} | "
            f"size={self.width_px}x{self.height_px} | "
            f"crs={'YES' if self.crs_wkt else 'MISSING'} | "
            f"date={'YES' if self.has_temporal_info() else 'MISSING'} | "
            f"sensor={self.sensor or 'UNKNOWN'} | "
            f"missing_fields={missing})"
        )
