from __future__ import annotations

import getpass

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..auth.api import _validate_token

from aiel.auth.credentials import (
    CREDENTIALS_PATH,
    delete_profile,
    get_current_base_url,
    list_profiles,
    resolve_token,
    save_profile,
)

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command("login")
def login(
    profile: str = typer.Option("default", help="Profile name"),
    token: str = typer.Option(None, help="Paste token (discouraged: use prompt)"),
) -> None:
    """Authenticate and persist a CLI profile."""
    base_url = (get_current_base_url()).rstrip("/")

    if token is None:
        console.print(Panel.fit("Enter your AIEL token (input hidden)."))
        token = getpass.getpass("AIEL_TOKEN: ").strip()

    if not token:
        raise typer.BadParameter("Token cannot be empty.")

    me = _validate_token(base_url, token)
    token_source = save_profile(profile, base_url, token, me.get("email"), me.get("tenant_name"))

    console.print(
        Panel.fit(
            f"[green]Logged in[/green]\n"
            f"profile: [bold]{profile}[/bold]\n"
            f"base_url: [bold]{base_url}[/bold]\n"
            f"user: [bold]{me.get('email') or me.get('id') or 'unknown'}[/bold]\n"
            f"scopes: [bold]{me.get('scopes') or 'unknown'}[/bold]\n"
            f"stored_in: [bold]{token_source}[/bold]\n"
            f"creds_file: {CREDENTIALS_PATH}"
        )
    )


@app.command("status")
def status() -> None:
    """Show whether the CLI is authenticated for the current profile."""
    resolved = resolve_token()
    base_url = get_current_base_url()
    if not resolved:
        console.print(Panel.fit("[yellow]Not logged in.[/yellow]\nRun: aiel auth login"))
        raise typer.Exit(code=1)

    token, source = resolved
    try:
        me = _validate_token(base_url, token)
        who = me.get("email") or me.get("id") or "unknown"
        console.print(Panel.fit(f"[green]Authenticated[/green]\nwho: [bold]{who}[/bold]\nbase_url: [bold]{base_url}[/bold]\nsource: [bold]{source}[/bold]"))
    except Exception as e:
        console.print(Panel.fit(f"[red]Token present but invalid[/red]\nbase_url: {base_url}\nsource: {source}\nerror: {e}"))
        raise typer.Exit(code=1)


@app.command("logout")
def logout(profile: str = typer.Option("default", help="Profile name")) -> None:
    """Delete the stored credentials for the selected profile."""
    delete_profile(profile)
    console.print(Panel.fit(f"[green]Logged out[/green]\nprofile: [bold]{profile}[/bold]"))


@app.command("list")
def list_cmd() -> None:
    """List stored profiles, highlighting the active one."""
    data = list_profiles()
    current = data.get("current_profile") or "default"
    profiles = data.get("profiles") or {}

    table = Table(title="AIEL Auth Profiles")
    table.add_column("Profile", style="bold")
    table.add_column("Current")
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

    if not profiles:
        console.print(Panel.fit("[yellow]No stored profiles.[/yellow]\nRun: aiel auth login"))
        return

    console.print(table)
    console.print(Panel.fit("Next step: `aiel config set workspace <slug>`"))


@app.command("revoke")
def revoke(
    all: bool = typer.Option(False, "--all", help="Revoke all tokens for the user (server-side)"),
) -> None:
    """Placeholder for server-side token revocation (kept for roadmap visibility)."""
    """
    Requires backend support (recommended endpoints):
      POST /v1/auth/revoke         -> revoke current token
      POST /v1/auth/revoke?all=1   -> revoke all tokens
    """
    console.print(Panel.fit("Coming soon"))
    # resolved = resolve_token()
    # base_url = get_current_base_url()
    # if not resolved:
    #     console.print(Panel.fit("[yellow]Not logged in.[/yellow]"))
    #     raise typer.Exit(code=1)

    # token, _ = resolved
    # url = base_url.rstrip("/") + "/v1/auth/revoke"
    # headers = {"Authorization": f"Bearer {token}"}
    # params = {"all": "1"} if all else None

    # with httpx.Client(timeout=10.0) as client:
    #     r = client.post(url, headers=headers, params=params)
    #     if r.status_code >= 400:
    #         console.print(Panel.fit(f"[red]Revoke failed[/red]\nstatus: {r.status_code}\nbody: {r.text}"))
    #         raise typer.Exit(code=1)

    # console.print(Panel.fit("[green]Revoked token(s)[/green]\nTip: run `aiel auth logout` to remove local creds too."))
