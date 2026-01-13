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

console = Console()

app = typer.Typer(no_args_is_help=True, help="Manage CLI configuration")
set_app = typer.Typer(no_args_is_help=True, help="Set config values")
app.add_typer(set_app, name="set")

T = TypeVar("T", bound=Dict[str, Any])


def _current_profile(data: Dict[str, Any]) -> str:
    return data.get("current_profile") or "default"


def _get_profile(data: Dict[str, Any], name: str) -> Dict[str, Any]:
    return (data.get("profiles") or {}).get(name) or {}


def _save_profile(data: Dict[str, Any], name: str, profile: Dict[str, Any]) -> None:
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
    Arrow-key selection using questionary.select (inline terminal UI).

    Returns the selected row (dict).
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
        use_shortcuts=True,   # lets user type to jump
        qmark="",
        pointer="➜",
    ).ask()

    # None = user cancelled (Esc / Ctrl+C)
    if selected_key is None:
        raise typer.Exit(130)

    chosen = key_to_row.get(str(selected_key))
    if not chosen:
        console.print("[red]Invalid selection.[/red]")
        raise typer.Exit(2)

    return chosen


@app.command("list")
def list_cmd() -> None:
    """Show current config (workspace/project) for the active profile."""
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
def set_workspace_cmd(
    workspace: str = typer.Argument(
        ...,
        help="Workspace slug (required). Example: onboarding_team2",
    )
) -> None:
    """Set the active workspace (required) and then pick a default project (prompted)."""
    data = list_profiles()
    current = _current_profile(data)
    prof = _get_profile(data, current)

    me = _get_me(prof)
    workspaces = me.get("workspaces") or []
    if not workspaces:
        console.print("[red]No workspaces returned by /v1/auth/me.[/red]")
        raise typer.Exit(2)

    # Validate workspace slug (required)
    ws = next((w for w in workspaces if w.get("slug") == workspace), None)
    if not ws:
        available = ", ".join(sorted([w.get("slug", "") for w in workspaces if w.get("slug")]))
        console.print(f"[red]Workspace slug not found:[/red] {workspace}")
        if available:
            console.print(f"[dim]Available workspaces:[/dim] {available}")
        raise typer.Exit(2)

    # Pick default project within workspace (prompted)
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

    # Persist
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
def set_project_cmd(
    project: Optional[str] = typer.Argument(
        None,
        help="Project slug. If omitted, you will be prompted to choose.",
    )
) -> None:
    """Select the default project (uses the currently selected workspace)."""
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
        console.print("[red]Selected workspace is not available for this user anymore.[/red]")
        raise typer.Exit(2)

    projects = active_ws.get("projects") or []
    if not projects:
        console.print("[red]No projects available in this workspace.[/red]")
        raise typer.Exit(2)

    # Choose project
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
def show_default_workspace():
    print("done")