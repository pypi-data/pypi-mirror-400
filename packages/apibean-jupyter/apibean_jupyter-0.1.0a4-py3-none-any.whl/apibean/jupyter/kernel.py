"""
Kernel management utilities for apibean-jupyter.

This module provides a lightweight abstraction layer on top of
Jupyter's KernelSpec system, allowing apibean to dynamically decide
how a Python kernel should be selected or installed at runtime.

The design supports three kernel strategies:

- SYSTEM:
    Use an existing system kernel without modification.
- MANAGED:
    Ensure a dedicated kernel is installed and managed by apibean.
- AUTO:
    Automatically decide between SYSTEM and MANAGED depending on
    the runtime environment (e.g. virtualenv, existing kernels).

This module is intentionally free of traitlets and ServerApp
dependencies, making it easy to test in isolation.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

from enum import Enum
from pathlib import Path
from typing import Optional

from jupyter_client.kernelspec import KernelSpecManager


class KernelMode(str, Enum):
    """
    Kernel selection and management strategy.

    This enum controls how apibean-jupyter determines which Jupyter
    kernel should be used when starting a server.

    Attributes:
        AUTO:
            Automatically choose between a managed kernel and an
            existing system kernel, based on the runtime environment.
        MANAGED:
            Always ensure a dedicated kernel is installed and use it.
        SYSTEM:
            Do not install or modify kernels; let Jupyter use its
            default or an existing system kernel.
    """
    AUTO = "auto"
    MANAGED = "managed"
    SYSTEM = "system"


class KernelManager:
    """
    Manage the lifecycle and selection of a Jupyter kernel for apibean.

    This class encapsulates the logic for deciding whether a kernel
    should be installed, reused, or delegated to the system default,
    without directly coupling to Jupyter ServerApp internals.

    Typical responsibilities include:

    - Detecting whether the application is running inside a virtual
      environment.
    - Ensuring a managed kernel is installed when required.
    - Reusing existing kernels when appropriate.
    - Injecting workspace paths into the kernel environment.

    The result of this process is a kernel name that can be passed
    to Jupyter ServerApp, or ``None`` to allow Jupyter to decide.
    """
    def __init__(
        self,
        mode: KernelMode,
        name: str,
        display_name: str,
        python_executable: str,
        user: bool = True,
        workspace_root: Optional[Path] = None,
    ):
        """
        Initialize a KernelManager instance.

        Args:
            mode:
                Kernel management strategy to apply.
            name:
                The internal name of the kernel (used by Jupyter).
            display_name:
                Human-readable name shown in Jupyter UI.
            python_executable:
                Path to the Python executable used to install the kernel.
            user:
                Whether to install the kernel in the user kernel directory.
            workspace_root:
                Optional workspace root directory to be injected into
                the kernel's PYTHONPATH.
        """
        self.mode = mode
        self.name = name
        self.display_name = display_name
        self.python = python_executable
        self.user = user
        self.workspace_root = workspace_root
        self.ksm = None

    def prepare(self) -> str | None:
        """
        Prepare the kernel according to the selected KernelMode.

        Depending on the mode, this method may install a kernel,
        reuse an existing one, or defer entirely to Jupyter's
        default behavior.

        Returns:
            The name of the kernel to be used by Jupyter ServerApp,
            or ``None`` if Jupyter should select the default kernel
            (SYSTEM mode).
        """
        if self.mode == KernelMode.SYSTEM:
            return None

        if self.mode == KernelMode.MANAGED:
            self._ensure_managed()
            return self.name

        if self.mode == KernelMode.AUTO:
            return self._auto_decide()

    def _auto_decide(self) -> str | None:
        """
        Automatically decide which kernel strategy to use.

        Decision order:

        1. If running inside a virtual environment, ensure and use
           a managed kernel.
        2. If a kernel with the configured name already exists,
           reuse it as a system kernel.
        3. Otherwise, fall back to installing and using a managed kernel.

        Returns:
            The selected kernel name, or ``None`` if delegation to
            the system default is required.
        """
        self.ksm = self.ksm or KernelSpecManager()

        # 1. Nếu đang chạy trong uv / venv → managed
        if self._running_in_virtual_env():
            self._ensure_managed()
            return self.name

        # 2. Nếu kernel đã tồn tại → system
        if self.name in self.ksm.find_kernel_specs():
            return self.name

        # 3. Fallback → managed
        self._ensure_managed()
        return self.name

    def _running_in_virtual_env(self) -> bool:
        """
        Detect whether the application is running inside a virtual environment.

        This method supports both ``virtualenv`` and ``venv`` styles
        by checking Python runtime prefixes.

        Returns:
            True if running inside a virtual environment, False otherwise.
        """
        return (
            hasattr(sys, "real_prefix")
            or sys.prefix != sys.base_prefix
        )

    def _ensure_managed(self):
        """
        Ensure that a managed kernel is installed and available.

        If a kernel with the configured name already exists, this
        method does nothing. Otherwise, it installs a new kernel
        using ``ipykernel`` and optionally patches its environment
        with workspace-specific settings.
        """
        self.ksm = self.ksm or KernelSpecManager()

        if self.name in self.ksm.find_kernel_specs():
            return

        cmd = [
            self.python,
            "-m", "ipykernel",
            "install",
            "--name", self.name,
            "--display-name", self.display_name,
            "--user",
        ]
        subprocess.check_call(cmd)

        if self.workspace_root:
            self._patch_kernelspec_env()

    def _patch_kernelspec_env(self):
        """
        Patch the kernel specification to inject workspace configuration.

        This method modifies the kernel's ``kernel.json`` to:

        - Prepend the workspace root to PYTHONPATH.
        - Preserve any existing PYTHONPATH values.
        - Mark the kernel as apibean-managed via metadata.

        This allows kernels to automatically resolve project-local
        imports without additional user configuration.
        """
        self.ksm = self.ksm or KernelSpecManager()

        spec_dir = Path(self.ksm.user_kernel_dir) / self.name
        kernel_json = spec_dir / "kernel.json"

        spec = json.loads(kernel_json.read_text())
        env = spec.setdefault("env", {})

        paths = [str(self.workspace_root)]

        if "PYTHONPATH" in env:
            paths.append(env["PYTHONPATH"])

        env["PYTHONPATH"] = os.pathsep.join(paths)

        spec.setdefault("metadata", {}).setdefault(
            "apibean", {}
        )["workspace"] = True

        kernel_json.write_text(json.dumps(spec, indent=2))
