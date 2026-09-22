"""
geoai/ingest/validator.py
Raster validation — runs before any expensive processing.
Returns (is_valid, list_of_errors) — never raises for fixable problems.
"""
from __future__ import annotations
from pathlib import Path
from typing import Tuple, List


def validate_raster(path: Path) -> Tuple[bool, List[str]]:
    """
    Validate a raster file before ingestion.
    Returns (is_valid, errors).
    is_valid=False means the file should NOT be ingested.
    Errors are human-readable strings.
    """
    try:
        import rasterio
        from rasterio.errors import RasterioError, NotGeoreferencedWarning
    except ImportError:
        return False, ["rasterio is not installed: pip install rasterio"]

    errors: List[str] = []
    path = Path(path)

    # --- File existence ---
    if not path.exists():
        return False, [f"File does not exist: {path}"]
    if path.stat().st_size == 0:
        return False, [f"File is empty (0 bytes): {path}"]
    if path.suffix.lower() not in {".tif", ".tiff", ".geotiff", ".img", ".vrt"}:
        errors.append(
            f"Unexpected file extension '{path.suffix}'. Expected .tif/.tiff. Proceeding anyway."
        )

    # --- Rasterio open ---
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", NotGeoreferencedWarning)
            with rasterio.open(path) as ds:
                # Band count
                if ds.count == 0:
                    errors.append("Raster has 0 bands — cannot process.")
                    return False, errors

                # Dimensions
                if ds.width == 0 or ds.height == 0:
                    errors.append(f"Invalid dimensions: {ds.width}x{ds.height}")
                    return False, errors

                # CRS — warn, don't fail (some valid rasters lack CRS)
                if ds.crs is None:
                    errors.append(
                        "WARNING: No CRS found. Spatial queries and bounds will be unavailable."
                    )

                # Transform
                if ds.transform is None:
                    errors.append(
                        "WARNING: No geotransform. Tile bounds cannot be computed."
                    )

                # Read first tile to verify data is accessible
                try:
                    window = rasterio.windows.Window(0, 0, min(64, ds.width), min(64, ds.height))
                    data = ds.read(1, window=window)
                    if data.size == 0:
                        errors.append("WARNING: First tile read returned empty array.")
                except Exception as e:
                    errors.append(f"ERROR: Could not read raster data: {e}")
                    return False, errors

    except Exception as e:
        errors.append(f"ERROR: Cannot open raster file: {e}")
        return False, errors

    is_valid = not any(e.startswith("ERROR") for e in errors)
    return is_valid, errors
