#!/usr/bin/env python3
"""Run one read-only show command on selected inventory nodes."""

from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from netmiko import ConnectHandler

from credentials import connection_credentials


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "inventory" / "nodes.csv"


def run(row: dict[str, str], command: str) -> tuple[str, str, str]:
    if row["kind"] == "cisco_xrd":
        params = {
            "device_type": "cisco_xr",
            **connection_credentials(row["kind"]),
        }
    elif row["kind"] == "cisco_iol":
        params = {
            "device_type": "cisco_ios",
            **connection_credentials(row["kind"]),
        }
    else:
        return row["name"], "skipped", "Linux node is not a network device"

    session = None
    try:
        session = ConnectHandler(
            host=row["mgmt_ipv4"],
            conn_timeout=10,
            auth_timeout=15,
            banner_timeout=25,
            fast_cli=False,
            **params,
        )
        return row["name"], "ok", session.send_command(command, read_timeout=60)
    except Exception as exc:
        return (
            row["name"],
            "failed",
            f"{type(exc).__name__}: {exc}".replace("\n", " ")[:500],
        )
    finally:
        if session is not None:
            session.disconnect()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("--nodes", required=True, help="Comma-separated names")
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    selected = {item.strip() for item in args.nodes.split(",") if item.strip()}

    with INVENTORY.open(newline="", encoding="utf-8") as file:
        rows = [row for row in csv.DictReader(file) if row["name"] in selected]
    found = {row["name"] for row in rows}
    if found != selected:
        raise SystemExit(f"Unknown nodes: {', '.join(sorted(selected - found))}")

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(run, row, args.command): row["name"] for row in rows
        }
        for future in as_completed(futures):
            results.append(future.result())

    failed = 0
    for name, status, output in sorted(results):
        print(f"### {name}|{status}|{args.command}")
        print(output.rstrip())
        failed += status == "failed"
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
