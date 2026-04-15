import subprocess
import sys

import pytest


def test_import_pyrogram_has_no_uvloop_deprecation_warning():
    result = subprocess.run(
        [sys.executable, "-W", "default", "-c", "import pyrogram"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "uvloop.install() is deprecated" not in result.stderr
    assert "set_event_loop_policy' is deprecated" not in result.stderr
    assert "AbstractEventLoopPolicy' is deprecated" not in result.stderr


def test_get_event_loop_prefers_uvloop_when_available():
    pytest.importorskip("uvloop")

    script = (
        "import asyncio; "
        "from pyrogram import utils; "
        "asyncio.set_event_loop(None); "
        "loop = utils.get_event_loop(); "
        "print(type(loop).__module__.split('.', 1)[0]); "
        "loop.close()"
    )
    result = subprocess.run(
        [sys.executable, "-W", "default", "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "uvloop"
    assert "DeprecationWarning" not in result.stderr
