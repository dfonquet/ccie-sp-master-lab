#!/usr/bin/env python3
"""Render the authoritative CSV inventory as a self-contained SVG diagram."""

from __future__ import annotations

import csv
import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODES_CSV = ROOT / "inventory" / "nodes.csv"
LINKS_CSV = ROOT / "inventory" / "links.csv"
OUTPUT = ROOT / "docs" / "topology.svg"

WIDTH = 1800
HEIGHT = 1320

POSITIONS = {
    "AUTO1": (150, 105),
    "RR1": (740, 115),
    "RR2": (1080, 115),
    "P1": (250, 330),
    "P3": (650, 330),
    "P5": (1050, 330),
    "P7": (1500, 330),
    "P2": (250, 540),
    "P4": (650, 540),
    "P6": (1050, 540),
    "P8": (1500, 540),
    "PE1": (100, 760),
    "PE2": (320, 760),
    "PE3": (540, 760),
    "PE4": (760, 760),
    "PE5": (980, 760),
    "PE6": (1200, 760),
    "PE7": (1420, 760),
    "PE8": (1640, 760),
    "CE1": (120, 1000),
    "CE2": (310, 1000),
    "CE3": (500, 1000),
    "CE4": (690, 1000),
    "CE5": (880, 1000),
    "CE6": (1070, 1000),
    "CE7": (1260, 1000),
    "CE8": (1450, 1000),
    "CE9": (1640, 1000),
    "C1": (120, 1210),
    "C2": (1640, 1210),
}

GROUP_STYLE = {
    "core-plane-a": ("#2563eb", 4, ""),
    "core-plane-b": ("#2563eb", 4, ""),
    "core-rung": ("#7c3aed", 3, "10 7"),
    "core-diagonal": ("#db2777", 3, "8 7"),
    "pe-core": ("#0891b2", 3, ""),
    "rr-core": ("#9333ea", 3, ""),
    "customer": ("#16a34a", 2, ""),
    "customer-dual": ("#65a30d", 3, "7 5"),
    "client": ("#ea580c", 2, ""),
}

ROLE_STYLE = {
    "P": ("#dbeafe", "#1d4ed8"),
    "PE": ("#cffafe", "#0e7490"),
    "RR-PCE": ("#f3e8ff", "#7e22ce"),
    "CE": ("#dcfce7", "#15803d"),
    "CE-DUAL": ("#ecfccb", "#4d7c0f"),
    "CLIENT": ("#ffedd5", "#c2410c"),
    "AUTOMATION": ("#e2e8f0", "#334155"),
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def line_element(link: dict[str, str]) -> str:
    node_a = link["endpoint_a"].split(":", 1)[0]
    node_b = link["endpoint_b"].split(":", 1)[0]
    x1, y1 = POSITIONS[node_a]
    x2, y2 = POSITIONS[node_b]
    color, width, dash = GROUP_STYLE[link["group"]]
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2
    label = esc(link["id"])
    return (
        f'<g class="link"><line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="{width}"{dash_attr}/>'
        f'<text x="{mx:.0f}" y="{my - 6:.0f}" class="link-label">{label}</text></g>'
    )


def node_element(node: dict[str, str]) -> str:
    name = node["name"]
    x, y = POSITIONS[name]
    fill, stroke = ROLE_STYLE[node["role"]]
    width = 150 if name != "AUTO1" else 175
    height = 86
    left = x - width / 2
    top = y - height / 2
    role = esc(node["role"])
    mgmt = esc(node["mgmt_ipv4"])
    return (
        f'<g class="node"><rect x="{left}" y="{top}" width="{width}" '
        f'height="{height}" rx="14" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="3"/>'
        f'<text x="{x}" y="{y - 13}" class="node-name">{esc(name)}</text>'
        f'<text x="{x}" y="{y + 10}" class="node-role">{role}</text>'
        f'<text x="{x}" y="{y + 30}" class="node-mgmt">{mgmt}</text></g>'
    )


def render() -> str:
    nodes = load_csv(NODES_CSV)
    links = load_csv(LINKS_CSV)
    lines = [line_element(link) for link in links]
    node_shapes = [node_element(node) for node in nodes]

    legend_items = [
        ("Core planes", "#2563eb", ""),
        ("Rungs", "#7c3aed", "10 7"),
        ("Diagonals", "#db2777", "8 7"),
        ("PE/RR core", "#0891b2", ""),
        ("Customer", "#16a34a", ""),
        ("Dual-homed CE", "#65a30d", "7 5"),
    ]
    legend = []
    for index, (label, color, dash) in enumerate(legend_items):
        x = 310 + index * 225
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        legend.append(
            f'<line x1="{x}" y1="1270" x2="{x + 55}" y2="1270" '
            f'stroke="{color}" stroke-width="4"{dash_attr}/>'
            f'<text x="{x + 65}" y="1276" class="legend">{esc(label)}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">CCIE Service Provider master lab topology</title>
  <desc id="desc">Thirty-node dual-plane service provider topology with eight P routers, eight PE routers, two route reflectors and PCEs, nine customer edges, two clients and one automation workstation.</desc>
  <style>
    .background {{ fill: #f8fafc; }}
    .zone {{ fill: none; stroke: #cbd5e1; stroke-width: 2; stroke-dasharray: 8 8; }}
    .zone-label {{ font: 600 20px system-ui, sans-serif; fill: #475569; }}
    .title {{ font: 700 32px system-ui, sans-serif; fill: #0f172a; }}
    .subtitle {{ font: 16px system-ui, sans-serif; fill: #475569; }}
    .link-label {{ font: 11px ui-monospace, monospace; fill: #334155; text-anchor: middle; paint-order: stroke; stroke: #f8fafc; stroke-width: 4; }}
    .node-name {{ font: 700 20px system-ui, sans-serif; fill: #0f172a; text-anchor: middle; }}
    .node-role {{ font: 13px system-ui, sans-serif; fill: #334155; text-anchor: middle; }}
    .node-mgmt {{ font: 12px ui-monospace, monospace; fill: #475569; text-anchor: middle; }}
    .legend {{ font: 13px system-ui, sans-serif; fill: #334155; }}
  </style>
  <rect class="background" width="100%" height="100%"/>
  <text x="55" y="48" class="title">CCIE SP v5.1 Master Lab</text>
  <text x="55" y="76" class="subtitle">18 XRd + 11 IOL + AUTO1 | 47 data-plane links | dual-stack IS-IS and SR-MPLS</text>
  <rect x="285" y="245" width="1250" height="390" rx="24" class="zone"/>
  <text x="305" y="278" class="zone-label">Provider core</text>
  <rect x="55" y="680" width="1690" height="165" rx="24" class="zone"/>
  <text x="75" y="713" class="zone-label">Provider edge</text>
  <rect x="45" y="915" width="1710" height="170" rx="24" class="zone"/>
  <text x="65" y="948" class="zone-label">Customer edge</text>
  <path d="M235 105 H470" stroke="#64748b" stroke-width="2" stroke-dasharray="6 6"/>
  <rect x="470" y="77" width="205" height="56" rx="28" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>
  <text x="572" y="101" class="node-role">Management network</text>
  <text x="572" y="120" class="node-mgmt">10.201.255.0/24</text>
  {''.join(lines)}
  {''.join(node_shapes)}
  {''.join(legend)}
</svg>
"""


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(), encoding="utf-8", newline="\n")
    print(f"Rendered {len(load_csv(NODES_CSV))} nodes to {OUTPUT}")


if __name__ == "__main__":
    main()
