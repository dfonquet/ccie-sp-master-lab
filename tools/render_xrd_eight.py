#!/usr/bin/env python3
"""Render the authoritative XRd Eight v2 topology from CSV inventories."""

from __future__ import annotations

import csv
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "xrd-eight"

WIDTH = 1200
HEIGHT = 1160

POSITIONS = {
    "AUTO1": (120, 145),
    "RR":    (980, 145),

    "P1":    (300, 360),
    "P2":    (700, 360),
    "P3":    (300, 565),
    "P4":    (700, 565),

    "PE1":   (200, 790),
    "PE2":   (500, 790),
    "PE3":   (800, 790),

    "CE1":   (200, 1010),
    "CE2":   (500, 1010),
    "CE3":   (800, 1010),
}

ROLE_LABELS = {
    "P": "Provider Core",
    "PE": "Provider Edge",
    "RR": "Route Reflector",
    "CE": "Customer Edge",
    "AUTOMATION": "Automation",
}

ROLE_FILL = {
    "P": "#dbeafe",
    "PE": "#cffafe",
    "RR": "#f3e8ff",
    "CE": "#dcfce7",
    "AUTOMATION": "#e2e8f0",
}

ROLE_STROKE = {
    "P": "#2563eb",
    "PE": "#0891b2",
    "RR": "#7c3aed",
    "CE": "#15803d",
    "AUTOMATION": "#475569",
}

PURPOSE_COLORS = {
    "core": "#2563eb",
    "provider": "#0891b2",
    "control": "#7c3aed",
    "customer": "#16a34a",
    # Retained only for backward compatibility.
    "isp": "#0891b2",
}

PURPOSE_WIDTH = {
    "core": 3.0,
    "provider": 2.7,
    "control": 2.7,
    "customer": 2.7,
    "isp": 2.7,
}

LABEL_OFFSETS = {
    "P1-P2": (0, -10),
    "P1-P3": (-24, 0),
    "P1-P4": (18, -12),
    "P2-P3": (-18, 16),
    "P2-P4": (24, 0),
    "P3-P4": (0, -10),

    "PE1-P1": (-18, -4),
    "PE1-P3": (-18, 12),
    "PE2-P2": (16, -8),
    "PE2-P4": (16, 12),
    "PE3-P1": (-8, -12),
    "PE3-P4": (18, 10),

    "RR-P1": (-5, -10),
    "RR-P4": (12, -8),

    "CE1-PE1": (-22, 0),
    "CE1-PE2": (22, 0),
    "CE2-PE2": (22, 0),
    "CE3-PE3": (22, 0),
    "CE3-PE2": (-22, 0),
}


def load_csv(name: str) -> list[dict[str, str]]:
    with (PROFILE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def device_name(endpoint: str) -> str:
    return endpoint.split(":", 1)[0]


def svg() -> str:
    nodes = {row["name"]: row for row in load_csv("nodes.csv")}
    links = load_csv("links.csv")

    missing_positions = sorted(set(nodes) - set(POSITIONS))
    if missing_positions:
        raise ValueError(
            "Missing topology positions for: " + ", ".join(missing_positions)
        )

    unsupported_purposes = sorted(
        {link["purpose"] for link in links} - set(PURPOSE_COLORS)
    )
    if unsupported_purposes:
        raise ValueError(
            "Unsupported link purposes: " + ", ".join(unsupported_purposes)
        )

    xrd_count = sum(
        1 for node in nodes.values()
        if node["platform"].startswith("XRd")
    )
    ce_count = sum(
        1 for node in nodes.values()
        if node["role"] == "CE"
    )

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',

        """<style>
text {
  font-family: Inter, Segoe UI, Arial, sans-serif;
  fill: #172033;
}
.title {
  font-size: 30px;
  font-weight: 750;
}
.sub {
  font-size: 14px;
  fill: #536078;
}
.zone {
  fill: #f8fafc;
  stroke: #cbd5e1;
  stroke-width: 1.5;
  stroke-dasharray: 8 7;
}
.zone-title {
  font-size: 17px;
  font-weight: 650;
  fill: #4b5870;
}
.node {
  stroke-width: 2.4;
}
.name {
  font-size: 18px;
  font-weight: 750;
  text-anchor: middle;
}
.role {
  font-size: 12px;
  text-anchor: middle;
  fill: #536078;
}
.ip {
  font: 11px Consolas, monospace;
  text-anchor: middle;
  fill: #5d687b;
}
.link {
  fill: none;
}
.lid {
  font: 10px Consolas, monospace;
  font-weight: 650;
  fill: #475569;
  text-anchor: middle;
  paint-order: stroke;
  stroke: #f8fafc;
  stroke-width: 4px;
  stroke-linejoin: round;
}
.legend {
  font-size: 12px;
  fill: #445069;
}
.badge {
  font-size: 13px;
  font-weight: 650;
  fill: #334155;
}
</style>""",

        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#f3f6fa"/>',

        '<text x="42" y="48" class="title">'
        'CCIE SP XRd Eight v2 — Full-Dataplane Service Provider Lab'
        '</text>',

        f'<text x="42" y="75" class="sub">'
        f'{len(nodes)} nodes · {xrd_count} XRd vRouter 26.2.1 · '
        f'{ce_count} IOL-XE CE · AUTO1 · {len(links)} links · '
        'management 10.207.255.0/24'
        '</text>',

        '<rect x="890" y="28" width="265" height="56" '
        'rx="14" fill="#e2e8f0" stroke="#64748b" stroke-width="1.5"/>',

        '<text x="1022" y="52" class="badge" text-anchor="middle">'
        'Repository design'
        '</text>',

        '<text x="1022" y="71" class="role">'
        'Source-of-truth driven'
        '</text>',

        # Operations / control plane
        '<rect x="35" y="105" width="1130" height="120" '
        'rx="18" class="zone"/>',

        '<text x="55" y="137" class="zone-title">'
        'Operations and control plane'
        '</text>',

        # Provider core
        '<rect x="35" y="250" width="1130" height="390" '
        'rx="18" class="zone"/>',

        '<text x="55" y="283" class="zone-title">'
        'Provider core · P1–P4 full mesh · dual-stack IS-IS Level-2 · '
        'SR-MPLS foundation'
        '</text>',

        # Provider edge
        '<rect x="35" y="665" width="1130" height="205" '
        'rx="18" class="zone"/>',

        '<text x="55" y="698" class="zone-title">'
        'Provider edge · PE1–PE3 dual-homed into independent P routers'
        '</text>',

        # Customer edge
        '<rect x="35" y="895" width="1130" height="190" '
        'rx="18" class="zone"/>',

        '<text x="55" y="928" class="zone-title">'
        'Customer edge · CE1 and CE3 multihomed · CE2 single-homed baseline'
        '</text>',

        # Management network
        '<path d="M205 163 H445" stroke="#64748b" '
        'stroke-width="2" stroke-dasharray="7 6"/>',

        '<rect x="445" y="139" width="270" height="48" '
        'rx="24" fill="#e2e8f0" stroke="#64748b"/>',

        '<text x="580" y="159" class="role">'
        'Management network'
        '</text>',

        '<text x="580" y="177" class="ip">'
        '10.207.255.0/24'
        '</text>',
    ]

    # Links first so nodes render above them.
    for link in links:
        a = device_name(link["endpoint_a"])
        b = device_name(link["endpoint_b"])

        x1, y1 = POSITIONS[a]
        x2, y2 = POSITIONS[b]

        purpose = link["purpose"]
        color = PURPOSE_COLORS[purpose]
        width = PURPOSE_WIDTH[purpose]

        dash = ' stroke-dasharray="8 6"' if purpose == "control" else ""

        out.append(
            f'<path d="M{x1} {y1} L{x2} {y2}" '
            f'class="link" stroke="{color}" '
            f'stroke-width="{width}"{dash}/>'
        )

        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        dx, dy = LABEL_OFFSETS.get(link["id"], (0, -6))

        out.append(
            f'<text x="{mx + dx}" y="{my + dy}" class="lid">'
            f'{escape(link["id"])}</text>'
        )

    # Nodes
    for name, row in nodes.items():
        x, y = POSITIONS[name]
        role = row["role"]

        fill = ROLE_FILL.get(role, "#ffffff")
        stroke = ROLE_STROKE.get(role, "#64748b")
        role_label = ROLE_LABELS.get(role, role)

        out += [
            f'<rect x="{x - 82}" y="{y - 45}" width="164" height="90" '
            f'rx="14" class="node" fill="{fill}" stroke="{stroke}"/>',

            f'<text x="{x}" y="{y - 15}" class="name">'
            f'{escape(name)}</text>',

            f'<text x="{x}" y="{y + 5}" class="role">'
            f'{escape(role_label)}</text>',

            f'<text x="{x}" y="{y + 27}" class="ip">'
            f'{escape(row["mgmt_ipv4"])}</text>',
        ]

    # Legend
    legend_y = 1120

    out += [
        f'<line x1="105" y1="{legend_y}" x2="155" y2="{legend_y}" '
        'stroke="#2563eb" stroke-width="3"/>',
        f'<text x="165" y="{legend_y + 4}" class="legend">Core</text>',

        f'<line x1="260" y1="{legend_y}" x2="310" y2="{legend_y}" '
        'stroke="#0891b2" stroke-width="3"/>',
        f'<text x="320" y="{legend_y + 4}" class="legend">Provider uplink</text>',

        f'<line x1="475" y1="{legend_y}" x2="525" y2="{legend_y}" '
        'stroke="#7c3aed" stroke-width="3" stroke-dasharray="8 6"/>',
        f'<text x="535" y="{legend_y + 4}" class="legend">Control / RR</text>',

        f'<line x1="690" y1="{legend_y}" x2="740" y2="{legend_y}" '
        'stroke="#16a34a" stroke-width="3"/>',
        f'<text x="750" y="{legend_y + 4}" class="legend">Customer</text>',

        '<text x="42" y="1150" class="sub">'
        'Source of truth: profiles/xrd-eight/nodes.csv + links.csv · '
        'generated by tools/render_xrd_eight.py'
        '</text>',

        '</svg>',
    ]

    return "\n".join(out) + "\n"


if __name__ == "__main__":
    target = PROFILE / "topology.svg"
    target.write_text(svg(), encoding="utf-8", newline="\n")
    print(f"Rendered {target}")
