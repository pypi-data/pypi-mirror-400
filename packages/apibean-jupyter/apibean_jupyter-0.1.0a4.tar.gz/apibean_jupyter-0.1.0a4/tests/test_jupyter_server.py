import time
import threading
import pytest

from apibean.jupyter.server import JupyterServer
from apibean.jupyter.kernel import KernelMode
from apibean.jupyter.plugins import JupyterPlugin


# -----------------------------
# helpers
# -----------------------------

class SpyPlugin(JupyterPlugin):
    def __init__(self):
        self.calls = []

    def pre_initialize(self, ctx):
        self.calls.append(("pre_initialize", ctx))

    def post_initialize(self, app):
        self.calls.append(("post_initialize", app))

    def pre_start(self, app):
        self.calls.append(("pre_start", app))

    def post_start(self, app):
        self.calls.append(("post_start", app))

    def shutdown(self, app):
        self.calls.append(("shutdown", app))


# -----------------------------
# constructor
# -----------------------------

def test_initialize_builds_argv(dummy_app):
    server = JupyterServer(
        root_dir="/work",
        ip="0.0.0.0",
        port=9999,
        token="abc",
        lab=True,
        extra_args=["--debug"],
        manage_kernel=True,
        kernel_mode=KernelMode.MANAGED,
    )

    argv = dummy_app.argv

    assert "--ServerApp.root_dir" in argv
    assert "/work" in argv

    assert "--ServerApp.ip" in argv
    assert "0.0.0.0" in argv

    assert "--ServerApp.port" in argv
    assert "9999" in argv

    assert "--ServerApp.token" in argv
    assert "abc" in argv

    assert "--ServerApp.default_url=/lab" in argv
    assert "--debug" in argv

    assert dummy_app.manage_kernel is True
    assert dummy_app.kernel_mode == KernelMode.MANAGED


def test_initialize_calls_plugin_hooks(dummy_app):
    plugin = SpyPlugin()

    server = JupyterServer(
        plugins=[plugin],
    )

    names = [c[0] for c in plugin.calls]
    assert names == [
        "pre_initialize",
        "post_initialize",
    ]


# -----------------------------
# start
# -----------------------------

def test_start_blocking(dummy_app):
    server = JupyterServer()

    server.start(blocking=True)

    assert dummy_app.io_loop is not None
    assert server.is_running() is True


def test_start_non_blocking(dummy_app):
    server = JupyterServer()

    server.start(blocking=False)

    assert isinstance(server._thread, threading.Thread)
    assert server._thread.daemon is True

    # wait briefly for thread to run
    time.sleep(0.05)

    assert server.is_running() is True


def test_start_calls_plugin_hooks(dummy_app):
    plugin = SpyPlugin()
    server = JupyterServer(plugins=[plugin])

    server.start(blocking=True)

    names = [c[0] for c in plugin.calls]
    assert names == [
        "pre_initialize",
        "post_initialize",
        "pre_start",
        "post_start",
    ]


# -----------------------------
# stop
# -----------------------------

def test_stop_stops_ioloop(dummy_app):
    server = JupyterServer()
    server.start(blocking=True)

    loop = dummy_app.io_loop
    assert loop.stopped is False

    server.stop()

    assert loop.stopped is True


def test_stop_calls_plugin_shutdown(dummy_app):
    plugin = SpyPlugin()
    server = JupyterServer(plugins=[plugin])
    server.start(blocking=True)

    server.stop()

    names = [c[0] for c in plugin.calls]
    assert "shutdown" in names


# -----------------------------
# info / url
# -----------------------------

def test_url_property(dummy_app):
    server = JupyterServer()

    assert server.url == "http://127.0.0.1:8888/lab/?token=test-token"


def test_info_property(dummy_app):
    server = JupyterServer()

    info = server.info

    assert info["ip"] == "127.0.0.1"
    assert info["port"] == 8888
    assert info["token"] == "test-token"
    assert info["root_dir"] == "/tmp"
    assert info["pid"] == 12345
    assert info["version"] == "9.0.0"
