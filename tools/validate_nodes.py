#!/usr/bin/env python3
"""Validate management TCP and CLI access for every master-lab node."""

from __future__ import annotations

import argparse
import csv
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from netmiko import ConnectHandler

from credentials import connection_credentials


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = ROOT / "inventory" / "nodes.csv"


def validate(row: dict[str, str]) -> dict[str, str]:
    name = row["name"]
    host = row["mgmt_ipv4"]
    kind = row["kind"]
    result = {
        "name": name,
        "kind": kind,
        "host": host,
        "tcp22": "closed",
        "cli": "failed",
        "prompt": "",
        "version": "",
        "error": "",
    }
    if kind == "cisco_xrd":
        params = {
            "device_type": "cisco_xr",
            **connection_credentials(kind),
            "command": "show version | include Version",
        }
    elif kind == "cisco_iol":
        params = {
            "device_type": "cisco_ios",
            **connection_credentials(kind),
            "command": "show version | include Cisco IOS Software|Version",
        }
    else:
        params = {
            "device_type": "linux",
            **connection_credentials(kind),
            "command": "python3 --version && ansible --version | head -1",
        }

    command = params.pop("command")
    session = None
    try:
        session = ConnectHandler(
            host=host,
            conn_timeout=8,
            auth_timeout=12,
            banner_timeout=20,
            fast_cli=False,
            **params,
        )
        result["prompt"] = session.find_prompt().strip()
        output = session.send_command(command, read_timeout=15)
        result["version"] = " ".join(output.split())
        result["tcp22"] = "open"
        result["cli"] = "ok"
    except Exception as exc:  # Netmiko raises several transport-specific types.
        result["error"] = f"{type(exc).__name__}: {exc}".replace("\n", " ")[:240]
        try:
            with socket.create_connection((host, 22), timeout=3):
                result["tcp22"] = "open"
        except OSError:
            pass
    finally:
        if session is not None:
            session.disconnect()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--nodes", help="Comma-separated node names. Default: all.")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    with args.inventory.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    if args.nodes:
        selected = {name.strip() for name in args.nodes.split(",") if name.strip()}
        known = {row["name"] for row in rows}
        unknown = selected - known
        if unknown:
            raise SystemExit(f"Unknown nodes: {', '.join(sorted(unknown))}")
        rows = [row for row in rows if row["name"] in selected]

    results: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(validate, row): row["name"] for row in rows}
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda item: (item["kind"], item["name"]))
    for result in results:
        print(
            "|".join(
                [
                    result["name"],
                    result["kind"],
                    result["host"],
                    f"tcp22={result['tcp22']}",
                    f"cli={result['cli']}",
                    f"prompt={result['prompt']}",
                    f"version={result['version']}",
                    f"error={result['error']}",
                ]
            )
        )

    tcp_ok = sum(result["tcp22"] == "open" for result in results)
    cli_ok = sum(result["cli"] == "ok" for result in results)
    print(f"SUMMARY total={len(results)} tcp22_open={tcp_ok} cli_ok={cli_ok}")
    return 0 if cli_ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
