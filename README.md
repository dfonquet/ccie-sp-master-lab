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

## Study boundary

The profiles provide a stable service-provider foundation without pre-solving every exercise.

The following technologies are intentionally left as progressive study and implementation phases:

- Advanced MP-BGP services.
- MPLS L2VPN and L3VPN.
- EVPN and EVPN multihoming.
- Multicast services.
- SR-MPLS Traffic Engineering.
- SRv6 policies and advanced endpoint behaviors.
- Inter-AS Options A, B, and C.
- AAA and centralized authentication.
- RPKI and BGP origin validation.
- QoS and traffic management.
- Fast convergence and failure scenarios.
- Network automation and assurance workflows.


See [Deployment status](STATUS.md) for the exact acceptance boundary before moving to the next profile.

## What this repository contains

- Three isolated Containerlab profiles:
  - Master.
  - Inter-AS.
  - SRv6.
- Reproducible topology generation using Python.
- XRd provider-core nodes.
- IOL-XE customer-edge and client nodes.
- Redundant P, PE, RR, and PCE roles.
- Deterministic IPv4 and IPv6 addressing.
- Structured loopback and point-to-point allocation.
- Validated IS-IS, SR-MPLS, MP-BGP RR, and SRv6 foundation phases.
- AUTO1 automation workstation with:
  - Ansible.
  - Python.
  - pyATS and Genie.
  - Netmiko.
  - Nornir.
  - Scrapli.
  - NETCONF.
  - gNMI.
- Controlled deployment, inspection, validation, backup, rollback, and destruction tools.
- Progressive CCIE Service Provider exercises.
- Network topology diagrams.
- Addressing and interface inventories.
- Professional operating and troubleshooting guides.
- Validation and acceptance evidence.
- Documented engineering decisions.
- Resource-consumption findings.
- Platform limitations and validated workarounds.

## Repository safety boundary

This repository does not include:

- Cisco network operating-system images.
- Vendor licenses.
- Passwords or authentication secrets.
- API tokens.
- Private SSH keys.
- Device configuration backups.
- Generated runtime artifacts.

All proprietary software must be obtained from an authorized source and used according to the applicable vendor license.


8:38 a.m.

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
