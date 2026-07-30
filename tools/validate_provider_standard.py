#!/usr/bin/env python3
"""Validate the dual-stack provider standard on every XRd P/PE/RR node."""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from netmiko import ConnectHandler


ROOT = Path(__file__).resolve().parents[1]
PROVIDER_GROUPS = {
    "core-plane-a",
    "core-plane-b",
    "core-rung",
    "core-diagonal",
    "pe-core",
    "rr-core",
}
ISIS_TOKENS = (
    "distribute link-state",
    "advertise passive-only",
    "single-topology",
    "segment-routing mpls sr-prefer",
    "segment-routing mpls",
    "fast-reroute per-prefix",
    "hello-padding disable",
)


def xrd_interface_name(name: str) -> str:
    port = name.rsplit("-", 1)[-1]
    return f"GigabitEthernet0/0/0/{port}"


def load_expected() -> tuple[
    list[dict[str, str]],
    dict[str, list[tuple[str, str]]],
    dict[str, int],
]:
    with (ROOT / "inventory" / "nodes.csv").open(
        newline="", encoding="utf-8"
    ) as file:
        nodes = [
            row for row in csv.DictReader(file) if row["kind"] == "cisco_xrd"
        ]

    interfaces: dict[str, list[tuple[str, str]]] = defaultdict(list)
    neighbors: dict[str, int] = defaultdict(int)
    with (ROOT / "inventory" / "links.csv").open(
        newline="", encoding="utf-8"
    ) as file:
        for link in csv.DictReader(file):
            if link["group"] not in PROVIDER_GROUPS:
                continue
            for side in ("a", "b"):
                endpoint = link[f"endpoint_{side}"]
                node, interface = endpoint.split(":", 1)
                address = link[f"endpoint_{side}_ipv6"]
                interfaces[node].append((xrd_interface_name(interface), address))
                neighbors[node] += 1
    return nodes, interfaces, neighbors


def validate_node(
    row: dict[str, str],
    expected_interfaces: list[tuple[str, str]],
    expected_neighbors: int,
) -> dict[str, object]:
    result: dict[str, object] = {
        "name": row["name"],
        "status": "failed",
        "addresses": "0/0",
        "neighbors": f"0/{expected_neighbors}",
        "bfd_up": 0,
        "missing": [],
        "error": "",
    }
    session = None
    try:
        session = ConnectHandler(
            host=row["mgmt_ipv4"],
            device_type="cisco_xr",
            username="clab",
            password="clab@123",
            conn_timeout=10,
            auth_timeout=15,
            banner_timeout=25,
            fast_cli=False,
        )
        loopback_config = session.send_command(
            "show running-config interface Loopback0", read_timeout=30
        )
        loopback6 = row["loopback_ipv6"]
        missing = []
        if f"ipv6 address {loopback6}" not in loopback_config:
            missing.append(f"loopback:{loopback6}")

        address_matches = 0
        for interface, address in expected_interfaces:
            output = session.send_command(
                f"show running-config interface {interface}", read_timeout=30
            )
            if f"ipv6 address {address}" in output:
                address_matches += 1
            else:
                missing.append(f"{interface}:{address}")

        isis_config = session.send_command(
            "show running-config router isis CORE", read_timeout=60
        )
        for token in ISIS_TOKENS:
            if token not in isis_config:
                missing.append(f"isis:{token}")

        neighbors_output = session.send_command(
            "show isis neighbors", read_timeout=30
        )
        neighbor_up = sum(
            bool(re.search(r"\bUp\b", line))
            for line in neighbors_output.splitlines()
        )
        bfd_output = session.send_command("show bfd session", read_timeout=30)
        bfd_up = sum(
            bool(re.search(r"\bUP\b", line.upper()))
            for line in bfd_output.splitlines()
        )

        result["addresses"] = (
            f"{address_matches + (not any(item.startswith('loopback:') for item in missing))}"
            f"/{len(expected_interfaces) + 1}"
        )
        result["neighbors"] = f"{neighbor_up}/{expected_neighbors}"
        result["bfd_up"] = bfd_up
        result["missing"] = missing
        result["status"] = (
            "ok"
            if not missing and neighbor_up >= expected_neighbors
            else "failed"
        )
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}".replace("\n", " ")[:300]
    finally:
        if session is not None:
            session.disconnect()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    nodes, interfaces, neighbors = load_expected()

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                validate_node,
                row,
                interfaces[row["name"]],
                neighbors[row["name"]],
            ): row["name"]
            for row in nodes
        }
        for future in as_completed(futures):
            results.append(future.result())

    for result in sorted(results, key=lambda item: str(item["name"])):
        missing = ",".join(result["missing"]) if result["missing"] else "-"
        print(
            f"{result['name']}|{result['status']}|"
            f"ipv6={result['addresses']}|isis={result['neighbors']}|"
            f"bfd_up={result['bfd_up']}|missing={missing}|error={result['error']}"
        )
    passed = sum(result["status"] == "ok" for result in results)
    print(
        f"SUMMARY nodes={len(results)} passed={passed} "
        f"failed={len(results) - passed}"
    )
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
