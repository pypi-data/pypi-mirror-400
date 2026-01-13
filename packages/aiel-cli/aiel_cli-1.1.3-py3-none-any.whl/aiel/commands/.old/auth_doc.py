from __future__ import annotations

import getpass
import os
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ...auth.api import _validate_token
from aiel.auth.credentials import (
    CREDENTIALS_PATH,
    delete_profile,
    get_current_base_url,
    list_profiles,
    resolve_token,
    save_profile,
)

app = typer.Typer(
    no_args_is_help=True,
    help=(
        "Authenticate the AIEL CLI.\n\n"
        "This command group manages local auth profiles and verifies tokens against the AIEL API.\n"
        "Recommended: paste tokens via hidden prompt (no shell history)."
    ),
)
console = Console()


def _normalize_base_url(url: str) -> str:
    """Normalize base URL for API requests."""
    return (url or "").strip().rstrip("/")


def _prompt_token() -> str:
    """Securely prompt for an AIEL token (hidden input)."""
    console.print(Panel.fit("Enter your AIEL token (input hidden)."))
    return getpass.getpass("AIEL_TOKEN: ").strip()


def _get_token(token_opt: Optional[str]) -> str:
    """
    Resolve token from:
      1) explicit --token (discouraged)
      2) env var AIEL_TOKEN (CI friendly)
      3) secure hidden prompt
    """
    if token_opt and token_opt.strip():
        return token_opt.strip()

    env = os.getenv("AIEL_TOKEN", "").strip()
    if env:
        return env

    return _prompt_token()


def _validate_or_exit(base_url: str, token: str) -> dict:
    """
    Validate token against backend and return identity payload.

    Expected keys (best effort):
      - email
      - id
      - scopes
      - tenant_name

    Exits with code 1 on validation failure.
    """
    try:
        return _validate_token(base_url, token)
    except Exception as e:
        # Intentionally keep message short and safe (no token echo).
        console.print(
            Panel.fit(
                "[red]Authentication failed[/red]\n"
                f"base_url: [bold]{base_url}[/bold]\n"
                f"error: {type(e).__name__}: {e}"
            )
        )
        raise typer.Exit(code=1)


@app.command("login")
def login(
    profile: str = typer.Option(
        "default",
        "--profile",
        "-p",
        help="Profile name to save credentials under (e.g., default, staging, prod).",
        show_default=True,
    ),
    token: Optional[str] = typer.Option(
        None,
        "--token",
        help=(
            "Paste token directly (discouraged). Prefer prompt or AIEL_TOKEN env var "
            "to avoid leaking secrets into shell history."
        ),
    ),
) -> None:
    """
    Log in to AIEL by validating a token and saving it to a local profile.

    Token input priority:
      1) --token (discouraged)
      2) AIEL_TOKEN env var (recommended for CI)
      3) hidden prompt (recommended for humans)

    On success, the CLI stores:
      - base_url
      - token (secure ref if keyring is available)
      - user email
      - tenant name
    """
    base_url = _normalize_base_url(get_current_base_url())
    resolved_token = _get_token(token)

    if not resolved_token:
        raise typer.BadParameter("Token cannot be empty.")

    me = _validate_or_exit(base_url, resolved_token)

    token_source = save_profile(
        profile=profile,
        base_url=base_url,
        token=resolved_token,
        user_email=me.get("email"),
        tenant_name=me.get("tenant_name"),
    )

    who = me.get("email") or me.get("id") or "unknown"
    scopes = me.get("scopes") or "unknown"

    console.print(
        Panel.fit(
            "[green]Logged in[/green]\n"
            f"profile: [bold]{profile}[/bold]\n"
            f"base_url: [bold]{base_url}[/bold]\n"
            f"user: [bold]{who}[/bold]\n"
            f"scopes: [bold]{scopes}[/bold]\n"
            f"stored_in: [bold]{token_source}[/bold]\n"
            f"creds_file: {CREDENTIALS_PATH}"
        )
    )


@app.command("status")
def status() -> None:
    """
    Show current authentication status.

    - If no local token is found, exits with code 1.
    - If a token exists, validates it with the backend:
        - success -> prints identity
        - failure -> prints error and exits with code 1

    This command is safe to use in automation to verify auth state.
    """
    resolved = resolve_token()
    base_url = _normalize_base_url(get_current_base_url())

    if not resolved:
        console.print(Panel.fit("[yellow]Not logged in.[/yellow]\nRun: aiel auth login"))
        raise typer.Exit(code=1)

    token, source = resolved
    me = _validate_or_exit(base_url, token)

    who = me.get("email") or me.get("id") or "unknown"
    console.print(
        Panel.fit(
            "[green]Authenticated[/green]\n"
            f"who: [bold]{who}[/bold]\n"
            f"base_url: [bold]{base_url}[/bold]\n"
            f"source: [bold]{source}[/bold]"
        )
    )


@app.command("logout")
def logout(
    profile: str = typer.Option(
        "default",
        "--profile",
        "-p",
        help="Profile name to delete locally.",
        show_default=True,
    )
) -> None:
    """
    Log out locally by deleting the stored profile.

    Note:
      - This does NOT revoke tokens server-side.
      - Use `revoke` (when enabled) to invalidate tokens in the backend.
    """
    delete_profile(profile)
    console.print(Panel.fit(f"[green]Logged out[/green]\nprofile: [bold]{profile}[/bold]"))


@app.command("list")
def list_cmd() -> None:
    """
    List stored authentication profiles.

    Shows:
      - which profile is current
      - the user and tenant associated with each profile
      - where the token is stored (keyring/file/none)
    """
    data = list_profiles()
    current = data.get("current_profile") or "default"
    profiles: dict = data.get("profiles") or {}

    if not profiles:
        console.print(Panel.fit("[yellow]No stored profiles.[/yellow]\nRun: aiel auth login"))
        return

    table = Table(title="AIEL Auth Profiles")
    table.add_column("Profile", style="bold")
    table.add_column("Current", justify="center")
    table.add_column("User")
    table.add_column("Tenant")
    table.add_column("Token Storage")

    for name, p in profiles.items():
        token_storage = "keyring" if "token_ref" in p else ("file" if "token" in p else "none")
        table.add_row(
            name,
            "✅" if name == current else "",
            str(p.get("user") or ""),
            str(p.get("tenant") or ""),
            token_storage,
        )

    console.print(table)
    console.print("\nTip:", style="italic")
    console.print("  Use different profiles for staging/prod to avoid accidents.", style="cyan")


@app.command("revoke")
def revoke(
    all: bool = typer.Option(
        False,
        "--all",
        help="Revoke all tokens for the current user (server-side). Requires backend support.",
    ),
) -> None:
    """
    Revoke token(s) server-side.

    Requires backend endpoints (recommended):
      - POST /v1/auth/revoke         -> revoke current token
      - POST /v1/auth/revoke?all=1   -> revoke all tokens

    Current behavior:
      - Not implemented in this CLI module yet.
    """
    # Intentionally explicit: avoids implying security behavior that doesn't exist.
    console.print(Panel.fit("[yellow]Coming soon[/yellow]\nServer-side token revocation is not enabled yet."))
