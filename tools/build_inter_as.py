#!/usr/bin/env python3
"""Generate the isolated, dual-stack CCIE SP Inter-AS profile."""

from __future__ import annotations

import csv
import ipaddress
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "inter-as"
CONFIG = ROOT / "configs" / "inter-as"
TOPOLOGY = ROOT / "topology" / "ccie-sp-inter-as.clab.yml"
XR_IMAGE = "ios-xr/xrd-control-plane:24.2.11"
IOL_IMAGE = "vrnetlab/cisco_iol:17.12.01"
AUTO_IMAGE = "ccie-sp-automation:1.0"


@dataclass(frozen=True)
class Node:
    name: str
    role: str
    asn: int | None
    igp: str
    node_id: int
    mgmt: str
    kind: str = "cisco_xrd"

    @property
    def loopback4(self) -> str:
        if self.asn == 500:
            return f"10.50.0.{self.node_id}"
        if self.asn == 65100:
            return f"10.65.100.{self.node_id}"
        if self.asn == 65200:
            return f"10.65.200.{self.node_id}"
        return f"10.200.0.{self.node_id}"

    @property
    def loopback6(self) -> str:
        if self.asn == 500:
            return f"2001:db8:500::{self.node_id}"
        if self.asn == 65100:
            return f"2001:db8:6510::{self.node_id}"
        if self.asn == 65200:
            return f"2001:db8:6520::{self.node_id}"
        return f"2001:db8:ce::{self.node_id}"


@dataclass
class Link:
    link_id: int
    a: str
    b: str
    link_type: str
    a_if: str = ""
    b_if: str = ""

    @property
    def network4(self) -> ipaddress.IPv4Network:
        base = int(ipaddress.IPv4Address("10.240.0.0"))
        return ipaddress.IPv4Network((base + (self.link_id - 1) * 2, 31))

    @property
    def network6(self) -> ipaddress.IPv6Network:
        return ipaddress.IPv6Network(f"2001:db8:2400:{self.link_id:x}::/127")


NODES = [
    Node("P1", "P", 500, "isis", 1, "10.202.255.101"),
    Node("P2", "P", 500, "isis", 2, "10.202.255.102"),
    Node("P3", "ASBR", 500, "isis", 3, "10.202.255.103"),
    Node("P4", "ASBR", 500, "isis", 4, "10.202.255.104"),
    Node("PE1", "PE", 500, "isis", 11, "10.202.255.111"),
    Node("PE2", "PE", 500, "isis", 12, "10.202.255.112"),
    Node("PE3", "PE", 500, "isis", 13, "10.202.255.113"),
    Node("PE4", "PE", 500, "isis", 14, "10.202.255.114"),
    Node("RR500", "RR", 500, "isis", 50, "10.202.255.150"),
    Node("P5", "ASBR", 65100, "ospf", 5, "10.202.255.105"),
    Node("P7", "ASBR", 65100, "ospf", 7, "10.202.255.107"),
    Node("PE5", "PE", 65100, "ospf", 15, "10.202.255.115"),
    Node("PE7", "PE", 65100, "ospf", 17, "10.202.255.117"),
    Node("RR65100", "RR", 65100, "ospf", 51, "10.202.255.151"),
    Node("P6", "ASBR", 65200, "ospf", 6, "10.202.255.106"),
    Node("P8", "ASBR", 65200, "ospf", 8, "10.202.255.108"),
    Node("PE6", "PE", 65200, "ospf", 16, "10.202.255.116"),
    Node("PE8", "PE", 65200, "ospf", 18, "10.202.255.118"),
    Node("RR65200", "RR", 65200, "ospf", 52, "10.202.255.152"),
    Node("CE-A", "CE", None, "none", 1, "10.202.255.201", "cisco_iol"),
    Node("CE-B", "CE", None, "none", 2, "10.202.255.202", "cisco_iol"),
    Node("CE-C", "CE", None, "none", 3, "10.202.255.203", "cisco_iol"),
]
NODE_MAP = {node.name: node for node in NODES}


def make_links() -> list[Link]:
    raw = [
        # AS500: redundant IS-IS core.
        ("P1", "P3", "internal"), ("P2", "P4", "internal"),
        ("P1", "P2", "internal"), ("P3", "P4", "internal"),
        ("PE1", "P1", "internal"), ("PE2", "P2", "internal"),
        ("PE3", "P3", "internal"), ("PE4", "P4", "internal"),
        ("RR500", "P3", "internal"), ("RR500", "P4", "internal"),
        # AS65100: OSPFv2 IPv4 plus OSPFv3 IPv6 domain.
        ("P5", "P7", "internal"), ("PE5", "P5", "internal"),
        ("PE5", "P7", "internal"), ("PE7", "P5", "internal"),
        ("PE7", "P7", "internal"), ("RR65100", "P5", "internal"),
        ("RR65100", "P7", "internal"),
        # AS65200: OSPFv2 IPv4 plus OSPFv3 IPv6 domain.
        ("P6", "P8", "internal"), ("PE6", "P6", "internal"),
        ("PE6", "P8", "internal"), ("PE8", "P6", "internal"),
        ("PE8", "P8", "internal"), ("RR65200", "P6", "internal"),
        ("RR65200", "P8", "internal"),
        # Diverse inter-provider links and private peering.
        ("P3", "P5", "external"), ("P4", "P7", "external"),
        ("P3", "P6", "external"), ("P4", "P8", "external"),
        ("P7", "P8", "external"),
        # Multihomed customer sites for Options A/B/C service tests.
        ("PE1", "CE-A", "customer"), ("PE5", "CE-A", "customer"),
        ("PE2", "CE-B", "customer"), ("PE6", "CE-B", "customer"),
        ("PE7", "CE-C", "customer"), ("PE8", "CE-C", "customer"),
    ]
    counters: dict[str, int] = defaultdict(int)
    links = []
    for number, (a, b, link_type) in enumerate(raw, 1):
        a_if = (
            f"Gi0-0-0-{counters[a]}"
            if NODE_MAP[a].kind == "cisco_xrd"
            else f"Ethernet0/{counters[a] + 1}"
        )
        counters[a] += 1
        b_if = (
            f"Gi0-0-0-{counters[b]}"
            if NODE_MAP[b].kind == "cisco_xrd"
            else f"Ethernet0/{counters[b] + 1}"
        )
        counters[b] += 1
        links.append(Link(number, a, b, link_type, a_if, b_if))
    return links


LINKS = make_links()


def records(name: str):
    for link in LINKS:
        if link.a == name:
            yield link, link.a_if, link.network4[0], link.network6[0], link.b
        elif link.b == name:
            yield link, link.b_if, link.network4[1], link.network6[1], link.a


def xrd_if(name: str) -> str:
    return f"GigabitEthernet0/0/0/{name.rsplit('-', 1)[-1]}"


def render_base(node: Node) -> str:
    if node.kind == "cisco_iol":
        lines = [
            f"hostname {node.name}", "no ip domain lookup", "ipv6 unicast-routing",
            "interface Loopback0", f" ip address {node.loopback4} 255.255.255.255",
            f" ipv6 address {node.loopback6}/128", " no shutdown", "!",
        ]
        for link, interface, address4, address6, peer in records(node.name):
            lines += [
                f"interface {interface}", f" description {node.name}--{peer} IAS{link.link_id:03d}",
                f" ip address {address4} 255.255.255.254",
                f" ipv6 address {address6}/127", " no shutdown", "!",
            ]
        return "\n".join(lines + ["end", ""])

    lines = [
        f"hostname {node.name}", "!", "interface Loopback0",
        f" description INTER-AS ASN {node.asn} {node.role}",
        f" ipv4 address {node.loopback4} 255.255.255.255",
        f" ipv6 address {node.loopback6}/128", " no shutdown", "!",
    ]
    for link, interface, address4, address6, peer in records(node.name):
        lines += [
            f"interface {xrd_if(interface)}",
            f" description {node.name}--{peer} {link.link_type} IAS{link.link_id:03d}",
            f" ipv4 address {address4} 255.255.255.254",
            f" ipv6 address {address6}/127", " no shutdown", "!",
        ]
    return "\n".join(lines) + "\n"


def internal_records(node: Node):
    for record in records(node.name):
        link, _interface, _address4, _address6, peer = record
        if link.link_type == "internal" and NODE_MAP[peer].asn == node.asn:
            yield record


def render_igp(node: Node) -> str:
    if node.kind != "cisco_xrd":
        return ""
    if node.igp == "isis":
        lines = [
            "router isis AS500", " is-type level-2-only",
            f" net 49.0500.0000.0000.{node.node_id:04d}.00",
            " address-family ipv4 unicast", "  metric-style wide", " !",
            " address-family ipv6 unicast", "  metric-style wide",
            "  single-topology", " !", " interface Loopback0", "  passive",
            "  address-family ipv4 unicast", "  !",
            "  address-family ipv6 unicast", "  !", " !",
        ]
        for _link, interface, *_ in internal_records(node):
            lines += [
                f" interface {xrd_if(interface)}", "  point-to-point",
                "  address-family ipv4 unicast", "   metric 10", "  !",
                "  address-family ipv6 unicast", "   metric 10", "  !", " !",
            ]
        return "\n".join(lines + ["!", ""])

    process = str(node.asn)
    lines = [
        f"router ospf {process}", f" router-id {node.loopback4}",
        " area 0", "  interface Loopback0", "   passive enable", "  !",
    ]
    for _link, interface, *_ in internal_records(node):
        lines += [f"  interface {xrd_if(interface)}", "   network point-to-point", "  !"]
    lines += [" !", "!", f"router ospfv3 {process}", f" router-id {node.loopback4}",
              " address-family ipv6 unicast", " !", " area 0",
              "  interface Loopback0", "   passive", "  !"]
    for _link, interface, *_ in internal_records(node):
        lines += [f"  interface {xrd_if(interface)}", "   network point-to-point", "  !"]
    return "\n".join(lines + [" !", "!", ""])


def bgp_clients(asn: int) -> list[Node]:
    return [n for n in NODES if n.asn == asn and n.role in {"PE", "ASBR"}]


def rr_for(asn: int) -> Node:
    return next(n for n in NODES if n.asn == asn and n.role == "RR")


def render_bgp(node: Node) -> str:
    if node.kind != "cisco_xrd" or node.role == "P":
        return ""
    lines = ["route-policy PASS", " pass", "end-policy", "!", f"router bgp {node.asn}",
             f" bgp router-id {node.loopback4}"]
    if node.role == "RR":
        lines += [" address-family vpnv4 unicast", " !", " address-family vpnv6 unicast", " !"]
        for client in bgp_clients(node.asn or 0):
            lines += [
                f" neighbor {client.loopback4}", f"  remote-as {node.asn}",
                "  update-source Loopback0", "  address-family vpnv4 unicast",
                "   route-reflector-client", "  !",
                "  address-family vpnv6 unicast", "   route-reflector-client", "  !", " !",
            ]
    else:
        rr = rr_for(node.asn or 0)
        lines += [
            " address-family ipv4 unicast", " !", " address-family ipv6 unicast", " !",
            " address-family vpnv4 unicast", " !", " address-family vpnv6 unicast", " !",
            f" neighbor {rr.loopback4}", f"  remote-as {node.asn}",
            "  update-source Loopback0", "  address-family vpnv4 unicast", "  !",
            "  address-family vpnv6 unicast", "  !", " !",
        ]
        for link, _interface, address4, address6, peer_name in records(node.name):
            peer = NODE_MAP[peer_name]
            if link.link_type != "external" or peer.asn == node.asn:
                continue
            peer4 = link.network4[1] if link.a == node.name else link.network4[0]
            peer6 = link.network6[1] if link.a == node.name else link.network6[0]
            lines += [
                f" neighbor {peer4}", f"  remote-as {peer.asn}",
                "  address-family ipv4 unicast",
                "   route-policy PASS in", "   route-policy PASS out", "  !", " !",
                f" neighbor {peer6}", f"  remote-as {peer.asn}",
                "  address-family ipv6 unicast",
                "   route-policy PASS in", "   route-policy PASS out", "  !", " !",
            ]
    return "\n".join(lines + ["!", ""])


def validate() -> None:
    names = [n.name for n in NODES]
    if len(names) != len(set(names)):
        raise ValueError("duplicate node")
    endpoints = set()
    for link in LINKS:
        for endpoint in ((link.a, link.a_if), (link.b, link.b_if)):
            if endpoint in endpoints:
                raise ValueError(f"duplicate interface {endpoint}")
            endpoints.add(endpoint)
    if len([n for n in NODES if n.kind == "cisco_xrd"]) != 19:
        raise ValueError("Inter-AS profile must contain exactly 19 XRd nodes")
    if {n.asn for n in NODES if n.role == "RR"} != {500, 65100, 65200}:
        raise ValueError("one RR per provider AS is required")


def write_topology() -> None:
    lines = [
        "name: ccie-sp-inter-as", "", "mgmt:",
        "  network: ccie-sp-inter-as-mgmt", "  ipv4-subnet: 10.202.255.0/24",
        "", "topology:", "  kinds:", "    cisco_xrd:", f"      image: {XR_IMAGE}",
        "    cisco_iol:", f"      image: {IOL_IMAGE}", "", "  nodes:",
    ]
    for index, node in enumerate(NODES):
        lines += [f"    {node.name}:", f"      kind: {node.kind}",
                  f"      mgmt-ipv4: {node.mgmt}", f"      startup-delay: {(index // 2) * 15}"]
    lines += [
        "    AUTO1:", "      kind: linux", f"      image: {AUTO_IMAGE}",
        "      mgmt-ipv4: 10.202.255.250", "      env:",
        "        AUTO1_PASSWORD: ${CCIE_AUTO_PASSWORD}", "      binds:",
        "        - ..:/workspace", "", "  links:",
    ]
    for link in LINKS:
        lines.append(f'    - endpoints: ["{link.a}:{link.a_if}", "{link.b}:{link.b_if}"]')
    TOPOLOGY.parent.mkdir(parents=True, exist_ok=True)
    TOPOLOGY.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_inventory() -> None:
    PROFILE.mkdir(parents=True, exist_ok=True)
    with (PROFILE / "nodes.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["name", "role", "asn", "igp", "kind", "mgmt_ipv4", "loopback_ipv4", "loopback_ipv6"])
        for node in NODES:
            writer.writerow([node.name, node.role, node.asn or "", node.igp, node.kind,
                             node.mgmt, f"{node.loopback4}/32", f"{node.loopback6}/128"])
        writer.writerow(["AUTO1", "AUTOMATION", "", "none", "linux", "10.202.255.250", "", ""])
    with (PROFILE / "links.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["id", "endpoint_a", "endpoint_a_ipv4", "endpoint_a_ipv6",
                         "endpoint_b", "endpoint_b_ipv4", "endpoint_b_ipv6", "type"])
        for link in LINKS:
            writer.writerow([f"IAS{link.link_id:03d}", f"{link.a}:{link.a_if}",
                             f"{link.network4[0]}/31", f"{link.network6[0]}/127",
                             f"{link.b}:{link.b_if}", f"{link.network4[1]}/31",
                             f"{link.network6[1]}/127", link.link_type])


def write_configs() -> None:
    for phase in ("00-base", "10-igp", "20-bgp"):
        (CONFIG / phase).mkdir(parents=True, exist_ok=True)
    for node in NODES:
        (CONFIG / "00-base" / f"{node.name}.cfg").write_text(
            render_base(node), encoding="utf-8", newline="\n"
        )
        if node.kind == "cisco_xrd":
            (CONFIG / "10-igp" / f"{node.name}.cfg").write_text(
                render_igp(node), encoding="utf-8", newline="\n"
            )
            if node.role != "P":
                (CONFIG / "20-bgp" / f"{node.name}.cfg").write_text(
                    render_bgp(node), encoding="utf-8", newline="\n"
                )


def main() -> None:
    validate()
    write_topology()
    write_inventory()
    write_configs()
    print(f"Generated Inter-AS: {len(NODES) + 1} nodes, {len(LINKS)} links, 3 AS domains")


if __name__ == "__main__":
    main()
