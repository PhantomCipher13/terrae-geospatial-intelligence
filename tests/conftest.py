"""
tests/conftest.py - Shared pytest fixtures.
All tests run fully offline — no network calls permitted.
"""
import os
import sys
import tempfile
import pytest
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Enforce offline mode for all tests
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def valid_geotiff(tmp_path):
    """Create a minimal valid 3-band RGB uint8 GeoTIFF with CRS."""
    import rasterio
    from rasterio.transform import from_bounds
    from rasterio.crs import CRS
    rng = np.random.default_rng(0)
    data = rng.integers(0, 255, (3, 64, 64), dtype=np.uint8)
    p = tmp_path / "test_rgb.tif"
    with rasterio.open(p, "w", driver="GTiff", width=64, height=64,
                       count=3, dtype="uint8",
                       crs=CRS.from_epsg(4326),
                       transform=from_bounds(77.0, 28.0, 78.0, 29.0, 64, 64)) as ds:
        ds.write(data)
        ds.update_tags(ACQUISITION_DATE="2024-06-15")
        for i, name in enumerate(["Red","Green","Blue"], 1):
            ds.update_tags(i, name=name)
    return p


@pytest.fixture
def multispectral_geotiff(tmp_path):
    """4-band uint16 GeoTIFF (like Sentinel-2 subset)."""
    import rasterio
    from rasterio.transform import from_bounds
    from rasterio.crs import CRS
    rng = np.random.default_rng(1)
    data = rng.integers(100, 3000, (4, 128, 128), dtype=np.uint16)
    p = tmp_path / "test_ms.tif"
    with rasterio.open(p, "w", driver="GTiff", width=128, height=128,
                       count=4, dtype="uint16",
                       crs=CRS.from_epsg(32644),
                       transform=from_bounds(500000, 3000000, 600000, 3100000, 128, 128),
                       nodata=0) as ds:
        ds.write(data)
        for i, name in enumerate(["Red","Green","Blue","NIR"], 1):
            ds.update_tags(i, name=name)
    return p


@pytest.fixture
def no_crs_geotiff(tmp_path):
    """Valid GeoTIFF but missing CRS."""
    import rasterio
    rng = np.random.default_rng(2)
    data = rng.integers(0, 255, (3, 32, 32), dtype=np.uint8)
    p = tmp_path / "no_crs.tif"
    with rasterio.open(p, "w", driver="GTiff", width=32, height=32,
                       count=3, dtype="uint8") as ds:
        ds.write(data)
    return p


@pytest.fixture
def no_date_geotiff(tmp_path):
    """Valid GeoTIFF with CRS but NO acquisition date tag."""
    import rasterio
    from rasterio.transform import from_bounds
    from rasterio.crs import CRS
    rng = np.random.default_rng(3)
    data = rng.integers(0, 255, (3, 32, 32), dtype=np.uint8)
    p = tmp_path / "no_date.tif"
    with rasterio.open(p, "w", driver="GTiff", width=32, height=32,
                       count=3, dtype="uint8",
                       crs=CRS.from_epsg(4326),
                       transform=from_bounds(0, 0, 1, 1, 32, 32)) as ds:
        ds.write(data)
    return p


@pytest.fixture
def mostly_nodata_geotiff(tmp_path):
    """GeoTIFF where >90% of pixels are nodata."""
    import rasterio
    from rasterio.transform import from_bounds
    from rasterio.crs import CRS
    data = np.zeros((3, 64, 64), dtype=np.uint8)
    data[:, 62:, 62:] = 100  # only 4 pixels non-nodata
    p = tmp_path / "mostly_nodata.tif"
    with rasterio.open(p, "w", driver="GTiff", width=64, height=64,
                       count=3, dtype="uint8",
                       crs=CRS.from_epsg(4326),
                       transform=from_bounds(0, 0, 1, 1, 64, 64),
                       nodata=0) as ds:
        ds.write(data)
    return p


@pytest.fixture
def mock_embedder():
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from terrae.providers.embeddings.mock_provider import MockEmbeddingProvider
        return MockEmbeddingProvider()


@pytest.fixture
def faiss_index():
    from terrae.providers.index.faiss_flat import FaissFlat
    return FaissFlat(embedding_dim=512)


@pytest.fixture
def metadata_db(tmp_path):
    from terrae.db.metadata_db import MetadataDB
    return MetadataDB(tmp_path / "test.db")
