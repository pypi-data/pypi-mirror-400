from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable, TypeVar

import typer
from rich.console import Console
from rich.panel import Panel

from ...data_plane import _state
from aiel.auth.credentials import (
    _current_profile, list_profiles
)
from ...utilities import format_file_tree, default_workspace
from ..info import default_workspace

console = Console()

app = typer.Typer(no_args_is_help=True, help="Manage CLI configuration")
set_app = typer.Typer(no_args_is_help=True, help="Set config values")
app.add_typer(set_app, name="")

@set_app.command("ls", help="help", rich_help_panel="HELP")
def show_files_updated():
    state = _state()
    profile = list_profiles()
    active_workspace = default_workspace(profile)

    ## FILES INFORMATION
    file_tree = format_file_tree(state.get('last_manifest'))
    console.print(file_tree)
    ## PROJECT INFORMATION
    data = ["[green]Project info[/green]"]
    for k in ("workspace", "project"):
        data.append(f"{k}: [dim]{active_workspace.get(k)['slug']}[/dim]")
    console.print(Panel.fit("\n".join(data)))

    ## REPO INFORMATION
    console.print(
    Panel.fit(
            f"[green]Repo info[/green]\n"
            f"Last commit: [dim]{state.get('last_pull_at')}[/dim]\n"
            f"Pending commit ID: [dim]{state.get('pending_commit_id')}[/dim]\n"
            f"version: [dim]{state.get('version')}[/dim]"
        )
    )