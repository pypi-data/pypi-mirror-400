import json
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, Tuple
import typer
import os
import stat
from rich.console import Console
from dataclasses import dataclass
from .config import settings
AIEL_DIR = Path(".aiel")
STATE_PATH = AIEL_DIR / "state.json"
INDEX_PATH = AIEL_DIR / "index.json"
COMMITS_DIR = AIEL_DIR / "commits"

REQUIRED_PROFILE_FIELDS = ("base_url", "token_ref")
REQUIRED_WP_PR_FIELDS = ("slug", "id")
console = Console()
# -------------------------
# Utilities (local files)
# -------------------------
def ensure_repo() -> None:
    if not settings.STATE_PATH.exists():
        raise typer.BadParameter("Not initialized. Run: aiel init ...")
    settings.AIEL_DIR.mkdir(exist_ok=True)
    settings.COMMITS_DIR.mkdir(exist_ok=True)
    return

def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text("utf-8"))

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), "utf-8")

def write_json_secure(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # best-effort restrictive perms on unix
    if os.name != "nt":
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0o600

def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def guess_content_type(path: str) -> str:
    p = Path(path)
    ext = p.suffix.lower()
    if ext == ".py":
        return "text/x-python"
    if ext == ".json":
        return "application/json"
    if ext in (".yaml", ".yml"):
        return "text/yaml"
    return "text/plain; charset=utf-8"

def walk_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        # ignore .aiel internal files
        if str(p).startswith(".aiel/") or str(p) == ".aiel":
            continue
        out.append(p)
    return out

def profile_is_set(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Returns (ok, reason). ok=False means user hasn't configured auth/profile yet.
    """
    profiles = data.get("profiles") or {}
    if not isinstance(profiles, dict) or not profiles:
        return False, "No profiles found"

    current = data.get("current_profile") or "default"
    prof = profiles.get(current)
    if not isinstance(prof, dict):
        return False, f"Current profile '{current}' not found"

    missing = [k for k in REQUIRED_PROFILE_FIELDS if not prof.get(k)]
    if missing:
        return False, f"Profile '{current}' missing: {', '.join(missing)}"

    return True, "OK"

def workspace_is_set(data: Dict[str, Any], field:str = 'workspace') -> Tuple[bool, str]:
    """
    Returns (ok, reason). ok=False means user hasn't configured auth/profile yet.
    """
    workspace = data.get(field) or {}
    if not isinstance(workspace, dict) or not workspace:
        return False, "No default workspace found"

    missing = [k for k in REQUIRED_WP_PR_FIELDS if not workspace.get(k)]
    if missing:
        return False, f"{field} '{workspace}' missing: {', '.join(missing)}"

    return True, "OK"

def pick_slug_name(v):
    if isinstance(v, dict):
        return f"\n  - slug: {v.get('slug')} \n  - name: {v.get('name')}"
    return v

def format_workspaces_with_projects(workspaces: Any) -> str:
    if not isinstance(workspaces, list):
        return str(workspaces)

    out = []
    for w in workspaces:
        if not isinstance(w, dict):
            continue
        out.append(f"\n- {w.get('name','')} [dim]({w.get('slug','')})[/dim]\n  [bold]Projects:[/bold]")

        projects = w.get("projects") or []
        if isinstance(projects, list) and projects:
            for p in projects:
                if not isinstance(p, dict):
                    continue
                out.append(f"  - {p.get('name','')} [dim]({p.get('slug','')})[/dim]")
        else:
            out.append("  - (no projects)")
    return "\n".join(out) if out else "(none)"

def format_workspaces(workspaces: Any) -> str:
    if not isinstance(workspaces, list):
        return str(workspaces)

    lines = []
    for w in workspaces:
        if not isinstance(w, dict):
            continue
        lines.append(f"- {w.get('name','')} ({w.get('slug','')})")
    return "\n".join(lines) if lines else "(none)"



def format_file_tree(manifest: Dict[str, Any]) -> str:
    # Build a nested dict tree: {"agents": {"hello.py": None, ...}, "LICENSE": None, ...}
    skip = {".DS_Store"}
    root: Dict[str, Any] = {}

    for path in sorted(k for k in manifest.keys() if k.split("/")[-1] not in skip):
        parts = [p for p in path.split("/") if p]
        node = root
        for i, part in enumerate(parts):
            is_last = i == len(parts) - 1
            if is_last:
                node.setdefault(part, None)
            else:
                node = node.setdefault(part, {})

    def render(node: Dict[str, Any], prefix: str = "") -> list[str]:
        lines: list[str] = []
        items = list(node.items())
        for idx, (name, child) in enumerate(items):
            last = idx == len(items) - 1
            branch = "└── " if last else "├── "
            lines.append(prefix + branch + name)
            if isinstance(child, dict):
                ext = "    " if last else "│   "
                lines.extend(render(child, prefix + ext))
        return lines

    return "\n".join(render(root))

def default_workspace(profiles):
    is_profile_set, message = profile_is_set(profiles)
    if not is_profile_set:
         return typer.echo(f"{message}")
    
    current_profile = profiles['profiles']
    default_profile = profiles['current_profile']
    active_workspace = current_profile[default_profile]
    is_workspace_set, message_wp = workspace_is_set(active_workspace)
    is_project_set, message_pr = workspace_is_set(active_workspace, 'project')
   
    if not is_workspace_set:
        return  console.print(f"[bold]{message_wp}[/bold]\n[dim]RUN: aiel config set workspace <workspace>[/dim]")
    
    if not is_project_set:
        return typer.echo(f"{message_pr}")
    
    for k in ("user", "tenant", "workspace", "project"):
       return active_workspace
