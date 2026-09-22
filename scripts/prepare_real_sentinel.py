"""
scripts/prepare_real_sentinel.py
Downloads and stages one real Sentinel-2 Level-2A temporal pair (512x512 crop).
Location: Greater Noida / NCR (MGRS: 43RGM, EPSG:32643)
Dates:
  - T0: 2023-05-19 (Sentinel-2A L2A, clear sky)
  - T1: 2023-12-05 (Sentinel-2A L2A, clear sky)

Bands:
  1: Blue (B02)
  2: Green (B03)
  3: Red (B04)
  4: NIR (B08)
Also saves Scene Classification Layer (SCL) for cloud/quality masking.

After running this preparation script, the application operates 100% OFFLINE.
"""
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.enums import Resampling

# AWS Element84 Public Sentinel-2 COG URLs for 43RGM
BASE_T0 = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/43/R/GM/2023/5/S2A_43RGM_20230519_0_L2A"
BASE_T1 = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/43/R/GM/2023/12/S2A_43RGM_20231205_0_L2A"

BAND_NAMES = ["B02", "B03", "B04", "B08"]  # Blue, Green, Red, NIR
CANONICAL_NAMES = ["Blue", "Green", "Red", "NIR"]

def extract_and_save_scene(base_url, date_str, out_path, scl_out_path, col_off=4000, row_off=4000, size=512):
    print(f"\nFetching real Sentinel-2 L2A crop for {date_str}...")
    t0 = time.time()
    
    window_10m = Window(col_off, row_off, size, size)
    # SCL is 20m resolution, so offset and size are halved
    window_20m = Window(col_off // 2, row_off // 2, size // 2, size // 2)

    bands_data = []
    meta_profile = None

    env = rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        AWS_NO_SIGN_REQUEST="YES",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"
    )

    with env:
        # Read 10m bands: B02, B03, B04, B08
        for b_name in BAND_NAMES:
            b_url = f"{base_url}/{b_name}.tif"
            print(f"  Reading {b_name} from {b_url.split('/')[-1]}...")
            with rasterio.open(b_url) as ds:
                if meta_profile is None:
                    # Calculate new transform for the window
                    new_transform = rasterio.windows.transform(window_10m, ds.transform)
                    meta_profile = ds.profile.copy()
                    meta_profile.update({
                        "count": 4,
                        "width": size,
                        "height": size,
                        "transform": new_transform,
                        "compress": "lzw",
                        "driver": "GTiff",
                    })
                arr = ds.read(1, window=window_10m)
                bands_data.append(arr)

        # Read SCL (Scene Classification Layer: 20m resolution)
        scl_url = f"{base_url}/SCL.tif"
        print(f"  Reading SCL from {scl_url.split('/')[-1]}...")
        with rasterio.open(scl_url) as ds_scl:
            scl_arr = ds_scl.read(
                1,
                window=window_20m,
                out_shape=(size, size),
                resampling=Resampling.nearest
            )
            scl_transform = meta_profile["transform"]
            scl_profile = meta_profile.copy()
            scl_profile.update({
                "count": 1,
                "dtype": "uint8",
                "nodata": 0,
            })

    # Stack 4 bands (C, H, W)
    stacked = np.stack(bands_data, axis=0)  # (4, 512, 512) uint16

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out_path, "w", **meta_profile) as dst:
        dst.write(stacked)
        for i, name in enumerate(CANONICAL_NAMES, start=1):
            dst.set_band_description(i, name)
            dst.update_tags(i, name=name, s2_band=BAND_NAMES[i-1])
        dst.update_tags(
            ACQUISITION_DATE=date_str,
            SENSOR="Sentinel-2",
            SENSOR_ID="Sentinel-2",
            PLATFORM="Sentinel-2A",
            PROCESSING_LEVEL="Level-2A",
            DATASET_NAME="Sentinel-2 L2A AWS Open Data",
            MGRS_TILE="43RGM",
            REFLECTANCE_SCALE="10000",
        )

    # Save SCL
    with rasterio.open(scl_out_path, "w", **scl_profile) as dst_scl:
        dst_scl.write(scl_arr.astype(np.uint8), 1)
        dst_scl.update_tags(
            ACQUISITION_DATE=date_str,
            DESCRIPTION="Sentinel-2 L2A Scene Classification Layer (resampled to 10m)",
        )

    print(f"  [SAVED] {out_path.name} (shape: {stacked.shape}, time: {time.time()-t0:.1f}s)")
    print(f"  [SAVED] {scl_out_path.name}")


def main():
    out_dir = Path("data/real/sentinel2")
    t0_tif = out_dir / "real_T0_20230519.tif"
    t1_tif = out_dir / "real_T1_20231205.tif"
    scl0_tif = out_dir / "scl_T0_20230519.tif"
    scl1_tif = out_dir / "scl_T1_20231205.tif"

    print("==================================================")
    print("  Staging Real Sentinel-2 L2A Validation Pair")
    print("==================================================")
    extract_and_save_scene(BASE_T0, "2023-05-19", t0_tif, scl0_tif)
    extract_and_save_scene(BASE_T1, "2023-12-05", t1_tif, scl1_tif)
    print("\nStage complete! Data saved to data/real/sentinel2/")

if __name__ == "__main__":
    main()
