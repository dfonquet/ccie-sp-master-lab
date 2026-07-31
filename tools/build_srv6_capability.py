#!/usr/bin/env python3
"""Generate the capability-first IOS XRd SRv6 mini-lab."""

from __future__ import annotations

import csv
import ipaddress
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "srv6"
CONFIG = ROOT / "configs" / "srv6"
TOPOLOGY = ROOT / "topology" / "ccie-sp-srv6.clab.yml"
XR_IMAGE = "ios-xr/xrd-control-plane:24.2.11"
MGMT_SUBNET = ipaddress.ip_network("10.203.255.0/24")
ISIS_INSTANCE = "SRV6"


@dataclass(frozen=True)
class Node:
    name: str
    role: str
    node_id: int
    mgmt: str

    @property
    def loopback6(self) -> str:
        return f"2001:db8:500:abcd::{self.node_id}"

    @property
    def locator(self) -> str:
        return f"2001:db8:600:{self.node_id}::/64"

    @property
    def net(self) -> str:
        return f"49.0001.0000.0000.{self.node_id:04d}.00"


@dataclass(frozen=True)
class Link:
    link_id: int
    a: str
    a_if: str
    b: str
    b_if: str

    @property
    def network6(self) -> ipaddress.IPv6Network:
        return ipaddress.ip_network(f"2001:db8:1000:{self.link_id:x}::/127")


NODES = [
    Node("P1", "P", 1, "10.203.255.101"),
    Node("P2", "P", 2, "10.203.255.102"),
    Node("PE1", "PE", 11, "10.203.255.111"),
]
LINKS = [
    Link(1, "PE1", "Gi0-0-0-0", "P1", "Gi0-0-0-0"),
    Link(2, "P1", "Gi0-0-0-1", "P2", "Gi0-0-0-0"),
]
NODE_MAP = {node.name: node for node in NODES}


def xr_interface(short_name: str) -> str:
    return f"GigabitEthernet0/0/0/{short_name.rsplit('-', 1)[-1]}"


def records(name: str):
    for link in LINKS:
        if link.a == name:
            yield link, link.a_if, link.network6[0], link.b
        elif link.b == name:
            yield link, link.b_if, link.network6[1], link.a


def render_base(node: Node) -> str:
    lines = [
        f"hostname {node.name}",
        "!",
        "interface Loopback0",
        f" description SRV6 NODE {node.role}",
        f" ipv6 address {node.loopback6}/128",
        " no shutdown",
        "!",
    ]
    for link, interface, address6, peer in records(node.name):
        lines += [
            f"interface {xr_interface(interface)}",
            f" description SRV6{link.link_id:03d} {node.name}--{peer}",
            f" ipv6 address {address6}/127",
            " no shutdown",
            "!",
        ]
    return "\n".join(lines) + "\n"


def render_canary(node: Node) -> str:
    """Render only configuration that is valid without data-plane links."""
    return "\n".join(
        [
            f"hostname {node.name}",
            "!",
            "interface Loopback0",
            f" description SRV6 CANARY {node.role}",
            f" ipv6 address {node.loopback6}/128",
            " no shutdown",
            "!",
            "",
        ]
    )


def render_isis(node: Node) -> str:
    lines = [
        f"router isis {ISIS_INSTANCE}",
        " is-type level-2-only",
        f" net {node.net}",
        " address-family ipv6 unicast",
        "  metric-style wide",
        "  single-topology",
        " !",
        " interface Loopback0",
        "  passive",
        "  address-family ipv6 unicast",
        "  !",
        " !",
    ]
    for _link, interface, _address6, _peer in records(node.name):
        lines += [
            f" interface {xr_interface(interface)}",
            "  circuit-type level-2-only",
            "  point-to-point",
            "  hello-padding disable",
            "  address-family ipv6 unicast",
            "   metric 10",
            "  !",
            " !",
        ]
    return "\n".join(lines + ["!", ""])


def render_srv6(node: Node) -> str:
    return "\n".join(
        [
            "segment-routing",
            " srv6",
            "  locators",
            "   locator MAIN",
            f"    prefix {node.locator}",
            "   !",
            "  !",
            " !",
            "!",
            f"router isis {ISIS_INSTANCE}",
            " address-family ipv6 unicast",
            "  segment-routing srv6",
            "   locator MAIN",
            "   !",
            "  !",
            " !",
            "!",
            "",
        ]
    )


def validate() -> None:
    if len(NODE_MAP) != len(NODES):
        raise ValueError("duplicate SRv6 node name")
    endpoints: set[tuple[str, str]] = set()
    for node in NODES:
        if ipaddress.ip_address(node.mgmt) not in MGMT_SUBNET:
            raise ValueError(f"management address outside {MGMT_SUBNET}: {node.name}")
        if ipaddress.ip_network(node.locator).prefixlen != 64:
            raise ValueError(f"locator must be /64: {node.name}")
    for link in LINKS:
        for endpoint in ((link.a, link.a_if), (link.b, link.b_if)):
            if endpoint in endpoints:
                raise ValueError(f"duplicate endpoint: {endpoint}")
            if endpoint[0] not in NODE_MAP:
                raise ValueError(f"unknown endpoint node: {endpoint[0]}")
            endpoints.add(endpoint)


def write_topology() -> None:
    lines = [
        "name: ccie-sp-srv6",
        "",
        "mgmt:",
        "  network: ccie-sp-srv6-mgmt",
        f"  ipv4-subnet: {MGMT_SUBNET}",
        "",
        "topology:",
        "  kinds:",
        "    cisco_xrd:",
        f"      image: {XR_IMAGE}",
        "",
        "  nodes:",
    ]
    for index, node in enumerate(NODES):
        lines += [
            f"    {node.name}:",
            "      kind: cisco_xrd",
            f"      mgmt-ipv4: {node.mgmt}",
            f"      startup-delay: {index * 15}",
        ]
    lines += ["", "  links:"]
    for link in LINKS:
        lines.append(
            f'    - endpoints: ["{link.a}:{link.a_if}", "{link.b}:{link.b_if}"]'
        )
    TOPOLOGY.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_inventory() -> None:
    PROFILE.mkdir(parents=True, exist_ok=True)
    with (PROFILE / "nodes.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            ["name", "role", "kind", "mgmt_ipv4", "loopback_ipv6", "locator"]
        )
        for node in NODES:
            writer.writerow(
                [node.name, node.role, "cisco_xrd", node.mgmt,
                 f"{node.loopback6}/128", node.locator]
            )
    with (PROFILE / "links.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            ["id", "endpoint_a", "endpoint_a_ipv6", "endpoint_b",
             "endpoint_b_ipv6", "purpose"]
        )
        for link in LINKS:
            writer.writerow(
                [f"SRV6{link.link_id:03d}", f"{link.a}:{link.a_if}",
                 f"{link.network6[0]}/127", f"{link.b}:{link.b_if}",
                 f"{link.network6[1]}/127", "underlay"]
            )


def write_configs() -> None:
    phases = {
        "00-canary": render_canary,
        "00-base": render_base,
        "10-isis-ipv6": render_isis,
        "20-srv6-locator": render_srv6,
    }
    for phase, renderer in phases.items():
        directory = CONFIG / phase
        directory.mkdir(parents=True, exist_ok=True)
        for node in NODES:
            (directory / f"{node.name}.cfg").write_text(
                renderer(node), encoding="utf-8", newline="\n"
            )


def main() -> None:
    validate()
    write_topology()
    write_inventory()
    write_configs()
    print(f"Generated SRv6 capability profile: {len(NODES)} XRd nodes, {len(LINKS)} links")


if __name__ == "__main__":
    main()
