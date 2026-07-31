#!/usr/bin/env python3
"""Validate generated SRv6 capability artifacts without deploying a lab."""

from __future__ import annotations

import csv
import ipaddress
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "srv6"
CONFIG = ROOT / "configs" / "srv6"
TOPOLOGY = ROOT / "topology" / "ccie-sp-srv6.clab.yml"


def read_csv(name: str) -> list[dict[str, str]]:
    with (PROFILE / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> int:
    nodes = read_csv("nodes.csv")
    links = read_csv("links.csv")
    expected = ({f"P{i}" for i in range(1, 7)} |
                {f"PE{i}" for i in range(1, 7)} |
                {"RR1", "RR2"} |
                {f"CE{i}" for i in range(1, 7)} |
                {"AUTO1"})
    if len(nodes) != 21 or {row["name"] for row in nodes} != expected:
        raise SystemExit("full SRv6 inventory must contain 21 expected nodes")
    if len(links) != 33:
        raise SystemExit("full SRv6 inventory must contain exactly 33 links")

    management = [ipaddress.ip_address(row["mgmt_ipv4"]) for row in nodes]
    routed = [row for row in nodes if row["loopback_ipv6"]]
    xr_nodes = [row for row in nodes if row["kind"] == "cisco_xrd"]
    loopbacks = [ipaddress.ip_interface(row["loopback_ipv6"]) for row in routed]
    locators = [ipaddress.ip_network(row["locator"]) for row in xr_nodes]
    if len(management) != len(set(management)):
        raise SystemExit("duplicate management address")
    if any(address not in ipaddress.ip_network("10.203.255.0/24") for address in management):
        raise SystemExit("management address outside SRv6 profile subnet")
    if len(loopbacks) != len(set(loopbacks)) or len(locators) != len(set(locators)):
        raise SystemExit("duplicate loopback or locator")
    if any(locator.prefixlen != 64 for locator in locators):
        raise SystemExit("every SRv6 locator must be /64")

    topology = TOPOLOGY.read_text(encoding="utf-8")
    required_topology = (
        "name: ccie-sp-srv6",
        "network: ccie-sp-srv6-mgmt",
        "ipv4-subnet: 10.203.255.0/24",
        "ios-xr/xrd-control-plane:24.2.11",
    )
    if any(item not in topology for item in required_topology):
        raise SystemExit("topology identity or management gate is missing")

    canary_config = (CONFIG / "00-canary" / "P1.cfg").read_text(encoding="utf-8")
    if "GigabitEthernet" in canary_config:
        raise SystemExit("P1 canary config must not reference data interfaces")

    for node in xr_nodes:
        name = node["name"]
        locator_config = (CONFIG / "20-srv6-locator" / f"{name}.cfg").read_text(
            encoding="utf-8"
        )
        isis_config = (CONFIG / "21-srv6-isis" / f"{name}.cfg").read_text(
            encoding="utf-8"
        )
        for command in (
            "segment-routing",
            " srv6",
            "   locator MAIN",
            f"    prefix {node['locator']}",
        ):
            if command not in locator_config:
                raise SystemExit(f"{name} missing generated command: {command.strip()}")
        if "router isis" in locator_config:
            raise SystemExit(f"{name} locator phase must not create an IS-IS process")
        for command in ("router isis SRV6", "segment-routing srv6", "locator MAIN"):
            if command not in isis_config:
                raise SystemExit(f"{name} missing IS-IS SRv6 command: {command}")

    print("SRv6 artifact validation passed: 21 nodes, 33 links, 14 unique /64 locators")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
