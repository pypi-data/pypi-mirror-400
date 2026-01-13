from pathlib import Path
from unittest.mock import MagicMock

import pytest

from apibean.jupyter.wrapper import ApibeanJupyterApp
from apibean.jupyter.kernel import KernelMode


def test_ensure_kernel_calls_kernel_manager(monkeypatch, server_app, tmp_path):
    fake_kernel_name = "apibean-test"

    mock_km = MagicMock()
    mock_km.prepare.return_value = fake_kernel_name
    mock_km.name = fake_kernel_name

    def fake_km_ctor(**kwargs):
        # kiểm tra tham số quan trọng
        assert kwargs["mode"] == KernelMode.MANAGED
        assert kwargs["workspace_root"] == tmp_path
        return mock_km

    monkeypatch.setattr(
        "apibean.jupyter.wrapper.KernelManager",
        fake_km_ctor,
    )

    server_app.workspace_root = str(tmp_path)

    kernel_name = server_app._ensure_kernel(KernelMode.MANAGED)

    assert kernel_name == fake_kernel_name
    mock_km.prepare.assert_called_once()
