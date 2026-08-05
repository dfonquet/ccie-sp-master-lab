#!/usr/bin/env python3
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; PROFILE=ROOT/"profiles"/"full-dataplane"
def read(name):
    with (PROFILE/name).open(encoding="utf-8",newline="") as f: return list(csv.DictReader(f))
def main():
    nodes,links=read("nodes.csv"),read("links.csv")
    assert len(nodes)==30 and len(links)==42
    assert sum(n["kind"]=="cisco_xrd_vrouter" for n in nodes)==10
    assert sum(n["kind"]=="cisco_xrd" for n in nodes)==2
    assert len({n["mgmt_ipv4"] for n in nodes})==30
    endpoints=[e for l in links for e in (l["endpoint_a"],l["endpoint_b"])]
    assert len(endpoints)==len(set(endpoints))
    for ce in (f"CE{i}" for i in range(1,9)):
        assert sum(l["purpose"]=="customer" and ce in (l["endpoint_a"].split(":")[0],l["endpoint_b"].split(":")[0]) for l in links)==2
    topology=(ROOT/"topology"/"ccie-sp-full-dataplane.clab.yml").read_text(encoding="utf-8")
    assert "XRD_NIC_TYPE: igb" in topology and "cisco_xrd-vrouter:26.2.1" in topology
    print("PASS Full Dataplane artifacts: 30 nodes, 42 links, 10 vRouter, all CEs dual-homed")
if __name__=="__main__": main()
