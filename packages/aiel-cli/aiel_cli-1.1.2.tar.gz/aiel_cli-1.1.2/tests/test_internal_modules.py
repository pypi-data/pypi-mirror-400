from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict
import importlib
from importlib.metadata import PackageNotFoundError

import pytest
import typer
from typer.testing import CliRunner

from aiel import cli, data_plane, utilities
from aiel.auth import credentials
from aiel.auth import api as auth_api
from aiel.cli_utils import friendly_errors
from aiel.commands import auth as auth_cmds, config as config_cmds, info as info_cmds
from aiel.config import settings
from aiel.errors import CliError


class FakeKeyring:
    def __init__(self) -> None:
        self.store: Dict[tuple[str, str], str] = {}

    def set_password(self, service: str, profile: str, token: str) -> None:
        self.store[(service, profile)] = token

    def get_password(self, service: str, profile: str) -> str | None:
        return self.store.get((service, profile))

    def delete_password(self, service: str, profile: str) -> None:
        self.store.pop((service, profile), None)


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def credentials_env(tmp_path, monkeypatch):
    cred_file = tmp_path / "credentials.json"
    monkeypatch.setattr(credentials, "CREDENTIALS_PATH", cred_file)
    monkeypatch.setattr(credentials, "keyring", FakeKeyring())
    monkeypatch.setattr(config_cmds, "CREDENTIALS_PATH", cred_file)
    monkeypatch.delenv("AIEL_TOKEN", raising=False)
    return cred_file


@pytest.fixture()
def repo_env(tmp_path, monkeypatch):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    aiel_dir = repo_dir / ".aiel"
    aiel_dir.mkdir()
    commits_dir = aiel_dir / "commits"
    commits_dir.mkdir()

    state_path = aiel_dir / "state.json"
    index_path = aiel_dir / "index.json"
    state = {
        "version": 1,
        "base_url": "https://api.aiel.test",
        "workspace_id": "ws",
        "project_id": "proj",
        "last_pull_at": None,
        "last_manifest": {},
        "pending_commit_id": None,
    }
    index = {"version": 1, "staged": {}}
    state_path.write_text(json.dumps(state, indent=2))
    index_path.write_text(json.dumps(index, indent=2))

    monkeypatch.chdir(repo_dir)
    monkeypatch.setattr(settings, "AIEL_DIR", aiel_dir)
    monkeypatch.setattr(settings, "COMMITS_DIR", commits_dir)
    monkeypatch.setattr(settings, "STATE_PATH", state_path)
    monkeypatch.setattr(settings, "INDEX_PATH", index_path)
    return repo_dir


def test_cli_debug_and_missing_plan(runner: CliRunner) -> None:
    result = runner.invoke(cli.app, ["--debug", "roadmap"])
    assert result.exit_code == 0
    assert "Debug mode enabled" in result.stdout

    with pytest.raises(typer.Exit):
        cli.coming_soon("totally-new")


def test_friendly_errors_decorator_handles_cli_error(capsys):
    @friendly_errors
    def boom():
        raise CliError("kaput", hint="check config", code=5)

    with pytest.raises(typer.Exit) as excinfo:
        boom()
    assert excinfo.value.exit_code == 5
    captured = capsys.readouterr().out
    assert "kaput" in captured

    @friendly_errors
    def crash(debug=False):
        raise RuntimeError("unexpected")

    with pytest.raises(RuntimeError):
        crash(debug=True)

    @friendly_errors
    def exit_fast():
        raise typer.Exit(7)

    with pytest.raises(typer.Exit) as excinfo:
        exit_fast()
    assert excinfo.value.exit_code == 7

    @friendly_errors
    def noisy():
        raise ValueError("boom")

    with pytest.raises(typer.Exit) as excinfo:
        noisy()
    assert excinfo.value.exit_code == 1


def test_auth_prompt_login(monkeypatch, runner: CliRunner):
    monkeypatch.setattr(auth_cmds, "get_current_base_url", lambda: "https://api")
    monkeypatch.setattr(auth_cmds, "_validate_token", lambda base_url, token: {"email": "x", "tenant_name": "t"})
    monkeypatch.setattr(auth_cmds, "save_profile", lambda *args, **kwargs: "file")
    monkeypatch.setattr(auth_cmds.getpass, "getpass", lambda prompt: "tok")
    result = runner.invoke(auth_cmds.app, ["login", "--profile", "prompted"])
    assert result.exit_code == 0
    assert "Logged in" in result.stdout


def test_auth_status_not_logged_in(monkeypatch, runner: CliRunner):
    monkeypatch.setattr(auth_cmds, "resolve_token", lambda: None)
    result = runner.invoke(auth_cmds.app, ["status"])
    assert result.exit_code != 0
    assert "Not logged in" in result.stdout


def test_auth_list_no_profiles(monkeypatch, runner: CliRunner):
    monkeypatch.setattr(auth_cmds, "list_profiles", lambda: {"profiles": {}, "current_profile": "default"})
    result = runner.invoke(auth_cmds.app, ["list"])
    assert result.exit_code == 0
    assert "No stored profiles" in result.stdout


def test_auth_status_invalid_token(monkeypatch, runner: CliRunner):
    monkeypatch.setattr(auth_cmds, "resolve_token", lambda: ("tok", "file"))
    monkeypatch.setattr(auth_cmds, "get_current_base_url", lambda: "https://api")

    def boom(base_url, token):
        raise RuntimeError("bad")

    monkeypatch.setattr(auth_cmds, "_validate_token", boom)
    result = runner.invoke(auth_cmds.app, ["status"])
    assert result.exit_code != 0
    assert "Token present but invalid" in result.stdout


def test_api_validate_token_success_and_failure(monkeypatch):
    responses = [{"json": {"ok": True}, "status": 200}, {"json": {}, "status": 401}]

    class DummyResponse:
        def __init__(self, payload):
            self.payload = payload
            self.status_code = payload["status"]

        def json(self):
            return self.payload["json"]

        def raise_for_status(self):
            if self.status_code >= 400:
                class Err(Exception):
                    pass
                raise Err()

    class DummyClient:
        def __init__(self, payload):
            self.payload = payload

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, url, headers=None):
            return DummyResponse(self.payload)

    payload = responses.pop(0)
    monkeypatch.setattr(auth_api.httpx, "Client", lambda timeout: DummyClient(payload))
    assert auth_api._validate_token("https://api", "tok") == {"ok": True}

    payload = responses.pop(0)
    monkeypatch.setattr(auth_api.httpx, "Client", lambda timeout: DummyClient(payload))
    with pytest.raises(typer.BadParameter):
        auth_api._validate_token("https://api", "tok")


def test_credentials_workflow(credentials_env, monkeypatch):
    cred_path = credentials_env
    monkeypatch.delenv("AIEL_TOKEN", raising=False)

    token_source = credentials.save_profile("default", "https://api", "token", "user@example.com", "tenant")
    assert token_source == "keyring"

    data = credentials.list_profiles()
    assert credentials._current_profile(data) == "default"
    assert credentials._get_profile(data, "default")["user"] == "user@example.com"
    assert credentials.get_current_base_url() == "https://api"
    assert credentials.resolve_token() == ("token", "keyring")

    monkeypatch.setattr(credentials, "_validate_token", lambda base, tok: {"who": "me"})
    profile = {"base_url": "https://api", "token_ref": "keyring:aiel:default"}
    assert credentials._get_me(profile) == {"who": "me"}

    credentials.delete_profile("default")
    assert credentials.list_profiles()["profiles"] == {}


def test_credentials_env_and_file_fallback(credentials_env, monkeypatch):
    cred_path = credentials_env
    monkeypatch.setenv("AIEL_TOKEN", "envtok")
    assert credentials.resolve_token() == ("envtok", "env")

    monkeypatch.setattr(credentials, "keyring", None)
    monkeypatch.delenv("AIEL_TOKEN", raising=False)
    credentials.write_json_secure(
        cred_path,
        {
            "version": 1,
            "current_profile": "default",
            "profiles": {"default": {"token": "filetok"}},
        },
    )
    assert credentials.resolve_token() == ("filetok", "file")


def test_credentials_config_dir_windows(monkeypatch, tmp_path):
    fake_os = SimpleNamespace(name="nt", environ={"APPDATA": str(tmp_path)})
    monkeypatch.setattr(credentials, "os", fake_os)
    cfg = credentials._config_dir()
    assert cfg.name == credentials.APP_NAME


def test_credentials_keyring_none(monkeypatch):
    monkeypatch.setattr(credentials, "keyring", None)
    assert credentials._keyring_set("p", "t")[0] is False
    assert credentials._keyring_get("p") is None
    assert credentials._keyring_del("p") is False

    class BadKeyring:
        def delete_password(self, service, profile):
            raise RuntimeError("boom")

    monkeypatch.setattr(credentials, "keyring", BadKeyring())
    assert credentials._keyring_del("p") is False


def test_credentials_resolve_token_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(credentials, "CREDENTIALS_PATH", tmp_path / "creds.json")
    monkeypatch.delenv("AIEL_TOKEN", raising=False)
    assert credentials.resolve_token() is None


def test_credentials_save_profile_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(credentials, "CREDENTIALS_PATH", tmp_path / "creds.json")
    monkeypatch.setattr(credentials, "_keyring_set", lambda profile, token: (False, "keyring-unavailable"))
    source = credentials.save_profile("default", "https://api", "token", "u", "t")
    assert source == "keyring-unavailable"
    data = credentials.read_json(tmp_path / "creds.json")
    assert data["profiles"]["default"]["token"] == "token"

    credentials.write_json_secure(
        tmp_path / "creds.json",
        {"current_profile": "default", "profiles": {"default": {}}},
    )
    assert credentials.resolve_token() is None

    credentials.write_json_secure(
        tmp_path / "creds.json",
        {"current_profile": "default", "profiles": {"default": {"base_url": "x"}}},
    )
    assert credentials.resolve_token() is None


def test_credentials_get_me_missing_fields(monkeypatch):
    profile = {}
    with pytest.raises(CliError):
        credentials._get_me(profile)

    monkeypatch.setattr(credentials, "resolve_token", lambda: "tok")
    monkeypatch.setattr(credentials, "_validate_token", lambda base, tok: {"ok": True})
    profile = {"base_url": "https://api", "token_ref": "keyring:aiel:default"}
    assert credentials._get_me(profile) == {"ok": True}


def test_utilities_helpers(repo_env, monkeypatch, tmp_path):
    missing_state = tmp_path / "missing_state.json"
    monkeypatch.setattr(settings, "STATE_PATH", missing_state)
    with pytest.raises(typer.BadParameter):
        utilities.ensure_repo()

    monkeypatch.setattr(settings, "STATE_PATH", settings.AIEL_DIR / "state.json")
    (settings.AIEL_DIR / "state.json").write_text("{}")
    utilities.ensure_repo()

    assert utilities.read_json(Path("absent.json"), {"v": 1}) == {"v": 1}
    utilities.write_json(Path("sample.json"), {"hello": "world"})
    assert utilities.read_json(Path("sample.json"), {})["hello"] == "world"
    utilities.write_json_secure(Path("secure.json"), {"ok": True})
    assert utilities.now_iso().endswith("Z")
    assert utilities.sha256_bytes(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert utilities.guess_content_type("script.py") == "text/x-python"
    assert utilities.guess_content_type("data.json") == "application/json"
    assert utilities.guess_content_type("config.yaml") == "text/yaml"
    assert "charset" in utilities.guess_content_type("README")

    nested = Path("pkg")
    nested.mkdir()
    (nested / "mod.py").write_text("# code")
    (Path(".aiel") / "skip.txt").write_text("")
    files = utilities.walk_files(Path("."))
    assert any(str(p).endswith("mod.py") for p in files)

    ok, reason = utilities.profile_is_set({"profiles": {}, "current_profile": "default"})
    assert not ok and "No profiles" in reason
    ok, reason = utilities.profile_is_set({"profiles": {"other": {}}, "current_profile": "default"})
    assert not ok and "Current profile" in reason
    profile_data = {"profiles": {"default": {"base_url": "x", "token_ref": "t"}}, "current_profile": "default"}
    assert utilities.profile_is_set(profile_data)[0]
    missing_profile = {"profiles": {"default": {"base_url": "", "token_ref": ""}}, "current_profile": "default"}
    ok, reason = utilities.profile_is_set(missing_profile)
    assert not ok and "missing" in reason

    assert not utilities.workspace_is_set({}, "workspace")[0]
    assert not utilities.workspace_is_set({"workspace": []}, "workspace")[0]
    ws_ok, ws_reason = utilities.workspace_is_set({"workspace": {"slug": "w", "id": 1}}, "workspace")
    assert ws_ok
    assert not utilities.workspace_is_set({"workspace": {"slug": "only"}}, "workspace")[0]

    assert "slug" in utilities.pick_slug_name({"slug": "w", "name": "Workspace"})
    formatted = utilities.format_workspaces_with_projects(
        [{"name": "Workspace", "slug": "w", "projects": [{"name": "Proj", "slug": "p"}]}]
    )
    assert "Proj" in formatted
    weird = utilities.format_workspaces_with_projects(
        [{"name": "Workspace", "slug": "w", "projects": ["skip-this"]}]
    )
    assert "Workspace" in weird
    formatted_empty = utilities.format_workspaces_with_projects(
        [{"name": "Workspace", "slug": "w", "projects": []}, "ignore-me"]
    )
    assert "(no projects)" in formatted_empty
    assert utilities.format_workspaces("raw") == "raw"
    assert "Workspace" in utilities.format_workspaces([{"name": "Workspace", "slug": "w"}])
    assert utilities.format_workspaces(["skip"]) == "(none)"
    manifest = {"README.md": {"version": 1}, "src/app.py": {"version": 1}}
    tree = utilities.format_file_tree(manifest)
    assert "README.md" in tree

    workspace_profiles = {
        "current_profile": "default",
        "profiles": {
            "default": {
                "base_url": "https://api",
                "token_ref": "keyring:aiel:default",
                "workspace": {"slug": "w", "id": 1},
                "project": {"slug": "p", "id": 2},
            }
        },
    }
    assert utilities.default_workspace(workspace_profiles)["workspace"]["slug"] == "w"
    assert utilities.default_workspace({"profiles": {}, "current_profile": "default"}) is None
    missing_ws = {
        "current_profile": "default",
        "profiles": {"default": {"base_url": "x", "token_ref": "y", "project": {"slug": "p", "id": 2}}},
    }
    assert utilities.default_workspace(missing_ws) is None
    missing_ws["profiles"]["default"]["workspace"] = {"slug": "w", "id": 1}
    missing_ws["profiles"]["default"]["project"] = {}
    assert utilities.default_workspace(missing_ws) is None


def test_data_plane_helpers(repo_env, monkeypatch):
    monkeypatch.setenv("AIEL_TOKEN", "envtoken")
    assert data_plane._token() == "envtoken"

    monkeypatch.delenv("AIEL_TOKEN", raising=False)
    monkeypatch.setattr(credentials, "resolve_token", lambda: ("credtoken", "file"))
    assert data_plane._token() == "credtoken"

    monkeypatch.setattr(credentials, "resolve_token", lambda: None)
    with pytest.raises(typer.BadParameter):
        data_plane._token()

    monkeypatch.setenv("AIEL_TOKEN", "envtoken")
    assert data_plane._headers()["X-API-Token"] == "envtoken"

    state = data_plane._state()
    index = data_plane._index()
    data_plane._save_state(state)
    data_plane._save_index(index)
    monkeypatch.setattr(data_plane, "list_profiles", lambda: {"profiles": {}, "current_profile": "default"})
    assert data_plane._base_ws_proj()[1:] == ("ws", "proj")

    manifest = data_plane._manifest_to_map({"files": [{"path": "README.md", "version": 1}]})
    assert manifest["README.md"]["version"] == 1

    class DummyResponse:
        def __init__(self, payload):
            self.payload = payload

        def json(self):
            return self.payload

        def raise_for_status(self):
            return None

    class DummyClient:
        def __init__(self):
            self.calls = []

        def get(self, url, headers=None):
            self.calls.append(("get", url))
            return DummyResponse({"files": []})

        def post(self, url, params=None, headers=None, json=None):
            self.calls.append(("post", url))
            return DummyResponse({"signed_url": "https://signed", "upload_id": "id"})

        def delete(self, url, headers=None):
            self.calls.append(("delete", url))
            return DummyResponse({})

    client = DummyClient()
    assert data_plane._dp_get_manifest(client) == {"files": []}
    assert data_plane._dp_sign_download(client, "README.md")["signed_url"]
    assert data_plane._dp_sign_upload(client, "README.md", "text/plain", 1, 4, "sha")["upload_id"] == "id"

    put_called = {}

    class DummyPut:
        def __init__(self):
            self.status_code = 200

        def raise_for_status(self):
            put_called["ok"] = True

    monkeypatch.setattr(data_plane.httpx, "put", lambda *args, **kwargs: DummyPut())
    data_plane._gcs_put_signed_url("https://signed", "text/plain", b"data")

    client = DummyClient()
    assert data_plane._dp_commit_upload(client, "id", expected_version=1) == {"signed_url": "https://signed", "upload_id": "id"}
    assert data_plane._dp_delete_file(client, "README.md") == {}


def test_config_q_select_and_commands(monkeypatch, credentials_env):
    rows = [{"slug": "proj", "name": "Project"}]

    def fake_select(*args, **kwargs):
        return SimpleNamespace(ask=lambda: kwargs["choices"][0].value)

    monkeypatch.setattr(config_cmds.questionary, "select", fake_select)
    result = config_cmds._q_select(
        prompt="Pick",
        rows=rows,
        label_fn=lambda row: row["name"],
        key_fn=lambda row: row["slug"],
    )
    assert result == rows[0]

    with pytest.raises(typer.Exit):
        config_cmds._q_select(prompt="Pick", rows=[], label_fn=lambda r: "", key_fn=lambda r: "")

    def fake_select_none(*args, **kwargs):
        return SimpleNamespace(ask=lambda: None)

    monkeypatch.setattr(config_cmds.questionary, "select", fake_select_none)
    with pytest.raises(typer.Exit):
        config_cmds._q_select(
            prompt="Pick",
            rows=rows,
            label_fn=lambda row: row["name"],
            key_fn=lambda row: row["slug"],
        )


def test_config_q_select_invalid(monkeypatch):
    rows = [{"slug": "proj", "name": "Project"}]

    def fake_select_other(*args, **kwargs):
        return SimpleNamespace(ask=lambda: "missing-key")

    monkeypatch.setattr(config_cmds.questionary, "select", fake_select_other)
    with pytest.raises(typer.Exit):
        config_cmds._q_select(
            prompt="Pick",
            rows=rows,
            label_fn=lambda row: row["name"],
            key_fn=lambda row: row["slug"],
        )


def test_config_save_profile_helper(tmp_path, monkeypatch):
    target = tmp_path / "creds.json"
    monkeypatch.setattr(config_cmds, "CREDENTIALS_PATH", target)
    data = {"profiles": {}}
    profile = {"workspace": {"slug": "ws"}}
    config_cmds._save_profile(data, "default", profile)
    saved = json.loads(target.read_text())
    assert "default" in saved["profiles"]


def test_config_list_and_error_paths(monkeypatch):
    profiles = {"current_profile": "default", "profiles": {"default": {}}}
    monkeypatch.setattr(config_cmds, "list_profiles", lambda: profiles)
    result = CliRunner().invoke(config_cmds.app, ["list"])
    assert result.exit_code == 0
    assert "not set" in result.stdout

    monkeypatch.setattr(config_cmds, "_get_me", lambda prof: {"workspaces": []})
    with pytest.raises(typer.Exit):
        config_cmds.set_workspace_cmd("missing")

    monkeypatch.setattr(
        config_cmds,
        "_get_me",
        lambda prof: {"workspaces": [{"slug": "ws", "id": "1", "projects": []}]},
    )
    with pytest.raises(typer.Exit):
        config_cmds.set_workspace_cmd("other")

    workspace_payload = {
        "workspaces": [
            {
                "slug": "ws",
                "id": "1",
                "name": "Workspace",
                "projects": [
                    {"id": "p1", "slug": "proj1", "name": "Proj1"},
                    {"id": "p2", "slug": "proj2", "name": "Proj2"},
                ],
            }
        ]
    }
    monkeypatch.setattr(config_cmds, "_get_me", lambda prof: workspace_payload)
    monkeypatch.setattr(config_cmds, "_save_profile", lambda data, name, prof: None)
    monkeypatch.setattr(config_cmds, "_q_select", lambda **kwargs: workspace_payload["workspaces"][0]["projects"][0])
    config_cmds.set_workspace_cmd("ws")

    data = {"current_profile": "default", "profiles": {"default": {"workspace": {"id": "1", "slug": "ws"}}}}
    monkeypatch.setattr(config_cmds, "list_profiles", lambda: data)
    monkeypatch.setattr(config_cmds, "_get_me", lambda prof: workspace_payload)
    with pytest.raises(typer.Exit):
        config_cmds.set_project_cmd("missing")

    # interactive branch
    monkeypatch.setattr(config_cmds, "_q_select", lambda **kwargs: workspace_payload["workspaces"][0]["projects"][1])
    config_cmds.set_project_cmd(project=None)

    data["profiles"]["default"]["workspace"] = None
    monkeypatch.setattr(config_cmds, "list_profiles", lambda: data)
    with pytest.raises(typer.Exit):
        config_cmds.set_project_cmd()


def test_config_workspace_no_projects(monkeypatch):
    saved = {}
    profiles = {
        "current_profile": "default",
        "profiles": {"default": {"project": {"id": "p", "slug": "proj"}}},
    }
    monkeypatch.setattr(config_cmds, "list_profiles", lambda: profiles)
    monkeypatch.setattr(
        config_cmds,
        "_get_me",
        lambda prof: {"workspaces": [{"slug": "ws", "id": "1", "name": "Workspace", "projects": []}]},
    )
    monkeypatch.setattr(config_cmds, "_save_profile", lambda data, name, profile: saved.setdefault("profile", profile))
    config_cmds.set_workspace_cmd("ws")
    assert "project" not in saved["profile"]


def test_config_project_workspace_missing(monkeypatch):
    data = {"current_profile": "default", "profiles": {"default": {"workspace": {"id": "missing"}}}}
    monkeypatch.setattr(config_cmds, "list_profiles", lambda: data)
    monkeypatch.setattr(config_cmds, "_get_me", lambda prof: {"workspaces": []})
    with pytest.raises(typer.Exit):
        config_cmds.set_project_cmd()


def test_config_project_no_projects(monkeypatch):
    data = {"current_profile": "default", "profiles": {"default": {"workspace": {"id": "1", "slug": "ws"}}}}
    monkeypatch.setattr(config_cmds, "list_profiles", lambda: data)
    monkeypatch.setattr(
        config_cmds,
        "_get_me",
        lambda prof: {"workspaces": [{"id": "1", "slug": "ws", "projects": []}]},
    )
    with pytest.raises(typer.Exit):
        config_cmds.set_project_cmd()


def test_info_workspace_missing(monkeypatch):
    monkeypatch.setattr(info_cmds, "list_profiles", lambda: {})
    monkeypatch.setattr(info_cmds, "default_workspace", lambda data: False)
    assert info_cmds.show_default_workspace() is False


def test_version_fallback(monkeypatch):
    import aiel.__init__ as aiel_init

    def raise_pkg(_):
        raise PackageNotFoundError()

    monkeypatch.setattr("importlib.metadata.version", raise_pkg)
    reloaded = importlib.reload(aiel_init)
    assert reloaded.__version__ == "0+unknown"
def test_auth_login_requires_token(monkeypatch, runner: CliRunner):
    monkeypatch.setattr(auth_cmds, "get_current_base_url", lambda: "https://api")
    result = runner.invoke(auth_cmds.app, ["login", "--token", ""])
    assert result.exit_code != 0
