# aiel — AI Execution Layer CLI

![PyPI](https://img.shields.io/pypi/v/aiel-cli)

`aiel` is the reference CLI for the AI Execution Layer: a workspace-centric automation platform that keeps AI workflows versioned, reviewable, and operator friendly. The CLI mirrors the day-to-day lifecycle for teams shipping AI automations—from authenticating against the platform, to selecting the right workspace/project, synchronizing code, and inspecting remote manifests.

Every command is transparent about its roadmap sprint, so teams can adopt the CLI confidently while newer subcommands are still rolling out.

---

## Features

- **Roadmap-aware UX**: discover commands and their target sprint directly from the CLI (`aiel roadmap` and `aiel commands`).
- **Profile-safe authentication**: `aiel auth ...` manages multiple environments, keyring-backed tokens (with file fallback), and human-friendly panels.
- **Workspace configuration**: `aiel config ...` drives interactive workspace/project selection powered by `/v1/auth/me`.
- **Git-inspired sync**: `aiel repo ...` offers familiar `init`, `status`, `add`, `commit`, `pull`, and `push` flows backed by the data plane.
- **Insightful observability**: `aiel info ...` and `aiel files ...` surface active context, manifests, and repo metadata for debugging.
- **Full test coverage**: the test suite exercises every route with fixtures and mocks, ensuring confidence in day-to-day automation.

---

## Installation

```bash
pip install aiel-cli
```

The CLI exposes the `aiel` entrypoint via Typer. Python 3.10+ is required.

---

## Quick Start

```bash
# 1. Discover the active roadmap
aiel roadmap

# 2. Authenticate (token prompt is hidden)
aiel auth login

# 3. Initialize repo metadata
aiel repo init

# 4. Select a workspace and project
aiel config set workspace onboarding_team2
aiel config set project linkedin_onboarding

# 5. Inspect context and manifests
aiel info workspace
aiel files ls

# 6. Sync a repo
aiel repo pull
aiel repo status
```

---

## Command Guide

| Group   | Highlights |
|---------|------------|
| `aiel roadmap` / `aiel commands` | Render sprint tables and hints for every command (including placeholders such as `aiel logs` and `aiel doctor`). |
| `aiel auth` | `login`, `status`, `list`, `logout`, and `revoke` (roadmap) with Rich panels to document base URLs, scopes, and storage locations. |
| `aiel config` | `list`, `set workspace`, `set project`, `set show` provide a safe workflow for selecting workspace/project context per profile. |
| `aiel repo` | Implements a Git-inspired flow (`status`, `init`, `add`, `commit`, `pull`, `push`) over `.aiel/` metadata and the data plane. |
| `aiel info` | Read-only introspection commands for workspace/projects. |
| `aiel files` | Read-only manifest view + repo metadata for the most recent pull. |

Each command prints detailed help (`--help`) and panels summarizing the action taken so operators have immediate context.

---

## Authentication & Configuration

1. `aiel auth login`  
   - Validates tokens via `/v1/auth/me` and stores them using keyring when available (file fallback otherwise).  
   - Panels indicate where the token was stored and which user/tenant is active.

2. `aiel auth status / list / logout`  
   - Status exits non-zero when the token is missing or invalid—ideal for CI smoke tests.  
   - `list` enumerates profiles, marking the active one and where the token is stored.  
   - `logout` removes local credentials per profile.

3. `aiel config set workspace`  
   - Fetches workspaces/projects via `_get_me` and guides the operator through selecting defaults.  
   - Auto-selects projects when only one is available; otherwise displays an interactive prompt (Questionary).

4. `aiel config set project`  
   - Ensures a workspace is selected, then prompts or validates the project slug.  
   - `aiel config list` reflects the active profile + workspace and project slug/name.

---

## Credentials & Local State

- Auth profiles live in `~/.config/aiel/credentials.json` with restrictive file permissions on Unix.
- Tokens can also be injected via `AIEL_TOKEN` for CI or non-interactive usage.
- Repo state lives under `.aiel/` in the working directory (`state.json`, `index.json`, `commits/`).
- Exclude local files and folders from repo commands with `.aielignore` (same idea as `.gitignore`).

---

## Repo Workflow

All state lives under `.aiel/` (state.json, index.json, commits/). The flow mirrors Git:

1. `aiel repo init`  
   - Creates `.aiel/state.json` and `.aiel/index.json` with normalized metadata from the active profile.

2. `aiel repo status`  
   - Compares working tree hashes vs the last manifest and prints staged vs unstaged sections.

3. `aiel repo add <path|.>`  
   - Computes sha256, content-types, and stages upserts or deletes into `index.json`.

4. `aiel repo commit -m "message"`  
   - Writes a local commit document under `.aiel/commits/` and marks it as pending.

5. `aiel repo pull`  
   - Uses signed download URLs from the data plane to refresh the working tree and update manifest metadata.

6. `aiel repo push`  
   - Signs uploads, streams bytes to the storage layer, commits uploads, deletes when needed, refreshes manifest metadata, and clears the index.

All network interactions are stubbed in the test suite, ensuring deterministic coverage without real API calls.

---

## Workspace Introspection

- `aiel info workspace` prints the resolved user, tenant, workspace, and project so there’s no ambiguity about the current context.
- `aiel info workspaces/projects` walks the payload returned by `_get_me` and prints structured tables for visibility.
- `aiel files ls` renders the last manifest as a tree and summarizes repo metadata (last pull, pending commit, version).

These commands are intentionally read-only and safe to run in CI/CD or during incident response.

---

## Testing

The repository ships with an end-to-end test suite covering every CLI route (unit + integration). Tests rely on a dedicated fixture configuration at `tests/data/test_profile.json`, which includes:

- `X-API-Token`: `<X-API-Token>`
- Workspace slug: `onboarding_team2`
- Project slug: `linkedin_onboarding`

Run the suite with coverage enforcement:

```bash
pip install -e .[dev]
pytest --cov=aiel --cov-report=term-missing --cov-fail-under=100
```

The tests patch network calls, use Typer’s `CliRunner`, and stage temporary `.aiel/` directories to exercise the entire workflow without hitting real services.

---

## Contributing

1. Fork and clone the repository.
2. Create a fresh virtual environment with Python 3.10+.
3. Install dependencies (`pip install -e .[dev]`).
4. Run `pytest --cov=aiel --cov-report=term-missing --cov-fail-under=100` before opening a PR.
5. Update the roadmap comments or README whenever you expose a new command.

Open issues or discussions if you need new command groups, additional transports, or would like to upstream scripts into `tools/`.
