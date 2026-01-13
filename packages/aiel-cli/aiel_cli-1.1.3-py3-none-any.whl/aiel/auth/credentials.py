from __future__ import annotations

import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from ..utilities import read_json, write_json_secure
from ..config import settings
from .api import _validate_token
from ..errors import CliError

try:
    import keyring  # optional
except Exception:  # pragma: no cover
    keyring = None  # type: ignore


APP_NAME = "aiel"
KEYRING_SERVICE = "aiel"

def _current_profile(data: Dict[str, Any]) -> str:
    return data.get("current_profile") or "default"

def _get_profile(data: Dict[str, Any], name: str) -> Dict[str, Any]:
    return (data.get("profiles") or {}).get(name) or {}

def _config_dir() -> Path:
    # cross-platform-ish without extra deps
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", str(Path.home())))
        return base / APP_NAME
    return Path.home() / ".config" / APP_NAME


CREDENTIALS_PATH = _config_dir() / "credentials.json"


@dataclass(frozen=True)
class Profile:
    name: str
    base_url: str
    token: str
    token_source: str  # env | keyring | file


def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"version": 1, "current_profile": "default", "profiles": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_secure(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # best-effort restrictive perms on unix
    if os.name != "nt":
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0o600


def _keyring_set(profile: str, token: str) -> Tuple[bool, str]:
    if keyring is None:
        return False, "keyring-unavailable"
    keyring.set_password(KEYRING_SERVICE, profile, token)
    return True, "keyring"


def _keyring_get(profile: str) -> Optional[str]:
    if keyring is None:
        return None
    return keyring.get_password(KEYRING_SERVICE, profile)


def _keyring_del(profile: str) -> bool:
    if keyring is None:
        return False
    try:
        keyring.delete_password(KEYRING_SERVICE, profile)
        return True
    except Exception:
        return False


def resolve_token() -> Optional[Tuple[str, str]]:
    """
    Returns (token, source) or None.
    Source: env | keyring | file
    """
    env = os.environ.get("AIEL_TOKEN")
    if env:
        return env, "env"

    data = read_json(CREDENTIALS_PATH)
    current = data.get("current_profile") or "default"
    prof = (data.get("profiles") or {}).get(current)
    if not prof:
        return None

    token_ref = prof.get("token_ref")
    if isinstance(token_ref, str) and token_ref.startswith("keyring:"):
        token = _keyring_get(current)
        if token:
            return token, "keyring"

    token = prof.get("token")
    if token:
        return token, "file"

    return None


def get_current_base_url(default: str = settings.BASE_URL) -> str:
    data = read_json(CREDENTIALS_PATH)
    current = data.get("current_profile") or "default"
    prof = (data.get("profiles") or {}).get(current)
    return (prof or {}).get("base_url") or default


def save_profile(profile: str, base_url: str, token: str, email:str, tenant:str) -> str:
    data = read_json(CREDENTIALS_PATH)
    data.setdefault("profiles", {})

    ok, token_source = _keyring_set(profile, token)
    if ok:
        data["profiles"][profile] = {"base_url": base_url, "token_ref": f"keyring:{APP_NAME}:{profile}", "user": email, "tenant": tenant}
    else:
        # fallback to file storage (less secure, but works everywhere)
        data["profiles"][profile] = {"base_url": base_url, "token": token, "user": email, "tenant": tenant }

    data["current_profile"] = profile
    write_json_secure(CREDENTIALS_PATH, data)
    return token_source


def delete_profile(profile: str) -> None:
    data = read_json(CREDENTIALS_PATH)
    profiles = data.get("profiles") or {}
    profiles.pop(profile, None)
    data["profiles"] = profiles

    if data.get("current_profile") == profile:
        data["current_profile"] = "default"

    write_json_secure(CREDENTIALS_PATH, data)
    _keyring_del(profile)


def list_profiles() -> Dict[str, Any]:
    return read_json(CREDENTIALS_PATH)


def _get_me(profile: Dict[str, Any]) -> Dict[str, Any]:
    base_url = profile.get("base_url")
    if not base_url:
        raise CliError(
            "Missing base_url in credentials profile.",
            hint="Run `aiel auth login` to create or select a profile.",
        )

    # IMPORTANT: pass token_ref. Your previous version called resolve_token() with no args.
    resolved = resolve_token()

    # Support both return shapes:
    # - token (str)
    # - (token, source)
    if isinstance(resolved, tuple):
        token = resolved[0]
    else:
        token = resolved

    if not token:
        raise CliError(
            "Missing credentials for the active profile.",
            hint="Run `aiel auth login` or set AIEL_TOKEN.",
        )

    return _validate_token(base_url, token)
