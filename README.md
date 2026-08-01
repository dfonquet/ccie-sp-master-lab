# CCIE SP v5.1 Master Lab

Reproducible 30-node service-provider lab for Cisco CCIE Service Provider
v5.1 practice. It combines a redundant dual-stack ISP backbone, customer
services, Segment Routing and a dedicated automation workstation.

![CCIE SP master topology](docs/topology.svg)

> **Start here:** read the
> [Professional lab operating guide](docs/LAB-OPERATING-GUIDE.md) before
> deploying a profile. It explains the repository, source of truth, profiles,
> addressing, configuration phases, deployment, validation, exercises,
> troubleshooting and safe synchronization from `AUTO1`.

The diagram is generated from the authoritative node and link inventories.
Orange `NEW` markers identify the validated 2026 expansion: P7, P8, PE7 and
PE8, connected through links `L040-L047`.

## Current implementation status

This repository provides three independent, runnable Containerlab profiles. Only one resource-intensive profile should be active at a time.

### 1. Master profile — 30 nodes

- Eight P routers.
- Eight PE routers.
- Two redundant RR/PCE nodes.
- Nine CE routers.
- Two client nodes.
- One AUTO1 automation workstation.
- Expanded links identified as `L040-L047`.

The following foundation has been validated:

- IPv4 and IPv6 addressing.
- Dual-stack IS-IS.
- SR-MPLS.
- Redundant route-reflector control plane.
- Physical and management connectivity.
- Expanded P and PE topology.

### 2. Inter-AS profile — 23 nodes

The Inter-AS profile provides a dual-provider topology designed for:

- Inter-AS Option A.
- Inter-AS Option B.
- Inter-AS Option C.
- eBGP and iBGP.
- MP-BGP address families.
- Route reflection inside each autonomous system.
- Dual-stack provider connectivity.
- Controlled failure and convergence exercises.

Its generated topology, management access, base configuration, addressing plan, and physical connectivity have been validated.

### 3. SRv6 profile — 21 nodes

The full SRv6 study profile contains:

- Six P routers.
- Six PE routers.
- Two route reflectors.
- Six CE routers.
- One AUTO1 automation workstation.
- Thirty-three physical links.

The following foundation has been validated on XRd `24.2.11`:

- Successful deployment of all 21 nodes.
- Management and CLI access to all network nodes.
- Base configuration on P, PE, RR, and CE nodes.
- IPv6 addressing on every provider and customer link.
- All `66/66` directed IPv6 link tests.
- IS-IS adjacencies.
- IPv6 loopback reachability.
- SRv6 locator configuration and advertisement.
- SRv6 platform capabilities and endpoint behaviors.


## Study and implementation boundary

The three profiles provide validated, operational service-provider foundations. Their physical connectivity, management access, deterministic addressing, base configurations, and profile-specific control-plane components have been tested.

The repository intentionally does not provide fully solved configurations for every technology. Instead, it supplies the topology, addressing, automation framework, baseline control plane, and validation tools required to implement and troubleshoot the following technologies as progressive exercises.

### Master profile exercises

- Advanced MP-BGP address families and routing policy.
- MPLS L3VPN and L2VPN services.
- EVPN and EVPN multihoming.
- Multicast routing and multicast VPN services.
- SR-MPLS Traffic Engineering and policy steering.
- Route-reflector and PCE design changes.
- QoS and traffic-management policies.
- Fast convergence, TI-LFA, and failure scenarios.
- AAA, TACACS+, RADIUS, and operational security.
- RPKI and BGP origin validation.
- Automation, configuration compliance, and assurance workflows.

### Inter-AS profile exercises

- Inter-AS Option A.
- Inter-AS Option B.
- Inter-AS Option C.
- eBGP and iBGP policy design.
- MP-BGP route exchange between autonomous systems.
- Route-reflector interaction between provider domains.
- IPv4 and IPv6 inter-provider connectivity.
- Inter-AS L3VPN and labeled-unicast scenarios.
- Routing-policy enforcement and route-leak prevention.
- Failure, convergence, and path-selection exercises.

### SRv6 profile exercises

- SRv6 SID allocation and locator design changes.
- SRv6 Traffic Engineering policies.
- Explicit SRv6 segment lists.
- Dynamic and static binding SIDs.
- SRv6 policy steering.
- SRv6 VPN services.
- SRv6 endpoint behaviors.
- Reduced encapsulation and uSID experimentation.
- SRv6 resiliency and failure scenarios.
- Automation and validation of SRv6 operational state.

### Validated starting point

Students begin from a functional baseline rather than an empty topology. Depending on the selected profile, the validated starting point includes:

- Successful Containerlab deployment.
- Management and CLI reachability.
- Base interface and loopback configuration.
- Deterministic IPv4 and IPv6 addressing.
- Operational physical links.
- Dual-stack IS-IS where required by the profile.
- SR-MPLS foundations in the Master profile.
- Autonomous-system separation in the Inter-AS profile.
- Operational IS-IS and SRv6 locators in the SRv6 profile.
- Backup, validation, and automation utilities through AUTO1.

This boundary keeps the infrastructure reproducible and functional while leaving the advanced service-provider technologies available for configuration, verification, troubleshooting, and redesign by the student.


See [Deployment status](STATUS.md) for the exact acceptance boundary before moving to the next profile.

## What this repository contains

### Lab profiles

The repository provides three isolated and independently operated Containerlab profiles:

- **Master — 30 nodes:** General CCIE Service Provider practice environment with redundant P, PE, RR/PCE, CE, client, and automation roles.
- **Inter-AS — 23 nodes:** Multi-provider environment designed for BGP, routing-policy, route-reflector, labeled-unicast, and Inter-AS Options A, B, and C exercises.
- **SRv6 — 21 nodes:** IPv6-native provider environment with six P routers, six PE routers, two route reflectors, six CE routers, AUTO1, IS-IS, and validated SRv6 locators.

Only one resource-intensive profile should be active at a time.

### Network platforms

- Cisco XRd Control Plane `24.2.11` for provider-core, PE, RR, and PCE roles.
- Cisco IOL-XE `17.12.1` for customer-edge and client roles.
- Linux-based AUTO1 container for automation, validation, and operational workflows.
- Containerlab `0.77.0` for topology orchestration and lifecycle management.

### Topology and configuration generation

- Reproducible topology generation using Python.
- CSV-based node and link sources of truth.
- Deterministic management, loopback, and point-to-point addressing.
- Structured IPv4 and IPv6 allocation.
- Automatically generated Containerlab topology files.
- Automatically generated initial device configurations.
- Consistent node naming, interface descriptions, and link identifiers.
- Separate management networks and lifecycle controls for each profile.

### Validated network foundations

Depending on the selected profile, the validated baseline includes:

- Management and CLI reachability.
- Physical and logical interface state.
- IPv4 and IPv6 point-to-point connectivity.
- Dual-stack IS-IS.
- SR-MPLS infrastructure.
- MP-BGP route-reflector foundations.
- Autonomous-system separation for Inter-AS exercises.
- IPv6 loopback reachability.
- SRv6 locator advertisement and operational state.
- Controlled configuration deployment and rollback.
- Platform-health, restart, and out-of-memory checks.

Advanced services remain progressive student exercises and are not delivered as fully solved configurations.

### AUTO1 automation workstation

AUTO1 provides a reproducible network-automation environment containing:

- Ansible.
- Python.
- pyATS and Genie.
- Netmiko.
- Nornir.
- Scrapli.
- NETCONF through `ncclient`.
- gNMI through `pygnmi`.
- Cisco automation collections and supporting libraries.

AUTO1 supports configuration rendering, check mode, controlled deployment, operational validation, configuration backup, compliance checks, and troubleshooting workflows.

### Operations and validation tools

- Profile-aware deployment and destruction through `labctl`.
- Protection against running multiple heavy profiles simultaneously.
- Static topology and addressing validation.
- Management and CLI reachability checks.
- Directed link-connectivity testing.
- Configuration backup tools.
- Controlled configuration-phase application.
- Commit-check and rollback workflows.
- Host CPU, memory, swap, disk, and load monitoring.
- Container restart and out-of-memory detection.
- Repeatable acceptance tests and evidence collection.

### Documentation

The repository includes:

- Network topology diagrams for every profile.
- Node, link, interface, and addressing inventories.
- Architecture and design rationale.
- Containerlab, Docker, network-image, and AUTO1 build instructions.
- Profile deployment and operating procedures.
- CCIE Service Provider blueprint mapping.
- Progressive study boundaries and suggested exercises.
- Troubleshooting and failure-injection guidance.
- Validation results and acceptance evidence.
- Resource-consumption findings.
- Platform limitations and validated workarounds.
- References to relevant vendor documentation and IETF RFCs.

## Repository safety and licensing boundary

This repository does not contain or distribute:

- Cisco network operating-system images.
- Vendor software archives or executables.
- Product licenses or entitlement files.
- Passwords or authentication secrets.
- API tokens.
- Private SSH keys.
- Local `.env` files.
- Device configuration backups.
- Container runtime state.
- Generated deployment artifacts.
- User-specific laboratory credentials.

Proprietary network software must be obtained from an authorized vendor source and used in accordance with the applicable license and entitlement requirements.

Runtime credentials must be supplied through ignored environment files, environment variables, or an approved secrets-management mechanism. They must never be embedded in generated configurations, committed to Git, or included in validation evidence.

## Documentation

| Guide | Purpose |
|---|---|
| [Professional operating guide](docs/LAB-OPERATING-GUIDE.md) | Start-to-finish explanation and safe operating workflow |
| [Lab 1 — Master ISP](profiles/master/README.md) | Complete master topology, operation and study order |
| [Lab 2 — Inter-AS](profiles/inter-as/README.md) | Complete multi-AS topology, addressing and workflow |
| [Lab 3 — SRv6](https://github.com/dfonquet/ccie-sp-master-lab/blob/main/profiles/srv6/README.md) | SRv6 study profile, topology scope, rollout gates and study workflow |
| [Laboratory profiles](profiles/README.md) | Profile isolation and one-lab-at-a-time model |
| [Complete build guide](docs/BUILD-GUIDE.md) | Step-by-step history, resources and design decisions |
| [Containerlab installation](docs/CONTAINERLAB-INSTALLATION.md) | Host design, installation, storage, images and lifecycle rationale |
| [Lab design catalog](docs/LAB-DESIGN-CATALOG.md) | Profile scale, addressing, IGP choices and study boundaries |
| [Architecture](docs/ARCHITECTURE.md) | Nodes, roles, redundancy and study modules |
| [Addressing](docs/ADDRESSING.md) | Management, loopbacks, links, IS-IS and SIDs |
| [Automation](docs/AUTOMATION.md) | AUTO1 design, tools and learning path |
| [AUTO1 Source of Truth](docs/AUTO1-SOURCE-OF-TRUTH.md) | BGP render, validation, diff, deploy and post-check workflow |
| [Multi-profile roadmap](docs/MULTI-PROFILE-ROADMAP.md) | Master, Inter-AS and SRv6 design and acceptance gates |
| [Validation](docs/VALIDATION.md) | Repeatable health and protocol checks |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Errors encountered and their resolutions |
| [IPv6 standard](IPV6-STANDARD.md) | Provider-specific IPv6 control-plane standard |
| [Operations](OPERATIONS.md) | Daily lifecycle and quick commands |
| [Blueprint matrix](BLUEPRINT-MATRIX.md) | Mapping to CCIE SP v5.1 domains |
| [Security](SECURITY.md) | Credential, image and publishing precautions |

## Architecture

| Role | Platform | Nodes |
|---|---|---|
| Provider core | XRd 24.2.11 | P1-P8 |
| Provider edge | XRd 24.2.11 | PE1-PE8 |
| Route reflector and PCE | XRd 24.2.11 | RR1-RR2 |
| Customer edge | IOL-XE 17.12.1 | CE1-CE9 |
| Customer test endpoints | IOL-XE 17.12.1 | C1-C2 |
| Automation workstation | Ubuntu 24.04 container | AUTO1 |

Total: 18 XRd nodes, 11 IOL nodes, one automation workstation, and 47
data-plane links.

The P backbone has two longitudinal planes, three inter-plane rungs, and two
diagonal paths. Every PE is dual-homed to a pair of P routers. RR1 and RR2
also provide redundant PCE roles. CE2, CE5, and CE8 are dual-homed customer
sites for PE-CE loop prevention and EVPN/L2VPN exercises.

## Images

```text
ios-xr/xrd-control-plane:24.2.11
vrnetlab/cisco_iol:17.12.01
```

The IOL artifact supplied in the folder named `17.15.01` was verified by CLI
as Dublin 17.12.1. This project deliberately uses the truthful image tag.

## Management

```text
Subnet: 10.201.255.0/24
Docker network: ccie-sp-master-mgmt
Ubuntu next hop from Windows: 192.168.192.10
```

Node addresses are listed in `inventory/nodes.csv`.

## Generated files

Run:

```bash
python3 tools/build_lab.py
```

This generates:

```text
topology/ccie-sp-master.clab.yml
inventory/nodes.csv
inventory/links.csv
configs/00-base/
configs/10-isis/
configs/15-provider-standard/
configs/20-sr-mpls/
```

The source of truth is `tools/build_lab.py`; generated files should not be
edited by hand.

## Configuration phases

1. `00-base`: hostnames, dual-stack loopbacks, link addressing, descriptions.
2. `10-isis`: dual-stack IS-IS Level 2, metrics, LFA and convergence.
3. `15-provider-standard`: non-destructive migration of the existing provider
   IPv6 plan plus the common P/PE/RR operational standard.
4. `20-sr-mpls`: SRGB, dual-stack Prefix-SIDs and the SR-TE hierarchy.
5. `30-bgp-rr`: dual route reflectors and VPNv4/VPNv6.
6. `40-l3vpn`: PE-CE routing and shared/extranet services.
7. `50-sr-te-pce`: SR policies, PCC/PCE, disjointness, affinity, and SRLG.
8. `60-multicast`: PIM, RP designs, mLDP, Tree-SID, and NG-mVPN.
9. `70-l2vpn-evpn`: VPWS, VPLS, EVPN, IRB, and multihoming.
10. `80-security-assurance`: AAA/RADIUS, LPTS, RPKI, telemetry, gNMI, and TWAMP.
11. `90-failure-drills`: TI-LFA, BGP-PIC, PCE failover and faults; read the
    [XRd BFD platform boundary](docs/FAILURE-DRILLS.md) before BFD practice.

Phases 30-90 are intentionally developed and validated incrementally. This
keeps each baseline exam-like and prevents untested feature combinations from
being hidden in one enormous startup configuration.

## Provider addressing standard

The deployed IPv4 addresses are immutable in the refinement phase:

```text
Provider loopbacks: 10.0.0.<node-id>/32
Point-to-point:     10.255.0.0/31 onward
```

The provider IPv6 plan follows the requested CCIE SP convention:

```text
Provider loopbacks: 2001:db8:500:abcd::<node-id>/128
Provider links:     2001:db8:1000:<101-125>::/127
```

Customer-facing IPv6 links retain their own access block and are not placed in
the provider IS-IS underlay.

## Automation

`AUTO1` uses `ccie-sp-automation:1.0` at `10.201.255.150`. See
`automation/README.md` for its Ansible, Python, pyATS/Genie, NETCONF and gNMI
examples.

## Platform boundaries

XRd Control Plane is suitable for the routing, MPLS, SR, VPN, PCE, security,
and model-driven management portions of this lab. Physical clocking,
line-card-specific QoS, real MACsec, optical behavior, and some L2 data-plane
counters require either design study or an on-demand XRv9k/physical platform.
