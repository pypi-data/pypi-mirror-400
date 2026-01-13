"""
AIEL CLI — Commit & Sync Commands (`aiel commit ...`)

This module implements a minimal, Git-inspired workflow for synchronizing local
files with the AIEL Data Plane (DP). It operates over a local metadata directory
(`.aiel/`) and a remote manifest managed by the DP API.

High-level responsibilities:

  • Initialize repo metadata in the current directory (`init`)
  • Track local changes against the last remote snapshot (`status`)
  • Stage files into a local index (`add`)
  • Create local commit documents (without pushing them yet) (`commit`)
  • Pull remote contents into the working tree (`pull`)
  • Push staged changes to the remote data plane (`push`)

Key concepts:

  - `.aiel/state.json`:
        Tracks:
          * base_url (DP endpoint)
          * workspace_id / project_id
          * last_pull_at
          * last_manifest (remote view of files)
          * pending_commit_id (local commit not yet reconciled remotely)

  - `.aiel/index.json`:
        Tracks:
          * version
          * `staged`: operations to apply (`upsert` or `delete`), including
            expected versions, sizes, content types, and SHA-256 checksums.

  - Remote manifest:
        Obtained via `_dp_get_manifest(client)` and converted with
        `_manifest_to_map(...)`. This represents the canonical file state on
        the data plane and is used to detect divergence and version conflicts.

Security / safety considerations:

  - All network calls use `httpx.Client` with explicit timeouts.
  - SHA-256 checksums are computed for files before upload.
  - `expected_version` is used to implement optimistic concurrency and to
    guard against overwriting other writers’ changes.
"""

import typer
import time
from pathlib import Path
import hashlib
from rich.console import Console
from ..config import settings
from ..utilities import (
    ensure_repo,
    walk_files,
    load_aielignore,
    should_ignore,
    sha256_bytes,
    guess_content_type,
    write_json,
    now_iso

)
from ..data_plane import (
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
from ..cli_utils import friendly_errors
from ..errors import CliError
from ..auth.credentials import list_profiles, _current_profile, _get_profile, get_current_base_url
app = typer.Typer(help="Commit-related commands")
console = Console()

import httpx


def _print_repo_context(command: str) -> None:
    data = list_profiles()
    profiles = data.get("profiles") or {}
    if not profiles:
        return

    current = _current_profile(data)
    prof = _get_profile(data, current) or {}
    tenant = prof.get("tenant")
    workspace = (prof.get("workspace") or {}).get("slug") or (prof.get("workspace") or {}).get("name")
    project = (prof.get("project") or {}).get("slug") or (prof.get("project") or {}).get("name")

    if not any([tenant, workspace, project]):
        return

    if tenant:
        console.print(f"On tenant [bold]{tenant}[/bold]")
    console.print(f"workspace: [bold]{workspace or 'not set'}[/bold]")
    console.print(f"project: [bold]{project or 'not set'}[/bold]\n")


@app.command("status")
@friendly_errors
def status():
    """
    Show staged and unstaged changes relative to the last remote snapshot.

    Behavior:
      - Ensures the current directory is initialized as an AIEL repo.
      - Loads:
          * local state (`_state()`) for `last_manifest`
          * local index (`_index()`) for `staged` entries
      - Computes working tree changes by:
          * walking all files under the current directory
          * hashing file contents (SHA-256)
          * comparing against `last_manifest` entries

    Output:
      - "Staged" section showing operations in the local index (`upsert`/`delete`)
      - "Unstaged working tree changes" showing files that differ from the last
        pull snapshot (modified/new), excluding already staged paths.

    This command is analogous to a simplified `git status`:
      • staged   → index changes ready to commit/push
      • unstaged → local edits not yet staged with `aiel add ...`
    """
    ensure_repo()
    _print_repo_context("status")
    s = _state()
    ix = _index()

    last = s.get("last_manifest") or {}
    staged = ix.get("staged") or {}

    # compute working tree changes vs last_manifest (by sha256)
    changed: list[str] = []
    deleted: list[str] = []
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
    for rel in last.keys():
        if should_ignore(Path(rel), Path(".")):
            continue
        if not Path(rel).exists():
            deleted.append(rel)

    console.print("=== Staged ===")
    if not staged:
        console.print("(none)")
    else:
        console.print('Changes to be committed:\n\t[i](use aiel commit -m "<message>" to create the commit)[/i]\n')
        for path, info in staged.items():
            op = info.get("op")
            color = "red" if op == "delete" else "green"
            console.print(f"{op}  [{color}]{path}[/{color}]")

    console.print("\n=== Unstaged working tree changes  ===")
    if not changed and not deleted:
        console.print("(none)")
    else:
        console.print("""Changes not staged for commit: \n\t[i](use "aiel add <file>..." to update what will be committed)[/i]\n\t[i](use "aiel add ." to update all changed files[/i]\n""")
        for p in sorted(set(changed)):
            if p in staged:
                continue
            console.print(f"modified/new  [red]{p}[/red]")
        for p in sorted(set(deleted)):
            if p in staged:
                continue
            console.print(f"deleted       [red]{p}[/red]")


@app.command("init")
@friendly_errors
def init(
    workspace_id: str | None = typer.Option(None, help="Workspace ID (optional if configured via aiel config)."),
    project_id: str | None = typer.Option(None, help="Project ID (optional if configured via aiel config)."),
):
    """
    Initialize `.aiel/` metadata in the current directory for AIEL sync operations.

    Creates:
      - `.aiel/state.json` with:
          • version
          • normalized base_url (from the active auth profile)
          • workspace_id + project_id (from args or active config)
          • last_pull_at = None
          • last_manifest = {}
          • pending_commit_id = None
      - `.aiel/index.json` with:
          • version
          • empty `staged` dict

    After running this for the first time, the typical flows are:
      - `aiel config set workspace ...` → set workspace/project if not already set
      - `aiel pull`   → to populate working tree from remote
      - `aiel add`    → to stage local changes
      - `aiel commit` → to snapshot staged changes locally
      - `aiel push`   → to send changes to the data plane
    """
    if settings.STATE_PATH.exists() and settings.INDEX_PATH.exists():
        typer.echo("✅ Repo already initialized.")
        _print_repo_context("init")
        typer.echo("Next: aiel config set workspace <slug>")
        return

    data = list_profiles()
    profiles = data.get("profiles") or {}
    if not profiles:
        raise CliError(
            "No auth profiles configured.",
            hint="Run `aiel auth login` before `aiel repo init`.",
        )

    current = _current_profile(data)
    prof = _get_profile(data, current)
    base_url = (prof.get("base_url") or get_current_base_url()).strip()
    if not base_url:
        raise CliError(
            "Missing base_url for the active profile.",
            hint="Run `aiel auth login` to select or create a profile.",
        )

    if workspace_id is None:
        workspace_id = (prof.get("workspace") or {}).get("id")
    if project_id is None:
        project_id = (prof.get("project") or {}).get("id")

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

    ignore_path = Path(".aielignore")
    if not ignore_path.exists():
        ignore_path.write_text(
            "# AIEL ignore file\n"
            ".aiel/\n"
            ".venv/\n"
            "__pycache__/\n"
            ".pytest_cache/\n"
            ".mypy_cache/\n"
            ".DS_Store\n",
            encoding="utf-8",
        )

    _print_repo_context("init")
    typer.echo("✅ Initialized .aiel/")
    if not workspace_id or not project_id:
        typer.echo("Next: aiel config set workspace <slug>")
        return
    typer.echo("Next: aiel repo pull")


@app.command("add")
@friendly_errors
def add(path: str = typer.Argument(".", help="File path or '.'")):
    """
    Stage a file or all files under '.' into `.aiel/index.json`.

    Behavior:
      - Ensures repo is initialized (presence of `.aiel/` and state/index files).
      - Reads the last remote manifest from state.
      - Determines the target set:
          • if `path == '.'` → walks all files under the current directory
          • else             → stages the specific file path (if it exists)

      For each file:
        - Skips directories and non-existent paths.
        - Reads bytes and computes SHA-256 checksum.
        - Infers content type via `guess_content_type(...)`.
        - Looks up the remote manifest entry for `expected_version`:
            * if missing, uses 0 (new file)
        - Adds an `upsert` entry into `index["staged"]`:
            * op: "upsert"
            * sha256
            * size_bytes
            * content_type
            * expected_version

    Notes:
      - This only modifies the local index, not the remote data plane.
      - To persist staged changes as a logical commit use `aiel commit`.
      - To send changes to the DP backend, run `aiel push`.
    """
    ensure_repo()
    _print_repo_context("add")
    s = _state()
    ix = _index()
    last = s.get("last_manifest") or {}

    targets: list[Path]
    if path == ".":
        targets = walk_files(Path("."))
    else:
        targets = [Path(path)]

    ignore_patterns = load_aielignore(Path("."))

    staged_any = False
    for p in targets:
        if p.is_dir():
            continue
        if should_ignore(p, Path("."), ignore_patterns):
            continue
        if not p.exists():
            rel = p.as_posix()
            remote = last.get(rel)
            if remote:
                ix["staged"][rel] = {
                    "op": "delete",
                    "expected_version": int(remote.get("version") or 0),
                }
                staged_any = True
                console.print(f" [red]-[/red] staged delete {rel}")
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
        remote_sha = remote.get("sha256")
        if remote_sha and remote_sha == sha:
            continue

        ix["staged"][rel] = {
            "op": "upsert",
            "sha256": sha,
            "size_bytes": size,
            "content_type": ctype,
            "expected_version": int(expected_version),
        }
        staged_any = True
        typer.echo(f"[green]+[/green] staged {rel}")

    if path == ".":
        for rel, remote in last.items():
            if should_ignore(Path(rel), Path("."), ignore_patterns):
                continue
            if not Path(rel).exists():
                ix["staged"][rel] = {
                    "op": "delete",
                    "expected_version": int(remote.get("version") or 0),
                }
                staged_any = True
                typer.echo(f"[red]-[/red]  staged delete {rel}")

    if staged_any:
        console.print('Changes to be committed:\n\t[i](use aiel commit -m "<message>" to create the commit)[/i]\n')
    _save_index(ix)


@app.command("commit")
@friendly_errors
def commit(message: str = typer.Option("", "-m", help="Commit message")):
    """
    Snapshot currently staged changes into a local commit file (does not push).

    Behavior:
      - Ensures repo is initialized.
      - Loads local index and confirms that `staged` is not empty.
      - Generates a commit_id with:
          • UTC timestamp
          • short SHA-1 suffix derived from current time
      - Writes a commit document into `.aiel/commits/`:
          {
            "commit_id",
            "message",
            "created_at",
            "staged": { ... }
          }
      - Updates state to mark `pending_commit_id` as this commit_id.

    The resulting commit:
      - Is purely local metadata.
      - Can later be associated with a `push` to the remote data plane.
      - Provides an audit trail of what was staged and when, even if the push
        fails or is deferred.
    """
    ensure_repo()
    _print_repo_context("commit")
    ix = _index()
    staged = ix.get("staged") or {}
    ignore_patterns = load_aielignore(Path("."))
    filtered = {path: info for path, info in staged.items() if not should_ignore(Path(path), Path("."), ignore_patterns)}
    if len(filtered) != len(staged):
        ix["staged"] = filtered
        _save_index(ix)
        typer.echo("⚠️  Some staged paths were ignored via .aielignore and removed from the index.")
    staged = filtered
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
    console.print('\t[i](use aiel push to upload your commits to the remote)[/i]\n')


@app.command("pull")
@friendly_errors
def pull():
    """
    Pull remote files into the local working tree.

    Steps:
      1. Ensure the current directory is an initialized AIEL repo.
      2. Use a shared `httpx.Client` with bounded timeout.
      3. Fetch the remote manifest via `_dp_get_manifest(client)` and convert to
         a path → metadata map via `_manifest_to_map(...)`.
      4. For each path in the manifest:
           - Request a signed download URL via `_dp_sign_download(client, path)`.
           - Perform a GET on the signed URL to fetch file bytes.
           - Write each file to disk (creating parent directories as needed).
      5. Update local state:
           - `last_pull_at` set to current ISO timestamp.
           - `last_manifest` updated to the new manifest map.
      6. Persist state with `_save_state(...)`.

    This is analogous to a "git pull" for a fully remote-managed tree, but
    implemented in terms of signed URLs and the AIEL data plane manifest.
    """
    ensure_repo()
    _print_repo_context("pull")
    with httpx.Client(timeout=30.0) as client:
        manifest = _dp_get_manifest(client)
        m = _manifest_to_map(manifest)

        ignore_patterns = load_aielignore(Path("."))
        for path in sorted(m.keys()):
            if should_ignore(Path(path), Path("."), ignore_patterns):
                continue
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
@friendly_errors
def push():
    """
    Push staged changes to the data plane.

    Steps:
      1. Ensure repo is initialized.
      2. Read staged entries from the local index.
      3. Use `httpx.Client` for all DP calls.
      4. Fetch a fresh remote manifest via `_dp_get_manifest(client)` and
         convert it to a map with `_manifest_to_map(...)`.
      5. For each staged path:
           - If op == "upsert":
               a. Validate local file exists.
               b. Compute SHA-256, size, and content-type.
               c. Resolve `expected_version`:
                    • prefer index value
                    • else use remote manifest version or 0
               d. Request a signed upload via `_dp_sign_upload(...)`.
               e. PUT file bytes to `signed_url` via `_gcs_put_signed_url(...)`.
               f. Commit upload via `_dp_commit_upload(...)` (updates CP index).
               g. Echo the new version to the user.
           - If op == "delete":
               a. Call `_dp_delete_file(...)`.
               b. Echo deletion to the user.
           - Else:
               a. Raise an error for unknown operations.

      6. Refresh remote manifest again (post-push) and update state:
           - `last_manifest`
           - `last_pull_at`
           - `pending_commit_id` cleared
      7. Clear `staged` entries in `.aiel/index.json` and persist.

    This is the main “write” operation of the CLI, applying local index operations
    to the remote data plane in a controlled, version-aware manner.
    """
    ensure_repo()
    _print_repo_context("push")
    ix = _index()
    staged = dict(ix.get("staged") or {})
    ignore_patterns = load_aielignore(Path("."))
    staged = {path: info for path, info in staged.items() if not should_ignore(Path(path), Path("."), ignore_patterns)}
    if not staged:
        ix["staged"] = {}
        _save_index(ix)
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
                typer.echo(f"[red]-[/red]  deleted {path}")

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
