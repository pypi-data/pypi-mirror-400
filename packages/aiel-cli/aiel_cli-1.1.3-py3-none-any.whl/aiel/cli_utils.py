from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, cast

import typer
from rich.console import Console
from rich.panel import Panel

from aiel.errors import CliError

console = Console()
F = TypeVar("F", bound=Callable[..., Any])


def friendly_errors(fn: F) -> F:
    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        debug = kwargs.pop("debug", False)  # optional; see below
        try:
            return fn(*args, **kwargs)
        except CliError as e:
            console.print(
                Panel.fit(
                    f"[bold red]Error:[/bold red] {e.message}"
                    + (f"\n\n[bold]Hint:[/bold] {e.hint}" if e.hint else ""),
                    border_style="red",
                    title="AIEL CLI",
                )
            )
            raise typer.Exit(e.code)
        except typer.Exit:
            raise
        except Exception as e:
            # Unexpected crash. Hide traceback unless debug.
            if debug:
                raise
            console.print(
                Panel.fit(
                    f"[bold red]Unexpected error:[/bold red] {type(e).__name__}: {e}\n\n"
                    f"[bold]Hint:[/bold] Re-run with [bold]--debug[/bold] to see a full traceback.",
                    border_style="red",
                    title="AIEL CLI",
                )
            )
            raise typer.Exit(1)

    return cast(F, wrapper)
