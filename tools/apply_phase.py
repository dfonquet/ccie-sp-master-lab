#!/usr/bin/env python3
"""Apply a generated configuration phase to selected lab-profile nodes."""

from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from netmiko import ConnectHandler


ROOT = Path(__file__).resolve().parents[1]
def compile_interactive_commands(text: str, *, is_xrd: bool) -> list[str]:
    """Convert indented IOS-style config into safe interactive CLI commands."""
    parsed: list[tuple[int, str]] = []
    raw_lines = text.splitlines()
    index = 0
    while index < len(raw_lines):
        raw_line = raw_lines[index]
        stripped = raw_line.strip()
        if stripped.lower().startswith("banner login ") and len(stripped) > 13:
            delimiter = stripped[-1]
            banner_lines = [stripped]
            index += 1
            while index < len(raw_lines):
                banner_line = raw_lines[index].rstrip()
                banner_lines.append(banner_line)
                if banner_line.strip() == delimiter:
                    break
                index += 1
            else:
                raise ValueError("Unterminated banner login block")
            parsed.append((0, "\n".join(banner_lines)))
            index += 1
            continue
        if (
            raw_line == raw_line.lstrip(" ")
            and stripped.lower().startswith("route-policy ")
        ):
            policy_lines = [stripped]
            index += 1
            while index < len(raw_lines):
                policy_line = raw_lines[index].rstrip()
                policy_lines.append(policy_line)
                if policy_line.strip().lower() == "end-policy":
                    break
                index += 1
            else:
                raise ValueError("Unterminated route-policy block")
            parsed.append((0, "\n".join(policy_lines)))
            index += 1
            continue
        if not stripped or stripped == "!" or stripped.lower() == "end":
            index += 1
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        parsed.append((indent, stripped))
        index += 1

    if is_xrd:
        # IOS XR's interactive ``exit`` returns to global configuration mode
        # for several nested router submodes. Re-enter the complete parent
        # path for every command so rendered hierarchy is applied exactly.
        commands: list[str] = []
        parents: dict[int, str] = {}
        for index, (indent, command) in enumerate(parsed):
            for level in [level for level in parents if level >= indent]:
                del parents[level]
            if commands:
                commands.append("root")
            commands.extend(parents[level] for level in sorted(parents))
            commands.append(command)
            next_indent = parsed[index + 1][0] if index + 1 < len(parsed) else -1
            if next_indent > indent:
                parents[indent] = command
        if commands:
            commands.append("root")
        return commands

    commands = []
    current_mode_indent = -1
    for index, (indent, command) in enumerate(parsed):
        desired_parent = indent - 1
        while current_mode_indent > desired_parent:
            commands.append("exit")
            current_mode_indent -= 1

        next_indent = parsed[index + 1][0] if index + 1 < len(parsed) else -1
        commands.append(command)
        if next_indent > indent:
            current_mode_indent = indent

    return commands


def connect_params(row: dict[str, str]) -> dict[str, object]:
    if row["kind"] == "cisco_xrd":
        return {
            "device_type": "cisco_xr",
            "username": "clab",
            "password": "clab@123",
        }
    return {
        "device_type": "cisco_ios",
        "username": "admin",
        "password": "admin",
    }


def apply_one(
    row: dict[str, str],
    phase_dir: Path,
    profile: str,
) -> dict[str, str]:
    name = row["name"]
    config_path = phase_dir / f"{name}.cfg"
    result = {"name": name, "status": "skipped", "details": ""}
    if not config_path.exists():
        return result

    is_xrd = row["kind"] == "cisco_xrd"
    commands = compile_interactive_commands(
        config_path.read_text(encoding="utf-8"),
        is_xrd=is_xrd,
    )
    session = None
    try:
        session = ConnectHandler(
            host=row["mgmt_ipv4"],
            conn_timeout=10,
            auth_timeout=15,
            banner_timeout=25,
            fast_cli=False,
            **connect_params(row),
        )
        output = session.send_config_set(
            commands,
            exit_config_mode=False,
            read_timeout=120,
            cmd_verify=False,
        )
        if is_xrd:
            output += session.commit(
                comment=f"CCIE-SP {profile} {phase_dir.name}",
                read_timeout=120,
            )
            session.exit_config_mode()
            verify = session.send_command(
                "show ipv4 interface brief",
                read_timeout=30,
            )
        else:
            session.exit_config_mode()
            session.save_config()
            verify = session.send_command(
                "show ip interface brief",
                read_timeout=30,
            )
        result["status"] = "ok"
        result["details"] = (
            f"commands={len(commands)} interfaces="
            f"{sum('up' in line.lower() for line in verify.splitlines())}"
        )
        cli_errors = (
            "% Invalid",
            "% Incomplete",
            "Invalid input detected",
            "Failed to commit",
        )
        if any(error in output for error in cli_errors):
            result["status"] = "failed"
            result["details"] = "CLI reported invalid or incomplete command"
    except Exception as exc:
        result["status"] = "failed"
        details = f"{type(exc).__name__}: {exc}"
        if session is not None and is_xrd:
            try:
                failed_config = session.send_command_timing(
                    "show configuration failed",
                    read_timeout=30,
                    strip_prompt=False,
                    strip_command=False,
                )
                if failed_config.strip():
                    details += f" | SHOW-FAILED: {failed_config}"
            except Exception as show_exc:
                details += f" | SHOW-FAILED-ERROR: {show_exc}"
        result["details"] = details.replace("\n", " ")[:4000]
    finally:
        if session is not None:
            session.disconnect()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", help="Configuration phase directory, e.g. 00-base")
    parser.add_argument(
        "--profile",
        choices=("master", "inter-as"),
        default="master",
        help="Inventory/configuration profile. Default: master.",
    )
    parser.add_argument(
        "--nodes",
        help="Comma-separated node names. Default: all nodes with phase configs.",
    )
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()

    config_root = ROOT / "configs"
    inventory = ROOT / "inventory" / "nodes.csv"
    if args.profile != "master":
        config_root = config_root / args.profile
        inventory = ROOT / "profiles" / args.profile / "nodes.csv"
    phase_dir = config_root / args.phase
    if not phase_dir.is_dir():
        raise SystemExit(f"Phase directory not found: {phase_dir}")

    with inventory.open(newline="", encoding="utf-8") as file:
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
        futures = {
            executor.submit(apply_one, row, phase_dir, args.profile): row["name"]
            for row in rows
        }
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda item: item["name"])
    for result in results:
        print(f"{result['name']}|{result['status']}|{result['details']}")

    failed = [result for result in results if result["status"] == "failed"]
    applied = [result for result in results if result["status"] == "ok"]
    print(
        f"SUMMARY phase={args.phase} selected={len(rows)} "
        f"applied={len(applied)} failed={len(failed)}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
