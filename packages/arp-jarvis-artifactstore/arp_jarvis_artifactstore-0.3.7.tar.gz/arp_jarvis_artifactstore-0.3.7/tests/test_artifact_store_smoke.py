from __future__ import annotations

from fastapi.testclient import TestClient
from arp_standard_server import AuthSettings

from jarvis_artifact_store.config import ArtifactStoreConfig
from jarvis_artifact_store.service import create_app


def test_artifact_roundtrip(tmp_path) -> None:
    config = ArtifactStoreConfig(artifact_dir=tmp_path, max_size_mb=None)
    app = create_app(config, auth_settings=AuthSettings(mode="disabled"))
    client = TestClient(app)

    payload = b"hello"
    create_resp = client.post("/v1/artifacts", content=payload, headers={"Content-Type": "text/plain"})
    assert create_resp.status_code == 200
    ref = create_resp.json()
    artifact_id = ref["artifact_id"]

    get_resp = client.get(f"/v1/artifacts/{artifact_id}")
    assert get_resp.status_code == 200
    assert get_resp.content == payload

    head_resp = client.head(f"/v1/artifacts/{artifact_id}")
    assert head_resp.status_code == 200
    assert head_resp.headers.get("Content-Type") == "text/plain"
    assert int(head_resp.headers.get("Content-Length", "0")) == len(payload)

    meta_resp = client.get(f"/v1/artifacts/{artifact_id}/metadata")
    assert meta_resp.status_code == 200
    assert meta_resp.json()["artifact_id"] == artifact_id
