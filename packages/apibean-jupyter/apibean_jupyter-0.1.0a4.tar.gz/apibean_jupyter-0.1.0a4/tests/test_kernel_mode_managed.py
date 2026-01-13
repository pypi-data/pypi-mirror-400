import subprocess
from unittest.mock import MagicMock

from apibean.jupyter.kernel import KernelManager, KernelMode


def test_prepare_managed_calls_ensure(monkeypatch):
    km = KernelManager(
        mode=KernelMode.MANAGED,
        name="apibean",
        display_name="Apibean",
        python_executable="python",
    )

    spy = MagicMock()
    monkeypatch.setattr(km, "_ensure_managed", spy)

    result = km.prepare()

    spy.assert_called_once()
    assert result == "apibean"


def test_ensure_managed_installs_kernel(monkeypatch):
    fake_ksm = MagicMock()
    fake_ksm.find_kernel_specs.return_value = {}

    monkeypatch.setattr(
        "apibean.jupyter.kernel.KernelSpecManager",
        lambda: fake_ksm,
    )

    check_call = MagicMock()
    monkeypatch.setattr(subprocess, "check_call", check_call)

    km = KernelManager(
        mode=KernelMode.MANAGED,
        name="apibean",
        display_name="Apibean",
        python_executable="python",
    )

    km._ensure_managed()

    check_call.assert_called_once()

