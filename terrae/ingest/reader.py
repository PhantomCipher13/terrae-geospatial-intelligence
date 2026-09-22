"""
terrae/ingest/reader.py
Raster metadata reader using rasterio.
Extracts ALL available metadata. Missing fields -> None, never fabricated.
"""
from __future__ import annotations
import datetime
import hashlib
import logging
import re
from pathlib import Path
from typing import Optional

from terrae.core.raster_metadata import RasterMetadata, BandInfo

logger = logging.getLogger(__name__)

# Date patterns to try against raster tags
_DATE_PATTERNS = [
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})",  # ISO datetime
    r"(\d{4}-\d{2}-\d{2})",                        # ISO date
    r"(\d{8})",                                     # YYYYMMDD compact
]


def _parse_date_from_tags(tags: dict) -> tuple[Optional[datetime.date], Optional[datetime.datetime]]:
    """Try to parse acquisition date from GDAL tags dictionary."""
    date_keys = [
        "ACQUISITION_DATE","DATE_ACQUIRED","SCENE_CENTER_TIME",
        "PRODUCT_START_TIME","TIFFTAG_DATETIME","datetime",
        "date","SENSING_TIME","START_TIME",
    ]
    for key in date_keys:
        val = tags.get(key) or tags.get(key.lower())
        if not val:
            continue
        val = str(val)
        for pat in _DATE_PATTERNS:
            m = re.search(pat, val)
            if m:
                raw = m.group(1)
                try:
                    if "T" in raw:
                        dt = datetime.datetime.fromisoformat(raw)
                        return dt.date(), dt
                    elif len(raw) == 10:
                        d = datetime.date.fromisoformat(raw)
                        return d, None
                    elif len(raw) == 8:
                        d = datetime.date(int(raw[:4]), int(raw[4:6]), int(raw[6:8]))
                        return d, None
                except ValueError:
                    continue
    return None, None


def _detect_sensor_from_tags(tags: dict, path: Path) -> tuple[Optional[str], Optional[str]]:
    """Try to infer sensor name and type from GDAL tags + filename."""
    sensor_keys = ["SPACECRAFT_ID","SATELLITE","PLATFORM","SENSOR","MISSION","SENSOR_ID"]
    sensor_name = None
    for key in sensor_keys:
        val = tags.get(key) or tags.get(key.lower())
        if val:
            sensor_name = str(val).strip()
            break

    # Try filename
    if sensor_name is None:
        fn = path.name.lower()
        if "s2" in fn or "sentinel2" in fn or "sentinel-2" in fn:
            sensor_name = "Sentinel-2"
        elif "s1" in fn or "sentinel1" in fn or "sentinel-1" in fn:
            sensor_name = "Sentinel-1"
        elif "lc08" in fn or "lc09" in fn or "landsat" in fn:
            sensor_name = "Landsat"
        elif "lc2" in fn or "lc02" in fn:
            sensor_name = "Landsat"

    # Determine type from name
    sensor_type = None
    if sensor_name:
        sn = sensor_name.lower()
        if any(k in sn for k in ("sentinel-1","s1","sar","slc","grd","ers","palsar","alos")):
            sensor_type = "sar"
        elif any(k in sn for k in ("sentinel-2","landsat","modis","spot","planet","pleiades","worldview")):
            sensor_type = "optical"

    return sensor_name, sensor_type


def _hash_file(path: Path, chunk: int = 1 << 20) -> str:
    """SHA-256 of first 4MB of file (fast partial hash for large rasters)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        data = f.read(4 * chunk)
        h.update(data)
    return h.hexdigest()


def read_metadata(path: Path) -> RasterMetadata:
    """
    Open a GeoTIFF/COG and extract all available metadata.
    Missing fields are None — never fabricated.
    Raises: FileNotFoundError, rasterio.errors.RasterioError on invalid files.
    """
    try:
        import rasterio
        from rasterio.crs import CRS
    except ImportError:
        raise ImportError("rasterio is required: pip install rasterio")

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Raster file not found: {path}")

    meta = RasterMetadata(source_path=path)

    # --- File hash (partial) ---
    try:
        meta.file_hash_sha256 = _hash_file(path)
    except Exception as e:
        logger.warning(f"Could not hash file {path}: {e}")

    with rasterio.open(path) as ds:
        # --- Dimensions ---
        meta.width_px = ds.width
        meta.height_px = ds.height
        meta.band_count = ds.count
        meta.dtype = str(ds.dtypes[0]) if ds.dtypes else None
        meta.nodata = ds.nodata

        # --- Spatial reference ---
        if ds.crs is not None:
            meta.crs_wkt = ds.crs.wkt
            try:
                meta.crs_epsg = ds.crs.to_epsg()
            except Exception:
                meta.crs_epsg = None
        else:
            logger.warning(f"No CRS found in {path.name}")

        # --- Affine transform ---
        if ds.transform is not None:
            t = ds.transform
            meta.affine_transform = (t.a, t.b, t.c, t.d, t.e, t.f)
            meta.res_x = abs(t.a)
            meta.res_y = abs(t.e)

        # --- Bounds ---
        if ds.bounds is not None and ds.crs is not None:
            b = ds.bounds
            meta.bounds_native = (b.left, b.bottom, b.right, b.top)
            # Attempt WGS84 transform
            try:
                from rasterio.warp import transform_bounds
                wgs84 = transform_bounds(
                    ds.crs, "EPSG:4326",
                    b.left, b.bottom, b.right, b.top
                )
                meta.bounds_wgs84 = wgs84
            except Exception as e:
                logger.warning(f"Could not reproject bounds to WGS84: {e}")

        # --- Per-band metadata ---
        tags_all = {**ds.tags()}
        for i in range(1, ds.count + 1):
            btags = ds.tags(i)
            bname = btags.get("name") or ds.descriptions[i-1] if ds.descriptions else None
            band = BandInfo(
                index=i,
                name=bname,
                description=ds.descriptions[i-1] if ds.descriptions else None,
                nodata=ds.nodatavals[i-1] if ds.nodatavals else None,
                dtype=str(ds.dtypes[i-1]),
            )
            meta.bands.append(band)
            tags_all.update({f"band{i}_{k}": v for k, v in btags.items()})

        meta.tags = tags_all

        # --- Temporal ---
        meta.acquisition_date, meta.acquisition_datetime = _parse_date_from_tags(tags_all)

        # --- Sensor ---
        meta.sensor, meta.sensor_type = _detect_sensor_from_tags(tags_all, path)

    # --- Metadata completeness score ---
    missing = meta.missing_fields()
    key_count = 8   # matches missing_fields() list length
    meta.metadata_completeness = (key_count - len(missing)) / key_count

    logger.info(meta.summary())
    return meta
