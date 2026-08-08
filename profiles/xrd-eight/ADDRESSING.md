# XRd Eight v2 Addressing Plan

> **Deterministic dual-stack addressing and infrastructure identifier model for the XRd Eight v2 Service Provider topology.**
>
> The addressing architecture is designed to remain stable across rebuilds, simplify troubleshooting, preserve predictable node identities, and provide a reproducible foundation for IS-IS, SR-MPLS, BGP, VPN, EVPN, traffic-engineering and automation exercises.

XRd Eight v2 uses an explicit and deterministic addressing model.

The topology does **not** calculate production-facing addresses dynamically from Python list order or Containerlab interface creation order. Physical links, endpoint assignments, node identities, loopbacks, IS-IS identifiers and Segment Routing Prefix-SIDs are deliberately predictable.

The addressing architecture separates the following functional domains:

- management connectivity;
- provider node identity;
- IPv4 point-to-point infrastructure;
- IPv6 point-to-point infrastructure;
- customer-facing physical connectivity;
- IS-IS system identity;
- Segment Routing Prefix-SID allocation;
- future service-specific addressing.

This separation makes the lab easier to rebuild, automate, validate and troubleshoot.

---

## Source of Truth

The XRd Eight v2 addressing model is maintained as repository data.

The primary addressing and inventory files are:

| File | Function |
| --- | --- |
| `profiles/xrd-eight/nodes.csv` | Generated node inventory |
| `profiles/xrd-eight/links.csv` | Generated normalized link inventory |
| `profiles/xrd-eight/links-v2.csv` | Explicit v2 endpoint and addressing definition |

`links-v2.csv` contains the explicit point-to-point addressing assignments consumed by `tools/build_xrd_eight.py`.

The builder verifies that:

- every expected physical link exists;
- every link ID has an addressing definition;
- endpoint names match the topology definition;
- endpoint interfaces match the expected physical design;
- link purpose matches the repository model;
- IPv4 endpoints use `/31`;
- IPv6 endpoints use `/127`;
- both IPv4 endpoints belong to the same network;
- both IPv6 endpoints belong to the same network;
- duplicate endpoint addresses do not exist;
- overlapping point-to-point networks do not exist.

The resulting workflow is:

```text
profiles/xrd-eight/links-v2.csv
                |
                | Explicit endpoint addressing
                v
      tools/build_xrd_eight.py
                |
        +-------+-----------------------------+
        |                                     |
        v                                     v
topology/ccie-sp-xrd-eight.clab.yml   configs/xrd-eight/00-foundation/
        |
        +------------------+
        |                  |
        v                  v
nodes.csv              links.csv
        \                  /
         \                /
          +-------> tools/render_xrd_eight.py
                          |
                          v
              profiles/xrd-eight/topology.svg
```

The repository addressing model can therefore be regenerated and validated before any XRd container is started.

---

## Design Principles

| Principle | Implementation |
| --- | --- |
| Deterministic node identity | Stable Node IDs `1-8` |
| Dedicated management plane | `10.207.255.0/24` |
| Stable provider IPv4 identities | `/32` loopbacks |
| Stable provider IPv6 identities | `/128` loopbacks |
| Efficient IPv4 point-to-point addressing | `/31` |
| Efficient IPv6 point-to-point addressing | `/127` |
| Native dual-stack infrastructure | IPv4 and IPv6 on every physical link |
| Explicit physical-link addressing | Stored in `links-v2.csv` |
| Stable IS-IS identity | System ID derived from Node ID |
| Stable SR-MPLS identity | Prefix-SID derived from Node ID |
| Incremental expansion | New links consume the next free allocation |
| Customer/service separation | CE service addressing remains scenario-defined |

---

## Address Blocks

| Purpose | Allocation |
| --- | --- |
| Management network | `10.207.255.0/24` |
| Provider IPv4 loopbacks | `10.70.0.<node-id>/32` |
| Provider IPv6 loopbacks | `2001:db8:570:abcd::<node-id>/128` |
| Point-to-point IPv4 links | Sequential `/31` beginning at `10.20.0.0/31` |
| Point-to-point IPv6 links | Sequential `/127` beginning at `2001:db8:2000:101::/127` |
| Current IPv4 P2P allocation | `10.20.0.0/31` through `10.20.0.36/31` |
| Current IPv6 P2P allocation | `2001:db8:2000:101::/127` through `2001:db8:2000:119::/127` |
| Next reserved IPv4 link | `10.20.0.38/31` |
| Next reserved IPv6 link | `2001:db8:2000:120::/127` |
| IS-IS process | `500-SP` |
| IS-IS area | `49.0001` |
| IS-IS level | Level 2 only |
| SRGB | `16000-23999` |
| IPv4 Prefix-SID index | Node ID `1-8` |
| IPv6 Prefix-SID index | `600 + Node ID`, producing `601-608` |

---

# Management Addressing

All twelve nodes connect to the dedicated Containerlab management network:

```text
10.207.255.0/24
```

Containerlab management network:

```text
ccie-sp-xrd-eight-mgmt
```

The management network is deliberately independent from the Service Provider transport topology.

This separation ensures that management access remains available while the routing or forwarding plane is intentionally modified, broken or reconstructed during lab exercises.

Typical management-plane functions include:

- SSH access;
- configuration deployment;
- automation from `AUTO1`;
- evidence collection;
- troubleshooting;
- configuration backup;
- telemetry experiments;
- protocol validation;
- recovery from routing failures.

A failure in IS-IS, SR-MPLS, BGP, VPN or EVPN should therefore not remove management access to the lab.

## Management Address Allocation

| Node | Function | Platform | Management IPv4 |
| --- | --- | --- | --- |
| `P1` | Provider Core | XRd vRouter 26.2.1 | `10.207.255.101` |
| `P2` | Provider Core | XRd vRouter 26.2.1 | `10.207.255.102` |
| `P3` | Provider Core | XRd vRouter 26.2.1 | `10.207.255.104` |
| `P4` | Provider Core | XRd vRouter 26.2.1 | `10.207.255.106` |
| `PE1` | Provider Edge | XRd vRouter 26.2.1 | `10.207.255.107` |
| `PE2` | Provider Edge | XRd vRouter 26.2.1 | `10.207.255.108` |
| `PE3` | Provider Edge | XRd vRouter 26.2.1 | `10.207.255.103` |
| `RR` | Route Reflector / Control Plane | XRd vRouter 26.2.1 | `10.207.255.105` |
| `CE1` | Customer Edge | IOL-XE 17.12.1 | `10.207.255.141` |
| `CE2` | Customer Edge | IOL-XE 17.12.1 | `10.207.255.143` |
| `CE3` | Customer Edge | IOL-XE 17.12.1 | `10.207.255.146` |
| `AUTO1` | Automation / Operations | Linux | `10.207.255.150` |

Management addresses intentionally remain independent from the logical provider Node-ID scheme.

The existing `10.207.255.0/24` management network is preserved while the provider infrastructure uses a clean sequential identity model.

---

# Provider Node-ID Model

The eight XRd provider and control-plane routers use stable Node IDs.

| Node | Role | Node ID |
| --- | --- | ---: |
| `P1` | Provider Core | `1` |
| `P2` | Provider Core | `2` |
| `P3` | Provider Core | `3` |
| `P4` | Provider Core | `4` |
| `PE1` | Provider Edge | `5` |
| `PE2` | Provider Edge | `6` |
| `PE3` | Provider Edge | `7` |
| `RR` | Route Reflector / Control Plane | `8` |

The same Node ID is reused across multiple infrastructure identifiers:

```text
                         Node ID
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
    IPv4 Loopback     IPv6 Loopback     IS-IS System ID
          |                 |                 |
          +-----------------+-----------------+
                            |
                            v
                 Segment Routing Identity
                  |                     |
                  v                     v
             IPv4 Prefix-SID       IPv6 Prefix-SID
                Node ID           600 + Node ID
```

For example, `PE2` uses:

```text
Node                    PE2
Node ID                 6
IPv4 Loopback           10.70.0.6/32
IPv6 Loopback           2001:db8:570:abcd::6/128
IS-IS System ID         0000.0000.0006
IPv4 Prefix-SID index   6
IPv6 Prefix-SID index   606
```

This deterministic correlation significantly reduces troubleshooting complexity.

---

# Provider Loopback Addressing

`Loopback0` represents the stable routing identity of each provider/control-plane XRd node.

## IPv4 Loopbacks

| Node | Node ID | IPv4 Loopback |
| --- | ---: | --- |
| `P1` | `1` | `10.70.0.1/32` |
| `P2` | `2` | `10.70.0.2/32` |
| `P3` | `3` | `10.70.0.3/32` |
| `P4` | `4` | `10.70.0.4/32` |
| `PE1` | `5` | `10.70.0.5/32` |
| `PE2` | `6` | `10.70.0.6/32` |
| `PE3` | `7` | `10.70.0.7/32` |
| `RR` | `8` | `10.70.0.8/32` |

## IPv6 Loopbacks

| Node | Node ID | IPv6 Loopback |
| --- | ---: | --- |
| `P1` | `1` | `2001:db8:570:abcd::1/128` |
| `P2` | `2` | `2001:db8:570:abcd::2/128` |
| `P3` | `3` | `2001:db8:570:abcd::3/128` |
| `P4` | `4` | `2001:db8:570:abcd::4/128` |
| `PE1` | `5` | `2001:db8:570:abcd::5/128` |
| `PE2` | `6` | `2001:db8:570:abcd::6/128` |
| `PE3` | `7` | `2001:db8:570:abcd::7/128` |
| `RR` | `8` | `2001:db8:570:abcd::8/128` |

These loopbacks provide stable identities for technologies including:

- IS-IS;
- SR-MPLS;
- iBGP;
- MP-BGP;
- Route Reflection;
- VPNv4;
- VPNv6;
- EVPN;
- BGP-LS;
- PCE/PCC;
- Segment Routing Policies;
- telemetry;
- automation and validation workflows.

---

# CE and Automation Addressing Boundary

The generated provider foundation does not assign provider-style Loopback0 identities to the CE nodes.

| Node | Role | Loopback Allocation |
| --- | --- | --- |
| `CE1` | Customer Edge | Scenario-defined |
| `CE2` | Customer Edge | Scenario-defined |
| `CE3` | Customer Edge | Scenario-defined |
| `AUTO1` | Automation / Operations | Not applicable |

This is intentional.

Customer loopbacks, prefixes and service identities depend on the scenario being implemented.

Examples include:

- static PE-CE routing;
- eBGP PE-CE;
- OSPF PE-CE;
- IPv4 L3VPN;
- IPv6 L3VPN;
- dual-PE L3VPN;
- L2VPN;
- VPWS;
- VPLS;
- EVPN;
- EVPN multihoming;
- customer migration scenarios.

The physical CE-facing point-to-point networks are reserved in the addressing inventory, but higher-layer customer service configuration remains outside the generated provider baseline.

---

# Point-to-Point Addressing Model

Every physical link in XRd Eight v2 has deterministic IPv4 and IPv6 addressing.

IPv4 uses:

```text
/31
```

IPv6 uses:

```text
/127
```

The topology is therefore dual-stack from the physical infrastructure layer onward.

IPv6 is not treated as an optional secondary exercise.

The same deterministic model applies to:

- P-to-P core links;
- PE-to-P provider links;
- RR-to-P control-plane links;
- CE-to-PE customer-facing links.

---

## IPv4 Allocation

The current IPv4 point-to-point sequence begins at:

```text
10.20.0.0/31
```

and currently extends through:

```text
10.20.0.36/31
```

The topology therefore consumes:

```text
19 IPv4 /31 networks
38 IPv4 endpoint addresses
```

The next available IPv4 allocation is:

```text
10.20.0.38/31
```

---

## IPv6 Allocation

The current IPv6 point-to-point sequence begins at:

```text
2001:db8:2000:101::/127
```

and currently extends through:

```text
2001:db8:2000:119::/127
```

The topology therefore consumes:

```text
19 IPv6 /127 networks
38 IPv6 endpoint addresses
```

The next available IPv6 allocation is:

```text
2001:db8:2000:120::/127
```

---

# Physical Link Inventory

XRd Eight v2 contains exactly **19 physical links**.

| Link Class | Count |
| --- | ---: |
| Provider Core | `6` |
| Provider Edge | `6` |
| Control Plane | `2` |
| Customer Edge | `5` |
| **Total** | **19** |

Link purposes are explicitly classified in the inventory.

| Purpose | Meaning |
| --- | --- |
| `core` | P-to-P provider core |
| `provider` | PE-to-P provider infrastructure |
| `control` | RR-to-P control-plane transport |
| `customer` | CE-to-PE customer-facing connectivity |

The builder retains backward compatibility with the historical `isp` purpose classification, but the current v2 link inventory uses the categories above.

---

# Provider Core Links

The four P routers form a complete physical graph.

This creates six core links:

```text
P1-P2
P1-P3
P1-P4
P2-P3
P2-P4
P3-P4
```

## Core Link Addressing

| Link | Endpoint A | Endpoint B | IPv4 A | IPv4 B | IPv6 A | IPv6 B |
| --- | --- | --- | --- | --- | --- | --- |
| `P1-P2` | `P1:eth1` | `P2:eth1` | `10.20.0.0/31` | `10.20.0.1/31` | `2001:db8:2000:101::/127` | `2001:db8:2000:101::1/127` |
| `P1-P3` | `P1:eth2` | `P3:eth1` | `10.20.0.2/31` | `10.20.0.3/31` | `2001:db8:2000:102::/127` | `2001:db8:2000:102::1/127` |
| `P1-P4` | `P1:eth3` | `P4:eth1` | `10.20.0.4/31` | `10.20.0.5/31` | `2001:db8:2000:103::/127` | `2001:db8:2000:103::1/127` |
| `P2-P3` | `P2:eth2` | `P3:eth2` | `10.20.0.6/31` | `10.20.0.7/31` | `2001:db8:2000:104::/127` | `2001:db8:2000:104::1/127` |
| `P2-P4` | `P2:eth3` | `P4:eth2` | `10.20.0.8/31` | `10.20.0.9/31` | `2001:db8:2000:105::/127` | `2001:db8:2000:105::1/127` |
| `P3-P4` | `P3:eth3` | `P4:eth3` | `10.20.0.10/31` | `10.20.0.11/31` | `2001:db8:2000:106::/127` | `2001:db8:2000:106::1/127` |

The full-mesh provider core provides multiple transport paths for:

- IS-IS ECMP;
- SR-MPLS;
- BFD;
- LFA;
- TI-LFA capability testing;
- link-failure testing;
- node-failure testing;
- Segment Routing policy;
- traffic-engineering exercises;
- convergence analysis.

---

# Provider Edge Links

Each PE connects to two different Provider Core routers.

The current topology is:

```text
PE1 -> P1 + P3
PE2 -> P2 + P4
PE3 -> P1 + P4
```

No PE depends on a single core router.

## Provider Edge Addressing

| Link | Endpoint A | Endpoint B | IPv4 A | IPv4 B | IPv6 A | IPv6 B |
| --- | --- | --- | --- | --- | --- | --- |
| `PE1-P1` | `PE1:eth1` | `P1:eth4` | `10.20.0.12/31` | `10.20.0.13/31` | `2001:db8:2000:107::/127` | `2001:db8:2000:107::1/127` |
| `PE1-P3` | `PE1:eth2` | `P3:eth4` | `10.20.0.14/31` | `10.20.0.15/31` | `2001:db8:2000:108::/127` | `2001:db8:2000:108::1/127` |
| `PE2-P2` | `PE2:eth1` | `P2:eth4` | `10.20.0.16/31` | `10.20.0.17/31` | `2001:db8:2000:109::/127` | `2001:db8:2000:109::1/127` |
| `PE2-P4` | `PE2:eth2` | `P4:eth4` | `10.20.0.18/31` | `10.20.0.19/31` | `2001:db8:2000:110::/127` | `2001:db8:2000:110::1/127` |
| `PE3-P1` | `PE3:eth1` | `P1:eth5` | `10.20.0.20/31` | `10.20.0.21/31` | `2001:db8:2000:111::/127` | `2001:db8:2000:111::1/127` |
| `PE3-P4` | `PE3:eth2` | `P4:eth5` | `10.20.0.22/31` | `10.20.0.23/31` | `2001:db8:2000:112::/127` | `2001:db8:2000:112::1/127` |

These links participate in the provider infrastructure and are eligible for:

- IS-IS;
- BFD;
- SR-MPLS;
- IPv4 transport;
- IPv6 transport;
- fast-reroute;
- convergence testing.

---

# Control-Plane Links

The `RR` router is dual-attached to the provider core.

Connectivity is:

```text
RR -> P1
RR -> P4
```

This gives the future BGP control-plane node independent paths through the transport network.

## Control-Plane Addressing

| Link | Endpoint A | Endpoint B | IPv4 A | IPv4 B | IPv6 A | IPv6 B |
| --- | --- | --- | --- | --- | --- | --- |
| `RR-P1` | `RR:eth1` | `P1:eth6` | `10.20.0.24/31` | `10.20.0.25/31` | `2001:db8:2000:113::/127` | `2001:db8:2000:113::1/127` |
| `RR-P4` | `RR:eth2` | `P4:eth6` | `10.20.0.26/31` | `10.20.0.27/31` | `2001:db8:2000:114::/127` | `2001:db8:2000:114::1/127` |

The `RR` node can later support study scenarios involving:

- IPv4 iBGP Route Reflection;
- IPv6 iBGP Route Reflection;
- VPNv4;
- VPNv6;
- EVPN;
- BGP-LS;
- PCE-related control-plane functions;
- centralized policy experiments.

These higher-layer roles are intentionally not part of the addressing foundation.

---

# Customer Edge Links

The customer topology deliberately includes both single-homed and dual-homed designs.

The physical layout is:

```text
CE1
 | \
 |  \
PE1  PE2

CE2
 |
PE2

CE3
 | \
 |  \
PE3  PE2
```

More explicitly:

```text
CE1 -> PE1 + PE2
CE2 -> PE2
CE3 -> PE3 + PE2
```

## Customer Link Addressing

| Link | Endpoint A | Endpoint B | IPv4 A | IPv4 B | IPv6 A | IPv6 B |
| --- | --- | --- | --- | --- | --- | --- |
| `CE1-PE1` | `CE1:eth1` | `PE1:eth3` | `10.20.0.28/31` | `10.20.0.29/31` | `2001:db8:2000:115::/127` | `2001:db8:2000:115::1/127` |
| `CE1-PE2` | `CE1:eth2` | `PE2:eth3` | `10.20.0.30/31` | `10.20.0.31/31` | `2001:db8:2000:116::/127` | `2001:db8:2000:116::1/127` |
| `CE2-PE2` | `CE2:eth1` | `PE2:eth4` | `10.20.0.32/31` | `10.20.0.33/31` | `2001:db8:2000:117::/127` | `2001:db8:2000:117::1/127` |
| `CE3-PE3` | `CE3:eth1` | `PE3:eth3` | `10.20.0.34/31` | `10.20.0.35/31` | `2001:db8:2000:118::/127` | `2001:db8:2000:118::1/127` |
| `CE3-PE2` | `CE3:eth2` | `PE2:eth5` | `10.20.0.36/31` | `10.20.0.37/31` | `2001:db8:2000:119::/127` | `2001:db8:2000:119::1/127` |

The physical connectivity supports the following study models:

| Customer | Connectivity | Intended Design Use |
| --- | --- | --- |
| `CE1` | Dual-homed to `PE1` and `PE2` | Redundancy, dual-PE services, EVPN multihoming |
| `CE2` | Single-homed to `PE2` | Baseline service |
| `CE3` | Dual-homed to `PE3` and `PE2` | Second independent multihoming scenario |

Potential future exercises include:

- eBGP multihoming;
- dual-PE L3VPN;
- Ethernet Segment Identifier design;
- EVPN Ethernet Segment routes;
- DF election;
- all-active multihoming;
- single-active multihoming;
- aliasing;
- mass withdrawal;
- PE failure;
- access-link failure;
- customer migration.

The addressing is reserved in the repository, but CE service configuration remains intentionally minimal in the generated startup baseline.

---

# Complete Link Address Summary

| # | Link | Purpose | IPv4 Network | IPv6 Network |
| ---: | --- | --- | --- | --- |
| `1` | `P1-P2` | Core | `10.20.0.0/31` | `2001:db8:2000:101::/127` |
| `2` | `P1-P3` | Core | `10.20.0.2/31` | `2001:db8:2000:102::/127` |
| `3` | `P1-P4` | Core | `10.20.0.4/31` | `2001:db8:2000:103::/127` |
| `4` | `P2-P3` | Core | `10.20.0.6/31` | `2001:db8:2000:104::/127` |
| `5` | `P2-P4` | Core | `10.20.0.8/31` | `2001:db8:2000:105::/127` |
| `6` | `P3-P4` | Core | `10.20.0.10/31` | `2001:db8:2000:106::/127` |
| `7` | `PE1-P1` | Provider | `10.20.0.12/31` | `2001:db8:2000:107::/127` |
| `8` | `PE1-P3` | Provider | `10.20.0.14/31` | `2001:db8:2000:108::/127` |
| `9` | `PE2-P2` | Provider | `10.20.0.16/31` | `2001:db8:2000:109::/127` |
| `10` | `PE2-P4` | Provider | `10.20.0.18/31` | `2001:db8:2000:110::/127` |
| `11` | `PE3-P1` | Provider | `10.20.0.20/31` | `2001:db8:2000:111::/127` |
| `12` | `PE3-P4` | Provider | `10.20.0.22/31` | `2001:db8:2000:112::/127` |
| `13` | `RR-P1` | Control | `10.20.0.24/31` | `2001:db8:2000:113::/127` |
| `14` | `RR-P4` | Control | `10.20.0.26/31` | `2001:db8:2000:114::/127` |
| `15` | `CE1-PE1` | Customer | `10.20.0.28/31` | `2001:db8:2000:115::/127` |
| `16` | `CE1-PE2` | Customer | `10.20.0.30/31` | `2001:db8:2000:116::/127` |
| `17` | `CE2-PE2` | Customer | `10.20.0.32/31` | `2001:db8:2000:117::/127` |
| `18` | `CE3-PE3` | Customer | `10.20.0.34/31` | `2001:db8:2000:118::/127` |
| `19` | `CE3-PE2` | Customer | `10.20.0.36/31` | `2001:db8:2000:119::/127` |

---

# IS-IS Identity Model

The provider infrastructure uses:

```text
router isis 500-SP
```

The generated design is:

```text
IS-IS Level 2 only
Area: 49.0001
```

The IS-IS System ID is derived directly from the provider Node ID.

## IS-IS NET Allocation

| Node | Node ID | IS-IS NET |
| --- | ---: | --- |
| `P1` | `1` | `49.0001.0000.0000.0001.00` |
| `P2` | `2` | `49.0001.0000.0000.0002.00` |
| `P3` | `3` | `49.0001.0000.0000.0003.00` |
| `P4` | `4` | `49.0001.0000.0000.0004.00` |
| `PE1` | `5` | `49.0001.0000.0000.0005.00` |
| `PE2` | `6` | `49.0001.0000.0000.0006.00` |
| `PE3` | `7` | `49.0001.0000.0000.0007.00` |
| `RR` | `8` | `49.0001.0000.0000.0008.00` |

Example:

```text
Node:
P4

Node ID:
4

IS-IS System ID:
0000.0000.0004

Complete NET:
49.0001.0000.0000.0004.00
```

This makes database inspection and troubleshooting immediately recognizable.

---

# IS-IS Participation Model

Provider infrastructure link purposes are classified as:

```text
core
provider
control
```

These links are eligible for the provider IS-IS foundation.

Customer links use:

```text
customer
```

and are excluded from provider IS-IS.

Conceptually:

```text
P / PE / RR Infrastructure
            |
    +-------+-------+
    |       |       |
   core  provider control
    |       |       |
    +-------+-------+
            |
            v
          IS-IS
          BFD
        SR-MPLS
          FRR


CE-facing Infrastructure
            |
         customer
            |
            v
      Service-specific
       configuration
```

This prevents customer-facing interfaces from accidentally becoming part of the Service Provider IGP.

---

# IGP Advertisement Model

The generated provider foundation uses:

```text
advertise passive-only
```

The stable provider loopbacks are the primary advertised infrastructure identities.

Physical `/31` and `/127` links remain necessary for:

- IS-IS adjacency formation;
- link-local forwarding;
- BFD;
- interface troubleshooting;
- metric calculation;
- SR-MPLS transport;
- failure detection;
- failure injection.

However, the transit point-to-point prefixes are not intended to become the primary provider routing identities.

This keeps the IGP focused on stable node reachability.

---

# Segment Routing MPLS Identifier Model

The generated provider foundation uses the following Segment Routing Global Block:

```text
16000-23999
```

The SRGB provides deterministic label interpretation when Prefix-SIDs are expressed as indices.

---

## IPv4 Prefix-SID Allocation

The IPv4 Prefix-SID index directly matches the provider Node ID.

| Node | IPv4 Loopback | Prefix-SID Index | Expected Label with SRGB 16000 |
| --- | --- | ---: | ---: |
| `P1` | `10.70.0.1/32` | `1` | `16001` |
| `P2` | `10.70.0.2/32` | `2` | `16002` |
| `P3` | `10.70.0.3/32` | `3` | `16003` |
| `P4` | `10.70.0.4/32` | `4` | `16004` |
| `PE1` | `10.70.0.5/32` | `5` | `16005` |
| `PE2` | `10.70.0.6/32` | `6` | `16006` |
| `PE3` | `10.70.0.7/32` | `7` | `16007` |
| `RR` | `10.70.0.8/32` | `8` | `16008` |

---

## IPv6 Prefix-SID Allocation

IPv6 Prefix-SID indices use the following formula:

```text
IPv6 Prefix-SID Index = 600 + Node ID
```

This produces indices `601-608`.

| Node | IPv6 Loopback | Prefix-SID Index | Expected Label with SRGB 16000 |
| --- | --- | ---: | ---: |
| `P1` | `2001:db8:570:abcd::1/128` | `601` | `16601` |
| `P2` | `2001:db8:570:abcd::2/128` | `602` | `16602` |
| `P3` | `2001:db8:570:abcd::3/128` | `603` | `16603` |
| `P4` | `2001:db8:570:abcd::4/128` | `604` | `16604` |
| `PE1` | `2001:db8:570:abcd::5/128` | `605` | `16605` |
| `PE2` | `2001:db8:570:abcd::6/128` | `606` | `16606` |
| `PE3` | `2001:db8:570:abcd::7/128` | `607` | `16607` |
| `RR` | `2001:db8:570:abcd::8/128` | `608` | `16608` |

---

# Infrastructure Identifier Correlation

The complete provider identity model can be summarized as follows.

| Node | ID | IPv4 Lo0 | IPv6 Lo0 | IS-IS System ID | IPv4 SID | IPv6 SID |
| --- | ---: | --- | --- | --- | ---: | ---: |
| `P1` | `1` | `10.70.0.1/32` | `2001:db8:570:abcd::1/128` | `0000.0000.0001` | `1` | `601` |
| `P2` | `2` | `10.70.0.2/32` | `2001:db8:570:abcd::2/128` | `0000.0000.0002` | `2` | `602` |
| `P3` | `3` | `10.70.0.3/32` | `2001:db8:570:abcd::3/128` | `0000.0000.0003` | `3` | `603` |
| `P4` | `4` | `10.70.0.4/32` | `2001:db8:570:abcd::4/128` | `0000.0000.0004` | `4` | `604` |
| `PE1` | `5` | `10.70.0.5/32` | `2001:db8:570:abcd::5/128` | `0000.0000.0005` | `5` | `605` |
| `PE2` | `6` | `10.70.0.6/32` | `2001:db8:570:abcd::6/128` | `0000.0000.0006` | `6` | `606` |
| `PE3` | `7` | `10.70.0.7/32` | `2001:db8:570:abcd::7/128` | `0000.0000.0007` | `7` | `607` |
| `RR` | `8` | `10.70.0.8/32` | `2001:db8:570:abcd::8/128` | `0000.0000.0008` | `8` | `608` |

The identity system is deliberately predictable.

For example:

```text
PE3
 |
 +-- Node ID: 7
 |
 +-- IPv4 Lo0: 10.70.0.7/32
 |
 +-- IPv6 Lo0: 2001:db8:570:abcd::7/128
 |
 +-- IS-IS System ID: 0000.0000.0007
 |
 +-- IPv4 Prefix-SID: 7
 |
 +-- IPv6 Prefix-SID: 607
```

A single logical identifier therefore makes it possible to correlate the node across multiple protocols.

---

# Addressing Validation

The repository includes a permanent addressing validator:

```text
tools/validate_xrd_eight_addressing.py
```

Run it with:

```bash
python3 tools/validate_xrd_eight_addressing.py
```

The validator verifies:

- expected physical links;
- IPv4 `/31` prefix length;
- IPv6 `/127` prefix length;
- IPv4 endpoint subnet membership;
- IPv6 endpoint subnet membership;
- duplicate IPv4 addresses;
- duplicate IPv6 addresses;
- overlapping IPv4 point-to-point networks;
- overlapping IPv6 point-to-point networks;
- IPv4 `/32` provider loopbacks;
- IPv6 `/128` provider loopbacks;
- duplicate loopback identities;
- loopback/link overlap.

The current XRd Eight v2 addressing plan validates as:

```text
ADDRESSING VALIDATION: PASSED

Links validated        : 19
IPv4 /31 networks      : 19
IPv6 /127 networks     : 19
IPv4 endpoint addresses: 38
IPv6 endpoint addresses: 38
IPv4 loopbacks         : 8
IPv6 loopbacks         : 8
Overlapping networks   : 0
Duplicate addresses    : 0
```

The static model therefore contains:

| Resource | Validated Quantity |
| --- | ---: |
| Physical links | `19` |
| IPv4 `/31` networks | `19` |
| IPv6 `/127` networks | `19` |
| IPv4 P2P endpoints | `38` |
| IPv6 P2P endpoints | `38` |
| Provider IPv4 loopbacks | `8` |
| Provider IPv6 loopbacks | `8` |
| Address overlaps | `0` |
| Duplicate addresses | `0` |

---

# Deterministic Build Validation

Addressing correctness is only one part of repository consistency.

The generated artifacts must also remain deterministic.

Regenerate the profile with:

```bash
python3 tools/build_xrd_eight.py
```

The expected generation summary is:

```text
Generated topology: topology/ccie-sp-xrd-eight.clab.yml
Generated ISP configs: 8
Generated CE configs: 3
Generated links: 19
Repository profile: profiles/xrd-eight
```

After an unchanged rebuild:

```bash
git status --short
```

should produce no unexpected modifications.

Generated CSV files use explicit LF line endings so rebuilding the profile does not create false Git modifications caused only by CRLF/LF conversion.

This allows a clean repository state to represent a genuinely deterministic build.

---

# Addressing Acceptance Boundary

Static validation proves that the repository addressing model is internally consistent.

It does **not** by itself prove that the deployed network is operational.

The complete validation chain is:

```text
Source-of-Truth Addressing
           |
           v
Configuration Generation
           |
           v
Static Address Validation
           |
           v
Containerlab Deployment
           |
           v
Physical Interface Validation
           |
           v
IPv4 / IPv6 Link Reachability
           |
           v
IS-IS Adjacency Validation
           |
           v
Loopback Reachability
           |
           v
SR-MPLS / Prefix-SID Validation
           |
           v
BGP Control-Plane Validation
           |
           v
Service Validation
```

This distinction prevents configuration-generation success from being confused with actual runtime protocol acceptance.

---

# Runtime Addressing Validation Targets

After deployment, the addressing layer should be validated against the following expectations.

| Validation Area | Expected State |
| --- | --- |
| Management nodes | `12/12` present |
| XRd provider nodes | `8/8` |
| IOL-XE customer nodes | `3/3` |
| Automation nodes | `1/1` |
| Physical links | `19/19` |
| Physical endpoints | `38/38` |
| IPv4 P2P networks | `19/19` |
| IPv6 P2P networks | `19/19` |
| Provider IPv4 loopbacks | `8/8` |
| Provider IPv6 loopbacks | `8/8` |
| Duplicate addresses | None |
| Overlapping networks | None |
| Provider IS-IS membership | Core/provider/control links only |
| Customer IS-IS membership | None |
| Prefix-SID identities | Unique and deterministic |

Protocol-specific runtime validation remains separate from static addressing validation.

---

# Expansion Policy

XRd Eight v2 is designed to permit incremental physical expansion without renumbering existing links.

The next currently unused allocations are:

```text
IPv4:
10.20.0.38/31
```

```text
IPv6:
2001:db8:2000:120::/127
```

A future twentieth physical link should normally consume these networks.

The preferred allocation policy is:

```text
Existing Link
     |
     +-- Address remains unchanged


New Physical Link
     |
     +-- Consume next available /31
     |
     +-- Consume next available /127
```

Existing addresses should only be changed when there is an explicit architectural reason to renumber the topology.

---

# Service Addressing Boundary

The current addressing plan defines the physical and provider infrastructure substrate.

It intentionally does not pre-allocate every future service prefix.

Service-specific addressing remains available for exercises involving:

- customer VRF loopbacks;
- L3VPN customer prefixes;
- VPNv6;
- PE-CE routing;
- L2VPN attachment circuits;
- VPWS;
- VPLS;
- EVPN bridge domains;
- EVPN Ethernet Segments;
- EVPN IRB;
- BGP-LU;
- BGP-LS;
- multicast sources and receivers;
- PCE/PCC;
- Segment Routing Policy endpoints;
- SRv6 locators;
- QoS traffic generators;
- Inter-AS scenarios.

This separation allows the same physical topology to support multiple independent study scenarios without modifying the provider infrastructure addressing foundation.

---

# Addressing Summary

| Component | Quantity / Allocation |
| --- | --- |
| Total nodes | `12` |
| XRd provider/control nodes | `8` |
| IOL-XE customer nodes | `3` |
| Automation nodes | `1` |
| Management network | `10.207.255.0/24` |
| Physical links | `19` |
| IPv4 P2P networks | `19 x /31` |
| IPv6 P2P networks | `19 x /127` |
| IPv4 physical endpoints | `38` |
| IPv6 physical endpoints | `38` |
| Provider IPv4 loopbacks | `8 x /32` |
| Provider IPv6 loopbacks | `8 x /128` |
| IS-IS process | `500-SP` |
| IS-IS level | Level 2 only |
| IS-IS area | `49.0001` |
| SRGB | `16000-23999` |
| IPv4 Prefix-SID indices | `1-8` |
| IPv6 Prefix-SID indices | `601-608` |
| Address overlaps | `0` |
| Duplicate addresses | `0` |
| Next IPv4 P2P allocation | `10.20.0.38/31` |
| Next IPv6 P2P allocation | `2001:db8:2000:120::/127` |

---

# Design Intent

The addressing plan is not simply an IP allocation table.

It is part of the reproducibility model of XRd Eight v2.

The infrastructure follows a deterministic relationship:

```text
Physical Topology
       |
       v
Stable Node ID
       |
       +----------------------+
       |                      |
       v                      v
Provider Loopback      IS-IS System ID
       |                      |
       +----------+-----------+
                  |
                  v
          Segment Routing SID
                  |
                  v
       Deterministic Generation
                  |
                  v
          Static Validation
                  |
                  v
          Runtime Validation
```

Every provider node can therefore be identified predictably before the topology starts.

Every physical link has a known IPv4 and IPv6 allocation.

Every IS-IS system identifier can be correlated with its router.

Every Segment Routing Prefix-SID can be correlated with the same Node ID.

Every future rebuild should reproduce the same addressing model unless the source-of-truth inventory is intentionally changed.

The objective is to maintain a Service Provider lab where the infrastructure addressing is **predictable, dual-stack, automation-friendly and operationally traceable**, providing a stable substrate for the higher layers of the XRd Eight v2 study environment.
















