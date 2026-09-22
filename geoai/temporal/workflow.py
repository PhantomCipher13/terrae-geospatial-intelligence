"""
geoai/temporal/workflow.py
Orchestrates temporal retrieval, registration, and change detection.
"""
import logging
from pathlib import Path
from typing import List, Optional
import rasterio
import numpy as np

from geoai.db.metadata_db import MetadataDB
from geoai.core.result import RegistrationResult, RegistrationStatus, ChangeVerdict
from geoai.providers.change.base import TemporalChangeResult
from geoai.providers.change.spectral_detector import SpectralChangeDetector

logger = logging.getLogger(__name__)

class TemporalAnalysisWorkflow:
    def __init__(self, db: MetadataDB, change_detector=None):
        self._db = db
        self._change_detector = change_detector or SpectralChangeDetector()

    def run_analysis(self, tile_id: str, query_text: Optional[str] = None) -> TemporalChangeResult:
        """
        Runs a temporal analysis workflow starting from a single tile.
        1. Looks up the tile's spatial bounds.
        2. Finds all tiles in the DB that overlap these bounds.
        3. Sorts them by acquisition_date.
        4. Loads the raw raster data for these tiles.
        5. Runs change detection on the temporal stack.
        6. Computes evidence-based change attribution across T0 and T_final.
        """
        # Get target tile bounds
        target_tile = self._db.get_tile(tile_id)
        if not target_tile:
            raise ValueError(f"Tile {tile_id} not found in DB")
            
        bounds = target_tile.get("bounds_wgs84")
        if not bounds:
            raise ValueError(f"Tile {tile_id} has no spatial bounds")
            
        if isinstance(bounds, str):
            import json
            bounds = json.loads(bounds)

        # Get scene for the target tile to know the window
        target_scene = self._db.get_scene(target_tile.get("scene_id"))
        if not target_scene:
            raise ValueError("Target scene not found")
            
        # In a real system, we'd do a spatial query in DB. 
        # For prototype, we fetch all tiles and filter by bounds (W, S, E, N).
        all_tiles = []
        with self._db._conn as conn:
            conn.row_factory = dict_factory
            cursor = conn.execute("SELECT * FROM tiles")
            for row in cursor.fetchall():
                # Require both identical pixel_window AND geographic overlap
                pw = row.get("pixel_window")
                tb = row.get("bounds_wgs84")
                if isinstance(tb, str):
                    import json
                    try:
                        tb = json.loads(tb)
                    except:
                        tb = None
                if pw == target_tile.get("pixel_window") and tb and _bounds_overlap(bounds, tb):
                    all_tiles.append(row)
                    
        # Sort by date
        def get_date(t):
            return t.get("acquisition_date") or ""
        all_tiles.sort(key=get_date)
        
        if len(all_tiles) < 2:
            return TemporalChangeResult(
                verdict=ChangeVerdict.ABSTAIN,
                abstain_reason=f"Only {len(all_tiles)} overlapping tiles found. Need at least 2."
            )

        # Load raster data for each tile
        observations = []
        timestamps = []
        valid_tiles = []
        
        # Quality mask collection across observations
        combined_valid_mask = None
        scl_applied_count = 0

        for tile in all_tiles:
            scene_id = tile.get("scene_id")
            scene = self._db.get_scene(scene_id)
            if not scene:
                continue
                
            source_path = scene.get("source_path")
            if not source_path:
                continue
                
            window_str = tile.get("pixel_window")
            
            try:
                import json
                col_off, row_off, width, height = json.loads(window_str)
                from rasterio.windows import Window
                window = Window(col_off, row_off, width, height)
                
                with rasterio.open(source_path) as src:
                    arr = src.read(window=window)
                    # Normalize to 0-1 for spectral detector
                    if arr.dtype == np.uint16:
                        arr = np.clip(arr / 10000.0, 0, 1).astype(np.float32)
                    elif arr.dtype == np.uint8:
                        arr = (arr / 255.0).astype(np.float32)
                    
                    # Reflectance consistency check
                    if np.mean(arr > 0.99) > 0.5:
                        logger.warning(f"Unusual reflectance range: >50% pixels near 1.0 in {source_path}")
                        
                    observations.append(arr)
                    timestamps.append(get_date(tile))
                    valid_tiles.append(tile)

                # Check for SCL (Scene Classification Layer) quality mask
                p = Path(source_path)
                scl_candidates = [
                    p.parent / f"scl_{p.name}",
                    p.parent / f"scl_{p.stem}.tif",
                    p.parent / f"scl_{p.name.replace('real_', '')}",
                    p.parent / f"scl_{p.stem.replace('real_', '')}.tif",
                    p.parent / f"scl_{tile.get('acquisition_date', '')[:10]}.tif",
                ]
                for sc in scl_candidates:
                    if sc.exists():
                        try:
                            with rasterio.open(sc) as scl_src:
                                scl_w = scl_src.read(1, window=window)
                                # Sentinel-2 L2A SCL classes: 3=Shadow, 8=Cloud Med, 9=Cloud High, 10=Cirrus, 11=Snow, 0=Nodata, 1=Saturated
                                is_invalid = np.isin(scl_w, [0, 1, 3, 8, 9, 10, 11])
                                is_valid = ~is_invalid
                                if combined_valid_mask is None:
                                    combined_valid_mask = is_valid
                                else:
                                    combined_valid_mask = combined_valid_mask & is_valid
                                scl_applied_count += 1
                                break
                        except Exception as e:
                            logger.warning(f"Could not read SCL mask from {sc}: {e}")

            except Exception as e:
                logger.warning(f"Failed to read tile {tile.get('tile_id')}: {e}")
                
        if len(observations) < 2:
             return TemporalChangeResult(
                verdict=ChangeVerdict.ABSTAIN,
                abstain_reason="Failed to load raster data for >= 2 observations."
            )
            
        # Determine dataset type and registration condition
        is_real_s2 = any(
            "real" in str((self._db.get_scene(t.get("scene_id")) or {}).get("source_path", "")).lower()
            for t in valid_tiles
        )
        dataset_type = "REAL SENTINEL-2 VALIDATION" if is_real_s2 else "SYNTHETIC VALIDATION"
        
        if is_real_s2:
            reg_note = "Real Sentinel-2 L2A co-registered by ESA Copernicus ground segment (identical MGRS UTM grid)."
            reg_method = "mgrs-grid-aligned"
        else:
            reg_note = "Prototype assumption: scenes are synthetically pre-aligned."
            reg_method = "prototype-skip"

        reg_result = RegistrationResult(
            status=RegistrationStatus.NOT_REQUIRED,
            method=reg_method,
            quality_metric=1.0,
            notes=[reg_note]
        )

        result = self._change_detector.detect(observations, timestamps, reg_result)

        # Apply cloud/quality mask to change evidence if SCL was available
        if combined_valid_mask is not None and result.evidence:
            ev = result.evidence[0]
            if ev.change_mask is not None:
                ev.change_mask = ev.change_mask & combined_valid_mask
                total_valid_px = int(np.sum(combined_valid_mask))
                ev.change_fraction = float(np.sum(ev.change_mask) / total_valid_px) if total_valid_px > 0 else 0.0

        # 6. Evidence-based change attribution
        try:
            from geoai.change.attribution import attribute_change
            change_mask = None
            if result.evidence:
                change_mask = result.evidence[0].change_mask

            attribution = attribute_change(
                obs_t0=observations[0],
                obs_t1=observations[-1],
                change_mask=change_mask,
                band_names=getattr(self._change_detector, "required_bands", None) or ["Blue", "Green", "Red", "NIR"],
                query_text=query_text,
                verdict=result.verdict.value,
                valid_mask=combined_valid_mask,
            )
            result.attribution = attribution
            result.notes.append(f"Attribution: {attribution.dominant_interpretation}")
        except Exception as e:
            logger.warning(f"Failed to compute change attribution: {e}")

        # 7. Multi-temporal trajectory persistence check (if >= 3 observations)
        if len(observations) >= 3:
            try:
                from geoai.temporal.persistence import analyze_temporal_persistence
                persistence = analyze_temporal_persistence(
                    observations=observations,
                    timestamps=timestamps,
                    threshold=getattr(self._change_detector, "_threshold", 0.15),
                    valid_mask=combined_valid_mask,
                    band_names=getattr(self._change_detector, "required_bands", None) or ["Blue", "Green", "Red", "NIR"],
                )
                result.persistence = persistence
                result.notes.append(f"Temporal Persistence: {persistence.category}")
                if result.attribution and getattr(result.attribution, "evidence_chain", None):
                    result.attribution.evidence_chain.temporal_trajectory = persistence.to_dict()
            except Exception as e:
                logger.warning(f"Failed to compute temporal persistence: {e}")

        # Attach dataset type and quality notes
        result.notes.append(f"DATASET_TYPE:{dataset_type}")
        if combined_valid_mask is not None:
            inv_pct = float(1.0 - (np.sum(combined_valid_mask) / combined_valid_mask.size))
            result.notes.append(f"Quality mask applied: {inv_pct:.1%} cloud/invalid pixels excluded.")
        else:
            result.notes.append("Quality mask: None available in dataset.")

        # Attach valid tiles to result notes for UI consumption
        result.notes.append(f"Analyzed {len(valid_tiles)} tiles.")
        # Store source paths in notes for UI 
        for t, obs in zip(valid_tiles, observations):
            scene = self._db.get_scene(t.get("scene_id"))
            result.notes.append(f"PATH:{scene.get('source_path')}|DATE:{get_date(t)}")
            
        return result

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def _bounds_overlap(b1, b2, eps=1e-5):
    # bounds are (left, bottom, right, top)
    if b1[0] >= b2[2] - eps or b2[0] >= b1[2] - eps: return False
    if b1[1] >= b2[3] - eps or b2[1] >= b1[3] - eps: return False
    return True
