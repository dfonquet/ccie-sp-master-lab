#!/usr/bin/env python3
"""Validate documentation facts against the repository Source of Truth."""

from __future__ import annotations

import ast
import csv
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SRGB_START = 16000
PROFILE_SOURCES = {
    "master": {
        "nodes": "inventory/nodes.csv",
        "links": "inventory/links.csv",
        "families": 2,
        "directions": 2,
    },
    "inter-as": {
        "nodes": "profiles/inter-as/nodes.csv",
        "links": "profiles/inter-as/links.csv",
        "families": 2,
        "directions": 2,
    },
    "srv6": {
        "nodes": "profiles/srv6/nodes.csv",
        "links": "profiles/srv6/links.csv",
        "families": 1,
        "directions": 2,
    },
}


def read(path: str | Path) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def csv_rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def tracked_markdown() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "*.md"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [ROOT / line for line in result.stdout.splitlines() if line]


def python_constant(path: str, name: str) -> object:
    tree = ast.parse(read(path), filename=path)
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in statement.targets):
            return ast.literal_eval(statement.value)
    raise ValueError(f"{name} not found in {path}")


def bgp_as_values() -> set[int]:
    paths = [
        "automation/inventory/group_vars/pe.yml",
        "automation/inventory/host_vars/RR1.yml",
        "automation/inventory/host_vars/RR2.yml",
    ]
    values: set[int] = set()
    for path in paths:
        match = re.search(r"(?m)^bgp_as:\s*(\d+)\s*$", read(path))
        if not match:
            raise ValueError(f"bgp_as missing from {path}")
        values.add(int(match.group(1)))
    return values


def prefix_sid_indexes() -> tuple[list[int], list[int]]:
    ipv4: list[int] = []
    ipv6: list[int] = []
    for config in sorted((ROOT / "configs/20-sr-mpls").glob("*.cfg")):
        family = None
        for raw_line in config.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if line == "address-family ipv4 unicast":
                family = "ipv4"
            elif line == "address-family ipv6 unicast":
                family = "ipv6"
            elif match := re.fullmatch(r"prefix-sid index (\d+)", line):
                (ipv4 if family == "ipv4" else ipv6).append(int(match.group(1)))
    return sorted(ipv4), sorted(ipv6)


def local_markdown_links(paths: list[Path]) -> list[str]:
    failures: list[str] = []
    pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    for document in paths:
        for raw_target in pattern.findall(document.read_text(encoding="utf-8")):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            file_part = unquote(target.split("#", 1)[0])
            resolved = (document.parent / file_part).resolve()
            if not resolved.exists():
                failures.append(f"{document.relative_to(ROOT)} -> {target}")
    return failures


def require(text: str, marker: str, location: str, failures: list[str]) -> None:
    normalized_text = " ".join(text.split())
    normalized_marker = " ".join(marker.split())
    if normalized_marker not in normalized_text:
        failures.append(f"{location}: missing {marker!r}")


def profile_facts() -> dict[str, dict[str, int]]:
    """Derive node, platform, link, and test counts for every lab profile."""
    profiles: dict[str, dict[str, int]] = {}
    for name, source in PROFILE_SOURCES.items():
        nodes = csv_rows(str(source["nodes"]))
        links = csv_rows(str(source["links"]))
        families = int(source["families"])
        directions = int(source["directions"])
        profiles[name] = {
            "nodes": len(nodes),
            "xrd": sum(row["kind"] == "cisco_xrd" for row in nodes),
            "iol": sum(row["kind"] == "cisco_iol" for row in nodes),
            "linux": sum(row["kind"] == "linux" for row in nodes),
            "links": len(links),
            "families": families,
            "directions": directions,
            "tests": len(links) * families * directions,
        }
    return profiles


def main() -> int:
    failures: list[str] = []
    profile = profile_facts()
    master = profile["master"]
    inter_as = profile["inter-as"]
    srv6 = profile["srv6"]
    mgmt_subnet = str(python_constant("tools/build_lab.py", "MGMT_SUBNET"))

    try:
        as_values = bgp_as_values()
    except ValueError as exc:
        failures.append(str(exc))
        as_values = set()
    if as_values != {500}:
        failures.append(f"Master BGP AS values must resolve only to 500; got {sorted(as_values)}")
    if re.search(r"(?m)^\s*(?:AS_NUMBER|MASTER_AS_NUMBER)\s*=\s*65000\s*$", read("tools/build_lab.py")):
        failures.append("tools/build_lab.py: contradictory AS65000 constant found")

    ipv4_indexes, ipv6_indexes = prefix_sid_indexes()
    master_nodes = csv_rows("inventory/nodes.csv")
    isp1_sr_nodes = sum(bool(row["isis_net"]) for row in master_nodes)
    expected_ipv4 = list(range(1, isp1_sr_nodes + 1))
    expected_ipv6 = list(range(601, 601 + isp1_sr_nodes))
    if ipv4_indexes != expected_ipv4:
        failures.append(f"IPv4 Prefix-SID indexes: expected {expected_ipv4}, got {ipv4_indexes}")
    if ipv6_indexes != expected_ipv6:
        failures.append(f"IPv6 Prefix-SID indexes: expected {expected_ipv6}, got {ipv6_indexes}")

    license_text = read("LICENSE")
    if license_text.startswith("Creative Commons Attribution 4.0 International"):
        license_name = "CC BY 4.0"
        license_badge = "License-CC%20BY%204.0"
    elif license_text.startswith("MIT License"):
        license_name = "MIT"
        license_badge = "License-MIT"
    else:
        failures.append("LICENSE: unsupported or unrecognized declared license")
        license_name = "unknown"
        license_badge = "License-unknown"
    facts = {
        "mgmt_subnet": mgmt_subnet,
        "master_as": next(iter(as_values), None),
        "ipv4_index_range": f"{ipv4_indexes[0]}-{ipv4_indexes[-1]}",
        "ipv6_index_range": f"{ipv6_indexes[0]}-{ipv6_indexes[-1]}",
        "ipv4_label_range": f"{SRGB_START + ipv4_indexes[0]}-{SRGB_START + ipv4_indexes[-1]}",
        "ipv6_label_range": f"{SRGB_START + ipv6_indexes[0]}-{SRGB_START + ipv6_indexes[-1]}",
        "license": license_name,
        "license_badge": license_badge,
    }

    readme = read("README.md")
    status = read("STATUS.md")
    matrix = read("BLUEPRINT-MATRIX.md")
    validation = read("docs/VALIDATION.md")
    profiles = read("profiles/README.md")
    inter_as_readme = read("profiles/inter-as/README.md")
    operating_guide = read("docs/LAB-OPERATING-GUIDE.md")

    for marker in (
        f"{master['nodes']} nodes, {master['links']} data links",
        f"{inter_as['nodes']} nodes, {inter_as['links']} links",
        f"{srv6['nodes']} nodes, {srv6['links']} links",
        f"`{facts['mgmt_subnet']}`",
        str(facts["license_badge"]),
    ):
        require(readme, marker, "README.md", failures)
    for marker in (
        "30 of 30 master-lab containers running",
        "18 Cisco XRd nodes",
        "11 Cisco IOL nodes",
        f"IPv6 Prefix-SIDs `{facts['ipv6_label_range']}`",
        f"`{facts['ipv6_index_range']}`",
        "Full 30-node management acceptance remains pending after the AUTO1 rebuild.",
        f"all {srv6['tests']} directional directly connected IPv6 tests passed",
        f"current bidirectional acceptance target is {inter_as['tests']} tests",
    ):
        require(status, marker, "STATUS.md", failures)
    require(
        matrix,
        "21-node infrastructure, IPv6 IS-IS, and locator baseline validated; advanced SRv6 services remain incremental",
        "BLUEPRINT-MATRIX.md",
        failures,
    )
    for marker in (
        f"structural_nodes={master['nodes']}",
        f"structural_links={master['links']}",
        "active_nodes=30",
        "active_links=47",
        "active_directed_dual_stack_tests=188",
    ):
        require(validation, marker, "docs/VALIDATION.md", failures)
    require(profiles, f"AS {facts['master_as']}", "profiles/README.md", failures)
    for marker in (
        "previous one-way validator passed 70/70 tests",
        f"current bidirectional acceptance target is {inter_as['tests']}/{inter_as['tests']} tests",
        "remains pending until the profile is deployed and observed again",
    ):
        require(inter_as_readme, marker, "profiles/inter-as/README.md", failures)
    for marker in (
        "complete 30-node management and 188-test Master acceptance remains pending",
        f"Current bidirectional target: {inter_as['tests']}/{inter_as['tests']} tests",
    ):
        require(operating_guide, marker, "docs/LAB-OPERATING-GUIDE.md", failures)

    markdown = tracked_markdown()
    for document in markdown:
        lines = document.read_text(encoding="utf-8").splitlines()
        first_line = next((line.strip() for line in lines if line.strip()), "")
        if not (first_line.startswith("# ") or first_line.startswith("<h1")):
            failures.append(f"{document.relative_to(ROOT)}: first line must be one H1")
    failures.extend(f"broken local link: {item}" for item in local_markdown_links(markdown))

    print("Documentation facts derived from Source of Truth:")
    for name, values in profile.items():
        summary = " ".join(f"{key}={value}" for key, value in values.items())
        print(f"  profile.{name}: {summary}")
    for key, value in facts.items():
        print(f"  {key}={value}")

    if failures:
        print("Documentation consistency validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print(f"PASS: documentation consistency ({len(markdown)} Markdown files checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
