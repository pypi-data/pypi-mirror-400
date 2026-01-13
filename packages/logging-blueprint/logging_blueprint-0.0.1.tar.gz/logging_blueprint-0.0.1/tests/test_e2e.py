"""'End-to-end' tests for the logging-blueprint package.

These tests seek to exercise the core public API of the logging-blueprint package. They are based on 'examples', which
are simple Python scripts that use some portions of the logging-blueprint package. The tests run these scripts and check
their outputs to ensure they behave as expected.

NOTE: This package is **EXPERIMENTAL** and breaking changes should be expected, even to "public" interfaces.
Contributors are welcome to make _justifiable_ breaking changes to the package as-needed (along with accompanying
changes to this test suite).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from subprocess import run

import pytest


@pytest.mark.json_extra
def test_apply_env_logging_emits_json_with_extras(tmp_path: Path, examples_dir: Path) -> None:
    script_src = examples_dir / "apply_env_logging.py"
    script_dst = tmp_path / "apply_env_logging.py"
    script_dst.write_text(script_src.read_text())

    env = os.environ.copy()
    env.update(
        {
            "PY_LOG": "warning,demo=info",
            "PY_LOG_STYLE": "json",
            "PY_LOG_STREAM": "stdout",
        }
    )

    project_root = Path(__file__).resolve().parent.parent
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{project_root}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else str(project_root)

    proc = run(
        [sys.executable, str(script_dst)],
        check=True,
        capture_output=True,
        text=True,
        env=env,
        cwd=tmp_path,
    )

    lines = [line for line in proc.stdout.splitlines() if line]
    assert proc.stderr == ""
    assert len(lines) == 2

    first, second = (json.loads(line) for line in lines)

    assert first["levelname"] == "INFO"
    assert first["name"] == "demo"
    assert first["message"] == "hello world"
    assert first["request_id"] == "abc123"

    assert second["levelname"] == "ERROR"
    assert second["name"] == "demo"
    assert second["message"] == "boom"
    assert second["user_id"] == 42
