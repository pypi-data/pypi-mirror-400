"""
AIEL CLI — Workspace & Project Introspection (`aiel info`)

This module exposes read-only commands that print *who you are* and *where you are*
in the AIEL environment, based entirely on the currently active profile.

It surfaces three main views:

  • `workspace`   — Show the active user, tenant, workspace, and project in a compact form.
  • `workspaces`  — Show all workspaces (and their projects) available to the current user.
  • `projects`    — Same structured view as `workspaces`, focused on project visibility.

All commands:

  - Read profile data from `list_profiles()`
  - Use `_get_me(...)` to call `/v1/auth/me` (or equivalent) and obtain the canonical
    user + tenant + workspace list
  - Format output using helper functions from `utilities`, including:
        • `pick_slug_name(...)`               → selects a slug/name representation
        • `format_workspaces_with_projects`   → renders workspaces + projects nicely
        • `default_workspace(...)`            → resolves the effective active workspace

These commands do **not** mutate configuration or server-side state; they are
intended for quick inspection and for helping users debug which workspace and
project they are currently targeting.
"""

from __future__ import annotations

import typer
from rich.console import Console

from aiel.auth.credentials import _current_profile, _get_me, _get_profile, list_profiles
from ..utilities import format_workspaces_with_projects, pick_slug_name, profile_is_set, workspace_is_set, default_workspace
from ..cli_utils import friendly_errors

console = Console()

# Root command group for this module. In the main CLI, this is usually mounted
# under `aiel info`.
app = typer.Typer(no_args_is_help=True, help="Inspect the active workspace context.")

# Sub-group used here purely as a container for the concrete commands defined
# below. The name is left empty so the commands sit directly under `aiel info`.
set_app = typer.Typer(no_args_is_help=True, help="Context inspection helpers.")
app.add_typer(set_app, name="")


@set_app.command("workspace", help="Show resolved workspace/project context.", rich_help_panel="Context")
@friendly_errors
def show_default_workspace() -> None:
    """
    Show the currently active workspace context for the active profile.

    Output includes:
      - user
      - tenant
      - workspace
      - project

    For each of these keys, the function calls `pick_slug_name(...)` on the
    corresponding value from `default_workspace(profile)` and prints a concise,
    human-readable representation.

    Behavior:
      - If no active workspace context can be resolved, returns False silently.
      - Otherwise, prints one line per key using Rich formatting.
    """
    profile = list_profiles()
    active_workspace = default_workspace(profile)
    if not active_workspace:
         return False
    
    for k in ("user", "tenant", "workspace", "project"):
        console.print(f"[bold]{k}[/bold][dim] {pick_slug_name(active_workspace.get(k))}[/dim]")


@set_app.command("workspaces")
@friendly_errors
def show_all_workspaces() -> None:
    """
    Show all workspaces available to the current user, including projects.

    Logic:
      1. Resolve current profile from stored profiles.
      2. Call `_get_me(...)` to obtain the canonical user payload.
      3. For each of the keys: "email", "tenant_name", "workspaces":
           - Call `format_workspaces_with_projects(me.get(k))`
           - Print a Rich-formatted line combining the key + formatted value.

    This gives a quick overview of:
      - which user is authenticated
      - which tenant the user belongs to
      - which workspaces/projects are assigned to that user
    """
    data = list_profiles()
    current = _current_profile(data)
    prof = _get_profile(data, current)
    me = _get_me(prof)
    for k in ("email", "tenant_name", "workspaces"):
            console.print(f"[bold]{k}[/bold] {format_workspaces_with_projects(me.get(k))}")


@set_app.command("projects")
@friendly_errors
def show_all_projects() -> None:
    """
    Show all projects grouped by workspace for the current user.

    Implementation detail:
      - Shares the same internal structure as `workspaces`, intentionally
        reusing `format_workspaces_with_projects(...)` to avoid duplication.

    The repeated loop over:
      ("email", "tenant_name", "workspaces")

    allows downstream formatting to decide how to highlight projects vs
    workspaces while still giving context on the authenticated user and tenant.
    """
    data = list_profiles()
    current = _current_profile(data)
    prof = _get_profile(data, current)
    me = _get_me(prof)
    for k in ("email", "tenant_name", "workspaces"):
            console.print(f"[bold]{k}[/bold] {format_workspaces_with_projects(me.get(k))}")
