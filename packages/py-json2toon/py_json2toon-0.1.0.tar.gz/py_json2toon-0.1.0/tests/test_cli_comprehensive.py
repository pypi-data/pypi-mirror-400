"""Comprehensive CLI testing to verify all commands work correctly."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from typing import Iterable, Sequence

import pytest


def _run_cli(args: Sequence[str]):
    """Run the CLI module with the given arguments."""
    cmd = [sys.executable, "-m", "json2toon.cli", *args]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout, result.stderr


def _write_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _strip_line_numbers(lines: Iterable[str]) -> str:
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        cleaned.append(stripped.lstrip("0123456789 "))
    return "\n".join(cleaned)


def test_cli_round_trip(tmp_path):
    """Verify CLI commands convert both directions and report stats."""
    test_json = tmp_path / "test.json"
    test_toon = tmp_path / "test.toon"
    output_json = tmp_path / "output.json"
    invalid_json = tmp_path / "invalid.json"

    test_data = {
        "name": "Alice",
        "age": 30,
        "active": True,
        "balance": None,
        "scores": [95, 87, 92],
        "address": {"city": "NYC", "zip": "10001"},
        "hobbies": ["reading", "coding", "hiking"],
    }

    _write_json(str(test_json), test_data)

    code, _, stderr = _run_cli(["to-toon", str(test_json), "-o", str(test_toon)])
    assert code == 0, f"to-toon failed: {stderr}"
    assert test_toon.read_text(encoding="utf-8").strip()

    code, _, stderr = _run_cli([
        "to-json",
        str(test_toon),
        "-o",
        str(output_json),
        "-P",
    ])
    assert code == 0, f"to-json failed: {stderr}"
    assert json.loads(output_json.read_text(encoding="utf-8")) == test_data

    code, stdout, stderr = _run_cli(["report", str(test_json), "-f", "json"])
    assert code == 0, f"report failed: {stderr}"
    report = json.loads(stdout)
    assert {"json_tokens", "toon_tokens", "savings", "savings_percent"} <= set(report.keys())

    invalid_json.write_text("{invalid json", encoding="utf-8")
    code, _, _ = _run_cli(["to-toon", str(invalid_json)])
    assert code != 0, "Invalid JSON should cause non-zero exit"

    missing = tmp_path / "missing.json"
    code, _, _ = _run_cli(["to-toon", str(missing)])
    assert code != 0, "Missing file should cause non-zero exit"
