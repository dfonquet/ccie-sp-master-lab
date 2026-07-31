# Lab 1 — CCIE SP Master ISP

The `master` profile is the primary ISP services lab. It is designed for the
CCIE Service Provider blueprint and extends it with realistic operations:
redundancy, automation, AAA, RPKI, observability, and failure testing.

![Lab 1 topology](../../docs/topology.svg)

## Summary

| Item | Implementation |
|---|---|
| Scale | 30 nodes and 47 links |
| Core | P1-P8, two longitudinal planes, rungs, and diagonals |
| Edge | PE1-PE8, each dual-homed to the core |
| Control plane | RR1/RR2 as redundant RR and PCE nodes |
| Customers | CE1-CE9, C1/C2 |
| Automation | AUTO1 |
| IGP | Dual-stack IS-IS Level 2 |
| Transport | SR-MPLS, SR-TE, and a TI-LFA foundation |
| Services | L3VPN, L2VPN/EVPN, multicast, and PE-CE routing |

The complete role and link-group description is in
[`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md). The
`inventory/nodes.csv` and `inventory/links.csv` files are authoritative.

## Addressing and identifiers

| Use | Plan |
|---|---|
| Management | `10.201.255.0/24` |
| Provider IPv4 loopback | `10.0.0.<ID>/32` |
| Provider IPv6 loopback | `2001:db8:500:abcd::<ID>/128` |
| Customer IPv4 loopback | `10.100.0.<ID>/32` |
| Customer IPv6 loopback | `2001:db8:100::<ID>/128` |
| Provider IPv4 P2P | `/31` starting at `10.255.0.0/31` |
| Provider IPv6 P2P | `2001:db8:1000:<link-id>::/127` |
| SRGB | `16000-23999` |

IDs 1-18 identify P, PE, and RR nodes. The IPv4 Prefix-SID uses the ID; the
IPv6 Prefix-SID uses `600 + ID`, avoiding the collision observed on XRd. See
the complete table in [`docs/ADDRESSING.md`](../../docs/ADDRESSING.md).

## How it works

1. IS-IS Level 2 discovers the dual-stack topology and advertises loopbacks.
2. SR-MPLS assigns a stable Node-SID to every provider loopback.
3. RR1 and RR2 remove the requirement for a full-mesh MP-BGP topology.
4. Every PE has two paths into the core; metrics distinguish primary, rung,
   and diagonal paths.
5. Multihomed CEs support SoO, sham-link, BGP multipath, EVPN multihoming, and
   access-failure exercises.
6. AUTO1 renders, applies, verifies, and backs up changes reproducibly.

## Configuration priority

Services are not applied until transport is stable:

1. `00-base`: hostnames, loopbacks, and links.
2. `10-isis`: dual-stack IS-IS.
3. `15-provider-standard`: IPv6 standard, LFA, and SR foundation.
4. `20-sr-mpls`: SRGB and Prefix-SIDs.
5. MP-BGP/RR and routing policies.
6. L3VPN, L2VPN/EVPN, multicast, and management services.
7. Controlled failures and convergence validation.

Use one or two canary nodes before expanding a phase:

```bash
python3 tools/apply_phase.py 10-isis --nodes P1,P3 --workers 1
python3 tools/validate_links.py --family both --workers 2
```

## Safe operation

```bash
./labctl status
./labctl deploy master
./labctl inspect master
./labctl destroy master
```

Only one heavy profile may be active. Do not use `--cleanup` unless persistent
router state is intentionally being removed.

## Minimum validation

- 30/30 containers running with no OOM events.
- Every directly connected link passes IPv4 and IPv6 tests.
- IS-IS adjacency counts match the inventory.
- All provider loopbacks are reachable over both families.
- Node-SIDs are unique and installed.
- PEs have redundant VPNv4/VPNv6 sessions to RR1 and RR2.
- No swap is used and at least 12 GiB remains available in the VM.

The detailed runbook is in
[`docs/VALIDATION.md`](../../docs/VALIDATION.md).

## Troubleshooting and references

- [Known errors and solutions](TROUBLESHOOTING.md)
- [Cisco and RFC references](REFERENCES.md)
- [General operations](../../OPERATIONS.md)
- [Automation from AUTO1](../../docs/AUTO1-SOURCE-OF-TRUTH.md)
