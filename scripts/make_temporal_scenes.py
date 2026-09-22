"""
scripts/make_temporal_scenes.py
Generates 3 realistic synthetic multispectral GeoTIFFs of the same area over time.
Used to test the temporal workflow offline without large downloads.

Dates:
- T0: 2024-01-15 (Baseline: Mostly vegetation/soil, some water)
- T1: 2024-03-20 (Construction started: Soil cleared, small buildings)
- T2: 2024-06-15 (Construction finished: Large built-up area)

Bands: Blue, Green, Red, NIR (4 bands)
Size: 512x512
CRS: EPSG:4326
"""
import argparse
import sys
from pathlib import Path
import numpy as np

try:
    import rasterio
    from rasterio.transform import from_origin
except ImportError:
    print("rasterio is required.")
    sys.exit(1)


def generate_scene(date_str, stage, output_path):
    size = 512
    bands = 4
    # Fixed seed for reproducibility across runs
    rng = np.random.default_rng(42)

    # Base background (vegetation + soil)
    # R, G, B, NIR
    bg = np.zeros((bands, size, size), dtype=np.uint16)
    
    # Grass/Vegetation (High NIR, low Red, med Green)
    bg[0, :, :] = rng.integers(200, 400, (size, size)) # Blue
    bg[1, :, :] = rng.integers(500, 900, (size, size)) # Green
    bg[2, :, :] = rng.integers(200, 500, (size, size)) # Red
    bg[3, :, :] = rng.integers(2000, 3500, (size, size)) # NIR

    # Water body (low everywhere, slightly higher blue)
    water_mask = np.zeros((size, size), dtype=bool)
    water_mask[50:150, 350:450] = True
    bg[0, water_mask] = rng.integers(400, 600, water_mask.sum())
    bg[1, water_mask] = rng.integers(300, 500, water_mask.sum())
    bg[2, water_mask] = rng.integers(100, 200, water_mask.sum())
    bg[3, water_mask] = rng.integers(50, 150, water_mask.sum())

    # Construction area (changes over time)
    # Bounding box of construction: row 250:400, col 100:250
    cx1, cx2 = 100, 250
    cy1, cy2 = 250, 400

    if stage >= 1:
        # T1: Soil cleared (High Red, low NIR)
        soil_mask = np.zeros((size, size), dtype=bool)
        soil_mask[cy1:cy2, cx1:cx2] = True
        bg[0, soil_mask] = rng.integers(800, 1000, soil_mask.sum())
        bg[1, soil_mask] = rng.integers(900, 1200, soil_mask.sum())
        bg[2, soil_mask] = rng.integers(1200, 1600, soil_mask.sum())
        bg[3, soil_mask] = rng.integers(1400, 1800, soil_mask.sum())
        
        # Small buildings
        bldg_mask = np.zeros((size, size), dtype=bool)
        bldg_mask[cy1+20:cy1+50, cx1+20:cx1+50] = True
        bg[0, bldg_mask] = 2000
        bg[1, bldg_mask] = 2000
        bg[2, bldg_mask] = 2000
        bg[3, bldg_mask] = 2200

    if stage >= 2:
        # T2: Full construction (Very bright, high reflectance all bands)
        bldg2_mask = np.zeros((size, size), dtype=bool)
        bldg2_mask[cy1+60:cy2-20, cx1+20:cx2-20] = True
        bg[0, bldg2_mask] = 2500
        bg[1, bldg2_mask] = 2500
        bg[2, bldg2_mask] = 2500
        bg[3, bldg2_mask] = 2600
        
        # Road (Grey)
        road_mask = np.zeros((size, size), dtype=bool)
        road_mask[cy2-15:cy2, cx1:cx2] = True
        bg[0, road_mask] = 1200
        bg[1, road_mask] = 1200
        bg[2, road_mask] = 1200
        bg[3, road_mask] = 1200

    # Add some temporal noise to everything
    noise = rng.integers(-50, 50, (bands, size, size))
    bg = np.clip(bg.astype(np.int32) + noise, 0, 65535).astype(np.uint16)

    # Geo transform (UTM Zone 43N over New Delhi approx, 10m resolution)
    transform = from_origin(700000.0, 3200000.0, 10.0, 10.0)
    crs = "EPSG:32643"

    # Save
    profile = {
        "driver": "GTiff",
        "height": size,
        "width": size,
        "count": bands,
        "dtype": rasterio.uint16,
        "crs": crs,
        "transform": transform,
        "nodata": 0,
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256
    }
    
    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(bg)
        dst.update_tags(
            ACQUISITION_DATE=date_str,
            SENSOR_ID="Sentinel-2",
            TIFFTAG_IMAGEDESCRIPTION="Synthetic Temporal Test Scene"
        )
        dst.set_band_description(1, "Blue")
        dst.set_band_description(2, "Green")
        dst.set_band_description(3, "Red")
        dst.set_band_description(4, "NIR")
        
    print(f"Created {output_path.name} (Stage {stage}, Date {date_str})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="data/sample/temporal")
    args = parser.parse_args()
    
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    generate_scene("2024-01-15T10:00:00Z", 0, out_dir / "scene_T0.tif")
    generate_scene("2024-03-20T10:00:00Z", 1, out_dir / "scene_T1.tif")
    generate_scene("2024-06-15T10:00:00Z", 2, out_dir / "scene_T2.tif")

if __name__ == "__main__":
    main()
