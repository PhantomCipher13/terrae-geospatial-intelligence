"""
scripts/make_test_geotiff.py
Creates a synthetic GeoTIFF for testing — does NOT require real satellite data.
Produces a 4-band (R,G,B,NIR) uint16 GeoTIFF with valid CRS and geotransform.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def make_test_geotiff(
    output_path: str = "data/sample/test_scene.tif",
    width: int = 512,
    height: int = 512,
    n_bands: int = 4,
    with_crs: bool = True,
    with_nodata: bool = True,
    with_date_tag: bool = True,
):
    import numpy as np
    try:
        import rasterio
        from rasterio.transform import from_bounds
        from rasterio.crs import CRS
    except ImportError:
        print("ERROR: rasterio not installed. Run: pip install rasterio")
        sys.exit(1)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(42)
    data = rng.integers(500, 3000, (n_bands, height, width), dtype=np.uint16)
    # Add some nodata patches
    if with_nodata:
        data[:, :20, :20] = 0  # top-left corner = nodata

    transform = from_bounds(77.0, 28.0, 78.0, 29.0, width, height) if with_crs else None
    crs = CRS.from_epsg(4326) if with_crs else None

    profile = {
        "driver": "GTiff",
        "dtype": "uint16",
        "width": width,
        "height": height,
        "count": n_bands,
        "crs": crs,
        "transform": transform,
        "nodata": 0,
        "compress": "lzw",
    }

    band_names = ["Red", "Green", "Blue", "NIR"][:n_bands]
    with rasterio.open(out, "w", **profile) as ds:
        ds.write(data)
        for i, name in enumerate(band_names, start=1):
            ds.update_tags(i, name=name)
        if with_date_tag:
            ds.update_tags(ACQUISITION_DATE="2024-06-15")

    print(f"[OK] Created test GeoTIFF: {out}")
    print(f"   Bands: {n_bands} | Size: {width}x{height} | CRS: {'EPSG:4326' if with_crs else 'NONE'}")
    return str(out)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="data/sample/test_scene.tif")
    p.add_argument("--bands", type=int, default=4)
    p.add_argument("--no-crs", action="store_true")
    p.add_argument("--no-date", action="store_true")
    args = p.parse_args()
    make_test_geotiff(
        output_path=args.output,
        n_bands=args.bands,
        with_crs=not args.no_crs,
        with_date_tag=not args.no_date,
    )
