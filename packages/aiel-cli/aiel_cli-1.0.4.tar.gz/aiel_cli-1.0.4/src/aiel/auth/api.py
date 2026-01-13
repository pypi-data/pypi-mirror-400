from __future__ import annotations

import httpx
import typer


def _validate_token(base_url: str, token: str) -> dict:
    """
    Expect your API to have something like GET /v1/me returning user info.
    If you don’t have it yet, add it—this makes CLI auth reliable.
    """
    url = base_url.rstrip("/") + "/v1/auth/me"
    headers = {"X-API-Token": f"{token}"}

    with httpx.Client(timeout=10.0) as client:
        r = client.get(url, headers=headers)
        if r.status_code >= 400:
            raise typer.BadParameter(f"Token validation failed ({r.status_code}).")
        return r.json()
