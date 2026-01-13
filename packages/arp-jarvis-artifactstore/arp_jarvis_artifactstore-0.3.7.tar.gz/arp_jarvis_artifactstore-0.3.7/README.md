# JARVIS Artifact Store

Internal JARVIS service that stores binary artifacts and returns stable artifact references.
This is a JARVIS-only contract (not part of the ARP Standard).

## Requirements

- Python >= 3.11

## Install

```bash
python3 -m pip install -e .
```

## Run

```bash
python3 -m pip install -e .
arp-jarvis-artifactstore
```

> [!TIP]
> Use `bash src/scripts/dev_server.sh --host ... --port ... --reload` for dev convenience.

## Configuration

Environment variables:
- `JARVIS_ARTIFACT_DIR` (default `./artifacts/`)
- `JARVIS_ARTIFACT_MAX_SIZE_MB` (optional guardrail)
- `ARP_AUTH_*` (JWT auth settings, shared across JARVIS services)

Auth is enabled by default (JWT). To disable for local dev, set `ARP_AUTH_PROFILE=dev-insecure`
or `ARP_AUTH_MODE=disabled`. Health/version endpoints are always exempt.
If no `ARP_AUTH_*` env vars are set, the service defaults to the dev Keycloak issuer.

## API (v0.3.7)

Health/version:
- `GET /v1/health`
- `GET /v1/version`

Artifacts:
- `POST /v1/artifacts` -> `ArtifactRef`
- `GET /v1/artifacts/{artifact_id}` (raw bytes)
- `HEAD /v1/artifacts/{artifact_id}` (metadata headers)
- `GET /v1/artifacts/{artifact_id}/metadata` -> `ArtifactRef`

## Notes

- Filesystem storage by default.
- Metadata is tracked in a small SQLite index under the artifact directory.
