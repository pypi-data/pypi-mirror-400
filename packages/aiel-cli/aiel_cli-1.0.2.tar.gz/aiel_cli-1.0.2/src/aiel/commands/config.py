"""
AIEL CLI — Configuration Management (`aiel config`)

This module provides interactive configuration features for the AIEL CLI, allowing
the user to select and persist:

  • Active workspace
  • Active project within that workspace

Configuration is stored inside the same profile structure created by `aiel auth`,
and persisted securely via `write_json_secure`.

Key features implemented here:
  - Read, update, and store configuration values per profile
  - Prompt-driven selection of workspaces and projects
  - Arrow-key terminal UI using `questionary.select`
  - Graceful exit codes for CI and scripting contexts
  - Validation and cross-checking against `/v1/auth/me` workspace/project lists

UX Guidelines:
  • Workspace selection always comes before project selection
  • Project selection may be auto-selected if only one exists
  • Interactive prompts automatically handle cancellation (Esc/Ctrl+C → exit code 130)
  • Safe persistence ensures JSON is written atomically and without leaking tokens

Nothing in this module performs authentication; it strictly manages local config.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable, TypeVar

import typer
from rich.console import Console
from rich.text import Text
import questionary

from aiel.auth.credentials import (
    list_profiles,
    write_json_secure,
    resolve_token,
    CREDENTIALS_PATH,
    _get_me
)
from ..cli_utils import friendly_errors

console = Console()

# Root command for config management
app = typer.Typer(
    no_args_is_help=True,
    help=(
        "Manage CLI configuration.\n\n"
        "Configuration values (workspace/project) are stored per profile, enabling "
        "multi-environment workflows such as dev/staging/production."
    ),
)

# Nested command group: `aiel config set`
set_app = typer.Typer(
    no_args_is_help=True,
    help=(
        "Set or update CLI configuration values.\n"
        "Examples:\n"
        "  • aiel config set workspace onboarding_team2\n"
        "  • aiel config set project my_project\n"
    )
)

app.add_typer(set_app, name="set")

T = TypeVar("T", bound=Dict[str, Any])


def _current_profile(data: Dict[str, Any]) -> str:
    """
    Return the currently active profile name.

    Falls back to "default" if not explicitly set.
    """
    return data.get("current_profile") or "default"


def _get_profile(data: Dict[str, Any], name: str) -> Dict[str, Any]:
    """
    Retrieve the profile dictionary for the given profile name.

    Returns an empty dict if the profile does not exist, allowing safe mutation.
    """
    return (data.get("profiles") or {}).get(name) or {}


def _save_profile(data: Dict[str, Any], name: str, profile: Dict[str, Any]) -> None:
    """
    Persist updated profile configuration to the credentials file.

    Uses secure JSON writer to ensure atomic writes and prevent corruption.
    """
    profiles = data.get("profiles") or {}
    profiles[name] = profile
    data["profiles"] = profiles
    write_json_secure(CREDENTIALS_PATH, data)


def _q_select(
    *,
    prompt: str,
    rows: List[T],
    label_fn: Callable[[T], str],
    key_fn: Callable[[T], str],
) -> T:
    """
    Render an interactive arrow-key selection prompt using questionary.

    Arguments:
        prompt: UI prompt string shown to user.
        rows: list of dictionaries representing selectable items.
        label_fn: maps a row to a readable text label for display.
        key_fn: maps a row to a stable unique key used as internal value.

    Behavior:
        - User navigates with ↑/↓ and confirms with Enter.
        - Returns the selected row.
        - If user cancels (Esc/Ctrl+C), exits with code 130.
        - If rows is empty, exits with code 2.

    This helper ensures a consistent UX across workspace and project selection.
    """
    if not rows:
        raise typer.Exit(2)

    key_to_row: Dict[str, T] = {}
    choices: List[questionary.Choice] = []

    for r in rows:
        k = str(key_fn(r))
        key_to_row[k] = r
        choices.append(questionary.Choice(title=str(label_fn(r)), value=k))

    selected_key = questionary.select(
        prompt,
        choices=choices,
        use_shortcuts=True,  # allows character-based jumping
        qmark="",
        pointer="➜",
    ).ask()

    if selected_key is None:
        raise typer.Exit(130)  # user aborted interaction

    chosen = key_to_row.get(str(selected_key))
    if not chosen:
        console.print("[red]Invalid selection.[/red]")
        raise typer.Exit(2)

    return chosen


@app.command("list")
@friendly_errors
def list_cmd() -> None:
    """
    Display the currently active profile’s configuration.

    Shows:
      - Active profile name
      - Selected workspace (name + slug)
      - Selected project (name + slug)

    If values are not configured, output indicates they are unset.
    """
    data = list_profiles()
    current = _current_profile(data)
    prof = _get_profile(data, current)

    ws = prof.get("workspace") or {}
    pr = prof.get("project") or {}

    console.print(Text(f"Active profile: {current}", style="bold"))
    if ws:
        console.print(f"Workspace: [bold]{ws.get('name','')}[/bold] ([dim]{ws.get('slug','')}[/dim])")
    else:
        console.print("Workspace: [dim]not set[/dim]")

    if pr:
        console.print(f"Project:   [bold]{pr.get('name','')}[/bold] ([dim]{pr.get('slug','')}[/dim])")
    else:
        console.print("Project:   [dim]not set[/dim]")


@set_app.command("workspace")
@friendly_errors
def set_workspace_cmd(
    workspace: str = typer.Argument(
        ...,
        help=(
            "Workspace slug to select for this profile.\n"
            "The CLI validates this against the authenticated user's /v1/auth/me workspace list."
        ),
    )
) -> None:
    """
    Set the active workspace and optionally choose a default project.

    Workflow:
      1. Loads authenticated user metadata via /v1/auth/me
      2. Validates the provided workspace slug
      3. If workspace has multiple projects → prompts the user to select one
      4. Saves workspace + project into the current profile

    Notes:
      - If workspace has no projects, the project field is cleared.
      - If only one project exists, it is auto-selected.
      - Selection uses interactive arrow-key UI via questionary.
    """
    data = list_profiles()
    current = _current_profile(data)
    prof = _get_profile(data, current)

    me = _get_me(prof)
    workspaces = me.get("workspaces") or []
    if not workspaces:
        console.print("[red]No workspaces returned by /v1/auth/me.[/red]")
        raise typer.Exit(2)

    ws = next((w for w in workspaces if w.get("slug") == workspace), None)
    if not ws:
        available = ", ".join(sorted([w.get("slug", "") for w in workspaces if w.get("slug")]))
        console.print(f"[red]Workspace slug not found:[/red] {workspace}")
        if available:
            console.print(f"[dim]Available workspaces:[/dim] {available}")
        raise typer.Exit(2)

    projects = ws.get("projects") or []
    chosen_project: Optional[Dict[str, Any]] = None

    if not projects:
        console.print("[yellow]This workspace has no projects. Workspace will be set; project cleared.[/yellow]")
    elif len(projects) == 1:
        chosen_project = projects[0]
    else:
        chosen_project = _q_select(
            prompt=f"Select default project for workspace '{ws.get('slug','')}' (↑/↓ then Enter):",
            rows=projects,
            key_fn=lambda p: str(p.get("slug") or p.get("id")),
            label_fn=lambda p: f"{p.get('name','')}  ({p.get('slug','')})",
        )

    prof["workspace"] = {"id": ws["id"], "slug": ws["slug"], "name": ws.get("name")}

    if chosen_project:
        prof["project"] = {
            "id": chosen_project["id"],
            "slug": chosen_project["slug"],
            "name": chosen_project.get("name"),
        }
    else:
        prof.pop("project", None)

    _save_profile(data, current, prof)

    console.print(Text("✅ Workspace selected", style="bold"))
    console.print(f"Workspace: [bold]{ws.get('name')}[/bold] ([dim]{ws.get('slug')}[/dim])")
    if chosen_project:
        console.print(f"Default project: [bold]{chosen_project.get('name')}[/bold] ([dim]{chosen_project.get('slug')}[/dim])")


@set_app.command("project")
@friendly_errors
def set_project_cmd(
    project: Optional[str] = typer.Argument(
        None,
        help=(
            "Project slug. If omitted, you will be prompted to select one.\n"
            "Uses the currently selected workspace saved in this profile."
        ),
    )
) -> None:
    """
    Set the default project for the active workspace.

    Behavior:
      • Requires that a workspace is already selected
      • If project slug is provided → validates it
      • If omitted:
          - auto-selects if only one project exists
          - otherwise shows an interactive prompt
      • Persists project selection into the current profile
    """
    data = list_profiles()
    current = _current_profile(data)
    prof = _get_profile(data, current)

    ws_saved = prof.get("workspace")
    if not ws_saved:
        console.print("[yellow]No workspace selected yet. Run:[/yellow] aiel config set workspace")
        raise typer.Exit(2)

    me = _get_me(prof)
    workspaces = me.get("workspaces") or []

    active_ws = next(
        (w for w in workspaces if w.get("id") == ws_saved.get("id") or w.get("slug") == ws_saved.get("slug")),
        None,
    )
    if not active_ws:
        console.print("[red]Selected workspace is no longer available for this user.[/red]")
        raise typer.Exit(2)

    projects = active_ws.get("projects") or []
    if not projects:
        console.print("[red]No projects available in this workspace.[/red]")
        raise typer.Exit(2)

    # Direct slug selection OR interactive selection
    if project:
        chosen = next((p for p in projects if p.get("slug") == project), None)
        if not chosen:
            console.print(f"[red]Project slug not found in this workspace:[/red] {project}")
            raise typer.Exit(2)
    elif len(projects) == 1:
        chosen = projects[0]
    else:
        chosen = _q_select(
            prompt=f"Select default project for workspace '{active_ws.get('slug','')}' (↑/↓ then Enter):",
            rows=projects,
            key_fn=lambda p: str(p.get("slug") or p.get("id")),
            label_fn=lambda p: f"{p.get('name','')}  ({p.get('slug','')})",
        )

    prof["project"] = {"id": chosen["id"], "slug": chosen["slug"], "name": chosen.get("name")}
    _save_profile(data, current, prof)

    console.print(Text("✅ Default project set", style="bold"))
    console.print(f"Project: [bold]{chosen.get('name')}[/bold] ([dim]{chosen.get('slug')}[/dim])")


@set_app.command("show")
@friendly_errors
def show_default_workspace():
    """
    Developer/debug helper to confirm the command is wired correctly.

    Currently prints a static "done". In future, may expose profile config
    resolution or debugging utilities.
    """
    print("done")
