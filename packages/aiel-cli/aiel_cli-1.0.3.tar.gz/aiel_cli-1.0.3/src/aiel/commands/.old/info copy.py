from __future__ import annotations

import typer
from rich.console import Console


from aiel.auth.credentials import (
    list_profiles,
    _get_me,
    _current_profile,
    _get_profile
)
from ...utilities import profile_is_set, workspace_is_set, pick_slug_name, format_workspaces_with_projects, default_workspace

console = Console()

app = typer.Typer(no_args_is_help=True, help="Manage CLI configuration")
set_app = typer.Typer(no_args_is_help=True, help="Set config values")
app.add_typer(set_app, name="")


@set_app.command("workspace", help="help", rich_help_panel="HELP")
def show_default_workspace():
    profile = list_profiles()
    active_workspace = default_workspace(profile)
    if not active_workspace:
         return False
    
    for k in ("user", "tenant", "workspace", "project"):
        console.print(f"[bold]{k}[/bold][dim] {pick_slug_name(active_workspace.get(k))}[/dim]")

@set_app.command("workspaces")
def show_all_workspaces():
    data = list_profiles()
    current = _current_profile(data)
    prof = _get_profile(data, current)
    me = _get_me(prof)
    for k in ("email", "tenant_name", "workspaces"):
            console.print(f"[bold]{k}[/bold] {format_workspaces_with_projects(me.get(k))}")

@set_app.command("projects")
def show_all_workspaces():
    data = list_profiles()
    current = _current_profile(data)
    prof = _get_profile(data, current)
    me = _get_me(prof)
    for k in ("email", "tenant_name", "workspaces"):
            console.print(f"[bold]{k}[/bold] {format_workspaces_with_projects(me.get(k))}")

