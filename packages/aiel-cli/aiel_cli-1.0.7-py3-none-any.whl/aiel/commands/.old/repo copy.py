

import typer
import time
from pathlib import Path
import hashlib
from ..config import settings
from ...utilities import (
    ensure_repo,
    walk_files,
    sha256_bytes,
    guess_content_type,
    write_json,
    now_iso

)
from ...data_plane import (
        _state, 
        _save_index,
        _index,
        _save_state,
        _dp_get_manifest,
        _manifest_to_map,
        _dp_sign_download,
        _dp_sign_upload,
        _gcs_put_signed_url,
        _dp_commit_upload,
        _dp_delete_file
    )
app = typer.Typer(help="Commit-related commands")

import httpx

@app.command("status")
def status():
    """
    Show staged + unstaged changes (minimal).
    """
    ensure_repo()
    s = _state()
    ix = _index()

    last = s.get("last_manifest") or {}
    staged = ix.get("staged") or {}

    # compute working tree changes vs last_manifest (by sha256)
    changed: list[str] = []
    for p in walk_files(Path(".")):
        rel = p.as_posix()
        b = p.read_bytes()
        sha = sha256_bytes(b)
        remote_sha = (last.get(rel) or {}).get("sha256")
        if remote_sha and remote_sha != sha:
            changed.append(rel)
        if not remote_sha:
            # new file not in remote snapshot
            changed.append(rel)

    typer.echo("=== Staged ===")
    if not staged:
        typer.echo("(none)")
    else:
        for path, info in staged.items():
            typer.echo(f"{info.get('op')}  {path}")

    typer.echo("\n=== Unstaged working tree changes (vs last pull snapshot) ===")
    if not changed:
        typer.echo("(none)")
    else:
        for p in sorted(set(changed)):
            if p in staged:
                continue
            typer.echo(f"modified/new  {p}")


@app.command("init")
def init(
    base_url: str = typer.Option(..., help="DP base URL, e.g. http://localhost:8000"),
    workspace_id: str = typer.Option(...),
    project_id: str = typer.Option(...),
):
    """Initialize .aiel metadata in the current directory."""
    settings.AIEL_DIR.mkdir(exist_ok=True)
    settings.COMMITS_DIR.mkdir(exist_ok=True)

    state = {
        "version": 1,
        "base_url": base_url.rstrip("/"),
        "workspace_id": workspace_id,
        "project_id": project_id,
        "last_pull_at": None,
        "last_manifest": {},
        "pending_commit_id": None,
    }
    index = {"version": 1, "staged": {}}

    write_json(settings.STATE_PATH, state)
    write_json(settings.INDEX_PATH, index)

    typer.echo("✅ Initialized .aiel/")
    typer.echo("Next: aiel pull")


@app.command("add")
def add(path: str = typer.Argument(".", help="File path or '.'")):
    """
    Stage a file or all files under '.' into .aiel/index.json.
    """
    ensure_repo()
    s = _state()
    ix = _index()
    last = s.get("last_manifest") or {}

    targets: list[Path]
    if path == ".":
        targets = walk_files(Path("."))
    else:
        targets = [Path(path)]

    for p in targets:
        if not p.exists() or p.is_dir():
            continue
        rel = p.as_posix()
        b = p.read_bytes()
        sha = sha256_bytes(b)
        size = len(b)
        ctype = guess_content_type(rel)

        remote = last.get(rel) or {}
        expected_version = remote.get("version")
        if expected_version is None:
            expected_version = 0  # new file

        ix["staged"][rel] = {
            "op": "upsert",
            "sha256": sha,
            "size_bytes": size,
            "content_type": ctype,
            "expected_version": int(expected_version),
        }
        typer.echo(f"➕ staged {rel}")

    _save_index(ix)




@app.command("commit")
def commit(message: str = typer.Option("", "-m", help="Commit message")):
    """
    Snapshot staging into a local commit file (does not push).
    """
    ensure_repo()
    ix = _index()
    staged = ix.get("staged") or {}
    if not staged:
        raise typer.BadParameter("Nothing staged. Run: aiel add ...")

    commit_id = f"c_{time.strftime('%Y%m%d_%H%M%S', time.gmtime())}_{hashlib.sha1(str(time.time()).encode()).hexdigest()[:6]}"
    commit_doc = {
        "commit_id": commit_id,
        "message": message or "",
        "created_at": now_iso(),
        "staged": staged,
    }
    write_json(settings.COMMITS_DIR / f"{commit_id}.json", commit_doc)

    s = _state()
    s["pending_commit_id"] = commit_id
    _save_state(s)

    typer.echo(f"✅ commit created: {commit_id}")
    typer.echo("Next: aiel push")

@app.command("pull")
def pull():
    """
    Pull remote files to local working tree:
      - GET manifest
      - for each path: downloads:sign + GET signed_url + write file
      - update state.last_manifest
    """
    ensure_repo()
    with httpx.Client(timeout=30.0) as client:
        manifest = _dp_get_manifest(client)
        m = _manifest_to_map(manifest)

        for path in sorted(m.keys()):
            signed = _dp_sign_download(client, path)
            url = signed["signed_url"]

            # download bytes directly
            rr = httpx.get(url, timeout=60.0)
            rr.raise_for_status()

            # write to disk
            out_path = Path(path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(rr.content)

            typer.echo(f"⬇️  {path}")

        s = _state()
        s["last_pull_at"] = now_iso()
        s["last_manifest"] = m
        _save_state(s)

    typer.echo("✅ Pull complete")


@app.command("push")
def push():
    """
    Push staged changes:
      - GET remote manifest (fresh)
      - for each upsert: sign -> PUT signed_url -> commit
      - for each delete: DELETE
      - GET remote manifest again and update state
      - clear staging on success
    """
    ensure_repo()
    ix = _index()
    staged = dict(ix.get("staged") or {})
    if not staged:
        raise typer.BadParameter("Nothing staged to push. Run: aiel add ...")

    with httpx.Client(timeout=30.0) as client:
        # fresh remote
        remote_manifest = _dp_get_manifest(client)
        remote = _manifest_to_map(remote_manifest)

        # apply staged
        for path, info in staged.items():
            op = info.get("op")
            if op == "upsert":
                # read current bytes
                p = Path(path)
                if not p.exists():
                    raise typer.BadParameter(f"Missing local file: {path}")

                data = p.read_bytes()
                sha = sha256_bytes(data)
                size = len(data)
                ctype = info.get("content_type") or guess_content_type(path)

                # expected_version: prefer staged; fallback to remote
                expected_version = info.get("expected_version")
                if expected_version is None:
                    expected_version = (remote.get(path) or {}).get("version")
                    expected_version = int(expected_version) if expected_version is not None else 0

                # 1) sign
                signed = _dp_sign_upload(client, path, ctype, expected_version, size, sha)
                upload_id = signed["upload_id"]
                signed_url = signed["signed_url"]

                # 2) PUT bytes to signed_url
                _gcs_put_signed_url(signed_url, ctype, data)

                # 3) commit upload (updates CP DB index)
                res = _dp_commit_upload(client, upload_id, expected_version=None)

                typer.echo(f"⬆️  pushed {path} -> version={res.get('version')}")

            elif op == "delete":
                _dp_delete_file(client, path)
                typer.echo(f"🗑️  deleted {path}")

            else:
                raise typer.BadParameter(f"Unknown op in index: {op}")

        # refresh state
        remote2 = _dp_get_manifest(client)
        m2 = _manifest_to_map(remote2)

        s = _state()
        s["last_manifest"] = m2
        s["last_pull_at"] = now_iso()
        s["pending_commit_id"] = None
        _save_state(s)

        # clear staging
        ix["staged"] = {}
        _save_index(ix)

    typer.echo("✅ Push complete")