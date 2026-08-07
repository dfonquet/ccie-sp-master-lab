#!/usr/bin/env python3

import csv
import ipaddress
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "xrd-eight"
LINKS = PROFILE / "links.csv"
NODES = PROFILE / "nodes.csv"

errors = []


def fail(message):
    errors.append(message)


# ---------------------------------------------------------
# Load link inventory
# ---------------------------------------------------------

with LINKS.open(newline="", encoding="utf-8") as f:
    links = list(csv.DictReader(f))

ipv4_networks = []
ipv6_networks = []
ipv4_addresses = {}
ipv6_addresses = {}


for link in links:
    lid = link["id"]

    try:
        a4 = ipaddress.ip_interface(link["ipv4_a"])
        b4 = ipaddress.ip_interface(link["ipv4_b"])
    except ValueError as exc:
        fail(f"{lid}: invalid IPv4 address: {exc}")
        continue

    try:
        a6 = ipaddress.ip_interface(link["ipv6_a"])
        b6 = ipaddress.ip_interface(link["ipv6_b"])
    except ValueError as exc:
        fail(f"{lid}: invalid IPv6 address: {exc}")
        continue

    # IPv4 must use /31
    if a4.network.prefixlen != 31 or b4.network.prefixlen != 31:
        fail(f"{lid}: IPv4 P2P must use /31")

    # IPv6 must use /127
    if a6.network.prefixlen != 127 or b6.network.prefixlen != 127:
        fail(f"{lid}: IPv6 P2P must use /127")

    # Endpoints must belong to the same network
    if a4.network != b4.network:
        fail(
            f"{lid}: IPv4 endpoints are in different networks: "
            f"{a4.network} != {b4.network}"
        )

    if a6.network != b6.network:
        fail(
            f"{lid}: IPv6 endpoints are in different networks: "
            f"{a6.network} != {b6.network}"
        )

    # Same address cannot appear twice
    for endpoint, addr in (
        (link["endpoint_a"], a4.ip),
        (link["endpoint_b"], b4.ip),
    ):
        if addr in ipv4_addresses:
            fail(
                f"{lid}: duplicate IPv4 {addr}: "
                f"{endpoint} and {ipv4_addresses[addr]}"
            )
        else:
            ipv4_addresses[addr] = endpoint

    for endpoint, addr in (
        (link["endpoint_a"], a6.ip),
        (link["endpoint_b"], b6.ip),
    ):
        if addr in ipv6_addresses:
            fail(
                f"{lid}: duplicate IPv6 {addr}: "
                f"{endpoint} and {ipv6_addresses[addr]}"
            )
        else:
            ipv6_addresses[addr] = endpoint

    ipv4_networks.append((lid, a4.network))
    ipv6_networks.append((lid, a6.network))


# ---------------------------------------------------------
# Check network overlap
# ---------------------------------------------------------

for i, (lid_a, net_a) in enumerate(ipv4_networks):
    for lid_b, net_b in ipv4_networks[i + 1:]:
        if net_a.overlaps(net_b):
            fail(
                f"IPv4 overlap: {lid_a} {net_a} "
                f"<-> {lid_b} {net_b}"
            )


for i, (lid_a, net_a) in enumerate(ipv6_networks):
    for lid_b, net_b in ipv6_networks[i + 1:]:
        if net_a.overlaps(net_b):
            fail(
                f"IPv6 overlap: {lid_a} {net_a} "
                f"<-> {lid_b} {net_b}"
            )


# ---------------------------------------------------------
# Check loopbacks
# ---------------------------------------------------------

with NODES.open(newline="", encoding="utf-8") as f:
    nodes = list(csv.DictReader(f))

seen_loopback4 = {}
seen_loopback6 = {}

for node in nodes:
    name = node["name"]

    if node["loopback_ipv4"]:
        lo4 = ipaddress.ip_interface(node["loopback_ipv4"])

        if lo4.network.prefixlen != 32:
            fail(f"{name}: IPv4 loopback must use /32")

        if lo4.ip in seen_loopback4:
            fail(
                f"Duplicate IPv4 loopback {lo4.ip}: "
                f"{name} and {seen_loopback4[lo4.ip]}"
            )

        seen_loopback4[lo4.ip] = name

        for lid, net in ipv4_networks:
            if lo4.ip in net:
                fail(
                    f"{name}: IPv4 loopback {lo4.ip} overlaps "
                    f"{lid} {net}"
                )

    if node["loopback_ipv6"]:
        lo6 = ipaddress.ip_interface(node["loopback_ipv6"])

        if lo6.network.prefixlen != 128:
            fail(f"{name}: IPv6 loopback must use /128")

        if lo6.ip in seen_loopback6:
            fail(
                f"Duplicate IPv6 loopback {lo6.ip}: "
                f"{name} and {seen_loopback6[lo6.ip]}"
            )

        seen_loopback6[lo6.ip] = name

        for lid, net in ipv6_networks:
            if lo6.ip in net:
                fail(
                    f"{name}: IPv6 loopback {lo6.ip} overlaps "
                    f"{lid} {net}"
                )


# ---------------------------------------------------------
# Result
# ---------------------------------------------------------

if errors:
    print()
    print("ADDRESSING VALIDATION: FAILED")
    print("=" * 60)

    for error in errors:
        print(f"[ERROR] {error}")

    print()
    print(f"Total errors: {len(errors)}")
    sys.exit(1)


print()
print("ADDRESSING VALIDATION: PASSED")
print("=" * 60)
print(f"Links validated       : {len(links)}")
print(f"IPv4 /31 networks     : {len(ipv4_networks)}")
print(f"IPv6 /127 networks    : {len(ipv6_networks)}")
print(f"IPv4 endpoint addresses: {len(ipv4_addresses)}")
print(f"IPv6 endpoint addresses: {len(ipv6_addresses)}")
print(f"IPv4 loopbacks        : {len(seen_loopback4)}")
print(f"IPv6 loopbacks        : {len(seen_loopback6)}")
print("Overlapping networks  : 0")
print("Duplicate addresses   : 0")
