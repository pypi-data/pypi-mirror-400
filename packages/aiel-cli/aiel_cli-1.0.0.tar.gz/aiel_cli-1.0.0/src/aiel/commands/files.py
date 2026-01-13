"""
AIEL CLI — Workspace View / File Tree (`aiel workspace ls`)

This module wires a small Typer command group that surfaces a *read-only* snapshot
of the current workspace state:

  • Renders the latest file manifest as a formatted file tree
  • Shows the active workspace and project slugs
  • Prints repository metadata (last pull, pending commit, version)

It is intentionally diagnostic/observability-focused and does not mutate any
server-side state. The information displayed is derived from:

  - `data_plane._state()`:
        Returns the last known runtime/checkout state, including:
            • `last_manifest`  : the most recent file manifest
            • `last_pull_at`   : timestamp of the last pull or sync
            • `pending_commit_id`: local commit not yet pushed (if any)
            • `version`        : logical or semantic version of the checkout

  - `aiel.auth.credentials.list_profiles()`:
        Provides the stored profile data, including information needed to
        determine which workspace/project is currently active.

  - `default_workspace(...)`:
        Resolves the "active workspace context" from the credentials/profile
        data structure, returning fields like workspace and project slugs.

  - `format_file_tree(...)`:
        Takes the manifest from `_state()` and produces a human-readable,
        Rich-friendly tree representation of the files in the current workspace.

Typical usage (from the CLI):

    aiel workspace ls

This gives users and operators a quick, human-friendly view of:
  • Which workspace/project they are currently targeting
  • What files are present in that workspace manifest
  • Repo metadata useful for debugging sync and versioning issues
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from ..data_plane import _state
from aiel.auth.credentials import list_profiles
from ..utilities import format_file_tree, default_workspace

console = Console()

# Root Typer app for this module. In the main CLI, this is typically mounted under
# a higher-level namespace (for example: `aiel workspace`).
app = typer.Typer(no_args_is_help=True, help="Manage CLI configuration")

# Sub-app used for attaching concrete commands. In this module, `ls` is exposed
# through this `set_app` instance.
set_app = typer.Typer(no_args_is_help=True, help="Set config values")
app.add_typer(set_app, name="")


@set_app.command("ls", help=" Display the current workspace file tree and related metadata.", rich_help_panel="Repo information")
def show_files_updated():
    """
    Display the current workspace file tree and related metadata.

    Output sections:
        1. Files information:
           - Uses `data_plane._state()` to fetch the latest manifest.
           - Renders the manifest via `format_file_tree(...)` as a Rich-friendly
             tree view, giving a quick visual overview of the workspace files.

        2. Project information:
           - Resolves the active workspace context via `default_workspace(...)`,
             using the profile data from `list_profiles()`.
           - Prints workspace and project slugs so users know which logical
             environment they are inspecting.

        3. Repo information:
           - Prints a small summary panel with:
               • Last commit/pull time (`last_pull_at`)
               • Pending commit ID (if any)
               • Version value from the state (`version`)
           - This helps diagnose whether the local view is up to date and if
             there are unpushed changes.

    Notes:
        - This command is read-only; it does not modify workspace or repo state.
        - Exit codes are standard Typer defaults unless an upstream dependency
          raises or fails.
    """
    state = _state()
    profile = list_profiles()
    active_workspace = default_workspace(profile) or {}

    # FILES INFORMATION
    file_tree = format_file_tree(state.get('last_manifest'))
    console.print(file_tree)

    # PROJECT INFORMATION
    data = ["[green]Project info[/green]"]
    for k in ("workspace", "project"):
        slug = (active_workspace.get(k) or {}).get("slug", "not-set")
        data.append(f"{k}: [dim]{slug}[/dim]")
    console.print(Panel.fit("\n".join(data)))

    # REPO INFORMATION
    console.print(
        Panel.fit(
            f"[green]Repo info[/green]\n"
            f"Last commit: [dim]{state.get('last_pull_at')}[/dim]\n"
            f"Pending commit ID: [dim]{state.get('pending_commit_id')}[/dim]\n"
            f"version: [dim]{state.get('version')}[/dim]"
        )
    )
