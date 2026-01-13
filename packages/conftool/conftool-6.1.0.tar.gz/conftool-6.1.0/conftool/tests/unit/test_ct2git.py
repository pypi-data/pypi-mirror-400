import asyncio

from unittest import mock
import pytest

from conftool import kvobject, configuration
from conftool.cli import conftool2git
from conftool.tests.unit import MockBackend


def test_parse_args_defaults():
    """Test that the default arguments are parsed correctly."""
    args = conftool2git.parse_args(["/path/to/repo"])
    assert args.bind_addr == "0.0.0.0"
    assert args.port == 1312
    assert args.config == "/etc/conftool/config.yaml"
    assert args.no_startup_sync is False
    assert args.max_queue_size == conftool2git.MAX_QUEUE_SIZE
    assert args.repo == "/path/to/repo"


def test_parse_args_custom():
    """Test that the custom arguments are parsed correctly."""
    args = conftool2git.parse_args(
        [
            "--bind-addr",
            # invalid IP address, but it's just a string for testing. Cope,netowrk people.
            "342.0.294.1",
            "--port",
            "161",
            "--config",
            "/etc/alternative.yaml",
            "--no-startup-sync",
            "--max-queue-size",
            "42",
            "/path/to/repo",
        ]
    )
    assert args.bind_addr == "342.0.294.1"
    assert args.port == 161
    assert args.config == "/etc/alternative.yaml"
    assert args.no_startup_sync is True
    assert args.max_queue_size == 42
    assert args.repo == "/path/to/repo"
