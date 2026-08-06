#!/usr/bin/env python3
"""Render the authoritative XRd Eight topology from its CSV inventories."""
from __future__ import annotations

import csv
from collections import defaultdict
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "xrd-eight"

POSITIONS = {
    "AUTO1": (110, 115), "R2": (930, 125),
    "XR1": (315, 330), "XR2": (685, 330),
    "R1": (315, 535), "R3": (685, 535),
    "R5": (205, 755), "XR4": (500, 755), "XR3": (795, 755),
    "R4": (205, 985), "R7": (500, 985), "R10": (795, 985),
}

ALIASES = {
    "XR1": "P1", "XR2": "P2", "R1": "P3", "R3": "P4",
    "R5": "PE1", "XR4": "PE2", "XR3": "PE3", "R2": "RR / PCE / RP",
}

COLORS = {"isp": "#1593b5", "customer": "#3aa65a"}


def load_csv(name: str) -> list[dict[str, str]]:
    with (PROFILE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def svg() -> str:
    nodes = {row["name"]: row for row in load_csv("nodes.csv")}
    links = load_csv("links.csv")
    pair_seen: defaultdict[tuple[str, str], int] = defaultdict(int)
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1160" viewBox="0 0 1200 1160">',
        '<style>text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#172033}.title{font-size:30px;font-weight:750}.sub{font-size:14px;fill:#536078}.zone{fill:#f8fafc;stroke:#cbd5e1;stroke-width:1.5;stroke-dasharray:8 7}.zone-title{font-size:17px;font-weight:650;fill:#4b5870}.node{stroke-width:2.4}.name{font-size:18px;font-weight:750;text-anchor:middle}.role{font-size:12px;text-anchor:middle;fill:#536078}.ip{font:11px Consolas,monospace;text-anchor:middle;fill:#5d687b}.link{fill:none;stroke-width:2.5}.lid{font:10px Consolas,monospace;fill:#5f6b7d;text-anchor:middle}.legend{font-size:12px;fill:#445069}.badge{font-size:13px;font-weight:650;fill:#176b37}</style>',
        '<rect width="1200" height="1160" fill="#f3f6fa"/>',
        '<text x="42" y="48" class="title">CCIE SP XRd Eight — Compact Full-Dataplane Lab</text>',
        '<text x="42" y="75" class="sub">12 nodes · 8 XRd vRouter 26.2.1 · 3 IOL-XE · AUTO1 · 20 links · management 10.207.255.0/24</text>',
        '<rect x="820" y="30" width="335" height="58" rx="14" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>',
        '<text x="840" y="54" class="badge">✓ Runtime observed: 12/12 containers</text>',
        '<text x="840" y="75" class="badge">✓ 8/8 XR healthy · restart 0 · OOM false</text>',
        '<rect x="35" y="105" width="1130" height="115" rx="18" class="zone"/>',
        '<text x="55" y="137" class="zone-title">Operations and control plane</text>',
        '<rect x="35" y="245" width="1130" height="390" rx="18" class="zone"/>',
        '<text x="55" y="278" class="zone-title">Provider core · four-node complete graph · dual-stack IS-IS / SR-MPLS study foundation</text>',
        '<rect x="35" y="655" width="1130" height="205" rx="18" class="zone"/>',
        '<text x="55" y="688" class="zone-title">Provider edge · each PE attached to two different P routers</text>',
        '<rect x="35" y="880" width="1130" height="190" rx="18" class="zone"/>',
        '<text x="55" y="913" class="zone-title">Customer edge · two physical links per site to one PE (bundle/access exercises)</text>',
        '<path d="M200 150 H455" stroke="#64748b" stroke-width="2" stroke-dasharray="7 6"/>',
        '<rect x="455" y="126" width="255" height="48" rx="24" fill="#e2e8f0" stroke="#64748b"/>',
        '<text x="582" y="147" class="role">Management network</text><text x="582" y="164" class="ip">10.207.255.0/24</text>',
    ]

    for link in links:
        a = link["endpoint_a"].split(":", 1)[0]
        b = link["endpoint_b"].split(":", 1)[0]
        x1, y1 = POSITIONS[a]
        x2, y2 = POSITIONS[b]
        key = tuple(sorted((a, b)))
        offset = pair_seen[key] * 8 - (4 if sum(1 for x in links if tuple(sorted((x["endpoint_a"].split(":",1)[0], x["endpoint_b"].split(":",1)[0]))) == key) > 1 else 0)
        pair_seen[key] += 1
        color = "#7c3aed" if "R2" in (a, b) else COLORS[link["purpose"]]
        out.append(f'<path d="M{x1} {y1+offset} L{x2} {y2+offset}" class="link" stroke="{color}"/>')
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + offset - 5
        out.append(f'<text x="{mx}" y="{my}" class="lid">{escape(link["id"])}</text>')

    role_fill = {"P": "#dbeafe", "PE": "#cffafe", "RR-PCE-RP": "#f3e8ff", "CE": "#dcfce7", "AUTOMATION": "#e2e8f0"}
    role_stroke = {"P": "#2563eb", "PE": "#0891b2", "RR-PCE-RP": "#7c3aed", "CE": "#15803d", "AUTOMATION": "#475569"}
    for name, row in nodes.items():
        x, y = POSITIONS[name]
        role = row["role"]
        out += [
            f'<rect x="{x-82}" y="{y-45}" width="164" height="90" rx="14" class="node" fill="{role_fill[role]}" stroke="{role_stroke[role]}"/>',
            f'<text x="{x}" y="{y-15}" class="name">{escape(name)}</text>',
            f'<text x="{x}" y="{y+5}" class="role">{escape(ALIASES.get(name, role))}</text>',
            f'<text x="{x}" y="{y+27}" class="ip">{escape(row["mgmt_ipv4"])}</text>',
        ]

    out += [
        '<line x1="185" y1="1115" x2="235" y2="1115" stroke="#2563eb" stroke-width="3"/><text x="245" y="1119" class="legend">P complete-mesh</text>',
        '<line x1="390" y1="1115" x2="440" y2="1115" stroke="#1593b5" stroke-width="3"/><text x="450" y="1119" class="legend">PE/core</text>',
        '<line x1="565" y1="1115" x2="615" y2="1115" stroke="#7c3aed" stroke-width="3"/><text x="625" y="1119" class="legend">RR/PCE/RP</text>',
        '<line x1="770" y1="1115" x2="820" y2="1115" stroke="#3aa65a" stroke-width="3"/><text x="830" y="1119" class="legend">Customer dual-link</text>',
        '<text x="42" y="1148" class="sub">Source of truth: profiles/xrd-eight/nodes.csv + links.csv · generated by tools/render_xrd_eight.py</text>',
        '</svg>',
    ]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    target = PROFILE / "topology.svg"
    target.write_text(svg(), encoding="utf-8", newline="\n")
    print(f"Rendered {target}")
