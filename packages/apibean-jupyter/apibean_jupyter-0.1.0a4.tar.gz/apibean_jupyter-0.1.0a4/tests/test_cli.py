from __future__ import annotations

import argparse
import json
import sys

import pytest

from apibean.jupyter import cli


# ---------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------

def test_build_parser_returns_argparse_parser():
    parser = cli.build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_parses_defaults():
    parser = cli.build_parser()
    args = parser.parse_args([])

    assert args.root is None
    assert args.ip == "127.0.0.1"
    assert args.port is None
    assert args.token is None
    assert args.no_lab is False
    assert args.info is False
    assert args.manage_kernel is False
    assert args.kernel_mode == "auto"


# ---------------------------------------------------------------------
# run_from_args
# ---------------------------------------------------------------------

def test_run_from_args_info_mode_prints_info_and_does_not_start(mocker, capsys):
    mock_server = mocker.Mock()
    mock_server.info = {"ip": "127.0.0.1", "port": 8888}

    mocker.patch(
        "apibean.jupyter.cli.JupyterServer",
        return_value=mock_server,
    )

    args = argparse.Namespace(
        root="notebooks",
        ip="127.0.0.1",
        port=8888,
        token=None,
        no_lab=False,
        info=True,
        manage_kernel=False,
        kernel_mode="auto",
    )

    cli.run_from_args(args)

    # Server.start must NOT be called
    mock_server.start.assert_not_called()

    # Info must be printed as JSON
    out = capsys.readouterr().out
    parsed = json.loads(out)

    assert parsed["ip"] == "127.0.0.1"
    assert parsed["port"] == 8888


def test_run_from_args_starts_server_blocking(mocker, capsys):
    mock_server = mocker.Mock()
    mock_server.url = "http://127.0.0.1:8888/"
    mock_server.info = {}

    mocker.patch(
        "apibean.jupyter.cli.JupyterServer",
        return_value=mock_server,
    )

    args = argparse.Namespace(
        root=".",
        ip="127.0.0.1",
        port=None,
        token=None,
        no_lab=False,
        info=False,
        manage_kernel=False,
        kernel_mode="auto",
    )

    cli.run_from_args(args)

    mock_server.start.assert_called_once_with(blocking=True)

    out = capsys.readouterr().out
    assert "Jupyter starting at" in out


def test_run_from_args_no_lab_flag(mocker, capsys):
    mock_server = mocker.Mock()
    mock_server.url = "url"
    mock_server.info = {}

    ctor = mocker.patch(
        "apibean.jupyter.cli.JupyterServer",
        return_value=mock_server,
    )

    args = argparse.Namespace(
        root=None,
        ip="127.0.0.1",
        port=None,
        token=None,
        no_lab=True,
        info=False,
        manage_kernel=False,
        kernel_mode="auto",
    )

    cli.run_from_args(args)

    out = capsys.readouterr().out
    assert "Jupyter starting at" in out

    ctor.assert_called_once()
    kwargs = ctor.call_args.kwargs

    assert kwargs["lab"] is False


def test_run_from_args_manage_kernel_and_kernel_mode_passed(mocker, capsys):
    mock_server = mocker.Mock()
    mock_server.url = "url"
    mock_server.info = {}

    ctor = mocker.patch(
        "apibean.jupyter.cli.JupyterServer",
        return_value=mock_server,
    )

    args = argparse.Namespace(
        root="notebooks",
        ip="0.0.0.0",
        port=9999,
        token="abc",
        no_lab=False,
        info=False,
        manage_kernel=True,
        kernel_mode="managed",
    )

    cli.run_from_args(args)

    out = capsys.readouterr().out
    assert "Jupyter starting at" in out

    ctor.assert_called_once_with(
        root_dir="notebooks",
        ip="0.0.0.0",
        port=9999,
        token="abc",
        lab=True,
        manage_kernel=True,
        kernel_mode="managed",
    )


# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------

def test_main_parses_args_and_runs(mocker):
    mock_run = mocker.patch("apibean.jupyter.cli.run_from_args")

    mocker.patch.object(
        sys,
        "argv",
        ["apibean-jupyter", "--root", "notebooks"],
    )

    cli.main()

    mock_run.assert_called_once()
