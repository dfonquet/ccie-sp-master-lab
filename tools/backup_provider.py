#!/usr/bin/env python3
"""Back up XR provider configuration and key operational state."""

from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from netmiko import ConnectHandler

from credentials import connection_credentials


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "inventory" / "nodes.csv"
COMMANDS = (
    "show running-config",
    "show ipv4 interface brief",
    "show ipv6 interface brief",
    "show isis neighbors",
    "show isis database summary",
    "show isis segment-routing label table",
    "show bfd session",
)


def back_up(row: dict[str, str], output_dir: Path) -> tuple[str, str]:
    session = None
    try:
        session = ConnectHandler(
            host=row["mgmt_ipv4"],
            device_type="cisco_xr",
            **connection_credentials(row["kind"]),
            conn_timeout=10,
            auth_timeout=15,
            banner_timeout=25,
            fast_cli=False,
        )
        sections = []
        for command in COMMANDS:
            output = session.send_command(command, read_timeout=60)
            sections.append(f"### {command}\n{output.rstrip()}\n")
        (output_dir / f"{row['name']}.txt").write_text(
            "\n".join(sections),
            encoding="utf-8",
            newline="\n",
        )
        return row["name"], "ok"
    except Exception as exc:
        return row["name"], f"failed:{type(exc).__name__}:{exc}".replace(
            "\n", " "
        )[:300]
    finally:
        if session is not None:
            session.disconnect()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inventory",
        type=Path,
        default=INVENTORY,
        help="Node inventory CSV. Default: master inventory.",
    )
    parser.add_argument("--nodes", help="Comma-separated XR node names")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument(
        "--label",
        default="manual",
        help="Short label included in the backup directory name",
    )
    args = parser.parse_args()

    with args.inventory.open(newline="", encoding="utf-8") as file:
        rows = [
            row for row in csv.DictReader(file) if row["kind"] == "cisco_xrd"
        ]
    if args.nodes:
        selected = {item.strip() for item in args.nodes.split(",") if item.strip()}
        rows = [row for row in rows if row["name"] in selected]

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = ROOT / "artifacts" / "backups" / f"{timestamp}-{args.label}"
    output_dir.mkdir(parents=True, exist_ok=False)

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(back_up, row, output_dir): row["name"] for row in rows
        }
        for future in as_completed(futures):
            results.append(future.result())

    for name, status in sorted(results):
        print(f"{name}|{status}")
    failed = [item for item in results if item[1] != "ok"]
    print(
        f"SUMMARY nodes={len(rows)} backed_up={len(rows) - len(failed)} "
        f"failed={len(failed)} directory={output_dir}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
