#!/usr/bin/env python3
"""Render the authoritative Full Dataplane SVG from profile CSV files."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "full-dataplane"
OUTPUT = PROFILE / "topology.svg"

ROWS = {"RR1": (700, 235), "RR2": (1300, 235)}
for i, name in enumerate(("P1", "P2", "P3", "P4")): ROWS[name] = (350 + i * 430, 450)
for i, name in enumerate(("PE1", "PE2", "PE3", "PE4", "PE5", "PE6")): ROWS[name] = (190 + i * 325, 690)
for i, name in enumerate(("CE1", "CE2", "CE3", "CE4", "CE5", "CE6", "CE7", "CE8")): ROWS[name] = (120 + i * 245, 940)
for i, name in enumerate(("C1", "C2", "C3", "C4")): ROWS[name] = (250 + i * 500, 1165)
for i, name in enumerate(("AUTO1", "RPKI1", "RPKI2", "AAA1", "AAA2", "OBS1")): ROWS[name] = (220 + i * 310, 90)

with (PROFILE / "nodes.csv").open(encoding="utf-8", newline="") as fh:
    NODES = {row["name"]: row for row in csv.DictReader(fh)}
with (PROFILE / "links.csv").open(encoding="utf-8", newline="") as fh:
    LINKS = list(csv.DictReader(fh))

COLORS = {
    "P": ("#dbeafe", "#2563eb"), "PE": ("#cffafe", "#0891b2"),
    "RR-PCE": ("#f3e8ff", "#9333ea"), "CE-MH": ("#dcfce7", "#16a34a"),
    "CLIENT": ("#ffedd5", "#ea580c"), "AUTOMATION": ("#e2e8f0", "#475569"),
    "RPKI": ("#fef3c7", "#ca8a04"), "AAA": ("#fee2e2", "#dc2626"),
    "OBSERVABILITY": ("#e0e7ff", "#4f46e5"),
}
LINK_STYLE = {
    "core-ring": ("#2563eb", "4", ""), "core-diagonal": ("#ec4899", "3", "9 6"),
    "pe-core": ("#0891b2", "3", ""), "rr-core": ("#9333ea", "3", ""),
    "customer": ("#16a34a", "2.5", "7 5"), "client": ("#ea580c", "2", ""),
}

def esc(text): return text.replace("&", "&amp;").replace("<", "&lt;")

edges = []
for link in LINKS:
    a, b = link["endpoint_a"].split(":")[0], link["endpoint_b"].split(":")[0]
    x1, y1 = ROWS[a]; x2, y2 = ROWS[b]; color, width, dash = LINK_STYLE[link["purpose"]]
    edges.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}" opacity=".82"/><text x="{(x1+x2)//2}" y="{(y1+y2)//2-5}" class="link">{link["id"]}</text>')

boxes = []
for name, node in NODES.items():
    x, y = ROWS[name]; fill, stroke = COLORS[node["role"]]
    boxes.append(f'<g><rect x="{x-82}" y="{y-48}" width="164" height="96" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="3"/><text x="{x}" y="{y-12}" class="name">{name}</text><text x="{x}" y="{y+12}" class="role">{esc(node["role"])}</text><text x="{x}" y="{y+34}" class="ip">{node["mgmt_ipv4"]}</text></g>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="1320" viewBox="0 0 2000 1320" role="img" aria-labelledby="title desc">
<title id="title">CCIE SP Full Dataplane topology</title><desc id="desc">Prepared 30-node redundant service-provider topology with ten XRd vRouter forwarding nodes and 42 links.</desc>
<style>.bg{{fill:#f8fafc}}.zone{{fill:none;stroke:#cbd5e1;stroke-width:2;stroke-dasharray:9 7}}.title{{font:700 34px system-ui;fill:#0f172a}}.subtitle{{font:16px system-ui;fill:#475569}}.zone-title{{font:700 18px system-ui;fill:#334155}}.name{{font:700 18px system-ui;text-anchor:middle;fill:#0f172a}}.role{{font:13px system-ui;text-anchor:middle;fill:#334155}}.ip{{font:11px ui-monospace;text-anchor:middle;fill:#475569}}.link{{font:9px ui-monospace;text-anchor:middle;fill:#64748b;paint-order:stroke;stroke:#f8fafc;stroke-width:3px}}.legend{{font:13px system-ui;fill:#334155}}</style>
<rect class="bg" width="100%" height="100%"/><text x="45" y="48" class="title">CCIE SP Full Dataplane</text><text x="45" y="78" class="subtitle">30 nodes | 10 XRd vRouter + 2 XRd CP + 12 IOL-XE + 6 services | 42 links | prepared, not deployed</text>
<rect x="35" y="105" width="1930" height="90" rx="18" class="zone"/><text x="55" y="130" class="zone-title">Operations, trust and assurance services</text>
<rect x="35" y="205" width="1930" height="115" rx="18" class="zone"/><text x="55" y="230" class="zone-title">Redundant RR / PCE control plane</text>
<rect x="35" y="330" width="1930" height="240" rx="18" class="zone"/><text x="55" y="355" class="zone-title">Ultra-redundant P fabric · IS-IS Level 2 · SR-MPLS foundation</text>
<rect x="35" y="580" width="1930" height="220" rx="18" class="zone"/><text x="55" y="605" class="zone-title">Dual-homed provider edge</text>
<rect x="35" y="810" width="1930" height="235" rx="18" class="zone"/><text x="55" y="835" class="zone-title">Eight dual-homed CE sites · EVPN MH / L2VPN / L3VPN study boundary</text>
<rect x="35" y="1055" width="1930" height="165" rx="18" class="zone"/><text x="55" y="1080" class="zone-title">Customer test endpoints</text>
{''.join(edges)}{''.join(boxes)}
<line x1="430" y1="1270" x2="490" y2="1270" stroke="#2563eb" stroke-width="4"/><text x="500" y="1275" class="legend">Core ring</text><line x1="620" y1="1270" x2="680" y2="1270" stroke="#ec4899" stroke-width="3" stroke-dasharray="9 6"/><text x="690" y="1275" class="legend">Core diagonals</text><line x1="850" y1="1270" x2="910" y2="1270" stroke="#0891b2" stroke-width="3"/><text x="920" y="1275" class="legend">PE/RR core</text><line x1="1070" y1="1270" x2="1130" y2="1270" stroke="#16a34a" stroke-width="3" stroke-dasharray="7 5"/><text x="1140" y="1275" class="legend">Dual-homed customer</text>
<text x="45" y="1305" class="subtitle">Source of truth: profiles/full-dataplane/nodes.csv + links.csv · generated by tools/render_full_dataplane.py</text></svg>'''
OUTPUT.write_text(svg, encoding="utf-8", newline="\n")
print(f"Rendered {OUTPUT}")
