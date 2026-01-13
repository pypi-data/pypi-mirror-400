from __future__ import annotations

"""
Primary Typer application that wires together every command group exposed by the
CLI. Commands are grouped by developer workflows (auth, config, repo, info,
files) so that new contributors can skim the layout and immediately understand
where to look for a given feature.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .commands import _index, auth, config, files, info, repo
from .roadmap import PLAN, by_sprint
from .cli_utils import friendly_errors

app = typer.Typer(no_args_is_help=True, add_completion=True)
auth_app = typer.Typer(no_args_is_help=True)

app.add_typer(
    auth.app,
    name="auth",
    help="Authenticate the CLI and manage auth profiles.",
)

app.add_typer(
    repo.app,
    name="repo",
    help="Sync local workspace files with the AIEL cloud.",
)

app.add_typer(
    config.app,
    name="config",
    help="Manage CLI configuration (workspace and project).",
)

app.add_typer(
    info.app,
    name="info",
    help="Inspect the active user, tenant, workspace, and project.",
)

app.add_typer(
    files.app,
    name="files",
    help="Browse and inspect files stored remotely in the workspace.",
)

console = Console()


def coming_soon(cmd: str) -> None:
    """
    Render a friendly roadmap panel for commands that are planned but not yet implemented.
    """
    plan = PLAN.get(cmd)
    if not plan:
        console.print(
            Panel.fit(f"[yellow]Planned[/yellow]\ncommand: [bold]{cmd}[/bold]\nsprint: [bold]TBD[/bold]\nintent: TBD")
        )
        raise typer.Exit(code=0)

    console.print(
        Panel.fit(
            f"[yellow]Planned (not implemented yet)[/yellow]\n"
            f"command: [bold]{plan.command}[/bold]\n"
            f"sprint: [bold]Sprint {plan.sprint}[/bold]\n"
            f"intent: {plan.intent}"
        )
    )
    raise typer.Exit(code=0)


@app.callback()
@friendly_errors
def main(
    debug: bool = typer.Option(False, "--debug", help="Show full tracebacks."),
) -> None:
    """
    Root callback kept for parity with `friendly_errors` helper.
    """
    if debug:
        console.print(Panel.fit("[cyan]Debug mode enabled[/cyan]\nTracebacks will be printed in full."))


@app.command()
@friendly_errors
def roadmap() -> None:
    """Show the command roadmap and sprint plan."""
    groups = by_sprint()
    for sprint, items in groups.items():
        table = Table(title=f"Sprint {sprint}")
        table.add_column("Command", style="bold")
        table.add_column("Intent")
        for p in items:
            table.add_row(p.command, p.intent)
        console.print(table)


@app.command()
@friendly_errors
def version() -> None:
    """Print CLI version and point to the roadmap entry."""
    console.print(
        Panel.fit(
            f"[green]aiel[/green] version [bold]{__version__}[/bold]\n"
            "Include this output when opening support tickets."
        )
    )
    coming_soon("aiel version")


@app.command()
@friendly_errors
def commands() -> None:
    """Show every command grouped by logical domain."""
    groups = _index.by_group()
    for sprint, items in groups.items():
        table = Table(title=f"command {sprint}")
        table.add_column("Command", style="bold")
        table.add_column("help")
        table.add_column("hint")
        for p in items:
            table.add_row(p.command, p.help, p.hint)
        console.print(table)


@app.command()
@friendly_errors
def logs() -> None:
    """Placeholder for future streaming log support."""
    coming_soon("aiel logs")


@app.command()
@friendly_errors
def doctor() -> None:
    """Placeholder for environment diagnostics."""
    coming_soon("aiel doctor")
