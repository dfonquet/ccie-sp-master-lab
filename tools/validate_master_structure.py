#!/usr/bin/env python3
"""Validate the offline 38-node Master/ISP-2 structural definition."""

from __future__ import annotations

import csv
import ipaddress
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODES_PATH = ROOT / "inventory" / "nodes.csv"
LINKS_PATH = ROOT / "inventory" / "links.csv"
TOPOLOGY_PATH = ROOT / "topology" / "ccie-sp-master.clab.yml"

EXPECTED_ISP2_NODES = {
    "ASBR-ISP2": ("ASBR-ISP2", "cisco_xrd", "10.201.255.151", "10.65.2.1/32", "2001:db8:6502::1/128"),
    "RR-ISP2": ("RR-ISP2", "cisco_xrd", "10.201.255.152", "10.65.2.7/32", "2001:db8:6502::7/128"),
    "ISP2-P1": ("P-ISP2", "cisco_iol", "10.201.255.153", "10.65.2.2/32", "2001:db8:6502::2/128"),
    "ISP2-P2": ("P-ISP2", "cisco_iol", "10.201.255.154", "10.65.2.3/32", "2001:db8:6502::3/128"),
    "ISP2-P3": ("TRANSIT-ISP2", "cisco_iol", "10.201.255.155", "10.65.2.4/32", "2001:db8:6502::4/128"),
    "ISP2-P4": ("TRANSIT-ISP2", "cisco_iol", "10.201.255.156", "10.65.2.5/32", "2001:db8:6502::5/128"),
    "ISP2-P5": ("PE-SERVICE-EDGE", "cisco_iol", "10.201.255.157", "10.65.2.6/32", "2001:db8:6502::6/128"),
    "SOURCE1": ("TRAFFIC-SOURCE", "linux", "10.201.255.158", "", ""),
}

EXPECTED_LINK_ENDPOINTS = {
    "L048": ("P1:Gi0-0-0-5", "ASBR-ISP2:Gi0-0-0-0"),
    "L049": ("ASBR-ISP2:Gi0-0-0-1", "ISP2-P1:Ethernet0/1"),
    "L050": ("ASBR-ISP2:Gi0-0-0-2", "ISP2-P2:Ethernet0/1"),
    "L051": ("ISP2-P1:Ethernet0/2", "ISP2-P3:Ethernet0/1"),
    "L052": ("ISP2-P2:Ethernet0/2", "ISP2-P5:Ethernet0/1"),
    "L053": ("ISP2-P3:Ethernet0/2", "ISP2-P4:Ethernet0/1"),
    "L054": ("ISP2-P4:Ethernet0/2", "ISP2-P5:Ethernet0/2"),
    "L055": ("ISP2-P3:Ethernet0/3", "RR-ISP2:Gi0-0-0-0"),
    "L056": ("ISP2-P4:Ethernet0/3", "RR-ISP2:Gi0-0-0-1"),
    "L057": ("ISP2-P5:Ethernet0/3", "SOURCE1:eth1"),
}

FORBIDDEN_BOOTSTRAP = (
    "router ospf", "router ospfv3", "router bgp", "router isis",
    "segment-routing", "mpls", "evpn", "pim", "multicast-routing", "vrf ",
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    nodes = rows(NODES_PATH)
    links = rows(LINKS_PATH)
    node_map = {row["name"]: row for row in nodes}
    link_map = {row["id"]: row for row in links}

    if len(nodes) != 38 or len(node_map) != 38:
        fail(f"expected 38 unique nodes, got rows={len(nodes)} unique={len(node_map)}")
    if len(links) != 57 or len(link_map) != 57:
        fail(f"expected 57 unique links, got rows={len(links)} unique={len(link_map)}")
    if [row["id"] for row in links] != [f"L{index:03d}" for index in range(1, 58)]:
        fail("link IDs are not contiguous L001-L057")

    management = [ipaddress.ip_address(row["mgmt_ipv4"]) for row in nodes]
    if len(management) != len(set(management)):
        fail("duplicate management address")
    if any(address not in ipaddress.ip_network("10.201.255.0/24") for address in management):
        fail("management address outside 10.201.255.0/24")

    for name, expected in EXPECTED_ISP2_NODES.items():
        row = node_map.get(name)
        if not row:
            fail(f"missing node {name}")
        actual = tuple(row[key] for key in ("role", "kind", "mgmt_ipv4", "loopback_ipv4", "loopback_ipv6"))
        if actual != expected:
            fail(f"{name} expected {expected}, got {actual}")
        if row["isis_net"] or row["prefix_sid_index"] or row["ipv6_prefix_sid_index"]:
            fail(f"{name} must not inherit ISP-1 IS-IS/SR identifiers")

    endpoints: set[str] = set()
    networks4: list[tuple[str, ipaddress.IPv4Network]] = []
    networks6: list[tuple[str, ipaddress.IPv6Network]] = []
    for link in links:
        for side in ("a", "b"):
            endpoint = link[f"endpoint_{side}"]
            if endpoint in endpoints:
                fail(f"duplicate endpoint {endpoint}")
            endpoints.add(endpoint)
            if endpoint.split(":", 1)[0] not in node_map:
                fail(f"unknown node in endpoint {endpoint}")
        a4 = ipaddress.ip_interface(link["endpoint_a_ipv4"])
        b4 = ipaddress.ip_interface(link["endpoint_b_ipv4"])
        a6 = ipaddress.ip_interface(link["endpoint_a_ipv6"])
        b6 = ipaddress.ip_interface(link["endpoint_b_ipv6"])
        if a4.network != b4.network or a4.network.prefixlen != 31:
            fail(f"{link['id']} invalid IPv4 /31 pair")
        if a6.network != b6.network or a6.network.prefixlen != 127:
            fail(f"{link['id']} invalid IPv6 /127 pair")
        networks4.append((link["id"], a4.network))
        networks6.append((link["id"], a6.network))

    for networks in (networks4, networks6):
        for index, (left_id, left) in enumerate(networks):
            for right_id, right in networks[index + 1:]:
                if left.overlaps(right):
                    fail(f"overlap {left_id} {left} with {right_id} {right}")

    for link_id, expected in EXPECTED_LINK_ENDPOINTS.items():
        row = link_map.get(link_id)
        actual = (row["endpoint_a"], row["endpoint_b"]) if row else None
        if actual != expected:
            fail(f"{link_id} expected endpoints {expected}, got {actual}")
        expected_index = int(link_id[1:])
        if ipaddress.ip_interface(row["endpoint_a_ipv4"]).ip != ipaddress.ip_address(f"10.255.0.{2 * (expected_index - 1)}"):
            fail(f"{link_id} does not continue the deterministic IPv4 plan")
        if ipaddress.ip_interface(row["endpoint_a_ipv6"]).network != ipaddress.ip_network(f"2001:db8:1000:{100 + expected_index}::/127"):
            fail(f"{link_id} does not continue the deterministic IPv6 plan")

    iol_endpoints = [endpoint for endpoint in endpoints if endpoint.split(":", 1)[0].startswith("ISP2-P")]
    if any(endpoint.rsplit(":", 1)[1] not in {"Ethernet0/1", "Ethernet0/2", "Ethernet0/3"} for endpoint in iol_endpoints):
        fail("ISP-2 IOL endpoint outside Ethernet0/1-3")

    topology = TOPOLOGY_PATH.read_text(encoding="utf-8")
    for name, expected in EXPECTED_ISP2_NODES.items():
        if f"    {name}:" not in topology or f"      mgmt-ipv4: {expected[2]}" not in topology:
            fail(f"topology missing node or management address for {name}")
    for endpoint_a, endpoint_b in EXPECTED_LINK_ENDPOINTS.values():
        if f'["{endpoint_a}", "{endpoint_b}"]' not in topology:
            fail(f"topology missing link {endpoint_a}--{endpoint_b}")

    startup = ROOT / "topology" / "startup"
    for name in ("ASBR-ISP2", "RR-ISP2"):
        text = (startup / f"{name}.cfg").read_text(encoding="utf-8").lower()
        if any(token in text for token in FORBIDDEN_BOOTSTRAP):
            fail(f"{name} bootstrap contains a forbidden routing/service token")
    for name in ("ISP2-P1", "ISP2-P2", "ISP2-P3", "ISP2-P4", "ISP2-P5"):
        text = (startup / f"{name}.partial.cfg").read_text(encoding="utf-8").lower()
        if any(token in text for token in FORBIDDEN_BOOTSTRAP):
            fail(f"{name} bootstrap contains a forbidden routing/service token")

    print("PASS: 38 nodes, 57 links, L048-L057, unique addressing and bootstrap policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
