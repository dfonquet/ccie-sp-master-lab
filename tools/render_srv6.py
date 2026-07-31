#!/usr/bin/env python3
"""Render the authoritative full SRv6 profile as SVG."""
from __future__ import annotations
import csv, html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE, OUTPUT = ROOT / "profiles" / "srv6", ROOT / "profiles" / "srv6" / "topology.svg"
POSITIONS = {
 "RR1":(500,120),"RR2":(1300,120),"P1":(350,350),"P2":(650,270),"P3":(950,270),
 "P4":(1250,350),"P5":(1100,540),"P6":(500,540),"PE1":(180,650),"PE2":(430,735),
 "PE3":(700,650),"PE4":(970,650),"PE5":(1240,735),"PE6":(1500,650),"CE1":(180,900),
 "CE2":(430,985),"CE3":(700,900),"CE4":(970,900),"CE5":(1240,985),"CE6":(1500,900),
 "AUTO1":(1620,130)}
STYLE={"P":("#dbeafe","#1d4ed8"),"PE":("#dcfce7","#15803d"),"RR":("#fef3c7","#b45309"),
       "CE":("#f3e8ff","#7e22ce"),"AUTOMATION":("#e2e8f0","#475569")}

def read(name):
    with (PROFILE/name).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))

def render():
    nodes,links=read("nodes.csv"),read("links.csv"); edges=[]; boxes=[]
    for link in links:
        a=link["endpoint_a"].split(":",1)[0];b=link["endpoint_b"].split(":",1)[0]
        x1,y1=POSITIONS[a];x2,y2=POSITIONS[b];access=link["purpose"]=="access"
        dash=' stroke-dasharray="8 5"' if access else ""
        edges.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{"#7e22ce" if access else "#64748b"}" stroke-width="{3 if access else 2}"{dash}/>')
    for n in nodes:
        x,y=POSITIONS[n["name"]];fill,stroke=STYLE[n["role"]];loop=n["loopback_ipv6"] or "automation"
        boxes.append(f'<g><rect x="{x-82}" y="{y-48}" width="164" height="96" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="3"/><text x="{x}" y="{y-17}" class="name">{html.escape(n["name"])}</text><text x="{x}" y="{y+5}" class="role">{n["role"]}</text><text x="{x}" y="{y+25}" class="ip">{n["mgmt_ipv4"]}</text><text x="{x}" y="{y+41}" class="tiny">{html.escape(loop)}</text></g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1100" viewBox="0 0 1800 1100"><style>.bg{{fill:#f8fafc}}.title{{font:700 32px system-ui;fill:#0f172a}}.subtitle{{font:16px system-ui;fill:#475569}}.name{{font:700 18px system-ui;text-anchor:middle;fill:#0f172a}}.role{{font:13px system-ui;text-anchor:middle;fill:#334155}}.ip{{font:11px ui-monospace;text-anchor:middle;fill:#475569}}.tiny{{font:9px ui-monospace;text-anchor:middle;fill:#64748b}}.legend{{font:14px system-ui;fill:#334155}}</style><rect class="bg" width="100%" height="100%"/><text x="45" y="48" class="title">CCIE SP / JNCIE-SP SRv6 full study profile</text><text x="45" y="77" class="subtitle">21 nodes | 14 XRd + 6 IOL-XE + AUTO1 | 33 links | validated functional underlay</text>{''.join(edges)}{''.join(boxes)}<line x1="500" y1="1050" x2="565" y2="1050" stroke="#64748b" stroke-width="2"/><text x="575" y="1055" class="legend">Provider underlay</text><line x1="760" y1="1050" x2="825" y2="1050" stroke="#7e22ce" stroke-width="3" stroke-dasharray="8 5"/><text x="835" y="1055" class="legend">PE-CE access</text><text x="45" y="1082" class="subtitle">Generated from profiles/srv6/nodes.csv and links.csv</text></svg>'''

if __name__=="__main__":
    OUTPUT.write_text(render(),encoding="utf-8",newline="\n");print(f"Rendered SRv6 topology to {OUTPUT}")
