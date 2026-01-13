from unittest.mock import MagicMock

from apibean.jupyter.kernel import KernelManager, KernelMode


def test_prepare_system_mode():
    km = KernelManager(
        mode=KernelMode.SYSTEM,
        name="apibean",
        display_name="Apibean",
        python_executable="python",
    )

    result = km.prepare()

    assert result is None
