"""
scripts/prepare_tmid.py
Fetches and stages the intermediate Sentinel-2A L2A observation:
Date: 2023-10-06 (MGRS 43RGM, col_off=4000, row_off=4000, size=512)
Saves:
  data/real/sentinel2/real_Tmid_20231006.tif
  data/real/sentinel2/scl_Tmid_20231006.tif
"""
import sys
import time
from pathlib import Path
import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.enums import Resampling

BASE_URL = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/43/R/GM/2023/10/S2A_43RGM_20231006_0_L2A"
BAND_NAMES = ["B02", "B03", "B04", "B08"]
CANONICAL_NAMES = ["Blue", "Green", "Red", "NIR"]
DATE_STR = "2023-10-06"

def main():
    out_dir = Path("data/real/sentinel2")
    out_path = out_dir / f"real_Tmid_{DATE_STR.replace('-', '')}.tif"
    scl_out_path = out_dir / f"scl_Tmid_{DATE_STR.replace('-', '')}.tif"

    col_off, row_off, size = 4000, 4000, 512
    window_10m = Window(col_off, row_off, size, size)
    window_20m = Window(col_off // 2, row_off // 2, size // 2, size // 2)

    print(f"Staging intermediate observation for {DATE_STR}...")
    t0 = time.time()
    bands_data = []
    meta_profile = None

    env = rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        AWS_NO_SIGN_REQUEST="YES",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"
    )

    with env:
        for b_name in BAND_NAMES:
            b_url = f"{BASE_URL}/{b_name}.tif"
            print(f"  Reading {b_name}...")
            with rasterio.open(b_url) as ds:
                if meta_profile is None:
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

        scl_url = f"{BASE_URL}/SCL.tif"
        print("  Reading SCL...")
        with rasterio.open(scl_url) as ds_scl:
            scl_arr = ds_scl.read(
                1,
                window=window_20m,
                out_shape=(size, size),
                resampling=Resampling.nearest
            )
            scl_profile = meta_profile.copy()
            scl_profile.update({
                "count": 1,
                "dtype": "uint8",
                "nodata": 0,
            })

    stacked = np.stack(bands_data, axis=0)

    with rasterio.open(out_path, "w", **meta_profile) as dst:
        dst.write(stacked)
        for i, name in enumerate(CANONICAL_NAMES, start=1):
            dst.set_band_description(i, name)
            dst.update_tags(i, name=name, s2_band=BAND_NAMES[i-1])
        dst.update_tags(
            ACQUISITION_DATE=DATE_STR,
            SENSOR="Sentinel-2",
            SENSOR_ID="Sentinel-2",
            PLATFORM="Sentinel-2A",
            PROCESSING_LEVEL="Level-2A",
            DATASET_NAME="Sentinel-2 L2A AWS Open Data",
            MGRS_TILE="43RGM",
            REFLECTANCE_SCALE="10000",
        )

    with rasterio.open(scl_out_path, "w", **scl_profile) as dst_scl:
        dst_scl.write(scl_arr.astype(np.uint8), 1)
        dst_scl.update_tags(
            ACQUISITION_DATE=DATE_STR,
            DESCRIPTION="Sentinel-2 L2A Scene Classification Layer (resampled to 10m)",
        )

    print(f"[DONE] Saved {out_path.name} and {scl_out_path.name} in {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
