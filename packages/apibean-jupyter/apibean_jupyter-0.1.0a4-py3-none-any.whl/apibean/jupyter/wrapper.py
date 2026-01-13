"""
Custom Jupyter ServerApp integration for apibean.

This module defines :class:`ApibeanJupyterApp`, a subclass of
``jupyter_server.serverapp.ServerApp`` that integrates apibean-specific
kernel management and workspace handling.

Key responsibilities:

- Optional management and installation of a dedicated Jupyter kernel
- Injection of workspace paths into kernel execution environment
- Seamless operation inside `uv run` and similar ephemeral environments
- Compatibility with plugin-based server lifecycle orchestration

This class is not intended to be launched directly from the command line.
Instead, it is instantiated and controlled programmatically via higher-
level wrappers such as :class:`JupyterServer`.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from jupyter_server.serverapp import ServerApp
from traitlets import Unicode

from .kernel import KernelManager, KernelMode


class ApibeanJupyterApp(ServerApp):
    """
    Jupyter ServerApp integrated with apibean kernel management.

    ``ApibeanJupyterApp`` extends the standard Jupyter ``ServerApp`` by
    injecting a configurable kernel management layer. This allows
    applications to:

    - Automatically provision a managed kernel
    - Bind kernels to a specific workspace or project root
    - Select kernel behavior via ``auto``, ``managed``, or ``system`` modes

    The class relies on :class:`KernelManager` to prepare kernels and
    optionally modify their execution environment (e.g. ``PYTHONPATH``).

    Notes
    -----
    - This class is a singleton; use ``ApibeanJupyterApp.instance()``.
    - Kernel management is opt-in and controlled by ``manage_kernel``.
    - The underlying Jupyter server lifecycle is still governed by
      ``ServerApp``.

    Attributes
    ----------
    kernel_name:
        Name of the kernel managed by apibean-jupyter.
    workspace_root:
        Workspace root directory injected into kernel execution environment.
    """

    kernel_name = Unicode(
        default_value="apibean",
        help="Kernel name managed by apibean-jupyter",
        config=True,
    )

    workspace_root = Unicode(
        default_value="",
        help="Workspace root to be injected into the kernel PYTHONPATH",
        config=True,
    )

    @classmethod
    def clear_instance(cls):
        cls._instance = None

    def initialize(self, argv=None, manage_kernel=False, kernel_mode = KernelMode.AUTO):
        """
        Initialize the Jupyter application with optional kernel management.

        This method extends ``ServerApp.initialize`` by performing
        apibean-specific kernel preparation *before* the standard Jupyter
        initialization sequence.

        The initialization flow is:

        1. Optionally prepare or select a kernel via ``KernelManager``
        2. Delegate to ``ServerApp.initialize`` for core setup
        3. Set the prepared kernel as the default kernel (if applicable)

        Parameters
        ----------
        argv:
            Command-line arguments forwarded to ``ServerApp.initialize``.
        manage_kernel:
            If ``True``, apibean-jupyter will ensure the kernel specified by
            ``kernel_name`` is available and configured.
        kernel_mode:
            Kernel selection strategy:
            - ``auto``: use managed kernel if available, otherwise system
            - ``managed``: force use of apibean-managed kernel
            - ``system``: use system-installed kernels only

        Notes
        -----
        - This method does not start the server.
        - Kernel preparation occurs before traitlets configuration parsing.
        """
        kernel_name = self._ensure_kernel(kernel_mode) if manage_kernel else None

        super().initialize(argv)

        if kernel_name:
            self.kernel_spec_manager.default_kernel_name = kernel_name

    # ------------------------------------------------------------------ #
    # kernel integration
    # ------------------------------------------------------------------ #

    def _ensure_kernel(self, kernel_mode):
        """
        Ensure that an appropriate kernel is available for the server.

        This method delegates kernel preparation to :class:`KernelManager`,
        passing along configuration such as kernel name, Python executable,
        workspace root, and kernel mode.

        The returned kernel name is later assigned as the default kernel
        for the Jupyter server.

        Parameters
        ----------
        kernel_mode:
            Kernel management mode controlling how kernels are selected or
            installed.

        Returns
        -------
        str
            The name of the prepared or selected kernel.

        Side Effects
        ------------
        - May install or update a Jupyter kernel specification
        - May write kernel metadata to the user kernels directory
        """
        workspace = self._resolve_workspace_root()

        km = KernelManager(
            mode=kernel_mode,
            name=self.kernel_name,
            display_name=f"Python ({self.kernel_name})",
            python_executable=sys.executable,
            user=True,
            workspace_root=workspace,
        )

        kernel_name = km.prepare()

        self.log.info(
            "apibean-jupyter kernel ready: %s (workspace=%s)",
            km.name,
            workspace or "<none>",
        )

        return kernel_name

    def _resolve_workspace_root(self) -> Optional[Path]:
        """
        Resolve the workspace root directory for kernel execution.

        Resolution strategy:

        1. If ``workspace_root`` trait is explicitly set, use it
        2. Otherwise, if the current working directory contains a
           ``pyproject.toml``, treat it as the workspace root
        3. If neither condition is met, return ``None``

        The resolved workspace root is used to inject paths into the kernel
        environment (e.g. via ``PYTHONPATH``).

        Returns
        -------
        pathlib.Path or None
            Absolute path to the workspace root, or ``None`` if no suitable
            workspace could be determined.
        """
        if self.workspace_root:
            return Path(self.workspace_root).resolve()

        # fallback: uv / cwd
        cwd = Path.cwd()
        if (cwd / "pyproject.toml").exists():
            return cwd

        return None
