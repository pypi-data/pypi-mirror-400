from __future__ import annotations

import hashlib
import sqlite3
from contextlib import contextmanager
from typing import Iterator
import uuid
from dataclasses import dataclass
from pathlib import Path

from .config import ArtifactStoreConfig
from .errors import InvalidArtifactIdError, NotFoundError, StorageFullError
from .utils import now


@dataclass(frozen=True)
class ArtifactMetadata:
    artifact_id: str
    path: Path
    content_type: str | None
    size_bytes: int
    checksum_sha256: str | None
    created_at: str

    @property
    def uri(self) -> str:
        return str(self.path)


class FilesystemArtifactStore:
    def __init__(self, config: ArtifactStoreConfig) -> None:
        self._artifact_dir = config.artifact_dir
        self._max_size_mb = config.max_size_mb
        self._artifact_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self._artifact_dir / "artifact_index.sqlite"
        self._init_db()

    def put(self, data: bytes, *, content_type: str | None) -> ArtifactMetadata:
        self._check_size(len(data))
        artifact_id = uuid.uuid4().hex
        artifact_path = self._artifact_dir / artifact_id
        checksum = _sha256(data)
        artifact_path.write_bytes(data)
        metadata = ArtifactMetadata(
            artifact_id=artifact_id,
            path=artifact_path,
            content_type=content_type,
            size_bytes=len(data),
            checksum_sha256=checksum,
            created_at=now(),
        )
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO artifacts (artifact_id, path, content_type, size_bytes, checksum_sha256, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    metadata.artifact_id,
                    str(metadata.path),
                    metadata.content_type,
                    metadata.size_bytes,
                    metadata.checksum_sha256,
                    metadata.created_at,
                ),
            )
        return metadata

    def get_metadata(self, artifact_id: str) -> ArtifactMetadata:
        _validate_artifact_id(artifact_id)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT artifact_id, path, content_type, size_bytes, checksum_sha256, created_at "
                "FROM artifacts WHERE artifact_id = ?",
                (artifact_id,),
            ).fetchone()
        if not row:
            raise NotFoundError("Artifact not found.")
        return ArtifactMetadata(
            artifact_id=row["artifact_id"],
            path=Path(row["path"]),
            content_type=row["content_type"],
            size_bytes=row["size_bytes"],
            checksum_sha256=row["checksum_sha256"],
            created_at=row["created_at"],
        )

    def get_path(self, artifact_id: str) -> Path:
        metadata = self.get_metadata(artifact_id)
        if not metadata.path.exists():
            raise NotFoundError("Artifact content missing.")
        return metadata.path

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self._index_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS artifacts ("
                "artifact_id TEXT PRIMARY KEY, "
                "path TEXT NOT NULL, "
                "content_type TEXT, "
                "size_bytes INTEGER NOT NULL, "
                "checksum_sha256 TEXT, "
                "created_at TEXT NOT NULL"
                ")"
            )

    def _check_size(self, incoming_size: int) -> None:
        if self._max_size_mb is None:
            return
        max_bytes = self._max_size_mb * 1024 * 1024
        if incoming_size > max_bytes:
            raise StorageFullError("Artifact exceeds configured max size.")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validate_artifact_id(artifact_id: str) -> None:
    if not artifact_id or Path(artifact_id).name != artifact_id:
        raise InvalidArtifactIdError("Invalid artifact_id.")
