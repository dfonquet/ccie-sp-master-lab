#!/usr/bin/env python3
"""Poll real management and CLI readiness instead of sleeping blindly."""

from __future__ import annotations

import argparse
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from credentials import connection_credentials
from validate_nodes import validate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = ROOT / "inventory" / "nodes.csv"


def require_credentials(rows: list[dict[str, str]]) -> None:
    """Fail before polling when a credential required by the inventory is absent."""
    for kind in sorted({row["kind"] for row in rows}):
        connection_credentials(kind)


def wait_for_nodes(
    rows: list[dict[str, str]],
    *,
    timeout: float,
    interval: float,
    workers: int,
    clock=time.monotonic,
    sleeper=time.sleep,
    validator=validate,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Return ready and pending rows after polling each node to CLI readiness."""
    pending = {row["name"]: row for row in rows}
    ready: dict[str, dict[str, str]] = {}
    deadline = clock() + timeout

    while pending:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(validator, row): name
                for name, row in pending.items()
            }
            for future in as_completed(futures):
                name = futures[future]
                result = future.result()
                if result["cli"] == "ok":
                    ready[name] = result
                    del pending[name]
                    print(f"READY {name} {result['kind']} {result['host']}", flush=True)

        print(
            f"READINESS ready={len(ready)}/{len(rows)} "
            f"pending={','.join(sorted(pending)) or 'none'}",
            flush=True,
        )
        now = clock()
        if not pending or now >= deadline:
            break
        sleeper(min(interval, max(0.0, deadline - now)))

    return (
        [ready[name] for name in sorted(ready)],
        [pending[name] for name in sorted(pending)],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--interval", type=float, default=10)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    with args.inventory.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    require_credentials(rows)

    started = time.monotonic()
    ready, pending = wait_for_nodes(
        rows,
        timeout=args.timeout,
        interval=args.interval,
        workers=args.workers,
    )
    elapsed = time.monotonic() - started
    print(
        f"SUMMARY total={len(rows)} ready={len(ready)} failed={len(pending)} "
        f"elapsed_seconds={elapsed:.1f}"
    )
    if pending:
        print("NOT_READY " + ",".join(row["name"] for row in pending))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
