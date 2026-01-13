"""
High-level wrapper for running a Jupyter Server/Lab instance.

This module defines :class:`JupyterServer`, a convenience façade around
``ApibeanJupyterApp`` that:

- Builds and normalizes Jupyter ServerApp arguments
- Integrates plugin-based lifecycle hooks
- Optionally manages Jupyter kernels (auto / managed / system)
- Supports blocking and non-blocking startup modes

The goal is to embed JupyterLab as a controllable component inside
larger applications (e.g. apibean-jupyter, codenote) rather than
running it as a standalone CLI process.

Typical usage::

    server = JupyterServer(root_dir="notebooks")
    server.start(blocking=False)
    print(server.url)
"""
from __future__ import annotations

import threading
from typing import Optional

from .kernel import KernelMode
from .plugins import JupyterPlugin
from .wrapper import ApibeanJupyterApp


class JupyterServer:
    """
    Embedded Jupyter Server/Lab controller.

    ``JupyterServer`` is a thin orchestration layer on top of
    :class:`ApibeanJupyterApp` that handles:

    - Argument construction for ``ServerApp``
    - Plugin lifecycle dispatch
    - Kernel management mode selection
    - Threaded or blocking execution

    It is designed to be instantiated programmatically and controlled
    from another Python application instead of being launched via
    ``jupyter lab`` or ``jupyter server`` CLI.

    Notes
    -----
    - The underlying Jupyter application is a *singleton*
      (``ApibeanJupyterApp.instance()``).
    - Calling ``start(blocking=False)`` will run the server in a daemon
      thread.
    - Kernel behavior is delegated to the KernelManager based on
      ``kernel_mode``.

    Parameters
    ----------
    root_dir:
        Root directory exposed by Jupyter (workspace / notebooks).
    ip:
        IP address to bind the Jupyter server to.
    port:
        TCP port for the Jupyter server. If ``None``, Jupyter will
        auto-select a free port.
    token:
        Authentication token. If ``None``, token authentication may
        be disabled depending on Jupyter defaults.
    lab:
        Whether to start JupyterLab (``/lab``) instead of the classic UI.
    extra_args:
        Additional raw command-line arguments forwarded to ServerApp.
    plugins:
        Optional list of :class:`JupyterPlugin` instances participating
        in the lifecycle.
    manage_kernel:
        Whether kernel installation/management should be handled by
        apibean-jupyter.
    kernel_mode:
        Kernel selection strategy (``auto``, ``managed``, ``system``).
    """
    def __init__(
        self,
        *,
        root_dir: Optional[str] = None,
        ip: str = "127.0.0.1",
        port: Optional[int] = None,
        token: Optional[str] = None,
        lab: bool = True,
        extra_args: Optional[list[str]] = None,
        plugins: Optional[list[JupyterPlugin]] = None,
        manage_kernel: bool = False,
        kernel_mode: str = KernelMode.AUTO,
    ):
        """
        Initialize a JupyterServer instance and prepare the ServerApp.

        This method:
        - Constructs the ServerApp argument list
        - Executes plugin ``pre_initialize`` hooks
        - Initializes the underlying ``ApibeanJupyterApp``
        - Executes plugin ``post_initialize`` hooks

        No network sockets or event loops are started at this stage.
        Use :meth:`start` to actually launch the server.

        Parameters
        ----------
        root_dir:
            Directory served by Jupyter as the workspace root.
        ip:
            IP address to bind to.
        port:
            Port number for the server.
        token:
            Authentication token string.
        lab:
            If ``True``, sets the default URL to ``/lab``.
        extra_args:
            Additional ServerApp CLI arguments.
        plugins:
            List of plugins receiving lifecycle callbacks.
        manage_kernel:
            Enable kernel installation/management logic.
        kernel_mode:
            Kernel management mode (auto / managed / system).
        """
        self._plugins = plugins or []
        self._thread: Optional[threading.Thread] = None

        argv: list[str] = []

        if root_dir:
            argv += ["--ServerApp.root_dir", root_dir]
        if ip:
            argv += ["--ServerApp.ip", ip]
        if port:
            argv += ["--ServerApp.port", str(port)]
        if token is not None:
            argv += ["--ServerApp.token", token]

        if lab:
            argv.append("--ServerApp.default_url=/lab")

        if extra_args:
            argv += extra_args

        for p in self._plugins:
            p.pre_initialize({"argv": argv})

        self.app = ApibeanJupyterApp.instance()
        self.app.initialize(argv,
            manage_kernel=manage_kernel,
            kernel_mode=kernel_mode,
        )

        for p in self._plugins:
            p.post_initialize(self.app)

    # - lifecycle -------------------------------

    def start(self, *, blocking: bool = True) -> None:
        """
        Start the Jupyter server.

        This method triggers the following lifecycle sequence:

        1. Plugin ``pre_start`` hooks
        2. Start the underlying Jupyter application
        3. Plugin ``post_start`` hooks

        Parameters
        ----------
        blocking:
            If ``True``, this call blocks the current thread until the
            Jupyter server exits.
            If ``False``, the server is started in a background daemon
            thread.

        Notes
        -----
        - In non-blocking mode, the thread is marked as ``daemon=True``.
        - The server is considered running once ``io_loop`` is created.
        """
        for p in self._plugins:
            p.pre_start(self.app)

        if blocking:
            self.app.start()
        else:
            self._thread = threading.Thread(
                target=self.app.start,
                name="JupyterServerThread",
                daemon=True,
            )
            self._thread.start()

        for p in self._plugins:
            p.post_start(self.app)

    def stop(self) -> None:
        """
        Stop the Jupyter server.

        This method:
        - Stops the underlying Tornado I/O loop if running
        - Calls plugin ``shutdown`` hooks

        It is safe to call this method multiple times.

        Notes
        -----
        This does not forcibly kill the process; it requests a graceful
        shutdown via the event loop.
        """
        if self.app.io_loop:
            self.app.io_loop.stop()

        for p in self._plugins:
            p.shutdown(self.app)

    def is_running(self) -> bool:
        """
        Check whether the Jupyter server is currently running.

        Returns
        -------
        bool
            ``True`` if the Jupyter application's I/O loop has been
            created, otherwise ``False``.
        """
        return self.app.io_loop is not None

    # - info ------------------------------------

    @property
    def url(self) -> str:
        """
        Public access URL for JupyterLab.

        Returns
        -------
        str
            Fully-qualified URL including authentication token,
            typically ending with ``/lab/?token=...``.
        """
        return f"{self.app.connection_url}lab/?token={self.app.token}"

    @property
    def info(self) -> dict:
        """
        Runtime information about the Jupyter server.

        Returns
        -------
        dict
            A dictionary containing connection and runtime metadata,
            including:

            - ip
            - port
            - token
            - base_url
            - connection_url
            - display_url
            - root_dir
            - pid
            - version
        """
        return {
            "ip": self.app.ip,
            "port": self.app.port,
            "token": self.app.token,
            "base_url": self.app.base_url,
            "connection_url": self.app.connection_url,
            "display_url": self.app.display_url,
            "root_dir": self.app.root_dir,
            "pid": self.app.pid,
            "version": self.app.version,
        }
