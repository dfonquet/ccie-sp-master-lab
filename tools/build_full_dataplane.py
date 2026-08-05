#!/usr/bin/env python3
"""Generate the isolated CCIE SP Full Dataplane profile."""
from __future__ import annotations
import csv
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "full-dataplane"
CONFIG = ROOT / "configs" / "full-dataplane" / "00-foundation"
TOPOLOGY = ROOT / "topology" / "ccie-sp-full-dataplane.clab.yml"
VR_IMAGE = "vrnetlab/cisco_xrd-vrouter:26.2.1"
CP_IMAGE = "ios-xr/xrd-control-plane:24.2.11"
IOL_IMAGE = "vrnetlab/cisco_iol:17.12.01"

@dataclass(frozen=True)
class Node:
    name: str; role: str; kind: str; mgmt: str; node_id: int

NODES = [
    *[Node(f"P{i}", "P", "cisco_xrd_vrouter", f"10.205.255.{100+i}", i) for i in range(1, 5)],
    *[Node(f"PE{i}", "PE", "cisco_xrd_vrouter", f"10.205.255.{110+i}", 10+i) for i in range(1, 7)],
    Node("RR1", "RR-PCE", "cisco_xrd", "10.205.255.121", 21), Node("RR2", "RR-PCE", "cisco_xrd", "10.205.255.122", 22),
    *[Node(f"CE{i}", "CE-MH", "cisco_iol", f"10.205.255.{130+i}", 30+i) for i in range(1, 9)],
    *[Node(f"C{i}", "CLIENT", "cisco_iol", f"10.205.255.{140+i}", 40+i) for i in range(1, 5)],
    Node("AUTO1", "AUTOMATION", "linux", "10.205.255.150", 50),
    Node("RPKI1", "RPKI", "linux", "10.205.255.160", 60), Node("RPKI2", "RPKI", "linux", "10.205.255.161", 61),
    Node("AAA1", "AAA", "linux", "10.205.255.170", 70), Node("AAA2", "AAA", "linux", "10.205.255.171", 71),
    Node("OBS1", "OBSERVABILITY", "linux", "10.205.255.180", 80),
]

PAIRS = [
    ("P1","P2","core-ring"),("P2","P3","core-ring"),("P3","P4","core-ring"),("P4","P1","core-ring"),
    ("P1","P3","core-diagonal"),("P2","P4","core-diagonal"),
    ("PE1","P1","pe-core"),("PE1","P2","pe-core"),("PE2","P1","pe-core"),("PE2","P3","pe-core"),
    ("PE3","P2","pe-core"),("PE3","P3","pe-core"),("PE4","P2","pe-core"),("PE4","P4","pe-core"),
    ("PE5","P3","pe-core"),("PE5","P4","pe-core"),("PE6","P1","pe-core"),("PE6","P4","pe-core"),
    ("RR1","P1","rr-core"),("RR1","P3","rr-core"),("RR2","P2","rr-core"),("RR2","P4","rr-core"),
    ("CE1","PE1","customer"),("CE1","PE2","customer"),("CE2","PE1","customer"),("CE2","PE2","customer"),
    ("CE3","PE2","customer"),("CE3","PE3","customer"),("CE4","PE3","customer"),("CE4","PE4","customer"),
    ("CE5","PE4","customer"),("CE5","PE5","customer"),("CE6","PE5","customer"),("CE6","PE6","customer"),
    ("CE7","PE1","customer"),("CE7","PE6","customer"),("CE8","PE3","customer"),("CE8","PE6","customer"),
    ("C1","CE1","client"),("C2","CE3","client"),("C3","CE5","client"),("C4","CE7","client"),
]

def build_links():
    ports = {n.name: 0 for n in NODES}; result = []
    for index, (a,b,purpose) in enumerate(PAIRS, 1):
        def endpoint(name):
            node = next(n for n in NODES if n.name == name); port = ports[name]; ports[name] += 1
            return f"Gi0-0-0-{port}" if node.kind == "cisco_xrd" else f"eth{port+1}"
        result.append(dict(id=f"FD{index:03d}",a=a,a_ep=endpoint(a),b=b,b_ep=endpoint(b),purpose=purpose,
            a4=f"10.50.255.{(index-1)*2}/31",b4=f"10.50.255.{(index-1)*2+1}/31",
            a6=f"2001:db8:1500:{index:x}::/127",b6=f"2001:db8:1500:{index:x}::1/127"))
    return result
LINKS = build_links()

def xr_if(ep, kind):
    return ep.replace("Gi","GigabitEthernet") if kind == "cisco_xrd" else f"GigabitEthernet0/0/0/{int(ep[3:])-1}"

def render_config(node):
    if node.kind == "linux": return ""
    lines=[f"hostname {node.name}"]
    if node.kind.startswith("cisco_xrd"):
        lines += ["interface Loopback0",f" description FULL-DATAPLANE NODE-ID {node.node_id}",f" ipv4 address 10.50.0.{node.node_id} 255.255.255.255",f" ipv6 address 2001:db8:550:abcd::{node.node_id}/128","!"]
    else:
        lines += ["ipv6 unicast-routing","interface Loopback0",f" ip address 10.50.0.{node.node_id} 255.255.255.255",f" ipv6 address 2001:db8:550:abcd::{node.node_id}/128","!"]
    for link in LINKS:
        if node.name not in (link["a"],link["b"]): continue
        side="a" if node.name==link["a"] else "b"; peer=link["b"] if side=="a" else link["a"]
        if node.kind.startswith("cisco_xrd"):
            ip=link[side+"4"].split("/")[0]
            lines += [f"interface {xr_if(link[side+'_ep'],node.kind)}",f" description {link['id']} -> {peer}",f" ipv4 address {ip} 255.255.255.254",f" ipv6 address {link[side+'6']}"," no shutdown","!"]
        else:
            iface=f"Ethernet0/{int(link[side+'_ep'][3:])}"; ip=link[side+"4"].split("/")[0]
            lines += [f"interface {iface}",f" description {link['id']} -> {peer}",f" ip address {ip} 255.255.255.254",f" ipv6 address {link[side+'6']}"," no shutdown","!"]
    if node.kind.startswith("cisco_xrd") and node.role in {"P","PE","RR-PCE"}:
        lines += ["router isis FULL-SP"," is-type level-2-only",f" net 49.0050.0000.0000.{node.node_id:04d}.00"," address-family ipv4 unicast","  metric-style wide","  segment-routing mpls"," !"," address-family ipv6 unicast","  metric-style wide","  single-topology"," !"," interface Loopback0","  passive","  address-family ipv4 unicast",f"   prefix-sid index {node.node_id}","  !","  address-family ipv6 unicast","  !"," !"]
        for link in LINKS:
            if node.name in (link["a"],link["b"]) and link["purpose"] in {"core-ring","core-diagonal","pe-core","rr-core"}:
                side="a" if node.name==link["a"] else "b"
                lines += [f" interface {xr_if(link[side+'_ep'],node.kind)}","  point-to-point","  address-family ipv4 unicast","   metric 10","  !","  address-family ipv6 unicast","   metric 10","  !"," !"]
        lines += ["!","segment-routing"," global-block 16000 23999","!","end"]
    else: lines += ["end"]
    return "\n".join(lines)+"\n"

def main():
    assert len(NODES)==30 and len(LINKS)==42
    PROFILE.mkdir(parents=True,exist_ok=True); CONFIG.mkdir(parents=True,exist_ok=True); TOPOLOGY.parent.mkdir(exist_ok=True)
    with (PROFILE/"nodes.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f,lineterminator="\n"); w.writerow(["name","role","kind","mgmt_ipv4","loopback_ipv4","loopback_ipv6","image"])
        for n in NODES:
            image=VR_IMAGE if n.kind=="cisco_xrd_vrouter" else CP_IMAGE if n.kind=="cisco_xrd" else IOL_IMAGE if n.kind=="cisco_iol" else "service-image-staged"
            w.writerow([n.name,n.role,n.kind,n.mgmt,f"10.50.0.{n.node_id}/32",f"2001:db8:550:abcd::{n.node_id}/128",image])
    with (PROFILE/"links.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f,lineterminator="\n"); w.writerow(["id","endpoint_a","ipv4_a","ipv6_a","endpoint_b","ipv4_b","ipv6_b","purpose"])
        for l in LINKS: w.writerow([l["id"],f"{l['a']}:{l['a_ep']}",l["a4"],l["a6"],f"{l['b']}:{l['b_ep']}",l["b4"],l["b6"],l["purpose"]])
    lines=["name: ccie-sp-full-dataplane","","mgmt:","  network: ccie-sp-full-dataplane-mgmt","  ipv4-subnet: 10.205.255.0/24","","topology:","  kinds:","    cisco_xrd_vrouter:",f"      image: {VR_IMAGE}","      env:","        XRD_NIC_TYPE: igb","    cisco_xrd:",f"      image: {CP_IMAGE}","    cisco_iol:",f"      image: {IOL_IMAGE}","","  nodes:"]
    for i,n in enumerate(NODES):
        lines += [f"    {n.name}:",f"      kind: {n.kind}",f"      mgmt-ipv4: {n.mgmt}"]
        if n.kind!="linux": lines += [f"      startup-config: ../configs/full-dataplane/00-foundation/{n.name}.cfg",f"      startup-delay: {i*90 if n.kind=='cisco_xrd_vrouter' else 900+i*10}"]
        else: lines += [f"      image: {'ccie-sp-automation:1.0' if n.name=='AUTO1' else 'alpine:3.20'}","      cmd: sleep infinity"]
    lines += ["","  links:"]
    for l in LINKS: lines += [f"    - endpoints: [\"{l['a']}:{l['a_ep']}\", \"{l['b']}:{l['b_ep']}\"]"]
    TOPOLOGY.write_text("\n".join(lines)+"\n",encoding="utf-8",newline="\n")
    for n in NODES:
        text=render_config(n)
        if text: (CONFIG/f"{n.name}.cfg").write_text(text,encoding="utf-8",newline="\n")
    roles={r:sum(n.role==r for n in NODES) for r in sorted({n.role for n in NODES})}
    table="\n".join(f"| {r} | {c} |" for r,c in roles.items())
    (PROFILE/"README.md").write_text(f"""# CCIE SP Full Dataplane Profile

> **Prepared, not deployed.** Image build, single-node canary, staged boot and live acceptance are required before this profile is called runnable.

This isolated 30-node profile adds a real XRd vRouter forwarding plane without replacing the resource-efficient Master profile.

## Architecture

| Role | Count |
|---|---:|
{table}

- 42 deterministic dual-stack links.
- Four-P complete graph: ring plus two diagonals.
- Six PEs and two RR/PCEs, all dual-attached to the core.
- Eight CE sites, every one dual-homed for EVPN MH, L2VPN and L3VPN drills.
- Redundant RPKI and AAA placeholders, AUTO1 and OBS1.

## Foundation and study boundary

The generated foundation contains hostnames, loopbacks, link addressing, provider IS-IS Level 2 and SR-MPLS Prefix-SID scaffolding. BGP services, PCE policies, SRv6, EVPN, VPNs, multicast, QoS, RPKI, AAA and telemetry remain student work.

## Resource and safety gate

Target: 96 GiB VM RAM and at least 14 vCPU. Boot no more than two vRouters concurrently. Stop at 80% host RAM, any swap use, sustained load above assigned vCPU, restart or OOM. The ten-vRouter ceiling is a design budget, not a live acceptance claim.

```bash
python3 tools/build_full_dataplane.py
python3 tools/validate_full_dataplane_artifacts.py
sudo containerlab apply -t topology/ccie-sp-full-dataplane.clab.yml --dry-run
```

`tools/build_full_dataplane.py` is the Source of Truth; generated artifacts must not be hand-edited.
""",encoding="utf-8",newline="\n")
    print(f"Generated Full Dataplane profile: {len(NODES)} nodes, {len(LINKS)} links")

if __name__=="__main__": main()
