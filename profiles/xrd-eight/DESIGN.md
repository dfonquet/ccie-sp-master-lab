


# XRd Eight v2 — Architecture and Design


![Authoritative XRd Eight topology](topology.svg)


> **Compact full-dataplane Service Provider architecture designed for advanced routing, Segment Routing, VPN, EVPN, convergence and NetDevOps practice.**
>
> XRd Eight v2 concentrates a broad set of Service Provider design and forwarding-plane scenarios into a deterministic 12-node topology built around eight Cisco XRd vRouter instances, three IOL-XE customer routers and one dedicated Linux automation node.

The objective of XRd Eight v2 is not to reproduce the largest possible Service Provider topology.

The objective is to build the **smallest topology that still provides meaningful architectural redundancy, path diversity, customer multihoming and real forwarding-plane behavior**, while remaining practical for repeated deployment on the measured local virtualization host.

The design therefore favors:

- forwarding-plane capability over raw node count;
- path diversity over linear topology size;
- deterministic infrastructure over manually maintained runtime state;
- reusable customer attachment models over single-purpose service layouts;
- realistic failure domains over cosmetic topology complexity;
- infrastructure automation without automating away the study objectives.

---

## Design Objective

XRd Eight v2 was created to provide a compact but technically dense Service Provider environment for advanced study.

The topology concentrates the infrastructure required for:

- IS-IS Level 2;
- dual-stack IPv4/IPv6 transport;
- Segment Routing MPLS;
- BFD;
- fast reroute;
- ECMP;
- convergence analysis;
- BGP Route Reflection;
- VPNv4 and VPNv6;
- L3VPN;
- L2VPN;
- VPWS;
- VPLS;
- EVPN;
- EVPN multihoming;
- Segment Routing Policies;
- PCE/PCC;
- multicast;
- QoS;
- RPKI;
- telemetry;
- NetDevOps automation.

The topology provides the **physical and transport foundation** for these technologies without preconfiguring all of them.

That separation is deliberate.

The repository should automate repetitive infrastructure construction while preserving the configuration, design, validation and troubleshooting work required from the engineer.

---

## Design Philosophy

XRd Eight v2 follows several core principles.

| Principle | Design Decision |
| --- | --- |
| Real dataplane behavior | Provider nodes use XRd vRouter rather than control-plane-only XRd |
| Compact topology | Eight XRd provider/control nodes |
| High path diversity | Four-node fully connected P core |
| PE redundancy | Every PE attaches to two independent P routers |
| Control-plane redundancy | RR attaches to two independent P routers |
| Customer diversity | Single-homed and dual-homed CE designs coexist |
| Dual-stack foundation | IPv4 and IPv6 are present from the beginning |
| Deterministic infrastructure | Topology and addressing are generated from repository data |
| Service-layer flexibility | BGP/VPN/EVPN/etc. remain study work |
| Automation-ready | Dedicated `AUTO1` Linux node |
| Reproducibility | Build, validate, deploy and destroy workflows are version controlled |

The design can be summarized as:

```text
Deterministic Infrastructure
            |
            v
      Dual-Stack IGP
            |
            v
         SR-MPLS
            |
            v
       BGP Control Plane
            |
            v
     VPN / EVPN Services
            |
            v
      Failure Scenarios
            |
            v
        Automation
```

---

# Architecture Overview

XRd Eight v2 contains twelve nodes.

| Function | Nodes | Quantity | Platform |
| --- | --- | ---: | --- |
| Provider Core | `P1`, `P2`, `P3`, `P4` | `4` | XRd vRouter 26.2.1 |
| Provider Edge | `PE1`, `PE2`, `PE3` | `3` | XRd vRouter 26.2.1 |
| Control Plane | `RR` | `1` | XRd vRouter 26.2.1 |
| Customer Edge | `CE1`, `CE2`, `CE3` | `3` | IOL-XE 17.12.1 |
| Automation / Operations | `AUTO1` | `1` | Local Linux image |
| **Total** |  | **12** |  |

The provider infrastructure therefore consists of:

```text
4 P routers
3 PE routers
1 RR
----------------
8 XRd vRouters
```

The customer and operational layer adds:

```text
3 IOL-XE CE routers
1 Linux automation node
------------------------
4 additional containers
```

Total:

```text
8 XRd + 3 IOL-XE + 1 AUTO1 = 12 containers
```

---

# Physical Topology

The topology contains **19 physical links**.

They are divided into four functional groups.

| Link Type | Quantity |
| --- | ---: |
| Provider Core | `6` |
| Provider Edge | `6` |
| Control Plane | `2` |
| Customer Edge | `5` |
| **Total** | **19** |

Conceptually:

```text
                           +------+
                           |  RR  |
                           +--+---+
                             / \
                            /   \
                           /     \
                         P1-------P4
                        /|\       /|\
                       / | \     / | \
                      /  |  \   /  |  \
                    P2---+---P3   |   \
                     \         \   |    \
                      \         \  |     \
                       PE2       PE1     PE3
                      / | \       \       /
                     /  |  \       \     /
                   CE1 CE2 CE3      \   /
                    \       /        \ /
                     +-----+----------
```

The exact physical topology is defined in:

```text
topology/ccie-sp-xrd-eight.clab.yml
```

and the authoritative link inventory is maintained under:

```text
profiles/xrd-eight/
```

---

# Provider Core Design

The provider core consists of four routers:

```text
P1
P2
P3
P4
```

These four routers form a **complete graph**.

Every P router connects directly to every other P router.

The six core links are:

```text
P1-P2
P1-P3
P1-P4
P2-P3
P2-P4
P3-P4
```

A four-node complete graph was chosen instead of a ring or simple square because it provides significantly greater path diversity without increasing the XRd node count.

The core therefore provides multiple alternate paths between any two provider nodes.

This makes the topology suitable for exercises involving:

- ECMP;
- IS-IS metric manipulation;
- shortest-path changes;
- Segment Routing path selection;
- LFA;
- TI-LFA testing;
- link protection;
- node protection;
- BFD;
- SRLG concepts;
- failure convergence;
- SR Policy;
- explicit path construction;
- traffic-engineering experiments.

---

## Why a Complete P Graph?

A simple four-router ring would provide redundancy, but most source/destination pairs would have limited alternate-path diversity.

The complete graph introduces six internal links:

```text
       P1
     / | \
    /  |  \
  P2---+---P4
    \  |  /
     \ | /
       P3
```

Each P router has direct connectivity to the other three P routers.

This permits:

- direct shortest paths;
- multiple alternative paths;
- equal-cost paths;
- unequal-cost paths after metric manipulation;
- meaningful fast-reroute calculations;
- more interesting SR Policy segment lists;
- failure testing without immediately partitioning the topology.

The intent is to obtain maximum study value from only four P routers.

---

# Provider Edge Design

The topology contains three Provider Edge routers:

```text
PE1
PE2
PE3
```

Each PE attaches to **two different P routers**.

| PE | Core Attachment 1 | Core Attachment 2 |
| --- | --- | --- |
| `PE1` | `P1` | `P3` |
| `PE2` | `P2` | `P4` |
| `PE3` | `P1` | `P4` |

This produces the following six provider-facing links:

```text
PE1-P1
PE1-P3

PE2-P2
PE2-P4

PE3-P1
PE3-P4
```

No Provider Edge router depends on a single core router.

This creates independent failure domains between the service edge and the provider core.

---

## PE Redundancy Objective

The dual-homed PE design enables exercises involving:

- core-link failure;
- P-router failure;
- ECMP;
- IS-IS reconvergence;
- BFD;
- fast reroute;
- Segment Routing path changes;
- BGP next-hop reachability;
- service continuity;
- VPN forwarding convergence;
- EVPN convergence;
- customer-service impact analysis.

For example, `PE1` normally has transport connectivity through both:

```text
PE1 -> P1
PE1 -> P3
```

A failure of `P1` therefore does not physically isolate `PE1`.

The same principle applies to all Provider Edge routers.

---

# Control-Plane Design

The dedicated control-plane node is:

```text
RR
```

Its physical attachments are:

```text
RR-P1
RR-P4
```

The node therefore has independent paths into the core.

| Node | Attachment 1 | Attachment 2 |
| --- | --- | --- |
| `RR` | `P1` | `P4` |

The initial role of this router is deliberately limited to infrastructure participation.

The repository does not preconfigure every possible control-plane function.

---

## Future RR Roles

The `RR` node can later be used for scenarios involving:

- IPv4 Route Reflection;
- IPv6 Route Reflection;
- VPNv4 Route Reflection;
- VPNv6 Route Reflection;
- EVPN Route Reflection;
- BGP-LS;
- PCE;
- PCEP;
- SR Policy;
- centralized policy functions;
- multicast control-plane experiments.

Depending on the exercise, the same router can also be used as a candidate for:

- stateful PCE;
- stateless PCE;
- BGP-LS collector;
- multicast RP;
- control-plane telemetry source.

These functions are intentionally not hard-coded into the generated foundation.

The topology provides the **connectivity required to build them manually or through reviewed automation**.

---

# Node Attachment Matrix

The current XRd Eight v2 infrastructure is summarized below.

| Node | Role | Physical Attachments |
| --- | --- | --- |
| `P1` | Provider Core | `P2`, `P3`, `P4`, `PE1`, `PE3`, `RR` |
| `P2` | Provider Core | `P1`, `P3`, `P4`, `PE2` |
| `P3` | Provider Core | `P1`, `P2`, `P4`, `PE1` |
| `P4` | Provider Core | `P1`, `P2`, `P3`, `PE2`, `PE3`, `RR` |
| `PE1` | Provider Edge | `P1`, `P3`, `CE1` |
| `PE2` | Provider Edge | `P2`, `P4`, `CE1`, `CE2`, `CE3` |
| `PE3` | Provider Edge | `P1`, `P4`, `CE3` |
| `RR` | Control Plane | `P1`, `P4` |
| `CE1` | Customer Edge | `PE1`, `PE2` |
| `CE2` | Customer Edge | `PE2` |
| `CE3` | Customer Edge | `PE3`, `PE2` |
| `AUTO1` | Automation | Management network only |

This matrix is intentionally asymmetric at the customer edge.

That asymmetry creates different service scenarios without increasing the CE count.

---

# Customer Edge Design

The customer topology contains three CE routers.

They do not all use the same connectivity model.

This is intentional.

---

## CE1 — Dual-Homed Customer

`CE1` connects to:

```text
PE1
PE2
```

Physical topology:

```text
PE1 ----- CE1 ----- PE2
```

This provides a dual-PE customer scenario.

Potential uses include:

- dual-homed L3VPN;
- eBGP multihoming;
- Site-of-Origin;
- redundant PE-CE routing;
- EVPN multihoming;
- Ethernet Segment Identifier;
- DF election;
- all-active mode;
- single-active mode;
- aliasing;
- mass withdrawal.

---

## CE2 — Single-Homed Baseline

`CE2` connects only to:

```text
PE2
```

Physical topology:

```text
PE2 ----- CE2
```

CE2 provides a deliberately simple baseline.

It can be used for:

- basic L3VPN;
- basic eBGP PE-CE;
- static PE-CE routing;
- OSPF PE-CE;
- simple VPWS;
- simple EVPN service;
- service migration testing.

The single-homed topology makes it useful as a control case when comparing behavior with CE1 and CE3.

---

## CE3 — Second Dual-Homed Customer

`CE3` connects to:

```text
PE3
PE2
```

Physical topology:

```text
PE3 ----- CE3 ----- PE2
```

CE3 creates a second independent multihoming domain.

Having two dual-homed customers allows the lab to support more complex EVPN scenarios without rebuilding physical connectivity.

Potential exercises include:

- multiple Ethernet Segments;
- independent ESI values;
- DF election across multiple segments;
- different redundancy modes;
- multiple bridge domains;
- PE failure impact across different customers.

---

# EVPN Multihoming Readiness

The current physical topology provides true multi-PE attachment for two customers.

```text
CE1
 +-- PE1
 +-- PE2

CE3
 +-- PE3
 +-- PE2
```

This is fundamentally different from attaching two CE interfaces to the same PE.

Because the CE nodes connect to **different Provider Edge routers**, the physical topology is suitable for real EVPN multihoming exercises.

The design can therefore support later work involving:

- Ethernet Segment routes;
- ESI;
- DF election;
- split horizon;
- all-active forwarding;
- single-active forwarding;
- aliasing;
- mass withdrawal;
- MAC mobility;
- PE failure;
- CE link failure.

No EVPN multihoming configuration is generated automatically by the foundation.

---

# Why XRd vRouter 26.2.1

The provider infrastructure uses:

```text
vrnetlab/cisco_xrd-vrouter:26.2.1
```

XRd vRouter was selected because this profile requires forwarding-plane behavior.

A control-plane-only environment is extremely useful for large topology scaling and routing-protocol experimentation, but some study scenarios require actual packet forwarding.

Examples include:

- MPLS label imposition;
- MPLS label swapping;
- MPLS disposition;
- SR-MPLS forwarding;
- VPN dataplane verification;
- EVPN dataplane validation;
- multicast forwarding;
- traffic-engineering experiments;
- convergence observation;
- packet-level failure testing.

The vRouter variant therefore provides functionality that a control-plane-only topology cannot fully reproduce.

---

## Local Image Validation

Before inclusion in the topology, the XRd image was locally validated as part of the lab build workflow.

The image verification process included Cisco-supplied image verification material before the image was wrapped for Containerlab use.

The local vrnetlab implementation uses:

```text
XRD_NIC_TYPE=igb
```

because the `igb` interface model was previously validated against the local XRd dataplane environment.

The topology therefore defines:

```yaml
cisco_xrd_vrouter:
  image: vrnetlab/cisco_xrd-vrouter:26.2.1
  env:
    XRD_NIC_TYPE: igb
```

---

# Why IOL-XE for Customer Routers

Customer Edge routers use:

```text
vrnetlab/cisco_iol:17.12.01
```

The CE role generally does not require the same dataplane resource profile as the provider infrastructure.

Using IOL-XE for CE nodes provides a more resource-efficient way to emulate:

- eBGP PE-CE;
- OSPF PE-CE;
- static routing;
- customer VLANs;
- subinterfaces;
- customer redundancy;
- L2 service attachment;
- failure scenarios.

This allows available compute resources to remain concentrated on the eight XRd vRouter provider nodes.

---

# AUTO1 Design

`AUTO1` provides a dedicated Linux operations and automation environment.

Management address:

```text
10.207.255.150
```

Its intended responsibilities include:

- Ansible;
- Python;
- Netmiko;
- NETCONF;
- `ncclient`;
- YANG;
- configuration generation;
- pre-checks;
- post-checks;
- configuration backup;
- evidence collection;
- state validation;
- failure-validation workflows.

AUTO1 remains logically outside the provider forwarding topology.

It reaches infrastructure devices through the management network.

This separation allows automation workflows to continue even when the provider data plane is intentionally broken.

---

# Infrastructure Foundation

The repository generates only the baseline required to make the provider topology deterministic.

Generated infrastructure includes:

- XRd hostnames;
- management assignments;
- provider loopbacks;
- IPv4 point-to-point addressing;
- IPv6 point-to-point addressing;
- IS-IS Level 2 foundation;
- IS-IS NET allocation;
- IPv4 Prefix-SIDs;
- IPv6 Prefix-SIDs;
- SRGB;
- BFD intent;
- per-prefix fast-reroute foundation;
- topology definition;
- node inventory;
- link inventory.

CE startup configurations remain intentionally minimal.

---

# IS-IS Design

The generated provider IGP uses:

```text
router isis 500-SP
```

with:

```text
is-type level-2-only
```

Area:

```text
49.0001
```

The infrastructure is dual-stack.

IPv4 and IPv6 participate in the same provider topology, with IPv6 configured using single-topology behavior.

The foundation includes:

- wide metrics;
- point-to-point circuits;
- BFD;
- IPv4 unicast;
- IPv6 unicast;
- SR-MPLS;
- passive Loopback0;
- per-prefix fast-reroute.

---

## Transit Prefix Advertisement

The generated design intentionally uses:

```text
advertise passive-only
```

The stable provider loopbacks are therefore the primary infrastructure prefixes advertised through IS-IS.

Transit `/31` and `/127` addresses remain available for:

- adjacency establishment;
- BFD;
- forwarding;
- troubleshooting;
- metric calculation;
- failure testing.

The intent is to keep the IGP routing model focused on stable provider identities rather than every physical transit prefix.

---

# Segment Routing Design

SR-MPLS is part of the generated transport foundation.

The configured SRGB is:

```text
16000-23999
```

IPv4 Prefix-SID indices use:

```text
1-8
```

matching the provider Node IDs.

IPv6 Prefix-SID indices use:

```text
601-608
```

The deterministic relationship is:

```text
Node ID N

IPv4 Prefix-SID = N
IPv6 Prefix-SID = 600 + N
```

This creates a predictable SID model for troubleshooting.

Example:

```text
PE3

Node ID:          7
IPv4 Prefix-SID:  7
IPv6 Prefix-SID: 607
```

---

# Fast-Reroute Design

The generated infrastructure currently provides:

```text
fast-reroute per-prefix
```

on provider infrastructure address families.

The topology is designed to later support advanced convergence exercises involving:

- LFA;
- TI-LFA;
- link protection;
- node protection;
- BFD;
- metric manipulation;
- SRLG-aware scenarios.

TI-LFA is deliberately not treated as an assumed baseline command.

Its syntax and behavior should first be validated against the active XRd 26.2.1 software before being promoted into the generated foundation.

---

# Study Boundary

XRd Eight v2 provides the infrastructure required for advanced Service Provider studies.

It deliberately does **not** solve the complete protocol stack automatically.

The following remain student or automation exercises.

---

## BGP

Not automatically configured:

- IPv4 iBGP;
- IPv6 iBGP;
- Route Reflection;
- next-hop policies;
- route policies;
- BGP-LS;
- BGP-LU.

---

## MPLS VPN

Not automatically configured:

- VPNv4;
- VPNv6;
- VRFs;
- route distinguishers;
- route targets;
- PE-CE routing;
- inter-VRF policy.

---

## L2VPN

Not automatically configured:

- VPWS;
- VPLS;
- bridge domains;
- attachment circuits;
- pseudowires.

---

## EVPN

Not automatically configured:

- EVPN address family;
- EVPN route reflection;
- EVI;
- bridge domains;
- EVPN VPWS;
- EVPN multihoming;
- ESI;
- DF election;
- all-active mode;
- single-active mode;
- aliasing;
- mass withdrawal.

---

## Segment Routing Policy and PCE

Not automatically configured:

- PCEP;
- PCC;
- stateful PCE;
- stateless PCE;
- candidate paths;
- explicit segment lists;
- affinity constraints;
- disjointness;
- SR Policy steering.

---

## Multicast

Not automatically configured:

- PIM;
- RP;
- BSR;
- Anycast RP;
- mLDP;
- Tree-SID;
- mVPN.

---

## SRv6

Not automatically configured:

- locators;
- SIDs;
- endpoint behaviors;
- SRv6 policies;
- service SIDs.

---

## Security and Operations

Not automatically configured:

- centralized AAA;
- TACACS+;
- RADIUS;
- RPKI origin validation;
- telemetry collectors;
- QoS;
- performance scoring.

These technologies should be introduced manually or through reviewed `AUTO1` automation workflows one phase at a time.

---

# Study Progression

The intended progression is:

```text
01. Physical topology
        |
        v
02. Dual-stack addressing
        |
        v
03. IS-IS
        |
        v
04. SR-MPLS
        |
        v
05. Convergence / FRR
        |
        v
06. BGP / Route Reflection
        |
        v
07. L3VPN / L2VPN
        |
        v
08. EVPN
        |
        v
09. EVPN Multihoming
        |
        v
10. SR Policy / PCE
        |
        v
11. Multicast / QoS
        |
        v
12. Automation and Failure Validation
```

The physical topology should remain stable while higher protocol layers are rebuilt repeatedly.

---

# Failure-Domain Design

The topology intentionally supports several independent failure scenarios.

## Core Link Failure

Any single P-to-P core link can be removed while alternative paths remain available.

Example:

```text
P1-P4 failure
```

The remaining core still contains:

```text
P1-P2-P4
P1-P3-P4
```

among other alternatives.

---

## Core Node Failure

The dense P topology allows individual core-router failures to be tested without immediately destroying all provider reachability.

Examples:

```text
P1 failure
P2 failure
P3 failure
P4 failure
```

Impact can be evaluated against:

- IS-IS convergence;
- Prefix-SID reachability;
- MPLS forwarding;
- BGP sessions;
- VPN services;
- EVPN services.

---

## PE Uplink Failure

Every PE has two core attachments.

Example:

```text
PE1-P1 failure
```

`PE1` remains attached through:

```text
PE1-P3
```

This permits realistic edge-convergence testing.

---

## RR Uplink Failure

`RR` attaches to both:

```text
P1
P4
```

Loss of one transport link does not physically isolate the Route Reflector.

---

## Customer Access Failure

Dual-homed customers provide failure cases such as:

```text
CE1-PE1 failure
CE1-PE2 failure

CE3-PE3 failure
CE3-PE2 failure
```

These are useful for later EVPN multihoming and dual-PE service convergence validation.

---

# Runtime Envelope

The eight-XRd design was selected based on actual runtime observations on the local Ubuntu virtualization host.

A full 12-container test successfully operated:

- eight XRd vRouter nodes;
- three IOL-XE CE nodes;
- one AUTO1 Linux node.

Measured results from the validated runtime are summarized below.

| Measurement | Observed Result |
| --- | ---: |
| XRd vRouter nodes | `8` |
| IOL-XE nodes | `3` |
| Automation nodes | `1` |
| Total containers | `12` |
| VM allocation during measurement | `16 vCPU / 86 GiB RAM` |
| RAM used after deployment | approximately `70 GiB` |
| RAM remaining available | approximately `16 GiB` |
| Swap usage | `0 B` |
| XRd restart count | `0` |
| XRd OOM state | `false` |
| Full CPU stall pressure | `0` |

The observed runtime demonstrates that the complete topology can operate within the measured host envelope without swap or OOM events.

---

# Runtime Acceptance Boundary

The previous runtime test validates the **platform capacity and ability to operate eight XRd vRouter instances simultaneously**.

It does not automatically validate every current v2 protocol command.

The acceptance model separates:

```text
Host Capacity
     |
     v
Container Runtime
     |
     v
Physical Topology
     |
     v
Generated Configuration
     |
     v
IGP Runtime
     |
     v
SR-MPLS Runtime
     |
     v
BGP / Service Runtime
```

Each layer should be validated independently.

---

# Resource Ceiling

Eight XRd vRouter nodes represent the normal full-dataplane ceiling for this profile on the measured VM configuration.

The design therefore uses the available XRd capacity for:

```text
P1
P2
P3
P4
PE1
PE2
PE3
RR
```

instead of allocating additional XRd instances to customer roles.

IOL-XE and Linux containers provide more economical CE and operations functions.

---

## Operational Resource Rule

Do not add another XRd node to the profile without performing a new resource-capacity test.

The current architecture assumes:

```text
8 XRd vRouters = validated full-dataplane provider footprint
```

Increasing this number may cause:

- memory exhaustion;
- OOM events;
- startup instability;
- excessive CPU contention;
- longer convergence times;
- unreliable dataplane behavior.

---

# Concurrent Lab Policy

XRd Eight v2 is a resource-intensive full-dataplane environment.

Another large dataplane profile should not be started concurrently on the same VM.

Before starting another heavy topology, destroy XRd Eight:

```bash
./profiles/xrd-eight/labctl destroy
```

The lifecycle wrapper uses Containerlab cleanup behavior to remove stale runtime artifacts.

Heavy profiles should therefore be treated as mutually exclusive workloads.

Examples include:

```text
XRd Eight
Master
Inter-AS
SRv6
Full Dataplane
JNCIE-SP
```

The preferred operational model is:

```text
Deploy one heavy lab
        |
        v
Perform study / validation
        |
        v
Collect evidence / backups
        |
        v
Destroy lab with cleanup
        |
        v
Deploy next heavy profile
```

---

# Why Not Add More XRd Nodes?

More nodes do not automatically produce a better study topology.

The important question is whether another node introduces a meaningful new failure domain, control-plane role or service scenario.

XRd Eight already provides:

- four fully meshed P routers;
- three dual-attached PE routers;
- one dual-attached control-plane router;
- two dual-homed customer sites;
- one single-homed customer baseline;
- nineteen physical links;
- multiple independent failure paths.

The marginal study value of another XRd router is therefore lower than the additional compute cost.

The current design intentionally spends compute resources on **dataplane fidelity rather than node count**.

---

# Why This Topology Is Compact but Not Simple

XRd Eight contains only eight provider/control-plane XRd nodes, but the topology is intentionally dense.

The core alone provides:

```text
4 nodes
6 physical links
```

Provider edge adds:

```text
3 nodes
6 provider uplinks
```

Control plane adds:

```text
1 node
2 transport links
```

Customer connectivity adds:

```text
3 CE nodes
5 customer-facing links
```

The topology therefore contains enough physical diversity to support realistic design and troubleshooting scenarios while remaining computationally manageable.

---

# Design vs Configuration

The physical topology represents an architectural framework.

It does not dictate a single final configuration.

For example, the same topology can be used for:

```text
Scenario A
IS-IS + SR-MPLS + L3VPN

Scenario B
IS-IS + SR-MPLS + EVPN

Scenario C
IS-IS + BGP-LU + VPN

Scenario D
IS-IS + SR Policy + PCE

Scenario E
IS-IS + Multicast + mVPN

Scenario F
Dual-stack Service Provider automation
```

This allows the topology to remain constant while protocol design changes.

---

# Automation Boundary

Automation should make the infrastructure reproducible without removing the need to understand the network.

The repository therefore automatically handles tasks such as:

- topology generation;
- deterministic addressing;
- node identities;
- IS-IS NET allocation;
- Prefix-SID allocation;
- configuration rendering;
- static validation;
- topology rendering.

Higher-layer configuration can then be:

```text
Manual
   or
AUTO1-driven
```

depending on the exercise.

Automation should be introduced in reviewed phases rather than pushing the complete intended network state at once.

---

# Repository Design Workflow

The intended engineering workflow is:

```text
Architecture decision
        |
        v
Repository source-of-truth change
        |
        v
Generate artifacts
        |
        v
Static validation
        |
        v
Git diff / review
        |
        v
CI validation
        |
        v
Pull Request
        |
        v
Merge to main
        |
        v
Runtime deployment
        |
        v
Protocol acceptance
```

The deployed environment should therefore always be traceable to a repository state.

---

# Design Acceptance Criteria

The physical design is considered structurally correct when the repository represents:

| Requirement | Expected State |
| --- | --- |
| P routers | `4` |
| PE routers | `3` |
| Control-plane XRd routers | `1` |
| XRd total | `8` |
| CE routers | `3` |
| Automation nodes | `1` |
| Total nodes | `12` |
| Core links | `6` |
| PE uplinks | `6` |
| RR uplinks | `2` |
| CE links | `5` |
| Total physical links | `19` |
| Dual-homed PE nodes | `3/3` |
| Dual-homed control node | `1/1` |
| Dual-homed customer sites | `2` |
| Single-homed customer sites | `1` |
| Provider links dual-stack | Yes |
| Provider Node IDs deterministic | Yes |

---

# Current Design Summary

XRd Eight v2 provides the following architectural foundation:

```text
                        XRd Eight v2

                  FULL-DATAPLANE SP LAB

                         12 Nodes
                            |
          +-----------------+------------------+
          |                                    |
          v                                    v
     Provider Domain                      Operations
          |                                    |
      8 XRd Nodes                           AUTO1
          |
   +------+-------+
   |              |
   v              v
4 x P           3 x PE
   |
   +-----------> RR

Customer Domain
      |
  3 x IOL-XE
      |
 +----+----+
 |         |
CE1       CE3
dual      dual

     CE2
    single
```

The architecture deliberately combines:

- a dense four-node provider core;
- redundant PE attachments;
- redundant control-plane attachment;
- single-homed and dual-homed customer models;
- native dual-stack infrastructure;
- real XRd forwarding behavior;
- deterministic configuration generation;
- an integrated automation environment.

The result is a topology designed not simply to **run protocols**, but to support the complete engineering cycle:

```text
Design
  ->
Implement
  ->
Validate
  ->
Break
  ->
Observe
  ->
Troubleshoot
  ->
Automate
  ->
Rebuild
```

XRd Eight v2 is therefore intended to function as a reusable **Service Provider engineering platform**, rather than as a single static certification exercise.
