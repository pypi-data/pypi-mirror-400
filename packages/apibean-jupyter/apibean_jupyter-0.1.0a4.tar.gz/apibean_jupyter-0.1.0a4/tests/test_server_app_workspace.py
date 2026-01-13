from pathlib import Path

from apibean.jupyter.wrapper import ApibeanJupyterApp


def test_resolve_workspace_from_config(server_app, tmp_path):
    server_app.workspace_root = str(tmp_path)

    root = server_app._resolve_workspace_root()

    assert root == tmp_path.resolve()


def test_resolve_workspace_from_cwd(monkeypatch, tmp_path, server_app):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'")

    monkeypatch.chdir(tmp_path)

    root = server_app._resolve_workspace_root()

    assert root == tmp_path.resolve()


def test_resolve_workspace_none(monkeypatch, tmp_path, server_app):
    monkeypatch.chdir(tmp_path)

    root = server_app._resolve_workspace_root()

    assert root is None
