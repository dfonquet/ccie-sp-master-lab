# Architecture

## Node roles

| Role | Nodes | Platform | Purpose |
|---|---|---|---|
| Provider core | P1-P8 | XRd 24.2.11 | Dual-plane transit backbone |
| Provider edge | PE1-PE8 | XRd 24.2.11 | VPN, multicast and customer services |
| RR/PCE | RR1-RR2 | XRd 24.2.11 | Redundant MP-BGP reflection and PCE |
| Customer edge | CE1-CE9 | IOL-XE 17.12.1 | PE-CE and access scenarios |
| Test endpoints | C1-C2 | IOL-XE 17.12.1 | End-to-end and multicast tests |
| Automation | AUTO1 | Ubuntu 24.04 | Ansible, Python, NETCONF, gNMI and pyATS |

Total: 30 nodes and 47 data-plane links.

## Backbone design

The P core has two longitudinal planes:

```text
Plane A: P1 -- P3 -- P5
Plane B: P2 -- P4 -- P6
```

It also includes:

- Three inter-plane rungs.
- Two diagonal paths.
- Distinct IGP metrics for primary, rung and diagonal paths.
- SRLG values in `inventory/links.csv`.
- Two diverse core attachments per PE.
- Two diverse core attachments per RR/PCE.

## Link groups

| Group | Count | Use |
|---|---:|---|
| `core-plane-a` | 2 | Primary upper backbone plane |
| `core-plane-b` | 2 | Primary lower backbone plane |
| `core-rung` | 3 | Inter-plane redundancy |
| `core-diagonal` | 2 | Alternate/disjoint paths |
| `pe-core` | 12 | Dual-homed PE attachments |
| `rr-core` | 4 | Redundant RR/PCE attachments |
| `customer` | 6 | Single-homed customer sites |
| `customer-dual` | 6 | CE2, CE5 and CE8 multihoming |
| `client` | 2 | CE1-C1 and CE9-C2 endpoints |

## Intended study modules

1. Dual-stack IS-IS and convergence.
2. SR-MPLS, TI-LFA, SR-TE and PCE.
3. MP-BGP and redundant route reflectors.
4. L3VPN with OSPF/BGP PE-CE and shared services.
5. VPWS, VPLS and EVPN.
6. PIM, mLDP and NG-mVPN.
7. SRv6 locator and uSID alternate phases.
8. AAA, RADIUS/TACACS+, RPKI and management security.
9. Telemetry, NETCONF, gNMI, Ansible, Python and pyATS.
10. Deterministic failure and convergence exercises.

![CCIE SP master topology](topology.svg)
