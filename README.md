CCIE Service Provider v5.1 Multi-Profile Lab

<div align="center">

**Reproducible service-provider labs for architecture, configuration, automation, validation, and troubleshooting practice.**

[![Validate generated lab](https://github.com/dfonquet/ccie-sp-master-lab/actions/workflows/validate.yml/badge.svg)](https://github.com/dfonquet/ccie-sp-master-lab/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Containerlab](https://img.shields.io/badge/Containerlab-0.77.0-blue.svg)](https://containerlab.dev/)
[![Cisco XRd](https://img.shields.io/badge/Cisco%20XRd-24.2.11-1ba0d7.svg)](https://www.cisco.com/)
[![IOS XE](https://img.shields.io/badge/IOL--XE-17.12.1-1ba0d7.svg)](https://www.cisco.com/)

[Start here](docs/LAB-OPERATING-GUIDE.md) ·
[Profiles](profiles/README.md) ·
[Deployment status](STATUS.md) ·
[Architecture](docs/ARCHITECTURE.md) ·
[Blueprint coverage](BLUEPRINT-MATRIX.md) ·
[Installation](docs/CONTAINERLAB-INSTALLATION.md)

</div>

---

## Overview

This repository contains three independent Containerlab profiles built for
Cisco CCIE Service Provider v5.1 study and service-provider engineering
practice. The profiles share a deterministic source-of-truth model, generated
topologies, structured configuration phases, validation tooling, and the
`AUTO1` automation workstation.

The project provides a tested infrastructure baseline without delivering every
advanced exercise as a solved configuration. The student retains responsibility
for implementing, verifying, breaking, troubleshooting, and redesigning the
service layers.

> [!IMPORTANT]
> Read the [Professional Lab Operating Guide](docs/LAB-OPERATING-GUIDE.md)
> before deployment. Run only **one resource-intensive profile at a time**.
> The profiles share the same CPU, RAM, KVM, storage, and licensed images.

## Choose a lab profile

| Profile | Scale | Validated foundation | Intended study scope |
|---|---:|---|---|
| [**Master ISP**](profiles/master/README.md) | 30 nodes, 47 data links | Dual-stack addressing, IS-IS, SR-MPLS, redundant RR foundation, expanded P/PE topology | MPLS, MP-BGP, L3VPN, L2VPN, EVPN, multicast, SR-TE/PCE, QoS, security, assurance, and failure drills |
| [**Inter-AS**](profiles/inter-as/README.md) | 23 nodes, 35 links | Generated topology, management and CLI access, base addressing, AS separation, and physical connectivity | eBGP/iBGP, routing policy, labeled unicast, route reflection, and Inter-AS Options A, B, and C |
| [**SRv6**](profiles/srv6/README.md) | 21 nodes, 33 links | Full deployment, base configuration, IS-IS, IPv6 loopback reachability, SRv6 locators, and `66/66` directed IPv6 link tests | SRv6 SID design, endpoint behaviors, SRv6-TE policies, VPN services, uSID, resiliency, and automation |

Each profile has its own topology, management subnet, inventories,
configuration artifacts, diagram, operating procedure, and acceptance boundary.

## Current implementation status

### Master ISP

- Eight P routers: `P1-P8`.
- Eight PE routers: `PE1-PE8`.
- Two redundant RR/PCE nodes: `RR1-RR2`.
- Nine CE routers: `CE1-CE9`.
- Two customer test endpoints: `C1-C2`.
- One automation workstation: `AUTO1`.
- Expanded nodes `P7`, `P8`, `PE7`, and `PE8` use links `L040-L047`.
- The expanded dual-stack IS-IS, SR-MPLS, and route-reflector foundations have
  been validated.

### Inter-AS

- Two independent provider domains.
- Separate IGP and BGP foundations for controlled multi-AS practice.
- Route-reflector roles within each provider domain.
- External and customer-facing links for Options A, B, and C exercises.
- Generated artifacts, management access, base configuration, addressing, and
  physical connectivity have been validated.

### SRv6

- Six P routers, six PE routers, two route reflectors, six CE routers, and
  `AUTO1`.
- All 21 containers deployed successfully during acceptance testing.
- Management and CLI access validated for all 20 network nodes.
- Base configurations applied to P, PE, RR, and CE roles.
- All `66/66` directed IPv6 link tests passed.
- IS-IS adjacencies, loopback reachability, SRv6 locator advertisement, and
  XRd `24.2.11` SRv6 capabilities were validated.

See [STATUS.md](STATUS.md) for the exact evidence, remaining work, and platform
boundaries. A successful baseline does not imply that every advanced service
phase has already been solved or accepted.

## Topology

The Master diagram below is generated from the authoritative node and link
inventories. Orange `NEW` markers identify the validated expansion.

![CCIE SP Master topology](docs/topology.svg)

Profile-specific diagrams:

- [Master ISP design and topology](profiles/master/DESIGN.md)
- [Inter-AS topology](profiles/inter-as/topology.svg)
- [SRv6 topology](profiles/srv6/topology.svg)
- [Cross-profile design catalog](docs/LAB-DESIGN-CATALOG.md)

## Architecture at a glance

### Master platform inventory

| Role | Platform | Nodes | Quantity |
|---|---|---|---:|
| Provider core | Cisco XRd Control Plane `24.2.11` | `P1-P8` | 8 |
| Provider edge | Cisco XRd Control Plane `24.2.11` | `PE1-PE8` | 8 |
| Route reflector and PCE | Cisco XRd Control Plane `24.2.11` | `RR1-RR2` | 2 |
| Customer edge | Cisco IOL-XE `17.12.1` | `CE1-CE9` | 9 |
| Customer test endpoints | Cisco IOL-XE `17.12.1` | `C1-C2` | 2 |
| Automation workstation | Ubuntu-based container | `AUTO1` | 1 |

The Master backbone uses two longitudinal planes, three inter-plane rungs, and
two diagonal paths. Every PE is dual-homed to a pair of P routers. `RR1` and
`RR2` provide redundant route-reflector and PCE roles. `CE2`, `CE5`, and `CE8`
are dual-homed customer sites for routing-policy, loop-prevention, L2VPN, EVPN,
and failure exercises.

Full architectural detail belongs in the
[Architecture Guide](docs/ARCHITECTURE.md), not in this landing page.

## Validated starting point

Depending on the selected profile, the starting point includes:

- Successful Containerlab deployment.
- Isolated management connectivity.
- Management and CLI reachability.
- Deterministic node, interface, link, and addressing inventories.
- Base interface and loopback configuration.
- Operational physical links.
- IPv4 and IPv6 point-to-point connectivity.
- Dual-stack IS-IS where required.
- SR-MPLS foundations in the Master profile.
- Autonomous-system separation in the Inter-AS profile.
- Operational IS-IS and SRv6 locators in the SRv6 profile.
- Backup, validation, rollback, and automation tooling through `AUTO1`.

## Study and implementation boundary

The following technologies remain progressive configuration and
troubleshooting exercises. Their presence in the roadmap does not mean that a
fully solved and accepted configuration is shipped in every profile.

<details>
<summary><strong>Master ISP exercises</strong></summary>

- Advanced MP-BGP address families and routing policy.
- MPLS L3VPN and L2VPN services.
- EVPN, IRB, and EVPN multihoming.
- Multicast routing and multicast VPN services.
- SR-MPLS Traffic Engineering and policy steering.
- PCC/PCE, affinity, disjointness, and SRLG exercises.
- QoS and traffic-management policy.
- Fast convergence, TI-LFA, BGP-PIC, and failure scenarios.
- AAA, TACACS+, RADIUS, LPTS, and operational security.
- RPKI and BGP origin validation.
- Automation, compliance, telemetry, and assurance workflows.

</details>

<details>
<summary><strong>Inter-AS exercises</strong></summary>

- Inter-AS Options A, B, and C.
- eBGP and iBGP policy design.
- MP-BGP route exchange between autonomous systems.
- Route-reflector interaction between provider domains.
- IPv4 and IPv6 inter-provider connectivity.
- Inter-AS L3VPN and labeled-unicast scenarios.
- Route-leak prevention, path selection, convergence, and failure testing.

</details>

<details>
<summary><strong>SRv6 exercises</strong></summary>

- SID allocation and locator redesign.
- Explicit segment lists and SRv6-TE policies.
- Dynamic and static binding SIDs.
- Policy steering and VPN services.
- Endpoint behavior validation.
- Reduced encapsulation and uSID experimentation.
- Resiliency, failure, and automation scenarios.

</details>

## Quick start

### Prerequisites

- Linux host or VM with nested KVM available.
- Docker Engine.
- Containerlab `0.77.0` or a validated compatible release.
- Locally built or imported authorized network images.
- Sufficient CPU, RAM, and disk for the selected profile.
- Runtime credentials stored outside Git.

For the complete host, Docker, Containerlab, image-transfer, vrnetlab, and
`AUTO1` build procedure, use the
[Containerlab Host, Image, and AUTO1 Build Guide](docs/CONTAINERLAB-INSTALLATION.md).

### Clone and prepare

```bash
git clone https://github.com/dfonquet/ccie-sp-master-lab.git
cd ccie-sp-master-lab

cp .env.example .env
chmod 0600 .env
${EDITOR:-nano} .env
```

The local `.env` file is ignored by Git. Never commit credentials.

### Generate and validate artifacts

```bash
python3 tools/build_lab.py
python3 tools/validate_srv6_artifacts.py
git diff --check
```

The relevant generator remains the source of truth. Generated topology,
inventory, and configuration artifacts should not be edited manually.

### Operate one profile

```bash
./labctl status
./labctl deploy master
./labctl inspect master
./labctl destroy master
```

Replace `master` with `inter-as` or `srv6` as required:

```bash
./labctl deploy inter-as
./labctl deploy srv6
```

`labctl` refuses to start another heavy profile while Containerlab nodes are
already active.

## Addressing and management

| Profile | Management subnet | Docker network |
|---|---|---|
| Master | `10.201.255.0/24` | `ccie-sp-master-mgmt` |
| Inter-AS | `10.202.255.0/24` | `ccie-sp-inter-as-mgmt` |
| SRv6 | `10.203.255.0/24` | `ccie-sp-srv6-mgmt` |

Master provider addressing follows these conventions:

```text
IPv4 loopbacks:      10.0.0.<node-id>/32
IPv4 P2P links:      10.255.0.0/31 onward
IPv6 loopbacks:      2001:db8:500:abcd::<node-id>/128
IPv6 provider links: 2001:db8:1000:<link-id>::/127
```

Customer-facing networks use separate access blocks and are not automatically
placed in the provider IS-IS underlay. See [Addressing](docs/ADDRESSING.md) and
the profile-specific inventories for authoritative values.

## Configuration phase model

| Phase | Scope | Boundary |
|---|---|---|
| `00-base` | Hostnames, loopbacks, descriptions, interface state, and link addressing | Validated baseline |
| `10-isis` | Dual-stack IS-IS Level 2, metrics, LFA, and convergence foundations | Validated baseline |
| `15-provider-standard` | Common P/PE/RR operational standard and IPv6 normalization | Validated baseline |
| `20-sr-mpls` | SRGB, Prefix-SIDs, SR-MPLS, and SR-TE hierarchy | Validated foundation |
| `30-bgp-rr` | Redundant RR, iBGP, VPNv4, VPNv6, and routing policy | Progressive |
| `40-l3vpn` | VRFs, RD/RT, PE-CE routing, shared services, and extranets | Progressive |
| `50-sr-te-pce` | SR policies, PCC/PCE, affinity, disjointness, and SRLG | Progressive |
| `60-multicast` | PIM, RP designs, mLDP, Tree-SID, and NG-mVPN | Progressive |
| `70-l2vpn-evpn` | VPWS, VPLS, EVPN, IRB, and multihoming | Progressive |
| `80-security-assurance` | AAA, LPTS, RPKI, telemetry, gNMI, and TWAMP | Progressive |
| `90-failure-drills` | TI-LFA, BGP-PIC, PCE failover, and controlled faults | Progressive |

See [Failure Drills](docs/FAILURE-DRILLS.md) before using BFD as an acceptance
criterion on XRd Control Plane virtual links.

## AUTO1 automation workstation

`AUTO1` uses the local `ccie-sp-automation:1.0` image and provides:

- Ansible.
- Python.
- pyATS and Genie.
- Netmiko and Nornir.
- Scrapli.
- NETCONF through `ncclient`.
- gNMI through `pygnmi`.
- Configuration rendering, check mode, controlled deployment, backup,
  validation, compliance, and troubleshooting workflows.

Start with:

- [AUTO1 automation guide](automation/README.md)
- [AUTO1 Source-of-Truth workflow](docs/AUTO1-SOURCE-OF-TRUTH.md)
- [Automation architecture](docs/AUTOMATION.md)

## Documentation map

### Start and operate

| Guide | Purpose |
|---|---|
| [Professional Lab Operating Guide](docs/LAB-OPERATING-GUIDE.md) | Start-to-finish repository and safe-operation workflow |
| [Deployment Status](STATUS.md) | Exact validation evidence, remaining work, and acceptance boundaries |
| [Operations](OPERATIONS.md) | Daily lifecycle and quick commands |
| [Validation](docs/VALIDATION.md) | Repeatable health, reachability, and protocol checks |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Failures encountered and their resolutions |

### Understand the design

| Guide | Purpose |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | Roles, redundancy, components, and study modules |
| [Addressing](docs/ADDRESSING.md) | Management, loopbacks, links, IS-IS, labels, and SIDs |
| [Lab Design Catalog](docs/LAB-DESIGN-CATALOG.md) | Cross-profile scale, addressing, IGP choices, and study boundaries |
| [IPv6 Standard](IPV6-STANDARD.md) | Provider IPv6 control-plane conventions |
| [CCIE SP Blueprint Matrix](BLUEPRINT-MATRIX.md) | Mapping to CCIE SP v5.1 domains |
| [Multi-Profile Roadmap](docs/MULTI-PROFILE-ROADMAP.md) | Profile evolution and acceptance gates |

### Build and automate

| Guide | Purpose |
|---|---|
| [Complete Build Guide](docs/BUILD-GUIDE.md) | Implementation history, host resources, and design decisions |
| [Containerlab Installation](docs/CONTAINERLAB-INSTALLATION.md) | Host, Docker, storage, licensed-image transfer, vrnetlab, and AUTO1 build |
| [Automation](docs/AUTOMATION.md) | Automation platform and learning path |
| [AUTO1 Source of Truth](docs/AUTO1-SOURCE-OF-TRUTH.md) | Render, check, diff, deploy, post-check, backup, and rollback workflow |

### Profile guides

| Profile | Operations | Design | Troubleshooting | References |
|---|---|---|---|---|
| Master | [Guide](profiles/master/README.md) | [Design](profiles/master/DESIGN.md) | [Troubleshooting](profiles/master/TROUBLESHOOTING.md) | [References](profiles/master/REFERENCES.md) |
| Inter-AS | [Guide](profiles/inter-as/README.md) | [Design](profiles/inter-as/DESIGN.md) | [Troubleshooting](profiles/inter-as/TROUBLESHOOTING.md) | [References](profiles/inter-as/REFERENCES.md) |
| SRv6 | [Guide](profiles/srv6/README.md) | [Design](profiles/srv6/DESIGN.md) | [Troubleshooting](profiles/srv6/TROUBLESHOOTING.md) | [References](profiles/srv6/REFERENCES.md) |

## Platform boundaries

Cisco XRd Control Plane is suitable for the routing, MPLS, Segment Routing,
VPN control plane, PCE, security, and model-driven management portions of this
project. It is not a substitute for every forwarding ASIC, line card, optical
system, or physical interface behavior.

The following areas may require design study, an on-demand XRv9k image, or
physical equipment:

- Physical clocking and synchronization.
- Hardware line-card QoS.
- Real forwarding-plane scale.
- MACsec encryption behavior.
- Optical transport characteristics.
- ASIC-dependent forwarding and counters.
- Some Layer 2 data-plane functions.
- Platform-dependent BFD behavior.

Documented limitations are laboratory boundaries, not successful feature
validation.

## Repository safety and licensing boundary

This repository does **not** contain or distribute:

- Cisco network operating-system images.
- Vendor archives, executables, licenses, or entitlement files.
- Passwords, authentication secrets, or API tokens.
- Private SSH keys.
- Local `.env` files.
- Device configuration backups.
- Container runtime state.
- Generated deployment artifacts containing local data.

Obtain proprietary software from an authorized source and use it according to
the applicable license and entitlement requirements. Supply runtime credentials
through ignored environment files, environment variables, or an approved
secret-management system.

See [SECURITY.md](SECURITY.md) before making a fork or deployment public.

## Contributing

Contributions should preserve the source-of-truth model, profile isolation,
documentation accuracy, and safety boundary.

Before opening a pull request:

```bash
python3 tools/build_lab.py
python3 -m compileall -q tools
git diff --check
```

Follow [CONTRIBUTING.md](CONTRIBUTING.md) for branch, validation, evidence, and
pull-request requirements.

## License

Repository-authored source code and documentation are available under the
[MIT License](LICENSE). Vendor software and network operating-system images are
not covered by this license and are not distributed by this project.

---

<div align="center">

Built as a reproducible study environment for serious CCIE Service Provider
practice, controlled experimentation, and documented engineering work.

</div>
