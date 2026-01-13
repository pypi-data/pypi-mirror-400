from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest
from typer.testing import CliRunner

from aiel import cli
from aiel.commands import auth, config as config_cmds, files, info, repo


@pytest.fixture(scope="session")
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="session")
def profile_payload() -> Dict[str, Any]:
    cfg_path = Path(__file__).parent / "data" / "test_profile.json"
    return json.loads(cfg_path.read_text())


@pytest.fixture()
def repo_root(tmp_path, monkeypatch, profile_payload):
    """
    Create a temporary working tree that mimics a repo initialized with `.aiel/`.
    """
    monkeypatch.chdir(tmp_path)
    aiel_dir = tmp_path / ".aiel"
    commits_dir = aiel_dir / "commits"
    commits_dir.mkdir(parents=True, exist_ok=True)

    (aiel_dir / "state.json").write_text(json.dumps(profile_payload["state"], indent=2))
    (aiel_dir / "index.json").write_text(json.dumps(profile_payload["index"], indent=2))
    (tmp_path / "README.md").write_text("# hello world\n")
    return tmp_path


def test_cli_root_commands(runner: CliRunner) -> None:
    result = runner.invoke(cli.app, ["roadmap"])
    assert result.exit_code == 0
    assert "Sprint" in result.stdout

    result = runner.invoke(cli.app, ["version"])
    assert result.exit_code == 0
    assert "version" in result.stdout

    result = runner.invoke(cli.app, ["commands"])
    assert result.exit_code == 0
    assert "aiel auth" in result.stdout

    result = runner.invoke(cli.app, ["logs"])
    assert result.exit_code == 0
    assert "Planned" in result.stdout

    result = runner.invoke(cli.app, ["doctor"])
    assert result.exit_code == 0
    assert "Planned" in result.stdout


def test_auth_login_and_status(monkeypatch, runner: CliRunner) -> None:
    monkeypatch.setattr(auth, "get_current_base_url", lambda: "https://api.test")
    monkeypatch.setattr(auth, "_validate_token", lambda base_url, token: {"email": "eng@aiel.test", "tenant_name": "Demo"})

    saved: Dict[str, Any] = {}

    def fake_save(profile, base_url, token, email, tenant):
        saved["profile"] = profile
        saved["base_url"] = base_url
        saved["token"] = token
        saved["email"] = email
        saved["tenant"] = tenant
        return "file"

    monkeypatch.setattr(auth, "save_profile", fake_save)

    result = runner.invoke(auth.app, ["login", "--profile", "ci", "--token", "abc"])
    assert result.exit_code == 0
    assert "Logged in" in result.stdout
    assert saved["profile"] == "ci"

    monkeypatch.setattr(auth, "resolve_token", lambda: ("abc", "file"))
    result = runner.invoke(auth.app, ["status"])
    assert result.exit_code == 0
    assert "Authenticated" in result.stdout


def test_auth_list_logout_and_revoke(monkeypatch, runner: CliRunner, profile_payload) -> None:
    profiles = profile_payload["profile"]
    profiles.setdefault("profiles", {}).setdefault(
        "staging",
        {
            "user": "staging@aiel.test",
            "tenant": "Staging",
            "token": "token",
        },
    )

    monkeypatch.setattr(auth, "list_profiles", lambda: profiles)
    result = runner.invoke(auth.app, ["list"])
    assert result.exit_code == 0
    assert "AIEL Auth Profiles" in result.stdout

    deleted = {}
    monkeypatch.setattr(auth, "delete_profile", lambda profile: deleted.setdefault("name", profile))
    result = runner.invoke(auth.app, ["logout", "--profile", "default"])
    assert result.exit_code == 0
    assert deleted["name"] == "default"

    result = runner.invoke(auth.app, ["revoke"])
    assert result.exit_code == 0
    assert "Coming soon" in result.stdout


def test_config_list_and_set_workspace(monkeypatch, runner: CliRunner, profile_payload) -> None:
    profiles = profile_payload["profile"]
    monkeypatch.setattr(config_cmds, "list_profiles", lambda: profiles)

    workspace_payload = {
        "workspaces": [
            {
                "id": "ws-onboarding_team2",
                "slug": "onboarding_team2",
                "name": "Onboarding Team 2",
                "projects": [
                    {
                        "id": "proj-linkedin",
                        "slug": "linkedin_onboarding",
                        "name": "LinkedIn Onboarding",
                    }
                ],
            }
        ]
    }
    monkeypatch.setattr(config_cmds, "_get_me", lambda prof: workspace_payload)

    saved = {}

    def capture_profile(data, name, profile):
        saved["profile"] = profile

    monkeypatch.setattr(config_cmds, "_save_profile", capture_profile)

    result = runner.invoke(config_cmds.app, ["list"])
    assert result.exit_code == 0
    assert "Active profile" in result.stdout

    result = runner.invoke(config_cmds.app, ["set", "workspace", "onboarding_team2"])
    assert result.exit_code == 0
    assert saved["profile"]["workspace"]["slug"] == "onboarding_team2"


def test_config_set_project(monkeypatch, runner: CliRunner, profile_payload) -> None:
    profiles = profile_payload["profile"]
    monkeypatch.setattr(config_cmds, "list_profiles", lambda: profiles)

    workspace_payload = {
        "workspaces": [
            {
                "id": profiles["profiles"]["default"]["workspace"]["id"],
                "slug": profiles["profiles"]["default"]["workspace"]["slug"],
                "name": profiles["profiles"]["default"]["workspace"]["name"],
                "projects": [
                    {
                        "id": "proj-linkedin",
                        "slug": "linkedin_onboarding",
                        "name": "LinkedIn Onboarding",
                    }
                ],
            }
        ]
    }
    monkeypatch.setattr(config_cmds, "_get_me", lambda prof: workspace_payload)

    saved = {}
    monkeypatch.setattr(config_cmds, "_save_profile", lambda data, name, profile: saved.setdefault("profile", profile))

    result = runner.invoke(config_cmds.app, ["set", "project"])
    assert result.exit_code == 0
    assert saved["profile"]["project"]["slug"] == "linkedin_onboarding"

    result = runner.invoke(config_cmds.set_app, ["show"])
    assert result.exit_code == 0
    assert "done" in result.stdout


def test_info_commands(monkeypatch, runner: CliRunner, profile_payload) -> None:
    profiles = profile_payload["profile"]

    monkeypatch.setattr(info, "list_profiles", lambda: profiles)
    monkeypatch.setattr(info, "_current_profile", lambda data: "default")
    monkeypatch.setattr(info, "_get_profile", lambda data, name: profiles["profiles"]["default"])

    workspace_context = {
        "workspace": {"slug": "onboarding_team2", "name": "Onboarding Team 2"},
        "project": {"slug": "linkedin_onboarding", "name": "LinkedIn Onboarding"},
    }
    monkeypatch.setattr(info, "default_workspace", lambda data: workspace_context)

    result = runner.invoke(info.app, ["workspace"])
    assert result.exit_code == 0
    assert "workspace" in result.stdout

    me_payload = {
        "email": "eng@aiel.test",
        "tenant_name": "Demo Tenant",
        "workspaces": [
            {
                "name": "Onboarding Team 2",
                "slug": "onboarding_team2",
                "projects": [{"name": "LinkedIn Onboarding", "slug": "linkedin_onboarding"}],
            }
        ],
    }
    monkeypatch.setattr(info, "_get_me", lambda prof: me_payload)

    result = runner.invoke(info.app, ["workspaces"])
    assert result.exit_code == 0
    assert "Demo Tenant" in result.stdout

    result = runner.invoke(info.app, ["projects"])
    assert result.exit_code == 0
    assert "LinkedIn Onboarding" in result.stdout


def test_files_ls(monkeypatch, runner: CliRunner, profile_payload) -> None:
    state = profile_payload["state"]
    profile = profile_payload["profile"]

    monkeypatch.setattr(files, "_state", lambda: state)
    monkeypatch.setattr(files, "list_profiles", lambda: profile)
    monkeypatch.setattr(files, "default_workspace", lambda data: profile["profiles"]["default"])
    monkeypatch.setattr(files, "format_file_tree", lambda manifest: "└── README.md")

    result = runner.invoke(files.app, ["ls"])
    assert result.exit_code == 0
    assert "Repo info" in result.stdout


def test_repo_init(tmp_path, runner: CliRunner, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        repo.app,
        [
            "init",
            "--base-url",
            "https://api.test",
            "--workspace-id",
            "ws-1",
            "--project-id",
            "proj-1",
        ],
    )
    assert result.exit_code == 0
    assert (tmp_path / ".aiel" / "state.json").exists()


def test_repo_status_and_add(repo_root, runner: CliRunner) -> None:
    # pre-populate staged entry to ensure branch coverage
    staged = {"legacy.txt": {"op": "delete"}}
    Path(".aiel/index.json").write_text(json.dumps({"version": 1, "staged": staged}, indent=2))
    state = json.loads((Path(".aiel") / "state.json").read_text())
    state.setdefault("last_manifest", {})["legacy.txt"] = {"sha256": "remote-hash", "version": 1}
    (Path(".aiel") / "state.json").write_text(json.dumps(state, indent=2))
    Path("legacy.txt").write_text("local-change")
    Path("new.md").write_text("brand new")
    extra = Path("notes.txt")
    extra.write_text("notes\n")

    result = runner.invoke(repo.app, ["status"])
    assert result.exit_code == 0
    assert "delete  legacy.txt" in result.stdout

    result = runner.invoke(repo.app, ["add", "notes.txt"])
    assert result.exit_code == 0
    index = json.loads((Path(".aiel") / "index.json").read_text())
    assert "notes.txt" in index["staged"]

    # path "." should stage all files and skip directories
    result = runner.invoke(repo.app, ["add", "."])
    assert result.exit_code == 0


def test_repo_status_empty(repo_root, runner: CliRunner) -> None:
    Path(".aiel/index.json").write_text(json.dumps({"version": 1, "staged": {}}, indent=2))
    readme = Path("README.md")
    if readme.exists():
        readme.unlink()
    result = runner.invoke(repo.app, ["status"])
    assert result.exit_code == 0
    assert "(none)" in result.stdout


def test_repo_commit(repo_root, runner: CliRunner) -> None:
    Path("data.txt").write_text("payload")
    runner.invoke(repo.app, ["add", "data.txt"])
    result = runner.invoke(repo.app, ["commit", "-m", "test commit"])
    assert result.exit_code == 0
    commits = list((Path(".aiel") / "commits").glob("c_*.json"))
    assert commits, "expected a commit document"


def test_repo_pull(monkeypatch, repo_root, runner: CliRunner) -> None:
    monkeypatch.setattr(repo, "_dp_get_manifest", lambda client: {"files": [{"path": "docs/guide.txt"}]})
    monkeypatch.setattr(repo, "_manifest_to_map", lambda manifest: {"docs/guide.txt": {"version": 1}})
    monkeypatch.setattr(
        repo,
        "_dp_sign_download",
        lambda client, path, expires_seconds=600: {"signed_url": f"https://signed/{path}"},
    )

    class DummyResponse:
        def __init__(self, content: bytes):
            self.content = content

        def raise_for_status(self):
            return None

    monkeypatch.setattr(repo.httpx, "get", lambda url, timeout=60.0: DummyResponse(b"fresh data"))

    class DummyClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(repo.httpx, "Client", lambda timeout=30.0: DummyClient())

    result = runner.invoke(repo.app, ["pull"])
    assert result.exit_code == 0
    assert Path("docs/guide.txt").exists()


def test_repo_push(monkeypatch, repo_root, runner: CliRunner) -> None:
    staged = {
        "README.md": {
            "op": "upsert",
            "content_type": "text/plain",
            "expected_version": 1,
        },
        "legacy.txt": {"op": "delete"},
    }
    Path("legacy.txt").write_text("old\n")
    Path(".aiel/index.json").write_text(json.dumps({"version": 1, "staged": staged}, indent=2))

    monkeypatch.setattr(repo, "_dp_get_manifest", lambda client: {"files": []})
    monkeypatch.setattr(repo, "_manifest_to_map", lambda manifest: {})
    monkeypatch.setattr(
        repo,
        "_dp_sign_upload",
        lambda client, path, content_type, expected_version, size_bytes, sha256: {
            "upload_id": "upload-1",
            "signed_url": "https://upload",
        },
    )
    monkeypatch.setattr(repo, "_gcs_put_signed_url", lambda signed_url, content_type, data: None)
    monkeypatch.setattr(repo, "_dp_commit_upload", lambda client, upload_id, expected_version=None: {"version": 2})
    monkeypatch.setattr(repo, "_dp_delete_file", lambda client, path: None)

    class DummyClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(repo.httpx, "Client", lambda timeout=30.0: DummyClient())

    result = runner.invoke(repo.app, ["push"])
    assert result.exit_code == 0
    index = json.loads((Path(".aiel") / "index.json").read_text())
    assert not index["staged"], "push should clear staged entries"


def test_repo_commit_requires_staged(repo_root, runner: CliRunner) -> None:
    Path(".aiel/index.json").write_text(json.dumps({"version": 1, "staged": {}}, indent=2))
    result = runner.invoke(repo.app, ["commit"])
    assert result.exit_code != 0


def test_repo_push_requires_staged(repo_root, runner: CliRunner) -> None:
    Path(".aiel/index.json").write_text(json.dumps({"version": 1, "staged": {}}, indent=2))
    result = runner.invoke(repo.app, ["push"])
    assert result.exit_code != 0
def test_repo_add_ignores_missing(repo_root, runner: CliRunner) -> None:
    result = runner.invoke(repo.app, ["add", "missing-file.txt"])
    assert result.exit_code == 0


def _patch_repo_network(monkeypatch):
    monkeypatch.setattr(repo, "_dp_get_manifest", lambda client: {"files": []})
    monkeypatch.setattr(repo, "_manifest_to_map", lambda manifest: {})
    monkeypatch.setattr(
        repo,
        "_dp_sign_upload",
        lambda client, path, content_type, expected_version, size_bytes, sha256: {
            "upload_id": "upload-1",
            "signed_url": "https://upload",
        },
    )
    monkeypatch.setattr(repo, "_gcs_put_signed_url", lambda signed_url, content_type, data: None)
    monkeypatch.setattr(repo, "_dp_commit_upload", lambda client, upload_id, expected_version=None: {"version": 2})
    monkeypatch.setattr(repo, "_dp_delete_file", lambda client, path: None)

    class DummyClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(repo.httpx, "Client", lambda timeout=30.0: DummyClient())


def test_repo_push_missing_file(monkeypatch, repo_root, runner: CliRunner) -> None:
    staged = {"ghost.txt": {"op": "upsert", "content_type": "text/plain", "expected_version": 0}}
    Path(".aiel/index.json").write_text(json.dumps({"version": 1, "staged": staged}, indent=2))
    _patch_repo_network(monkeypatch)
    result = runner.invoke(repo.app, ["push"])
    assert result.exit_code != 0


def test_repo_push_unknown_op(monkeypatch, repo_root, runner: CliRunner) -> None:
    staged = {"mystery.txt": {"op": "noop"}}
    Path(".aiel/index.json").write_text(json.dumps({"version": 1, "staged": staged}, indent=2))
    _patch_repo_network(monkeypatch)
    Path("mystery.txt").write_text("data")
    result = runner.invoke(repo.app, ["push"])
    assert result.exit_code != 0


def test_repo_push_expected_version_fallback(monkeypatch, repo_root, runner: CliRunner) -> None:
    Path("fallback.txt").write_text("payload")
    staged = {
        "fallback.txt": {
            "op": "upsert",
            "content_type": "text/plain",
            "sha256": "ignored",
            "size_bytes": 8,
        }
    }
    Path(".aiel/index.json").write_text(json.dumps({"version": 1, "staged": staged}, indent=2))

    monkeypatch.setattr(repo, "_dp_get_manifest", lambda client: {"files": [{"path": "fallback.txt", "version": 5}]})
    monkeypatch.setattr(repo, "_manifest_to_map", lambda manifest: {"fallback.txt": {"version": 5}})
    monkeypatch.setattr(
        repo,
        "_dp_sign_upload",
        lambda client, path, content_type, expected_version, size_bytes, sha256: {
            "upload_id": "upload-1",
            "signed_url": "https://upload",
        },
    )
    monkeypatch.setattr(repo, "_gcs_put_signed_url", lambda signed_url, content_type, data: None)
    monkeypatch.setattr(repo, "_dp_commit_upload", lambda client, upload_id, expected_version=None: {"version": 6})
    monkeypatch.setattr(repo, "_dp_delete_file", lambda client, path: None)

    class DummyClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(repo.httpx, "Client", lambda timeout=30.0: DummyClient())
    result = runner.invoke(repo.app, ["push"])
    assert result.exit_code == 0
