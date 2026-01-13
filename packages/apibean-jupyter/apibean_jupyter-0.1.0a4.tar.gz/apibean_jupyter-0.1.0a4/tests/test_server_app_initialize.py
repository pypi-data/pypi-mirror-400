from unittest.mock import MagicMock

from jupyter_server.serverapp import ServerApp
from jupyter_client.kernelspec import KernelSpecManager

from apibean.jupyter.wrapper import ApibeanJupyterApp
from apibean.jupyter.kernel import KernelMode


def test_initialize_without_manage_kernel(monkeypatch, server_app):
    # mock super().initialize để không sys.exit
    monkeypatch.setattr(ServerApp, "initialize", MagicMock())

    spy = MagicMock()
    monkeypatch.setattr(server_app, "_ensure_kernel", spy)

    server_app.initialize(argv=[], manage_kernel=False)

    spy.assert_not_called()


def test_initialize_with_manage_kernel(monkeypatch, server_app):
    # 1. Mock super().initialize
    monkeypatch.setattr(ServerApp, "initialize", MagicMock())

    # 2. GÁN KernelSpecManager THẬT
    server_app.kernel_spec_manager = KernelSpecManager()

    # 3. Spy _ensure_kernel
    spy = MagicMock(return_value="apibean-managed")
    monkeypatch.setattr(server_app, "_ensure_kernel", spy)

    # 4. Call initialize
    server_app.initialize(
        argv=[],
        manage_kernel=True,
        kernel_mode=KernelMode.MANAGED,
    )

    # 5. Assert
    spy.assert_called_once_with(KernelMode.MANAGED)
    assert server_app.kernel_spec_manager.default_kernel_name == "apibean-managed"
