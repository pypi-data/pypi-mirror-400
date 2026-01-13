from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True, slots=True)
class CommandModel:
    """
    One registry entry for a CLI command.

    Attributes:
        command: Full command invocation (e.g., "aiel auth login").
        help:    Short, user-facing description (one sentence).
        group:   Logical grouping label used for rendering (e.g., "main", "auth", "files").
        hint:    Optional operator tip (common usage, prerequisites, or gotchas).

    Conventions (recommended):
        - `help` should start with an action verb: "Show", "Print", "List", "Log in", "Log out".
        - Keep `help` to ~8–14 words; move details to `hint`.
        - Use `hint` for security and operational guidance (CI usage, profiles, etc.).
    """

    command: str
    help: str
    group: str
    hint: Optional[str] = None


# Update groups/wording here only.
PLAN: Dict[str, CommandModel] = {
    # -----------------------------
    # Main
    # -----------------------------
    "aiel roadmap": CommandModel(
        command="aiel roadmap",
        help="Show the CLI command roadmap and sprint plan.",
        group="main",
        hint="Use this to discover available commands and what’s coming next.",
    ),
    "aiel version": CommandModel(
        command="aiel version",
        help="Print CLI version and build info.",
        group="main",
        hint="Include this output when opening a support ticket.",
    ),
    # -----------------------------
    # Auth
    # -----------------------------
     "aiel auth": CommandModel(
        command="aiel auth",
        help="Manage CLI authentication and local auth profiles.",
        group="auth",
        hint="Run `aiel auth --help` to see subcommands. Prefer hidden prompt for tokens.",
    ),
    "aiel auth login": CommandModel(
        command="aiel auth login",
        help="Log in by validating a token and saving a profile.",
        group="auth",
        hint=(
            "Recommended: paste token via hidden prompt. "
            "Use `--profile staging` to separate environments."
        ),
    ),
    "aiel auth status": CommandModel(
        command="aiel auth status",
        help="Show whether the CLI is authenticated for the active profile.",
        group="auth",
        hint="Use this in scripts/CI to verify auth state; exits non-zero if invalid.",
    ),
    "aiel auth list": CommandModel(
        command="aiel auth list",
        help="List stored auth profiles and token storage type.",
        group="auth",
        hint="Use profiles like `default`, `staging`, and `prod` to avoid mistakes.",
    ),
    "aiel auth logout": CommandModel(
        command="aiel auth logout",
        help="Log out locally by deleting a stored profile.",
        group="auth",
        hint="This removes local credentials only; it does not revoke server-side access.",
    ),
    "aiel auth revoke": CommandModel(
        command="aiel auth revoke",
        help="Revoke token(s) server-side (requires backend support).",
        group="auth",
        hint="Planned: `--all` revokes all user tokens. Follow with `aiel auth logout` locally.",
    ),
    # -----------------------------
    # Config
    # -----------------------------
    "aiel config": CommandModel(
        command="aiel config",
        help="Manage CLI configuration for the active profile.",
        group="config",
        hint="Use this to view or modify workspace/project selections.",
    ),
    "aiel config list": CommandModel(
        command="aiel config list",
        help="Show workspace and project configured for the active profile.",
        group="config",
        hint="Run after login to verify environment selection.",
    ),
    "aiel config set workspace": CommandModel(
        command="aiel config set workspace",
        help="Select the active workspace and pick a default project.",
        group="config",
        hint="Workspace determines which projects become available for selection.",
    ),
    "aiel config set project": CommandModel(
        command="aiel config set project",
        help="Select or change the default project inside the active workspace.",
        group="config",
        hint="Requires a workspace to be configured first. Prompts if not provided.",
    ),
    "aiel config set show": CommandModel(
        command="aiel config set show",
        help="Debug helper showing the configuration command wiring.",
        group="config",
        hint="Currently prints 'done'; reserved for future tooling.",
    ),
    # -----------------------------
    # Workspace
    # -----------------------------
    "aiel files": CommandModel(
        command="aiel files",
        help="Show or manage workspace-level file and repo information.",
        group="files",
        hint="Run `aiel workspace ls` to inspect the active workspace’s files and metadata.",
    ),
    "aiel files ls": CommandModel(
        command="aiel files ls",
        help="List workspace files and show project and repo metadata.",
        group="files",
        hint=(
            "Useful for debugging what’s deployed or checked out. "
            "Relies on the last manifest from the data plane state."
        ),
    ),
    # -----------------------------
    # Info
    # -----------------------------
    "aiel info workspace": CommandModel(
        command="aiel info workspace",
        help="Show the active user, tenant, workspace, and project.",
        group="info",
        hint="Use this to confirm which workspace and project your CLI is targeting.",
    ),
    "aiel info workspaces": CommandModel(
        command="aiel info workspaces",
        help="List all workspaces and projects available to the current user.",
        group="info",
        hint="Useful for onboarding and debugging access when something is not visible.",
    ),
    "aiel info projects": CommandModel(
        command="aiel info projects",
        help="Show projects grouped under each workspace for the current user.",
        group="info",
        hint="Run this before selecting a project to see what’s available.",
    ),
    # -----------------------------
    # Commit
    # -----------------------------
    "aiel commit": CommandModel(
        command="aiel commit",
        help="Show and manage commit-style sync between local files and the data plane.",
        group="commit",
        hint="Run `aiel commit status` to see staged/unstaged changes.",
    ),
    "aiel commit status": CommandModel(
        command="aiel commit status",
        help="Show staged and unstaged changes vs the last remote snapshot.",
        group="commit",
        hint="Use this before add/commit/push to understand the current diff.",
    ),
    "aiel commit init": CommandModel(
        command="aiel commit init",
        help="Initialize .aiel metadata in the current directory.",
        group="commit",
        hint="Run once per repo to wire it to a workspace and project.",
    ),
    "aiel commit add": CommandModel(
        command="aiel commit add",
        help="Stage a file or all files under '.' into the local index.",
        group="commit",
        hint="Use `aiel commit add .` to stage the entire working tree.",
    ),
    "aiel commit commit": CommandModel(
        command="aiel commit commit",
        help="Snapshot staged changes into a local commit document.",
        group="commit",
        hint="Creates a pending commit; follow with `aiel commit push`.",
    ),
    "aiel commit pull": CommandModel(
        command="aiel commit pull",
        help="Pull remote files into the local working tree.",
        group="commit",
        hint="Refreshes local files and manifest from the data plane.",
    ),
    "aiel commit push": CommandModel(
        command="aiel commit push",
        help="Push staged changes to the data plane and update state.",
        group="commit",
        hint="Applies upserts/deletes remotely and clears the local staging area.",
    ),

}


def by_group() -> dict[str, list[CommandModel]]:
    """
    Group commands by `group` and return a stable, sorted mapping.

    Sorting rules:
        - groups are sorted alphabetically
        - commands within each group are sorted alphabetically by `command`
    """
    grouped: dict[str, list[CommandModel]] = {}

    for item in PLAN.values():
        grouped.setdefault(item.group, []).append(item)

    for group_name, items in grouped.items():
        grouped[group_name] = sorted(items, key=lambda x: x.command)

    return dict(sorted(grouped.items(), key=lambda kv: kv[0]))
