#!/usr/bin/env python3
"""Generate the 30-node CCIE SP master Containerlab topology and baselines."""

from __future__ import annotations

import csv
import ipaddress
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY_DIR = ROOT / "topology"
INVENTORY_DIR = ROOT / "inventory"
CONFIG_DIR = ROOT / "configs"

XR_IMAGE = "ios-xr/xrd-control-plane:24.2.11"
IOL_IMAGE = "vrnetlab/cisco_iol:17.12.01"
AUTOMATION_IMAGE = "ccie-sp-automation:1.0"
MGMT_SUBNET = "10.201.255.0/24"
MGMT_NETWORK = "ccie-sp-master-mgmt"

PROVIDER_LINK_GROUPS = {
    "core-plane-a",
    "core-plane-b",
    "core-rung",
    "core-diagonal",
    "pe-core",
    "rr-core",
}

BANNER_LINES = [
    "************************************************************",
    "*                                                          *",
    "*              CCIE SERVICE PROVIDER LAB                  *",
    "*                                                          *",
    "*        AUTHORIZED TRAINING AND AUTOMATION ONLY           *",
    "*                                                          *",
    "************************************************************",
]


@dataclass(frozen=True)
class Node:
    name: str
    role: str
    kind: str
    mgmt: str
    node_id: int
    startup_delay: int

    @property
    def is_xrd(self) -> bool:
        return self.kind == "cisco_xrd"

    @property
    def is_iol(self) -> bool:
        return self.kind == "cisco_iol"

    @property
    def is_linux(self) -> bool:
        return self.kind == "linux"

    @property
    def image(self) -> str:
        if self.is_xrd:
            return XR_IMAGE
        if self.is_iol:
            return IOL_IMAGE
        return AUTOMATION_IMAGE

    @property
    def loopback4(self) -> str:
        if self.is_xrd:
            return f"10.0.0.{self.node_id}"
        if self.is_iol:
            return f"10.100.0.{self.node_id}"
        return ""

    @property
    def loopback6(self) -> str:
        if self.is_xrd:
            return f"2001:db8:500:abcd::{self.node_id}"
        if self.is_iol:
            return f"2001:db8:100::{self.node_id}"
        return ""

    @property
    def legacy_loopback6(self) -> str:
        if self.is_xrd:
            return f"2001:db8:ffff::{self.node_id}"
        return self.loopback6

    @property
    def isis_net(self) -> str:
        return f"49.0001.0000.0000.{self.node_id:04d}.00"

    @property
    def prefix_sid_index(self) -> int:
        return self.node_id

    @property
    def ipv6_prefix_sid_index(self) -> int:
        return 600 + self.node_id


@dataclass(frozen=True)
class Link:
    link_id: int
    a: str
    a_if: str
    b: str
    b_if: str
    group: str
    metric: int
    srlg: int

    @property
    def ipv4_network(self) -> ipaddress.IPv4Network:
        base = int(ipaddress.IPv4Address("10.255.0.0"))
        return ipaddress.IPv4Network((base + ((self.link_id - 1) * 2), 31))

    @property
    def ipv6_network(self) -> ipaddress.IPv6Network:
        if self.group in PROVIDER_LINK_GROUPS:
            subnet_id = 100 + self.link_id
            return ipaddress.IPv6Network(
                f"2001:db8:1000:{subnet_id}::/127"
            )
        return ipaddress.IPv6Network(f"2001:db8:0:{self.link_id:x}::/127")

    @property
    def legacy_ipv6_network(self) -> ipaddress.IPv6Network:
        return ipaddress.IPv6Network(f"2001:db8:0:{self.link_id:x}::/127")

    @property
    def a_ipv4(self) -> str:
        return str(self.ipv4_network[0])

    @property
    def b_ipv4(self) -> str:
        return str(self.ipv4_network[1])

    @property
    def a_ipv6(self) -> str:
        return str(self.ipv6_network[0])

    @property
    def b_ipv6(self) -> str:
        return str(self.ipv6_network[1])

    @property
    def a_legacy_ipv6(self) -> str:
        return str(self.legacy_ipv6_network[0])

    @property
    def b_legacy_ipv6(self) -> str:
        return str(self.legacy_ipv6_network[1])


NODES = [
    Node("P1", "P", "cisco_xrd", "10.201.255.101", 1, 0),
    Node("P2", "P", "cisco_xrd", "10.201.255.102", 2, 0),
    Node("P3", "P", "cisco_xrd", "10.201.255.103", 3, 15),
    Node("P4", "P", "cisco_xrd", "10.201.255.104", 4, 15),
    Node("P5", "P", "cisco_xrd", "10.201.255.105", 5, 30),
    Node("P6", "P", "cisco_xrd", "10.201.255.106", 6, 30),
    Node("P7", "P", "cisco_xrd", "10.201.255.107", 15, 45),
    Node("P8", "P", "cisco_xrd", "10.201.255.108", 16, 45),
    Node("PE1", "PE", "cisco_xrd", "10.201.255.111", 7, 45),
    Node("PE2", "PE", "cisco_xrd", "10.201.255.112", 8, 45),
    Node("PE3", "PE", "cisco_xrd", "10.201.255.113", 9, 60),
    Node("PE4", "PE", "cisco_xrd", "10.201.255.114", 10, 60),
    Node("PE5", "PE", "cisco_xrd", "10.201.255.115", 11, 75),
    Node("PE6", "PE", "cisco_xrd", "10.201.255.116", 12, 75),
    Node("PE7", "PE", "cisco_xrd", "10.201.255.117", 17, 90),
    Node("PE8", "PE", "cisco_xrd", "10.201.255.118", 18, 90),
    Node("RR1", "RR-PCE", "cisco_xrd", "10.201.255.121", 13, 90),
    Node("RR2", "RR-PCE", "cisco_xrd", "10.201.255.122", 14, 90),
    Node("CE1", "CE", "cisco_iol", "10.201.255.131", 1, 105),
    Node("CE2", "CE-DUAL", "cisco_iol", "10.201.255.132", 2, 105),
    Node("CE3", "CE", "cisco_iol", "10.201.255.133", 3, 105),
    Node("CE4", "CE", "cisco_iol", "10.201.255.134", 4, 105),
    Node("CE5", "CE-DUAL", "cisco_iol", "10.201.255.135", 5, 105),
    Node("CE6", "CE", "cisco_iol", "10.201.255.136", 6, 105),
    Node("CE7", "CE", "cisco_iol", "10.201.255.137", 7, 105),
    Node("CE8", "CE-DUAL", "cisco_iol", "10.201.255.138", 8, 105),
    Node("CE9", "CE", "cisco_iol", "10.201.255.139", 9, 105),
    Node("C1", "CLIENT", "cisco_iol", "10.201.255.141", 10, 105),
    Node("C2", "CLIENT", "cisco_iol", "10.201.255.142", 11, 105),
    Node("AUTO1", "AUTOMATION", "linux", "10.201.255.150", 0, 0),
]

NODE_MAP = {node.name: node for node in NODES}


def build_links() -> list[Link]:
    raw_links = [
        # Dual-plane P backbone.
        ("P1", "Gi0-0-0-0", "P3", "Gi0-0-0-0", "core-plane-a", 10, 101),
        ("P3", "Gi0-0-0-1", "P5", "Gi0-0-0-0", "core-plane-a", 10, 101),
        ("P2", "Gi0-0-0-0", "P4", "Gi0-0-0-0", "core-plane-b", 10, 102),
        ("P4", "Gi0-0-0-1", "P6", "Gi0-0-0-0", "core-plane-b", 10, 102),
        ("P1", "Gi0-0-0-1", "P2", "Gi0-0-0-1", "core-rung", 20, 110),
        ("P3", "Gi0-0-0-2", "P4", "Gi0-0-0-2", "core-rung", 20, 120),
        ("P5", "Gi0-0-0-1", "P6", "Gi0-0-0-1", "core-rung", 20, 130),
        ("P1", "Gi0-0-0-2", "P4", "Gi0-0-0-3", "core-diagonal", 30, 140),
        ("P2", "Gi0-0-0-2", "P3", "Gi0-0-0-3", "core-diagonal", 30, 150),
        # Dual-homed PEs.
        ("PE1", "Gi0-0-0-0", "P1", "Gi0-0-0-3", "pe-core", 10, 201),
        ("PE1", "Gi0-0-0-1", "P2", "Gi0-0-0-3", "pe-core", 10, 202),
        ("PE2", "Gi0-0-0-0", "P1", "Gi0-0-0-4", "pe-core", 10, 203),
        ("PE2", "Gi0-0-0-1", "P2", "Gi0-0-0-4", "pe-core", 10, 204),
        ("PE3", "Gi0-0-0-0", "P3", "Gi0-0-0-4", "pe-core", 10, 205),
        ("PE3", "Gi0-0-0-1", "P4", "Gi0-0-0-4", "pe-core", 10, 206),
        ("PE4", "Gi0-0-0-0", "P3", "Gi0-0-0-5", "pe-core", 10, 207),
        ("PE4", "Gi0-0-0-1", "P4", "Gi0-0-0-5", "pe-core", 10, 208),
        ("PE5", "Gi0-0-0-0", "P5", "Gi0-0-0-2", "pe-core", 10, 209),
        ("PE5", "Gi0-0-0-1", "P6", "Gi0-0-0-2", "pe-core", 10, 210),
        ("PE6", "Gi0-0-0-0", "P5", "Gi0-0-0-3", "pe-core", 10, 211),
        ("PE6", "Gi0-0-0-1", "P6", "Gi0-0-0-3", "pe-core", 10, 212),
        # Route reflector and PCE redundancy.
        ("RR1", "Gi0-0-0-0", "P3", "Gi0-0-0-6", "rr-core", 10, 301),
        ("RR1", "Gi0-0-0-1", "P5", "Gi0-0-0-4", "rr-core", 10, 302),
        ("RR2", "Gi0-0-0-0", "P4", "Gi0-0-0-6", "rr-core", 10, 303),
        ("RR2", "Gi0-0-0-1", "P6", "Gi0-0-0-4", "rr-core", 10, 304),
        # Customer access and three dual-homed customer sites.
        ("PE1", "Gi0-0-0-2", "CE1", "Ethernet0/1", "customer", 10, 401),
        ("PE1", "Gi0-0-0-3", "CE2", "Ethernet0/1", "customer-dual", 10, 402),
        ("PE2", "Gi0-0-0-2", "CE2", "Ethernet0/2", "customer-dual", 10, 403),
        ("PE2", "Gi0-0-0-3", "CE3", "Ethernet0/1", "customer", 10, 404),
        ("PE3", "Gi0-0-0-2", "CE4", "Ethernet0/1", "customer", 10, 405),
        ("PE3", "Gi0-0-0-3", "CE5", "Ethernet0/1", "customer-dual", 10, 406),
        ("PE4", "Gi0-0-0-2", "CE5", "Ethernet0/2", "customer-dual", 10, 407),
        ("PE4", "Gi0-0-0-3", "CE6", "Ethernet0/1", "customer", 10, 408),
        ("PE5", "Gi0-0-0-2", "CE7", "Ethernet0/1", "customer", 10, 409),
        ("PE5", "Gi0-0-0-3", "CE8", "Ethernet0/1", "customer-dual", 10, 410),
        ("PE6", "Gi0-0-0-2", "CE8", "Ethernet0/2", "customer-dual", 10, 411),
        ("PE6", "Gi0-0-0-3", "CE9", "Ethernet0/1", "customer", 10, 412),
        # Multicast and service test endpoints.
        ("CE1", "Ethernet0/2", "C1", "Ethernet0/1", "client", 10, 501),
        ("CE9", "Ethernet0/2", "C2", "Ethernet0/1", "client", 10, 502),
        # Expansion links are appended to preserve all original link IDs/IPs.
        ("P5", "Gi0-0-0-5", "P7", "Gi0-0-0-0", "core-plane-a", 10, 103),
        ("P6", "Gi0-0-0-5", "P8", "Gi0-0-0-0", "core-plane-b", 10, 104),
        ("P7", "Gi0-0-0-1", "P8", "Gi0-0-0-1", "core-rung", 20, 160),
        ("P6", "Gi0-0-0-6", "P7", "Gi0-0-0-2", "core-diagonal", 30, 170),
        ("PE7", "Gi0-0-0-0", "P5", "Gi0-0-0-6", "pe-core", 10, 213),
        ("PE7", "Gi0-0-0-1", "P7", "Gi0-0-0-3", "pe-core", 10, 214),
        ("PE8", "Gi0-0-0-0", "P6", "Gi0-0-0-7", "pe-core", 10, 215),
        ("PE8", "Gi0-0-0-1", "P8", "Gi0-0-0-3", "pe-core", 10, 216),
    ]
    return [
        Link(index, *link)
        for index, link in enumerate(raw_links, start=1)
    ]


LINKS = build_links()


def validate_model() -> None:
    node_names = [node.name for node in NODES]
    mgmt_addresses = [node.mgmt for node in NODES]
    if len(node_names) != len(set(node_names)):
        raise ValueError("Duplicate node name")
    if len(mgmt_addresses) != len(set(mgmt_addresses)):
        raise ValueError("Duplicate management address")

    endpoints: set[tuple[str, str]] = set()
    ipv4_networks: set[ipaddress.IPv4Network] = set()
    ipv6_networks: set[ipaddress.IPv6Network] = set()
    for link in LINKS:
        if link.a not in NODE_MAP or link.b not in NODE_MAP:
            raise ValueError(f"L{link.link_id:03d} references an unknown node")
        for endpoint in ((link.a, link.a_if), (link.b, link.b_if)):
            if endpoint in endpoints:
                raise ValueError(f"Duplicate interface assignment: {endpoint}")
            endpoints.add(endpoint)
        if link.ipv4_network in ipv4_networks:
            raise ValueError(f"Duplicate IPv4 network: {link.ipv4_network}")
        if link.ipv6_network in ipv6_networks:
            raise ValueError(f"Duplicate IPv6 network: {link.ipv6_network}")
        ipv4_networks.add(link.ipv4_network)
        ipv6_networks.add(link.ipv6_network)


def config_interface_name(node: Node, topology_name: str) -> str:
    if node.is_xrd:
        port = topology_name.rsplit("-", 1)[-1]
        return f"GigabitEthernet0/0/0/{port}"
    return topology_name


def interface_records(node_name: str) -> list[tuple[str, str, str, Link, str]]:
    records: list[tuple[str, str, str, Link, str]] = []
    for link in LINKS:
        if link.a == node_name:
            records.append((link.a_if, link.a_ipv4, link.a_ipv6, link, link.b))
        elif link.b == node_name:
            records.append((link.b_if, link.b_ipv4, link.b_ipv6, link, link.a))
    return records


def provider_interface_records(
    node_name: str,
) -> list[tuple[str, str, str, Link, str]]:
    return [
        record
        for record in interface_records(node_name)
        if record[3].group in PROVIDER_LINK_GROUPS
    ]


def render_topology() -> str:
    lines = [
        "name: ccie-sp-master",
        "",
        "mgmt:",
        f"  network: {MGMT_NETWORK}",
        f"  ipv4-subnet: {MGMT_SUBNET}",
        "",
        "topology:",
        "  kinds:",
        "    cisco_xrd:",
        f"      image: {XR_IMAGE}",
        "    cisco_iol:",
        f"      image: {IOL_IMAGE}",
        "",
        "  nodes:",
    ]
    for node in NODES:
        lines.extend([f"    {node.name}:", f"      kind: {node.kind}"])
        if node.is_linux:
            lines.extend(
                [
                    f"      image: {node.image}",
                    f"      mgmt-ipv4: {node.mgmt}",
                    "      env:",
                    "        AUTO1_PASSWORD: ${CCIE_AUTO_PASSWORD}",
                    "        CCIE_XRD_USERNAME: ${CCIE_XRD_USERNAME}",
                    "        CCIE_XRD_PASSWORD: ${CCIE_XRD_PASSWORD}",
                    "        CCIE_IOL_USERNAME: ${CCIE_IOL_USERNAME}",
                    "        CCIE_IOL_PASSWORD: ${CCIE_IOL_PASSWORD}",
                    "      binds:",
                    "        - ../automation:/workspace",
                ]
            )
        else:
            lines.extend(
                [
                    f"      mgmt-ipv4: {node.mgmt}",
                    f"      startup-delay: {node.startup_delay}",
                ]
            )
    lines.extend(["", "  links:"])
    for link in LINKS:
        lines.append(
            f'    - endpoints: ["{link.a}:{link.a_if}", "{link.b}:{link.b_if}"]'
        )
    return "\n".join(lines) + "\n"


def render_xrd_base(node: Node) -> str:
    lines = [
        f"hostname {node.name}",
        "!",
        "banner login @",
        *BANNER_LINES,
        "@",
        "!",
        "interface Loopback0",
        f" description MgM-{node.node_id:06d} | CCIE-SP {node.role}",
        f" ipv4 address {node.loopback4} 255.255.255.255",
        f" ipv6 address {node.loopback6}/128",
        " no shutdown",
        "!",
    ]
    for topo_if, ipv4, ipv6, link, peer in interface_records(node.name):
        cli_if = config_interface_name(node, topo_if)
        lines.extend(
            [
                f"interface {cli_if}",
                f" description {node.name}--{peer} {link.group} L{link.link_id:03d}",
                f" ipv4 address {ipv4} 255.255.255.254",
                f" ipv6 address {ipv6}/127",
                " no shutdown",
                "!",
            ]
        )
    return "\n".join(lines) + "\n"


def render_iol_base(node: Node) -> str:
    lines = [
        f"hostname {node.name}",
        "no ip domain lookup",
        "ipv6 unicast-routing",
        "!",
        "interface Loopback0",
        f" description CCIE-SP NODE-ID {node.node_id}",
        f" ip address {node.loopback4} 255.255.255.255",
        f" ipv6 address {node.loopback6}/128",
        " no shutdown",
        "!",
    ]
    for topo_if, ipv4, ipv6, link, peer in interface_records(node.name):
        lines.extend(
            [
                f"interface {topo_if}",
                f" description {node.name}--{peer} {link.group} L{link.link_id:03d}",
                f" ip address {ipv4} 255.255.255.254",
                f" ipv6 address {ipv6}/127",
                " no shutdown",
                "!",
            ]
        )
    lines.append("end")
    return "\n".join(lines) + "\n"


def render_isis(node: Node) -> str:
    lines = [
        "router isis CORE",
        f" net {node.isis_net}",
        " is-type level-2-only",
        " distribute link-state",
        " log adjacency changes",
        " lsp-gen-interval maximum-wait 5000 initial-wait 50 secondary-wait 200",
        " address-family ipv4 unicast",
        "  metric-style wide",
        "  advertise passive-only",
        "  mpls traffic-eng level-2-only",
        "  mpls traffic-eng router-id Loopback0",
        " !",
        " address-family ipv6 unicast",
        "  metric-style wide",
        "  advertise passive-only",
        "  single-topology",
        " !",
        " interface Loopback0",
        "  passive",
        "  address-family ipv4 unicast",
        "  !",
        "  address-family ipv6 unicast",
        "  !",
        " !",
    ]
    for topo_if, _ipv4, _ipv6, link, _peer in interface_records(node.name):
        if link.group not in PROVIDER_LINK_GROUPS:
            continue
        cli_if = config_interface_name(node, topo_if)
        lines.extend(
            [
                f" interface {cli_if}",
                "  circuit-type level-2-only",
                "  point-to-point",
                "  hello-padding disable",
                "  address-family ipv4 unicast",
                "   fast-reroute per-prefix",
                f"   metric {link.metric}",
                "  !",
                "  address-family ipv6 unicast",
                "   fast-reroute per-prefix",
                f"   metric {link.metric}",
                "  !",
                " !",
            ]
        )
    return "\n".join(lines) + "\n"


def render_sr_mpls(node: Node) -> str:
    return "\n".join(
        [
            "segment-routing",
            " global-block 16000 23999",
            " traffic-eng",
            " !",
            "!",
            "router isis CORE",
            " address-family ipv4 unicast",
            "  segment-routing mpls sr-prefer",
            " !",
            " address-family ipv6 unicast",
            "  segment-routing mpls",
            " !",
            " interface Loopback0",
            "  address-family ipv4 unicast",
            f"   prefix-sid index {node.prefix_sid_index}",
            "  !",
            "  address-family ipv6 unicast",
            f"   prefix-sid index {node.ipv6_prefix_sid_index}",
            "  !",
            " !",
            "!",
            "",
        ]
    )


def render_provider_standard(node: Node) -> str:
    """Render the in-place migration from the deployed baseline.

    The commands deliberately never remove or replace an IPv4 address.
    """
    lines = [
        "banner login @",
        *BANNER_LINES,
        "@",
        "!",
        "interface Loopback0",
        f" description MgM-{node.node_id:06d} | CCIE-SP {node.role}",
        f" no ipv6 address {node.legacy_loopback6}/128",
        f" ipv6 address {node.loopback6}/128",
        "!",
    ]
    for topo_if, _ipv4, ipv6, link, _peer in provider_interface_records(node.name):
        cli_if = config_interface_name(node, topo_if)
        legacy_ipv6 = (
            link.a_legacy_ipv6 if link.a == node.name else link.b_legacy_ipv6
        )
        lines.extend(
            [
                f"interface {cli_if}",
                f" no ipv6 address {legacy_ipv6}/127",
                f" ipv6 address {ipv6}/127",
                "!",
            ]
        )

    lines.extend(
        [
            "router isis CORE",
            " is-type level-2-only",
            " distribute link-state",
            " address-family ipv4 unicast",
            "  metric-style wide",
            "  advertise passive-only",
            "  mpls traffic-eng level-2-only",
            "  mpls traffic-eng router-id Loopback0",
            "  segment-routing mpls sr-prefer",
            " !",
            " address-family ipv6 unicast",
            "  metric-style wide",
            "  advertise passive-only",
            "  single-topology",
            "  segment-routing mpls",
            " !",
            " interface Loopback0",
            "  passive",
            "  address-family ipv4 unicast",
            f"   prefix-sid index {node.prefix_sid_index}",
            "  !",
            "  address-family ipv6 unicast",
            f"   prefix-sid index {node.ipv6_prefix_sid_index}",
            "  !",
            " !",
        ]
    )
    for topo_if, _ipv4, _ipv6, link, _peer in provider_interface_records(
        node.name
    ):
        cli_if = config_interface_name(node, topo_if)
        lines.extend(
            [
                f" interface {cli_if}",
                "  circuit-type level-2-only",
                "  no bfd fast-detect ipv4",
                "  no bfd fast-detect ipv6",
                "  point-to-point",
                "  hello-padding disable",
                "  address-family ipv4 unicast",
                "   fast-reroute per-prefix",
                f"   metric {link.metric}",
                "  !",
                "  address-family ipv6 unicast",
                "   fast-reroute per-prefix",
                f"   metric {link.metric}",
                "  !",
                " !",
            ]
        )
    lines.extend(
        [
            "!",
            "segment-routing",
            " global-block 16000 23999",
            " traffic-eng",
            " !",
            "!",
        ]
    )
    return "\n".join(lines) + "\n"


def write_inventory() -> None:
    INVENTORY_DIR.mkdir(parents=True, exist_ok=True)
    with (INVENTORY_DIR / "nodes.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "name",
                "role",
                "kind",
                "image",
                "mgmt_ipv4",
                "loopback_ipv4",
                "loopback_ipv6",
                "isis_net",
                "prefix_sid_index",
                "ipv6_prefix_sid_index",
            ]
        )
        for node in NODES:
            writer.writerow(
                [
                    node.name,
                    node.role,
                    node.kind,
                    node.image,
                    node.mgmt,
                    f"{node.loopback4}/32" if node.loopback4 else "",
                    f"{node.loopback6}/128" if node.loopback6 else "",
                    node.isis_net if node.is_xrd else "",
                    node.prefix_sid_index if node.is_xrd else "",
                    node.ipv6_prefix_sid_index if node.is_xrd else "",
                ]
            )

    with (INVENTORY_DIR / "links.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "id",
                "endpoint_a",
                "endpoint_a_ipv4",
                "endpoint_a_ipv6",
                "endpoint_b",
                "endpoint_b_ipv4",
                "endpoint_b_ipv6",
                "group",
                "igp_metric",
                "srlg",
            ]
        )
        for link in LINKS:
            writer.writerow(
                [
                    f"L{link.link_id:03d}",
                    f"{link.a}:{link.a_if}",
                    f"{link.a_ipv4}/31",
                    f"{link.a_ipv6}/127",
                    f"{link.b}:{link.b_if}",
                    f"{link.b_ipv4}/31",
                    f"{link.b_ipv6}/127",
                    link.group,
                    link.metric,
                    link.srlg,
                ]
            )


def write_configs() -> None:
    for phase in ("00-base", "10-isis", "15-provider-standard", "20-sr-mpls"):
        (CONFIG_DIR / phase).mkdir(parents=True, exist_ok=True)

    for node in NODES:
        if node.is_xrd:
            base = render_xrd_base(node)
        elif node.is_iol:
            base = render_iol_base(node)
        else:
            continue
        (CONFIG_DIR / "00-base" / f"{node.name}.cfg").write_text(
            base, encoding="utf-8", newline="\n"
        )
        if node.is_xrd:
            (CONFIG_DIR / "10-isis" / f"{node.name}.cfg").write_text(
                render_isis(node), encoding="utf-8", newline="\n"
            )
            (CONFIG_DIR / "15-provider-standard" / f"{node.name}.cfg").write_text(
                render_provider_standard(node), encoding="utf-8", newline="\n"
            )
            (CONFIG_DIR / "20-sr-mpls" / f"{node.name}.cfg").write_text(
                render_sr_mpls(node), encoding="utf-8", newline="\n"
            )


def main() -> None:
    validate_model()
    TOPOLOGY_DIR.mkdir(parents=True, exist_ok=True)
    (TOPOLOGY_DIR / "ccie-sp-master.clab.yml").write_text(
        render_topology(), encoding="utf-8", newline="\n"
    )
    write_inventory()
    write_configs()
    print(
        f"Generated {len(NODES)} nodes, {len(LINKS)} links, "
        f"{sum(node.is_xrd for node in NODES)} XRd nodes, "
        f"{sum(node.is_iol for node in NODES)} IOL nodes, "
        f"{sum(node.is_linux for node in NODES)} automation node."
    )


if __name__ == "__main__":
    main()
