#!/usr/bin/env python3
"""Validate every full-profile link in both directions without changing state."""
from __future__ import annotations
import csv
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from netmiko import ConnectHandler
from credentials import connection_credentials

ROOT=Path(__file__).resolve().parents[1];PROFILE=ROOT/"profiles"/"srv6"
def rows(name):
    with (PROFILE/name).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))

def main():
    nodes={r["name"]:r for r in rows("nodes.csv")};tests=defaultdict(list)
    for link in rows("links.csv"):
        a=link["endpoint_a"].split(":",1)[0];b=link["endpoint_b"].split(":",1)[0]
        aa=link["endpoint_a_ipv6"].split("/",1)[0];ba=link["endpoint_b_ipv6"].split("/",1)[0]
        tests[a].append((link["id"],b,ba));tests[b].append((link["id"],a,aa))
    def check(name):
        row=nodes[name];xr=row["kind"]=="cisco_xrd"
        session=ConnectHandler(device_type="cisco_xr" if xr else "cisco_ios",host=row["mgmt_ipv4"],fast_cli=False,**connection_credentials(row["kind"]))
        result=[]
        for link,peer,dst in tests[name]:
            suffix="count 3" if xr else "repeat 3"
            output=session.send_command(f"ping ipv6 {dst} {suffix}",read_timeout=30)
            result.append((link,name,peer,dst,"Success rate is 100 percent" in output))
        session.disconnect();return result
    result=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(check,name) for name in tests]
        for future in as_completed(futures):result.extend(future.result())
    failed=[]
    for link,source,peer,dst,ok in sorted(result):
        print(f"{link}|{source}->{peer}|{dst}|{'PASS' if ok else 'FAIL'}")
        if not ok:failed.append((link,source,peer))
    print(f"SUMMARY tests={len(result)} passed={len(result)-len(failed)} failed={len(failed)}")
    return 1 if failed else 0
if __name__=="__main__":raise SystemExit(main())
