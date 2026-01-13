from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ArtifactStoreConfig:
    artifact_dir: Path
    max_size_mb: int | None


def artifact_store_config_from_env() -> ArtifactStoreConfig:
    artifact_dir = Path(os.getenv("JARVIS_ARTIFACT_DIR", "./artifacts"))
    max_size_raw = os.getenv("JARVIS_ARTIFACT_MAX_SIZE_MB")
    max_size = int(max_size_raw) if max_size_raw else None
    return ArtifactStoreConfig(artifact_dir=artifact_dir, max_size_mb=max_size)
