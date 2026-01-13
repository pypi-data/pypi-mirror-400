from unittest.mock import MagicMock

from apibean.jupyter.kernel import KernelManager, KernelMode


def test_auto_mode_virtualenv(monkeypatch):
    km = KernelManager(
        mode=KernelMode.AUTO,
        name="apibean",
        display_name="Apibean",
        python_executable="python",
    )

    monkeypatch.setattr(km, "_running_in_virtual_env", lambda: True)

    spy = MagicMock()
    monkeypatch.setattr(km, "_ensure_managed", spy)

    result = km.prepare()

    spy.assert_called_once()
    assert result == "apibean"


def test_auto_mode_existing_kernel(monkeypatch):
    km = KernelManager(
        mode=KernelMode.AUTO,
        name="apibean",
        display_name="Apibean",
        python_executable="python",
    )

    monkeypatch.setattr(km, "_running_in_virtual_env", lambda: False)

    fake_ksm = MagicMock()
    fake_ksm.find_kernel_specs.return_value = {"apibean": "/x"}

    monkeypatch.setattr(
        "apibean.jupyter.kernel.KernelSpecManager",
        lambda: fake_ksm,
    )

    spy = MagicMock()
    monkeypatch.setattr(km, "_ensure_managed", spy)

    result = km.prepare()

    spy.assert_not_called()
    assert result == "apibean"


def test_auto_mode_fallback(monkeypatch):
    km = KernelManager(
        mode=KernelMode.AUTO,
        name="apibean",
        display_name="Apibean",
        python_executable="python",
    )

    monkeypatch.setattr(km, "_running_in_virtual_env", lambda: False)

    fake_ksm = MagicMock()
    fake_ksm.find_kernel_specs.return_value = {}

    monkeypatch.setattr(
        "apibean.jupyter.kernel.KernelSpecManager",
        lambda: fake_ksm,
    )

    spy = MagicMock()
    monkeypatch.setattr(km, "_ensure_managed", spy)

    result = km.prepare()

    spy.assert_called_once()
    assert result == "apibean"
