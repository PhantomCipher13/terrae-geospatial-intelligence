"""
geoai/core/result.py
Result types shared across pipeline stages.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any


class QualityStatus(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    UNAVAILABLE = "UNAVAILABLE"


class RegistrationStatus(str, Enum):
    GOOD = "REGISTRATION_GOOD"
    BORDERLINE = "REGISTRATION_BORDERLINE"
    FAILED = "REGISTRATION_FAILED"
    NOT_REQUIRED = "REGISTRATION_NOT_REQUIRED"
    UNAVAILABLE = "REGISTRATION_UNAVAILABLE"


class ChangeVerdict(str, Enum):
    SUPPORTED = "SUPPORTED"
    REVIEW = "REVIEW"
    ABSTAIN = "ABSTAIN"


@dataclass
class QualityReport:
    """Result of a quality assessment pass on a single raster/tile."""
    status: QualityStatus
    nodata_fraction: Optional[float] = None         # None = could not compute
    missing_bands: Optional[List[int]] = None       # None = could not assess
    cloud_fraction: Optional[float] = None          # None = no cloud mask available
    invalid_pixel_fraction: Optional[float] = None
    metadata_completeness: Optional[float] = None   # 0.0–1.0
    spatial_resolution_m: Optional[float] = None
    has_acquisition_date: Optional[bool] = None
    has_crs: Optional[bool] = None
    has_geotransform: Optional[bool] = None
    notes: List[str] = field(default_factory=list)  # human-readable warnings/failures


@dataclass
class RegistrationResult:
    """Result of a co-registration attempt between two rasters."""
    status: RegistrationStatus
    method: Optional[str] = None                    # e.g. 'ECC', 'AROSICS', 'NONE'
    shift_x_px: Optional[float] = None             # Estimated pixel shift X
    shift_y_px: Optional[float] = None             # Estimated pixel shift Y
    quality_metric: Optional[float] = None         # e.g. NCC score 0–1
    n_tie_points: Optional[int] = None
    confidence: Optional[float] = None             # 0.0–1.0
    processing_time_s: Optional[float] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class RetrievalResult:
    """Single ranked result from semantic retrieval."""
    tile_id: str
    scene_id: str
    similarity_score: float
    rank: int
    bounds_wgs84: Optional[tuple] = None
    acquisition_date: Optional[str] = None
    sensor: Optional[str] = None
    sensor_type: Optional[str] = None
    source_path: Optional[str] = None
    embedding_model: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisPlan:
    """
    Describes which pipeline stages will be executed for a given query.
    Created by the QueryPlanner, consumed by the execution engine.
    """
    query_text: Optional[str] = None
    query_image_path: Optional[str] = None
    intent: Optional[str] = None               # e.g. 'semantic_retrieval', 'change_detection'
    requires_retrieval: bool = True
    requires_eo_reranking: bool = False
    requires_temporal_selection: bool = False
    requires_quality_gate: bool = False
    requires_registration: bool = False
    requires_spectral_analysis: bool = False
    requires_learned_change: bool = False
    requires_temporal_persistence: bool = False
    top_k: int = 10
    notes: List[str] = field(default_factory=list)
