import json
from pathlib import Path
from unittest.mock import MagicMock

from apibean.jupyter.kernel import KernelManager, KernelMode


def test_patch_kernelspec_env(tmp_path, monkeypatch):
    kernel_dir = tmp_path / "apibean"
    kernel_dir.mkdir(parents=True)

    kernel_json = kernel_dir / "kernel.json"
    kernel_json.write_text(
        json.dumps({
            "argv": ["python"],
            "env": {},
        })
    )

    fake_ksm = MagicMock()
    fake_ksm.user_kernel_dir = str(tmp_path)

    monkeypatch.setattr(
        "apibean.jupyter.kernel.KernelSpecManager",
        lambda: fake_ksm,
    )

    km = KernelManager(
        mode=KernelMode.MANAGED,
        name="apibean",
        display_name="Apibean",
        python_executable="python",
        workspace_root=Path("/workspace"),
    )

    km._patch_kernelspec_env()

    data = json.loads(kernel_json.read_text())

    assert "PYTHONPATH" in data["env"]
    assert "/workspace" in data["env"]["PYTHONPATH"]
    assert data["metadata"]["apibean"]["workspace"] is True
