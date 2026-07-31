#!/usr/bin/env python3
"""Render the authoritative Inter-AS inventories as SVG."""

from __future__ import annotations

import csv
import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "inter-as"
OUTPUT = PROFILE / "topology.svg"
POSITIONS = {
    "RR500": (400, 150), "P1": (220, 340), "P2": (540, 340),
    "P3": (220, 500), "P4": (540, 500),
    "PE1": (100, 690), "PE2": (300, 690), "PE3": (500, 690), "PE4": (700, 690),
    "RR65100": (1320, 140), "P5": (1140, 330), "P7": (1480, 330),
    "PE5": (1080, 520), "PE7": (1530, 520),
    "RR65200": (1320, 870), "P6": (1140, 1030), "P8": (1480, 1030),
    "PE6": (1080, 1190), "PE8": (1530, 1190),
    "CE-A": (865, 560), "CE-B": (865, 1010), "CE-C": (1700, 720),
    "AUTO1": (140, 1260),
}
AS_COLORS = {"500": ("#dbeafe", "#1d4ed8"), "65100": ("#dcfce7", "#15803d"),
             "65200": ("#fef3c7", "#b45309"), "": ("#f3f4f6", "#475569")}
LINK_COLORS = {"internal": "#64748b", "external": "#dc2626", "customer": "#7c3aed"}


def read(name: str) -> list[dict[str, str]]:
    with (PROFILE / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def render() -> str:
    nodes, links = read("nodes.csv"), read("links.csv")
    link_svg = []
    for link in links:
        a = link["endpoint_a"].split(":", 1)[0]
        b = link["endpoint_b"].split(":", 1)[0]
        x1, y1 = POSITIONS[a]
        x2, y2 = POSITIONS[b]
        color = LINK_COLORS[link["type"]]
        dash = ' stroke-dasharray="9 6"' if link["type"] == "external" else ""
        link_svg.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="3"{dash}/>'
        )
    node_svg = []
    for node in nodes:
        x, y = POSITIONS[node["name"]]
        fill, stroke = AS_COLORS[node["asn"]]
        width = 150
        node_svg.append(
            f'<g><rect x="{x - width/2}" y="{y - 42}" width="{width}" height="84" '
            f'rx="14" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
            f'<text x="{x}" y="{y - 10}" class="name">{esc(node["name"])}</text>'
            f'<text x="{x}" y="{y + 12}" class="role">{esc(node["role"])}</text>'
            f'<text x="{x}" y="{y + 31}" class="ip">{esc(node["mgmt_ipv4"])}</text></g>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1360" viewBox="0 0 1800 1360">
<style>
.bg{{fill:#f8fafc}} .zone{{fill:none;stroke-width:3;stroke-dasharray:10 7}}
.title{{font:700 32px system-ui;fill:#0f172a}} .subtitle{{font:16px system-ui;fill:#475569}}
.zone-title{{font:700 21px system-ui}} .name{{font:700 18px system-ui;text-anchor:middle;fill:#0f172a}}
.role{{font:13px system-ui;text-anchor:middle;fill:#334155}} .ip{{font:11px ui-monospace;text-anchor:middle;fill:#475569}}
.legend{{font:14px system-ui;fill:#334155}}
</style>
<rect class="bg" width="100%" height="100%"/>
<text x="45" y="46" class="title">CCIE SP Inter-AS · runnable profile</text>
<text x="45" y="74" class="subtitle">23 nodes · 19 XRd · 3 IOL · AUTO1 · 35 links · one heavy profile at a time</text>
<rect x="35" y="95" width="765" height="690" rx="24" class="zone" stroke="#1d4ed8"/>
<text x="55" y="128" class="zone-title" fill="#1d4ed8">AS500 · IS-IS L2 dual-stack · RR500</text>
<rect x="930" y="90" width="820" height="540" rx="24" class="zone" stroke="#15803d"/>
<text x="950" y="123" class="zone-title" fill="#15803d">AS65100 · OSPFv2 IPv4 + OSPFv3 IPv6 · RR65100</text>
<rect x="930" y="785" width="820" height="470" rx="24" class="zone" stroke="#b45309"/>
<text x="950" y="818" class="zone-title" fill="#b45309">AS65200 · OSPFv2 IPv4 + OSPFv3 IPv6 · RR65200</text>
{''.join(link_svg)}
{''.join(node_svg)}
<line x1="520" y1="1305" x2="580" y2="1305" stroke="#64748b" stroke-width="3"/>
<text x="590" y="1310" class="legend">Internal IGP</text>
<line x1="760" y1="1305" x2="820" y2="1305" stroke="#dc2626" stroke-width="3" stroke-dasharray="9 6"/>
<text x="830" y="1310" class="legend">External eBGP</text>
<line x1="1020" y1="1305" x2="1080" y2="1305" stroke="#7c3aed" stroke-width="3"/>
<text x="1090" y="1310" class="legend">Customer / Option A</text>
<text x="45" y="1340" class="subtitle">Generated from profiles/inter-as/nodes.csv and links.csv</text>
</svg>
"""


def main() -> None:
    OUTPUT.write_text(render(), encoding="utf-8", newline="\n")
    print(f"Rendered Inter-AS topology to {OUTPUT}")


if __name__ == "__main__":
    main()
