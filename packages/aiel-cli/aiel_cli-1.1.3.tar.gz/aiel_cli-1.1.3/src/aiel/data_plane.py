
import os
from typing import Any, Optional

import httpx
import typer

from .config import settings
from .utilities import read_json, write_json
from .errors import CliError
from .auth.credentials import list_profiles, _current_profile, _get_profile, get_current_base_url
# -------------------------
# API client (DP)
# -------------------------

def _token() -> str:
    tok = os.getenv("AIEL_TOKEN")
    if tok:
        return tok

    # Lazily import to avoid import cycle; credentials already depends on data_plane.
    from .auth.credentials import resolve_token

    resolved = resolve_token()
    token: Optional[str]
    if isinstance(resolved, tuple):
        token = resolved[0]
    else:
        token = resolved

    if token:
        return token

    raise typer.BadParameter("Missing credentials. Run `aiel auth login` or set the AIEL_TOKEN env var.")

def _headers() -> dict[str, str]:
    return {
        "X-API-Token": _token(),
        "X-Client": "aiel-cli",
    }

def _state() -> dict[str, Any]:
    return read_json(settings.STATE_PATH, {})

def _index() -> dict[str, Any]:
    return read_json(settings.INDEX_PATH, {"version": 1, "staged": {}})

def _save_state(s: dict[str, Any]) -> None:
    write_json(settings.STATE_PATH, s)

def _save_index(ix: dict[str, Any]) -> None:
    write_json(settings.INDEX_PATH, ix)

def _base_ws_proj() -> tuple[str, str, str]:
    s = _state()

    data = list_profiles()
    profiles = data.get("profiles") or {}
    prof = None
    if profiles:
        current = _current_profile(data)
        prof = _get_profile(data, current)

    base_url = None
    if prof:
        base_url = prof.get("base_url")
    if not base_url:
        base_url = s.get("base_url") or get_current_base_url()
    if not base_url:
        raise CliError(
            "Missing base_url for the active profile.",
            hint="Run `aiel auth login` to select or create a profile.",
        )

    ws = s.get("workspace_id")
    proj = s.get("project_id")
    if not ws and prof:
        ws = (prof.get("workspace") or {}).get("id")
    if not proj and prof:
        proj = (prof.get("project") or {}).get("id")

    if not ws or not proj:
        raise CliError(
            "Workspace or project is not configured.",
            hint="Run `aiel config set workspace <slug>` before repo operations.",
        )

    return base_url.rstrip("/"), ws, proj

def _dp_get_manifest(client: httpx.Client) -> dict[str, Any]:
    base_url, ws, proj = _base_ws_proj()
    r = client.get(f"{base_url}/v1/workspaces/{ws}/projects/{proj}/files", headers=_headers())
    r.raise_for_status()
    return r.json()

def _manifest_to_map(manifest: dict[str, Any]) -> dict[str, Any]:
    # your DP returns {files:[{path,version,...}]}
    files = manifest.get("files") or []
    out: dict[str, Any] = {}
    for f in files:
        out[f["path"]] = f
    return out

def _dp_sign_download(client: httpx.Client, path: str, expires_seconds: int = 600) -> dict[str, Any]:
    base_url, ws, proj = _base_ws_proj()
    r = client.post(
        f"{base_url}/v1/workspaces/{ws}/projects/{proj}/downloads:sign",
        params={"path": path},
        headers=_headers(),
        json={"expires_seconds": expires_seconds},
    )
    r.raise_for_status()
    return r.json()

def _dp_sign_upload(client: httpx.Client, path: str, content_type: str, expected_version: Optional[int], size_bytes: int, sha256: str) -> dict[str, Any]:
    base_url, ws, proj = _base_ws_proj()
    r = client.post(
        f"{base_url}/v1/workspaces/{ws}/projects/{proj}/uploads:sign",
        params={"path": path},
        headers=_headers(),
        json={
            "content_type": content_type,
            "expected_version": expected_version,
            "size_bytes": size_bytes,
            "sha256": sha256,
        },
    )
    r.raise_for_status()
    return r.json()

def _gcs_put_signed_url(signed_url: str, content_type: str, data: bytes) -> None:
    # IMPORTANT: this is direct to GCS; no X-API-Token.
    r = httpx.put(
        signed_url,
        headers={"Content-Type": content_type},
        content=data,
        timeout=60.0,
    )
    r.raise_for_status()

def _dp_commit_upload(client: httpx.Client, upload_id: str, expected_version: Optional[int] = None) -> dict[str, Any]:
    base_url, _ws, _proj = _base_ws_proj()
    payload = {}
    if expected_version is not None:
        payload["expected_version"] = expected_version
    r = client.post(
        f"{base_url}/v1/uploads/{upload_id}:commit",
        headers=_headers(),
        json=payload,
    )
    r.raise_for_status()
    return r.json()

def _dp_delete_file(client: httpx.Client, path: str) -> dict[str, Any]:
    base_url, ws, proj = _base_ws_proj()
    r = client.delete(
        f"{base_url}/v1/workspaces/{ws}/projects/{proj}/files/{path}",
        headers=_headers(),
    )
    r.raise_for_status()
    return r.json()
