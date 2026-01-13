"""
Command-line interface for apibean-jupyter.

This module defines the CLI entrypoint used to launch a Jupyter Server
integrated with apibean features, including managed kernel installation
and workspace-aware PYTHONPATH injection.

Typical usage::

    apibean-jupyter --root notebooks
    apibean-jupyter --root . --manage-kernel --kernel-mode auto
    apibean-jupyter --info

The CLI is intentionally lightweight and delegates most runtime behavior
to :class:`apibean.jupyter.server.JupyterServer`.
"""
import argparse
import json

from .kernel import KernelMode
from .server import JupyterServer


def build_parser() -> argparse.ArgumentParser:
    """
    Build and return the argument parser for the apibean-jupyter CLI.

    The parser defines options for configuring the embedded Jupyter Server,
    including network settings, notebook root directory, JupyterLab enablement,
    and kernel management behavior.

    Returns
    -------
    argparse.ArgumentParser
        A fully configured argument parser instance.
    """
    parser = argparse.ArgumentParser("apibean-jupyter")
    parser.add_argument("--root", help="Notebook root directory")
    parser.add_argument("--ip", default="127.0.0.1")
    parser.add_argument("--port", type=int)
    parser.add_argument("--token")
    parser.add_argument("--no-lab", action="store_true")
    parser.add_argument("--info", action="store_true")
    parser.add_argument("--manage-kernel", action="store_true")
    parser.add_argument("--kernel-mode",
        choices=[m.value for m in KernelMode],
        default="auto",
        help="Kernel mode: auto | managed | system",
    )
    return parser


def run_from_args(args: argparse.Namespace) -> None:
    """
    Run the Jupyter server using parsed command-line arguments.

    This function translates CLI arguments into a :class:`JupyterServer`
    instance and controls the startup behavior.

    If the ``--info`` flag is provided, the server is not started; instead,
    a JSON document describing the resolved server configuration is printed
    to stdout.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments produced by ``build_parser()``.
    """
    server = JupyterServer(
        root_dir=args.root,
        ip=args.ip,
        port=args.port,
        token=args.token,
        lab=not args.no_lab,
        manage_kernel=args.manage_kernel,
        kernel_mode=args.kernel_mode,
    )

    if args.info:
        print(json.dumps(server.info, indent=2))
        return

    print(f"🚀 Jupyter starting at: {server.url}")
    server.start(blocking=True)


def main():
    """
    CLI entrypoint for apibean-jupyter.

    This function parses command-line arguments and starts the Jupyter Server
    accordingly. It is intended to be used as the ``console_scripts`` entry
    point defined in ``pyproject.toml``.

    Example
    -------
    ::

        uv run --with apibean-jupyter apibean-jupyter --root notebooks
    """
    run_from_args(build_parser().parse_args())
