from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from arp_standard_server import AuthSettings
from jarvis_artifact_store.config import ArtifactStoreConfig, artifact_store_config_from_env
from jarvis_artifact_store.errors import InvalidArtifactIdError, NotFoundError
from jarvis_artifact_store.filesystem import FilesystemArtifactStore
from jarvis_artifact_store.service import create_app
from jarvis_artifact_store.utils import (
    DEFAULT_DEV_KEYCLOAK_ISSUER,
    auth_settings_from_env_or_dev_secure,
)


def test_auth_settings_default(monkeypatch) -> None:
    for key in list(os.environ):
        if key.startswith("ARP_AUTH_"):
            monkeypatch.delenv(key, raising=False)
    settings = auth_settings_from_env_or_dev_secure()
    assert settings.mode == "required"
    assert settings.issuer == DEFAULT_DEV_KEYCLOAK_ISSUER


def test_auth_settings_from_env(monkeypatch) -> None:
    monkeypatch.setenv("ARP_AUTH_MODE", "disabled")
    settings = auth_settings_from_env_or_dev_secure()
    assert settings.mode == "disabled"


def test_invalid_artifact_id_rejected(tmp_path) -> None:
    config = ArtifactStoreConfig(artifact_dir=tmp_path, max_size_mb=None)
    store = FilesystemArtifactStore(config)
    with pytest.raises(InvalidArtifactIdError):
        store.get_metadata("bad/evil")


def test_config_from_env(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("JARVIS_ARTIFACT_DIR", str(tmp_path / "artifacts"))
    monkeypatch.setenv("JARVIS_ARTIFACT_MAX_SIZE_MB", "12")
    config = artifact_store_config_from_env()
    assert config.artifact_dir.name == "artifacts"
    assert config.max_size_mb == 12


def test_not_found_metadata(tmp_path) -> None:
    config = ArtifactStoreConfig(artifact_dir=tmp_path, max_size_mb=None)
    store = FilesystemArtifactStore(config)
    with pytest.raises(NotFoundError):
        store.get_metadata("missing")


def test_storage_full_returns_413(tmp_path) -> None:
    config = ArtifactStoreConfig(artifact_dir=tmp_path, max_size_mb=0)
    app = create_app(config, auth_settings=AuthSettings(mode="disabled"))
    client = TestClient(app)

    resp = client.post("/v1/artifacts", content=b"data")
    assert resp.status_code == 413


def test_missing_file_returns_404(tmp_path) -> None:
    config = ArtifactStoreConfig(artifact_dir=tmp_path, max_size_mb=None)
    store = FilesystemArtifactStore(config)
    metadata = store.put(b"data", content_type="text/plain")
    metadata.path.unlink()

    app = create_app(config, auth_settings=AuthSettings(mode="disabled"))
    client = TestClient(app)
    resp = client.get(f"/v1/artifacts/{metadata.artifact_id}")
    assert resp.status_code == 404


def test_invalid_artifact_id_returns_422(tmp_path, monkeypatch) -> None:
    config = ArtifactStoreConfig(artifact_dir=tmp_path, max_size_mb=None)
    app = create_app(config, auth_settings=AuthSettings(mode="disabled"))
    client = TestClient(app)

    def _raise_invalid(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise InvalidArtifactIdError("bad id")

    monkeypatch.setattr(FilesystemArtifactStore, "get_metadata", _raise_invalid)
    resp = client.get("/v1/artifacts/badid")
    assert resp.status_code == 422
