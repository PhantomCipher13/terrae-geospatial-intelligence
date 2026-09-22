"""
geoai/db/metadata_db.py
SQLite metadata store — kept strictly SEPARATE from the vector index.
Uses stable tile_id (UUID string) as the primary key linking DB <-> FAISS.
No hardcoded paths — all paths come from config.
No network dependencies.
"""
from __future__ import annotations
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS scenes (
    scene_id        TEXT PRIMARY KEY,
    source_path     TEXT NOT NULL,
    file_hash       TEXT,
    band_count      INTEGER,
    dtype           TEXT,
    width_px        INTEGER,
    height_px       INTEGER,
    crs_epsg        INTEGER,
    bounds_wgs84    TEXT,          -- JSON [W,S,E,N] or NULL
    acquisition_date TEXT,         -- ISO date string or NULL
    sensor          TEXT,
    sensor_type     TEXT,
    processing_level TEXT,
    metadata_completeness REAL,
    ingest_timestamp TEXT NOT NULL,
    tags            TEXT           -- JSON blob
);

CREATE TABLE IF NOT EXISTS tiles (
    tile_id         TEXT PRIMARY KEY,
    scene_id        TEXT NOT NULL REFERENCES scenes(scene_id),
    tile_row        INTEGER,
    tile_col        INTEGER,
    pixel_window    TEXT,          -- JSON [col_off, row_off, w, h]
    bounds_wgs84    TEXT,          -- JSON [W,S,E,N] or NULL
    crs_epsg        INTEGER,
    band_count      INTEGER,
    dtype           TEXT,
    nodata_fraction REAL,
    is_empty        INTEGER,       -- 0/1 boolean
    acquisition_date TEXT,
    sensor          TEXT,
    sensor_type     TEXT,
    ingest_timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS embeddings (
    tile_id             TEXT PRIMARY KEY REFERENCES tiles(tile_id),
    embedding_model     TEXT NOT NULL,
    embedding_version   TEXT,
    embedding_dim       INTEGER,
    preprocessing_ver   TEXT,
    is_mock             INTEGER NOT NULL DEFAULT 0,
    index_backend       TEXT,
    indexed_timestamp   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS provenance (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    tile_id             TEXT NOT NULL REFERENCES tiles(tile_id),
    event_type          TEXT NOT NULL,  -- 'ingest','query','change_analysis'
    embedding_model     TEXT,
    embedding_version   TEXT,
    query_text          TEXT,
    similarity_score    REAL,
    verdict             TEXT,
    abstain_reason      TEXT,
    analysis_timestamp  TEXT NOT NULL,
    extra               TEXT            -- JSON blob for extra fields
);

CREATE INDEX IF NOT EXISTS idx_tiles_scene ON tiles(scene_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings(embedding_model);
CREATE INDEX IF NOT EXISTS idx_provenance_tile ON provenance(tile_id);
"""


class MetadataDB:
    """
    SQLite-backed metadata store.
    Thread-safety: not guaranteed for concurrent writes (single-process MVP).
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()
        logger.info(f"MetadataDB initialised at {self.db_path}")

    # ------------------------------------------------------------------ #
    # Scenes                                                               #
    # ------------------------------------------------------------------ #

    def scene_exists(self, file_hash: str) -> Optional[str]:
        """Return scene_id if a scene with this file_hash already exists, else None."""
        row = self._conn.execute(
            "SELECT scene_id FROM scenes WHERE file_hash = ?", (file_hash,)
        ).fetchone()
        return row["scene_id"] if row else None

    def insert_scene(self, scene_id: str, meta: dict) -> None:
        self._conn.execute(
            """INSERT OR REPLACE INTO scenes
               (scene_id, source_path, file_hash, band_count, dtype,
                width_px, height_px, crs_epsg, bounds_wgs84,
                acquisition_date, sensor, sensor_type, processing_level,
                metadata_completeness, ingest_timestamp, tags)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                scene_id,
                meta.get("source_path"),
                meta.get("file_hash"),
                meta.get("band_count"),
                meta.get("dtype"),
                meta.get("width_px"),
                meta.get("height_px"),
                meta.get("crs_epsg"),
                _json(meta.get("bounds_wgs84")),
                meta.get("acquisition_date"),
                meta.get("sensor"),
                meta.get("sensor_type"),
                meta.get("processing_level"),
                meta.get("metadata_completeness"),
                _now(),
                _json(meta.get("tags")),
            ),
        )
        self._conn.commit()

    # ------------------------------------------------------------------ #
    # Tiles                                                                #
    # ------------------------------------------------------------------ #

    def tile_exists(self, tile_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM tiles WHERE tile_id = ?", (tile_id,)
        ).fetchone()
        return row is not None

    def insert_tile(self, tile: dict) -> None:
        self._conn.execute(
            """INSERT OR IGNORE INTO tiles
               (tile_id, scene_id, tile_row, tile_col, pixel_window, bounds_wgs84,
                crs_epsg, band_count, dtype, nodata_fraction, is_empty,
                acquisition_date, sensor, sensor_type, ingest_timestamp)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                tile["tile_id"], tile["scene_id"],
                tile.get("tile_row"), tile.get("tile_col"),
                _json(tile.get("pixel_window")),
                _json(tile.get("bounds_wgs84")),
                tile.get("crs_epsg"), tile.get("band_count"),
                tile.get("dtype"), tile.get("nodata_fraction"),
                int(tile.get("is_empty", False)),
                tile.get("acquisition_date"), tile.get("sensor"),
                tile.get("sensor_type"), _now(),
            ),
        )
        self._conn.commit()

    def insert_tiles_batch(self, tiles: List[dict]) -> None:
        rows = [
            (
                t["tile_id"], t["scene_id"],
                t.get("tile_row"), t.get("tile_col"),
                _json(t.get("pixel_window")),
                _json(t.get("bounds_wgs84")),
                t.get("crs_epsg"), t.get("band_count"),
                t.get("dtype"), t.get("nodata_fraction"),
                int(t.get("is_empty", False)),
                t.get("acquisition_date"), t.get("sensor"),
                t.get("sensor_type"), _now(),
            )
            for t in tiles
        ]
        self._conn.executemany(
            """INSERT OR IGNORE INTO tiles
               (tile_id, scene_id, tile_row, tile_col, pixel_window, bounds_wgs84,
                crs_epsg, band_count, dtype, nodata_fraction, is_empty,
                acquisition_date, sensor, sensor_type, ingest_timestamp)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            rows,
        )
        self._conn.commit()

    # ------------------------------------------------------------------ #
    # Embeddings                                                           #
    # ------------------------------------------------------------------ #

    def insert_embedding(self, tile_id: str, emb_meta: dict) -> None:
        self._conn.execute(
            """INSERT OR REPLACE INTO embeddings
               (tile_id, embedding_model, embedding_version, embedding_dim,
                preprocessing_ver, is_mock, index_backend, indexed_timestamp)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                tile_id,
                emb_meta.get("embedding_model"),
                emb_meta.get("embedding_version"),
                emb_meta.get("embedding_dim"),
                emb_meta.get("preprocessing_ver"),
                int(emb_meta.get("is_mock", False)),
                emb_meta.get("index_backend"),
                _now(),
            ),
        )
        self._conn.commit()

    # ------------------------------------------------------------------ #
    # Retrieval                                                            #
    # ------------------------------------------------------------------ #

    def get_tile(self, tile_id: str) -> Optional[Dict[str, Any]]:
        row = self._conn.execute(
            """SELECT t.*, e.embedding_model, e.embedding_version, e.is_mock
               FROM tiles t
               LEFT JOIN embeddings e ON t.tile_id = e.tile_id
               WHERE t.tile_id = ?""",
            (tile_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_tiles_for_scene(self, scene_id: str) -> List[Dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM tiles WHERE scene_id = ? ORDER BY tile_row, tile_col",
            (scene_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_scene(self, scene_id: str) -> Optional[Dict[str, Any]]:
        row = self._conn.execute(
            "SELECT * FROM scenes WHERE scene_id = ?", (scene_id,)
        ).fetchone()
        return dict(row) if row else None

    def stats(self) -> Dict[str, int]:
        scenes = self._conn.execute("SELECT COUNT(*) FROM scenes").fetchone()[0]
        tiles = self._conn.execute("SELECT COUNT(*) FROM tiles").fetchone()[0]
        embedded = self._conn.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]
        return {"scenes": scenes, "tiles": tiles, "embedded": embedded}

    # ------------------------------------------------------------------ #
    # Provenance                                                           #
    # ------------------------------------------------------------------ #

    def log_provenance(self, tile_id: str, event: str, extra: dict | None = None) -> None:
        self._conn.execute(
            """INSERT INTO provenance
               (tile_id, event_type, embedding_model, embedding_version,
                query_text, similarity_score, verdict, abstain_reason,
                analysis_timestamp, extra)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                tile_id, event,
                extra.get("embedding_model") if extra else None,
                extra.get("embedding_version") if extra else None,
                extra.get("query_text") if extra else None,
                extra.get("similarity_score") if extra else None,
                extra.get("verdict") if extra else None,
                extra.get("abstain_reason") if extra else None,
                _now(),
                _json(extra),
            ),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


def _json(val: Any) -> Optional[str]:
    if val is None:
        return None
    try:
        return json.dumps(val)
    except Exception:
        return str(val)

def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"
