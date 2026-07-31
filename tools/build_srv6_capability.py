#!/usr/bin/env python3
"""Generate the validated capability canary and the full SRv6 study profile."""

from __future__ import annotations

import csv
import ipaddress
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "srv6"
CONFIG = ROOT / "configs" / "srv6"
TOPOLOGY = ROOT / "topology" / "ccie-sp-srv6.clab.yml"
XR_IMAGE = "ios-xr/xrd-control-plane:24.2.11"
IOL_IMAGE = "vrnetlab/cisco_iol:17.12.01"
AUTO_IMAGE = "ccie-sp-automation:1.0"
MGMT_SUBNET = ipaddress.ip_network("10.203.255.0/24")


@dataclass(frozen=True)
class Node:
    name: str
    role: str
    kind: str
    node_id: int
    mgmt: str

    @property
    def is_xr(self) -> bool:
        return self.kind == "cisco_xrd"

    @property
    def loopback6(self) -> str:
        block = "500:abcd" if self.is_xr else "700:ce"
        return f"2001:db8:{block}::{self.node_id}"

    @property
    def locator(self) -> str:
        return f"2001:db8:600:{self.node_id}::/64" if self.is_xr else ""

    @property
    def net(self) -> str:
        return f"49.0001.0000.0000.{self.node_id:04d}.00"


@dataclass(frozen=True)
class Link:
    link_id: int
    a: str
    b: str
    purpose: str

    @property
    def network6(self) -> ipaddress.IPv6Network:
        block = "1000" if self.purpose == "underlay" else "2000"
        return ipaddress.ip_network(f"2001:db8:{block}:{self.link_id:x}::/127")


NODES = [
    *[Node(f"P{i}", "P", "cisco_xrd", i, f"10.203.255.{100+i}") for i in range(1, 7)],
    *[Node(f"PE{i}", "PE", "cisco_xrd", 10+i, f"10.203.255.{110+i}") for i in range(1, 7)],
    Node("RR1", "RR", "cisco_xrd", 21, "10.203.255.121"),
    Node("RR2", "RR", "cisco_xrd", 22, "10.203.255.122"),
    *[Node(f"CE{i}", "CE", "cisco_iol", i, f"10.203.255.{200+i}") for i in range(1, 7)],
    Node("AUTO1", "AUTOMATION", "linux", 0, "10.203.255.250"),
]

UNDERLAY = [
    ("P1", "P2"), ("P2", "P3"), ("P3", "P4"),
    ("P4", "P5"), ("P5", "P6"), ("P6", "P1"),
    ("P1", "P4"), ("P2", "P5"), ("P3", "P6"),
    ("PE1", "P1"), ("PE1", "P2"), ("PE2", "P1"), ("PE2", "P3"),
    ("PE3", "P2"), ("PE3", "P4"), ("PE4", "P3"), ("PE4", "P5"),
    ("PE5", "P4"), ("PE5", "P6"), ("PE6", "P5"), ("PE6", "P6"),
    ("RR1", "P2"), ("RR1", "P5"), ("RR2", "P3"), ("RR2", "P6"),
]
ACCESS = [
    ("PE1", "CE1"), ("PE2", "CE2"), ("PE3", "CE3"),
    ("PE4", "CE4"), ("PE5", "CE5"), ("PE6", "CE6"),
    ("PE3", "CE2"), ("PE6", "CE5"),
]
LINKS = [
    *[Link(i, a, b, "underlay") for i, (a, b) in enumerate(UNDERLAY, 1)],
    *[Link(100+i, a, b, "access") for i, (a, b) in enumerate(ACCESS, 1)],
]
NODE_MAP = {node.name: node for node in NODES}
IF_COUNTERS: dict[str, int] = defaultdict(int)
ENDPOINTS: dict[tuple[int, str], str] = {}


def allocate_interfaces() -> None:
    for link in LINKS:
        for name in (link.a, link.b):
            node = NODE_MAP[name]
            index = IF_COUNTERS[name]
            IF_COUNTERS[name] += 1
            if node.kind == "cisco_xrd":
                interface = f"Gi0-0-0-{index}"
            else:
                interface = f"Ethernet0/{index + 1}"
            ENDPOINTS[(link.link_id, name)] = interface


def xr_interface(name: str) -> str:
    return f"GigabitEthernet0/0/0/{name.rsplit('-', 1)[-1]}"


def records(name: str):
    for link in LINKS:
        if link.a == name:
            yield link, ENDPOINTS[(link.link_id, name)], link.network6[0], link.b
        elif link.b == name:
            yield link, ENDPOINTS[(link.link_id, name)], link.network6[1], link.a


def render_base(node: Node) -> str:
    if node.kind == "linux":
        return ""
    lines = [f"hostname {node.name}", "!", "interface Loopback0",
             f" description SRV6 {node.role} LOOPBACK",
             f" ipv6 address {node.loopback6}/128", " no shutdown", "!"]
    for link, interface, address, peer in records(node.name):
        interface = xr_interface(interface) if node.is_xr else interface
        lines += [f"interface {interface}",
                  f" description SRV6-{link.purpose.upper()} {node.name}--{peer}",
                  f" ipv6 address {address}/127", " no shutdown", "!"]
    return "\n".join(lines) + "\n"


def render_canary(node: Node) -> str:
    return "\n".join([f"hostname {node.name}", "!", "interface Loopback0",
        f" description SRV6 CANARY {node.role}", f" ipv6 address {node.loopback6}/128",
        " no shutdown", "!", ""])


def render_isis(node: Node) -> str:
    lines = ["router isis SRV6", " is-type level-2-only", f" net {node.net}",
        " address-family ipv6 unicast", "  metric-style wide", "  single-topology",
        " !", " interface Loopback0", "  passive", "  address-family ipv6 unicast",
        "  !", " !"]
    for link, interface, _address, _peer in records(node.name):
        if link.purpose != "underlay":
            continue
        lines += [f" interface {xr_interface(interface)}", "  circuit-type level-2-only",
            "  point-to-point", "  hello-padding disable", "  address-family ipv6 unicast",
            "   metric 10", "  !", " !"]
    return "\n".join(lines + ["!", ""])


def render_locator(node: Node) -> str:
    return "\n".join(["segment-routing", " srv6", "  locators", "   locator MAIN",
        f"    prefix {node.locator}", "   !", "  !", " !", "!", ""])


def render_srv6_isis(_node: Node) -> str:
    return "\n".join(["router isis SRV6", " address-family ipv6 unicast",
        "  segment-routing srv6", "   locator MAIN", "   !", "  !", " !", "!", ""])


def validate() -> None:
    if len(NODE_MAP) != 21 or len(LINKS) != 33:
        raise ValueError("full SRv6 profile must contain 21 nodes and 33 links")
    seen = set()
    for node in NODES:
        if ipaddress.ip_address(node.mgmt) not in MGMT_SUBNET or node.mgmt in seen:
            raise ValueError(f"invalid or duplicate management address: {node.name}")
        seen.add(node.mgmt)


def write_topology() -> None:
    lines = ["name: ccie-sp-srv6", "", "mgmt:", "  network: ccie-sp-srv6-mgmt",
        f"  ipv4-subnet: {MGMT_SUBNET}", "", "topology:", "  kinds:",
        "    cisco_xrd:", f"      image: {XR_IMAGE}", "    cisco_iol:",
        f"      image: {IOL_IMAGE}", "", "  nodes:"]
    for index, node in enumerate(NODES):
        lines += [f"    {node.name}:", f"      kind: {node.kind}"]
        if node.kind == "linux":
            lines += [f"      image: {AUTO_IMAGE}", "      env:",
                "        AUTO1_PASSWORD: ${CCIE_AUTO_PASSWORD}", "      binds:",
                "        - ../automation:/workspace"]
        delay = index * 30 if node.kind == "cisco_xrd" else 420 + (index - 14) * 10
        lines += [f"      mgmt-ipv4: {node.mgmt}", f"      startup-delay: {delay}"]
    lines += ["", "  links:"]
    for link in LINKS:
        lines.append(f'    - endpoints: ["{link.a}:{ENDPOINTS[(link.link_id, link.a)]}", "{link.b}:{ENDPOINTS[(link.link_id, link.b)]}"]')
    TOPOLOGY.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_inventory() -> None:
    PROFILE.mkdir(parents=True, exist_ok=True)
    with (PROFILE / "nodes.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["name", "role", "kind", "mgmt_ipv4", "loopback_ipv6", "locator"])
        for node in NODES:
            writer.writerow([node.name, node.role, node.kind, node.mgmt,
                f"{node.loopback6}/128" if node.kind != "linux" else "", node.locator])
    with (PROFILE / "links.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["id", "endpoint_a", "endpoint_a_ipv6", "endpoint_b", "endpoint_b_ipv6", "purpose"])
        for link in LINKS:
            writer.writerow([f"SRV6{link.link_id:03d}",
                f"{link.a}:{ENDPOINTS[(link.link_id, link.a)]}", f"{link.network6[0]}/127",
                f"{link.b}:{ENDPOINTS[(link.link_id, link.b)]}", f"{link.network6[1]}/127", link.purpose])


def write_configs() -> None:
    phases = {"00-base": render_base, "10-isis-ipv6": render_isis,
              "20-srv6-locator": render_locator, "21-srv6-isis": render_srv6_isis}
    canary = CONFIG / "00-canary"
    canary.mkdir(parents=True, exist_ok=True)
    (canary / "P1.cfg").write_text(render_canary(NODE_MAP["P1"]), encoding="utf-8", newline="\n")
    for phase, renderer in phases.items():
        directory = CONFIG / phase
        directory.mkdir(parents=True, exist_ok=True)
        for old in directory.glob("*.cfg"):
            old.unlink()
        for node in NODES:
            if phase != "00-base" and not node.is_xr:
                continue
            text = renderer(node)
            if text:
                (directory / f"{node.name}.cfg").write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    allocate_interfaces()
    validate()
    write_topology()
    write_inventory()
    write_configs()
    print(f"Generated full SRv6 profile: {len(NODES)} nodes, {len(LINKS)} links")


if __name__ == "__main__":
    main()
