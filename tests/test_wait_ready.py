from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from wait_ready import wait_for_nodes  # noqa: E402


def test_wait_ready_retries_only_pending_nodes() -> None:
    rows = [
        {"name": "P1", "kind": "cisco_xrd", "mgmt_ipv4": "10.0.0.1"},
        {"name": "P2", "kind": "cisco_xrd", "mgmt_ipv4": "10.0.0.2"},
    ]
    attempts = {"P1": 0, "P2": 0}

    def validator(row: dict[str, str]) -> dict[str, str]:
        attempts[row["name"]] += 1
        cli = "ok" if row["name"] == "P1" or attempts[row["name"]] > 1 else "failed"
        return {**row, "host": row["mgmt_ipv4"], "cli": cli}

    times = iter([0.0, 0.0, 1.0])
    ready, pending = wait_for_nodes(
        rows,
        timeout=10,
        interval=1,
        workers=2,
        clock=lambda: next(times),
        sleeper=lambda _seconds: None,
        validator=validator,
    )

    assert [result["name"] for result in ready] == ["P1", "P2"]
    assert pending == []
    assert attempts == {"P1": 1, "P2": 2}


def test_wait_ready_returns_pending_at_timeout() -> None:
    rows = [{"name": "P1", "kind": "cisco_xrd", "mgmt_ipv4": "10.0.0.1"}]
    times = iter([0.0, 2.0])

    def validator(row: dict[str, str]) -> dict[str, str]:
        return {**row, "host": row["mgmt_ipv4"], "cli": "failed"}

    ready, pending = wait_for_nodes(
        rows,
        timeout=1,
        interval=1,
        workers=1,
        clock=lambda: next(times),
        sleeper=lambda _seconds: None,
        validator=validator,
    )

    assert ready == []
    assert [row["name"] for row in pending] == ["P1"]
