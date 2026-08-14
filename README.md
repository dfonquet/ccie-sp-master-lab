
<h1 align="center">
  CCIE Service Provider v5.1 Multi-Profile Lab
</h1>

<div align="center">

**Reproducible service-provider labs for architecture, manual study, automation, validation, troubleshooting, and controlled failure practice.**

[![Validate generated lab](https://github.com/dfonquet/ccie-sp-master-lab/actions/workflows/validate.yml/badge.svg)](https://github.com/dfonquet/ccie-sp-master-lab/actions/workflows/validate.yml)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-green.svg)](LICENSE)
[![Containerlab](https://img.shields.io/badge/Containerlab-0.77.0-blue.svg)](https://containerlab.dev/)
[![Cisco XRd](https://img.shields.io/badge/Cisco%20XRd-24.2.11-1ba0d7.svg)](https://www.cisco.com/)
[![IOS XE](https://img.shields.io/badge/IOL--XE-17.12.01-1ba0d7.svg)](https://www.cisco.com/)

[Start here](docs/LAB-OPERATING-GUIDE.md) ·
[Profiles](profiles/README.md) ·
[Deployment status](STATUS.md) ·
[Architecture](docs/ARCHITECTURE.md) ·
[Blueprint coverage](BLUEPRINT-MATRIX.md) ·
[Installation](docs/CONTAINERLAB-INSTALLATION.md)

</div>

---

## Overview

This repository contains several independent Containerlab profiles for Cisco
CCIE Service Provider v5.1 study and service-provider engineering practice.
The profiles share deterministic inventories, generated topology artifacts,
validation tooling, documentation, and the `AUTO1` automation workstation.

The principal profile is the **38-node Master lab**, formed by two clearly
separated provider domains:

- **ISP-1 / AS500**: the established IS-IS, SR-MPLS, MP-BGP, EVPN, multicast,
  L3VPN, customer-edge, and automation study environment.
- **ISP-2 / AS65002**: a lightweight dual-stack expansion using XRd Control
  Plane for its ASBR and route reflector, Cisco IOL for its internal routers,
  OSPFv2/OSPFv3 as its IGP, and a dedicated Linux traffic source.

The project provides a tested infrastructure baseline without shipping every
advanced exercise as a solved configuration. The student remains responsible
for configuring, validating, breaking, troubleshooting, and redesigning the
service layers.

> [!IMPORTANT]
> Read the [Professional Lab Operating Guide](docs/LAB-OPERATING-GUIDE.md)
> before deployment. Run only one resource-intensive profile at a time. The
> profiles share CPU, RAM, KVM, storage, Docker networks, and licensed images.

## Source-of-truth model

The Master deliberately distinguishes structural repository state from live
study configuration:

| State | Authority | Purpose |
|---|---|---|
| **REPO** | Topology, inventories, addressing, scripts, bootstrap files, validators, and documentation | Structural source of truth |
| **RUNTIME ACTUAL** | Running configuration on active routers | Source of truth for active study exercises |
| **IOL NVRAM** | Per-node binary NVRAM saved with `write memory` | Persistence of complete IOS configuration across destroy/deploy |

Runtime study configuration may include EVPN, PIM-SM, BSR/RP, L3VPN, VRFs,
MP-BGP VPNv4/VPNv6, eBGP PE-CE, dual-homing, route policies, local preference,
`as-override`, IPv4, and IPv6 before those exercises are promoted into
automation.

Do not assume generated startup files are a complete representation of the
active routers. Do not regenerate the Master while preserving manual runtime
work unless the intended workflow and backups have been reviewed.

## Lab profiles

| Profile | Scale | Foundation | Intended study scope |
|---|---:|---|---|
| [**Master ISP**](profiles/master/README.md) | 38 nodes, 57 links | ISP-1 plus deployed ISP-2 structure, management, bootstrap, and manual-study boundary | IS-IS, SR-MPLS, MP-BGP, EVPN, multicast, L3VPN, OSPF, eBGP Inter-AS, policy, and failures |
| [**Inter-AS**](profiles/inter-as/README.md) | 23 nodes, 35 links | Multi-AS topology, addressing, management, and physical connectivity | Options A/B/C, LU, routing policy, and route reflection |
| [**SRv6**](profiles/srv6/README.md) | 21 nodes, 33 links | IS-IS, IPv6 reachability, SRv6 locators, and directed-link validation | SRv6 behaviors, policies, VPNs, uSID, and resiliency |
| [**Full Dataplane**](profiles/full-dataplane/README.md) | 30 nodes, 42 links | Resource-intensive forwarding design | EVPN, VPN, multicast, QoS, telemetry, and packet forwarding |
| [**XRd Eight**](profiles/xrd-eight/README.md) | 12 nodes, 20 links | Compact XRd vRouter environment | Resource-bounded forwarding and failure practice |

Each profile has an independent topology, management network, inventory,
operating procedure, validation boundary, and resource profile.

## Master topology

![CCIE SP Master topology](docs/topology.svg)

The authoritative topology is defined by:

- `topology/ccie-sp-master.clab.yml`
- `inventory/nodes.csv`
- `inventory/links.csv`

The diagram is a documentation and study view. Inventory and topology files
remain the structural source of truth.

## Master inventory

| Domain | Role | Platform | Nodes | Qty. |
|---|---|---|---|---:|
| ISP-1 | Provider core | XRd Control Plane `24.2.11` | `P1-P8` | 8 |
| ISP-1 | Provider edge | XRd Control Plane `24.2.11` | `PE1-PE8` | 8 |
| ISP-1 | Route reflector / PCE | XRd Control Plane `24.2.11` | `RR1-RR2` | 2 |
| ISP-1 | Customer edge | Cisco IOL `17.12.01` | `CE1-CE9` | 9 |
| ISP-1 | Customer endpoints | Cisco IOL `17.12.01` | `C1-C2` | 2 |
| Shared management | Automation workstation | Ubuntu container | `AUTO1` | 1 |
| ISP-2 | ASBR | XRd Control Plane `24.2.11` | `ASBR-ISP2` | 1 |
| ISP-2 | Route reflector | XRd Control Plane `24.2.11` | `RR-ISP2` | 1 |
| ISP-2 | P/transit/service edge | Cisco IOL `17.12.01` | `ISP2-P1`–`ISP2-P5` | 5 |
| ISP-2 | Traffic generator | Ubuntu/Linux container | `SOURCE1` | 1 |
| **Total** |  |  |  | **38** |

Platform totals:

- **20 XRd Control Plane** nodes.
- **16 Cisco IOL** nodes.
- **2 Linux** containers: `AUTO1` and `SOURCE1`.
- **57 links**: `L001-L057`.

No XRd vRouter/full-dataplane node is required for the ISP-2 expansion.

## ISP-1 / AS500

ISP-1 preserves the established Master functions:

- Dual-stack IS-IS Level 2 underlay.
- SR-MPLS foundations.
- Redundant `RR1` and `RR2` route reflection.
- PCE study roles.
- MP-BGP VPNv4/VPNv6 study.
- EVPN study services.
- IPv4 PIM-SM with BSR/RP study.
- L3VPN and VRF study.
- Dual-homed CE sites.
- `AUTO1` automation workstation.

`RR1` retains its Route Reflector, PCE, BSR, and RP functions. It is not used
as a traffic-generator attachment point.

### PE-CE eBGP policy examples

The current study design includes these dual-homed customer sites:

| Customer | Primary PE | Backup PE | Study purpose |
|---|---|---|---|
| `CE2` | `PE1` | `PE2` | eBGP PE-CE, local preference, primary/backup selection, route policy, and failure testing |
| `CE5` | `PE4` | `PE3` | eBGP PE-CE, local preference, primary/backup selection, route policy, and failure testing |

Other dual-homing, EVPN, L3VPN, and multicast scenarios remain part of the
manual runtime study state unless explicitly promoted later.

## ISP-2 / AS65002

ISP-2 is a separate provider domain. It does not participate in ISP-1 IS-IS or
SR-MPLS during its initial phases.

### Roles

| Node | Platform | Role | Management |
|---|---|---|---|
| `ASBR-ISP2` | XRd Control Plane | Inter-AS border router | `10.201.255.151` |
| `RR-ISP2` | XRd Control Plane | Future route reflector | `10.201.255.152` |
| `ISP2-P1` | IOL | P router | `10.201.255.153` |
| `ISP2-P2` | IOL | P router | `10.201.255.154` |
| `ISP2-P3` | IOL | Transit router | `10.201.255.155` |
| `ISP2-P4` | IOL | Transit router | `10.201.255.156` |
| `ISP2-P5` | IOL | PE / service-edge router | `10.201.255.157` |
| `SOURCE1` | Linux | IPv4/IPv6 traffic source | `10.201.255.158` |

### ISP-2 links

| Link | Endpoints | Purpose |
|---|---|---|
| `L048` | `P1 ↔ ASBR-ISP2` | Future eBGP handoff between AS500 and AS65002 |
| `L049` | `ASBR-ISP2 ↔ ISP2-P1` | ISP-2 internal access |
| `L050` | `ASBR-ISP2 ↔ ISP2-P2` | ISP-2 internal access |
| `L051` | `ISP2-P1 ↔ ISP2-P3` | Internal transit |
| `L052` | `ISP2-P2 ↔ ISP2-P5` | Internal transit/service-edge path |
| `L053` | `ISP2-P3 ↔ ISP2-P4` | Internal transit |
| `L054` | `ISP2-P4 ↔ ISP2-P5` | Internal transit/service-edge path |
| `L055` | `ISP2-P3 ↔ RR-ISP2` | RR reachability path |
| `L056` | `ISP2-P4 ↔ RR-ISP2` | Redundant RR reachability path |
| `L057` | `ISP2-P5 ↔ SOURCE1` | Dedicated traffic-source access |

### ISP-2 routing design

- ASN: **AS65002**.
- IPv4 IGP: **OSPFv2**.
- IPv6 IGP: **OSPFv3**.
- Area: **Area 0**.
- Dual-stack loopbacks and point-to-point addressing.
- IPv4 point-to-point links use `/31`.
- IPv6 point-to-point links use `/127`.
- ISP-2 IPv6 aggregate: `2001:db8:6502::/48`.
- ISP-2 loopbacks: `10.65.2.1/32` through `10.65.2.7/32`.

OSPF remains entirely separate from ISP-1 IS-IS/SR-MPLS.

### SOURCE1

`SOURCE1` connects to **`ISP2-P5`**, not to `P5` in ISP-1:

```text
SOURCE1
   |
  L057
   |
ISP2-P5
   |
 ISP-2
```

This placement keeps traffic generation outside the existing ISP-1 route
reflector and multicast-control roles. It supports:

- IPv4 and IPv6 ping.
- Traceroute.
- `iperf3`.
- `tcpdump`.
- Future multicast experiments.
- Controlled service-edge and failure testing.

## ISP-2 manual implementation phases

ISP-2 is intentionally configured by hand before any automation is evaluated.

### Phase 1 — Internal foundation

- Nodes and management access.
- Hostnames and minimum bootstrap.
- Loopbacks.
- IPv4 and IPv6 link addressing.
- OSPFv2 Area 0.
- OSPFv3 Area 0.
- Internal dual-stack reachability.
- `RR-ISP2` reachability.
- `SOURCE1` connectivity.

### Phase 2 — Inter-AS unicast

- eBGP `AS500 ↔ AS65002` over `L048`.
- IPv4 unicast.
- IPv6 unicast.
- Import/export policy.
- Route control and path selection.

### Future independent study phases

- iBGP and route reflection inside ISP-2.
- BGP labeled-unicast.
- Inter-AS L3VPN Option A.
- Inter-AS L3VPN Option B.
- Route leaking and policy control.
- Failure scenarios.

These future protocols are not part of the structural bootstrap and must not
be anticipated by automatic startup generation.

## Cisco IOL configuration persistence

The Master provides complete IOL NVRAM persistence for:

```text
CE1-CE9
C1-C2
ISP2-P1-ISP2-P5
```

Containerlab bind-mounts the complete IOL binary NVRAM read/write. The normal
IOS workflow is therefore supported:

```text
CE2# copy running-config startup-config
```

or:

```text
CE2# write memory
```

The repository lifecycle wrapper mirrors each native PID-based NVRAM to a
stable node-centric path:

```text
topology/persistent/iol/<node>/nvram
```

Before `destroy`, `labctl` captures and backs up every complete NVRAM. Before
`deploy`, it restores each binary using the PID expected by Containerlab.

```bash
./labctl destroy master
./labctl deploy master
```

This preserves the complete saved configuration, including usernames,
management interfaces, SSH/HTTP settings, routing protocols, interfaces, ACLs,
prefix lists, route maps, and study policies. It does not parse or filter
`show running-config`.

Files under `topology/startup/*.partial.cfg` remain first-boot bootstrap only.
They are not the persistence mechanism and do not replace an existing NVRAM.

Inspect persistence state:

```bash
python3 tools/iol_nvram.py status
```

Create an additional backup:

```bash
python3 tools/iol_nvram.py backup --label before-study-change
```

Deliberately reset one stopped IOL to bootstrap:

```bash
python3 tools/iol_nvram.py reset --node CE2 --yes
```

> [!WARNING]
> Use `labctl` for Master lifecycle operations. Direct raw Containerlab
> lifecycle commands bypass the canonical NVRAM synchronization. Never use
> `containerlab destroy --cleanup` when saved runtime state must be preserved.

See [IOL NVRAM Persistence](docs/IOL-NVRAM-PERSISTENCE.md).

## Validated Master milestones

The ISP-1 runtime has been used to validate or study:

- Dual-stack IS-IS Level 2.
- SR-MPLS foundations.
- Redundant RR/PCE reachability.
- MP-BGP VPNv4/VPNv6.
- VRF `CUST-A` and L3VPN workflows.
- eBGP PE-CE.
- Dual-homed CE routing.
- Route policies and `as-override`.
- Local Preference primary/backup behavior.
- EVPN E-LAN signaling.
- IPv4 PIM-SM.
- Dynamic BSR/RP discovery.
- IGMP, RPF, `(*,G)`, and `(S,G)` state.
- IPv4 and IPv6 study workflows.

Some of these remain runtime-only manual configurations and have not been
promoted into generated startup configurations.

### EVPN milestone

The Master has been exercised with EVI `500`, including:

- BGP `l2vpn evpn` propagation through `RR1` and `RR2`.
- Bridge-domain and EVI association.
- Route-target import/export.
- EVPN Route Type 2 MAC advertisement.
- Route Type 3 / IMET participation.
- Remote next-hop and MAC-route correlation.

This validates signaling, not every possible EVPN forwarding, IRB, or
multihoming scenario.

### Multicast milestone

The Master has been exercised with:

- `RR1` as BSR and RP.
- RP address `10.0.0.13`.
- Group range `239.0.0.0/8`.
- `CE4` as receiver-side study node.
- `CE7` as source-side study node.
- `PE3` as receiver-side LHR.
- `PE5` as source-side FHR.

Validated state includes PIM neighbors, Candidate-RP advertisement, BSR
mapping, IGMP receiver interest, RPF, PIM Register signaling, shared-tree and
source-tree state, and MRIB outgoing-interface state.

## Quick start

### Prerequisites

- Linux host or VM with nested KVM.
- Docker Engine.
- Containerlab `0.77.0` or a validated compatible version.
- Authorized local Cisco images.
- Sufficient CPU, RAM, storage, and swap headroom.
- Runtime credentials stored outside Git.

See [Containerlab Installation](docs/CONTAINERLAB-INSTALLATION.md) for the
complete host and image preparation procedure.

### Clone and prepare

```bash
git clone https://github.com/dfonquet/ccie-sp-master-lab.git
cd ccie-sp-master-lab

cp .env.example .env
chmod 0600 .env
${EDITOR:-nano} .env
```

Never commit `.env`, passwords, SSH keys, device backups, or licensed images.

### Operate the Master

```bash
./labctl status
./labctl deploy master
./labctl inspect master
./labctl destroy master
```

`labctl` refuses to start another heavy profile while a lab is active. For the
Master it also coordinates IOL NVRAM capture, backup, restoration, and
readiness checks.

### Safe validation

```bash
python3 tools/iol_nvram.py status
python3 tools/validate_master_structure.py
python3 tools/validate_documentation.py
git diff --check
```

Do not run `tools/build_lab.py` merely to preserve manual runtime changes. A
generator is an intentional repository operation, not a runtime backup tool.

## Addressing conventions

| Profile | Management subnet | Docker network |
|---|---|---|
| Master | `10.201.255.0/24` | `ccie-sp-master-mgmt` |
| Inter-AS | `10.202.255.0/24` | `ccie-sp-inter-as-mgmt` |
| SRv6 | `10.203.255.0/24` | `ccie-sp-srv6-mgmt` |
| XRd Eight | `10.207.255.0/24` | `ccie-sp-xrd-eight-mgmt` |

ISP-1 conventions:

```text
IPv4 loopbacks:      10.0.0.<node-id>/32
IPv4 P2P links:      10.255.0.0/31 onward
IPv6 loopbacks:      2001:db8:500:abcd::<node-id>/128
IPv6 provider links: 2001:db8:1000:<link-id>::/127
```

ISP-2 conventions:

```text
ASN:                 65002
IPv4 loopbacks:      10.65.2.1/32 through 10.65.2.7/32
IPv4 P2P links:      /31
IPv6 aggregate:      2001:db8:6502::/48
IPv6 P2P links:      /127
IGP:                 OSPFv2 + OSPFv3, Area 0
```

See [Addressing](docs/ADDRESSING.md) and the inventories for authoritative
per-interface values.

## Configuration boundary

The established ISP-1 phase model remains available for structured exercises,
but the active runtime may contain additional manually configured study state.

| Scope | Status |
|---|---|
| Base management and bootstrap | Repository-managed |
| ISP-1 IS-IS and SR-MPLS foundation | Established Master foundation |
| ISP-1 EVPN, multicast, L3VPN, and PE-CE studies | May exist as manual runtime state |
| ISP-2 node and link structure | Repository-managed |
| ISP-2 management/bootstrap | Minimal repository-managed bootstrap |
| ISP-2 OSPFv2/OSPFv3 | Manual study phase |
| ISP-2 eBGP/iBGP/RR/LU | Manual future phases |
| ISP-2 Inter-AS L3VPN | Not implemented; future independent study |
| `AUTO1` | Preserved; not repurposed for automatic ISP-2 protocol configuration |

The intended ISP-2 workflow is:

```text
Design
  ↓
Offline validation
  ↓
Structural topology/inventory changes
  ↓
Controlled deployment window
  ↓
Manual ISP-2 configuration
  ↓
Troubleshooting and learning
  ↓
Validation
  ↓
Optional automation evaluation later
```

## AUTO1

`AUTO1` remains the automation workstation and provides tools such as:

- Ansible.
- Python.
- pyATS and Genie.
- Netmiko and Nornir.
- Scrapli.
- NETCONF and gNMI clients.
- Backup, validation, rendering, compliance, and troubleshooting workflows.

ISP-2 protocols are not automatically configured by `AUTO1` during the manual
study phases.

See:

- [AUTO1 automation guide](automation/README.md)
- [AUTO1 Source-of-Truth workflow](docs/AUTO1-SOURCE-OF-TRUTH.md)
- [Automation architecture](docs/AUTOMATION.md)

## Platform boundaries

Cisco XRd Control Plane is suitable for routing and service control-plane
study, including IS-IS, OSPF, BGP, MPLS/SR signaling, route reflection, PCE,
EVPN signaling, PIM state, and model-driven management.

It is not a substitute for every forwarding ASIC, line card, or hardware
feature. Successful control-plane state does not guarantee complete packet
forwarding for every EVPN, multicast, QoS, or dataplane scenario.

```text
EVPN signaling            -> validated/studied
EVPN CE-to-CE dataplane   -> platform-dependent

PIM control plane         -> validated/studied
Multicast state           -> validated/studied
End-to-end multicast data -> platform-dependent
```

Use a dataplane-capable environment when packet forwarding, hardware counters,
or platform-specific features are the acceptance criterion.

## Resource considerations

The 38-node Master contains 20 XRd Control Plane nodes, 16 IOL nodes, and two
Linux containers. ISP-2 intentionally uses IOL for five internal routers to
reduce CPU and RAM pressure.

Recommended operational principles:

- Run only one heavy profile at a time.
- Keep worker concurrency conservative.
- Monitor CPU, RAM, swap, disk, and container health.
- Allow XRd nodes sufficient readiness time.
- Back up runtime state before lifecycle or topology changes.
- Avoid XRd vRouter/full dataplane for the ISP-2 expansion.

## Documentation map

### Start and operate

| Guide | Purpose |
|---|---|
| [Lab Operating Guide](docs/LAB-OPERATING-GUIDE.md) | Safe start-to-finish operation |
| [Deployment Status](STATUS.md) | Validation evidence and remaining work |
| [Operations](OPERATIONS.md) | Daily lifecycle commands |
| [Validation](docs/VALIDATION.md) | Health and protocol checks |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Failure analysis and recovery |
| [IOL NVRAM Persistence](docs/IOL-NVRAM-PERSISTENCE.md) | Complete IOS startup persistence |

### Understand the design

| Guide | Purpose |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | Roles and redundancy |
| [Addressing](docs/ADDRESSING.md) | Management, loopbacks, and links |
| [Lab Design Catalog](docs/LAB-DESIGN-CATALOG.md) | Cross-profile comparison |
| [IPv6 Standard](IPV6-STANDARD.md) | IPv6 conventions |
| [Blueprint Matrix](BLUEPRINT-MATRIX.md) | CCIE SP v5.1 mapping |
| [Multi-Profile Roadmap](docs/MULTI-PROFILE-ROADMAP.md) | Evolution and acceptance gates |

### Profile guides

| Profile | Operations | Design | Troubleshooting |
|---|---|---|---|
| Master | [Guide](profiles/master/README.md) | [Design](profiles/master/DESIGN.md) | [Troubleshooting](profiles/master/TROUBLESHOOTING.md) |
| Inter-AS | [Guide](profiles/inter-as/README.md) | [Design](profiles/inter-as/DESIGN.md) | [Troubleshooting](profiles/inter-as/TROUBLESHOOTING.md) |
| SRv6 | [Guide](profiles/srv6/README.md) | [Design](profiles/srv6/DESIGN.md) | [Troubleshooting](profiles/srv6/TROUBLESHOOTING.md) |
| Full Dataplane | [Guide](profiles/full-dataplane/README.md) | [Design](profiles/full-dataplane/DESIGN.md) | Prepared, resource-intensive |
| XRd Eight | [Guide](profiles/xrd-eight/README.md) | [Design](profiles/xrd-eight/DESIGN.md) | [Operations](profiles/xrd-eight/OPERATIONS.md) |

## Repository safety

This repository does not distribute:

- Cisco network operating-system images.
- Vendor archives, executables, or entitlement files.
- Passwords, secrets, or API tokens.
- Private SSH keys.
- Local `.env` files.
- Device configuration backups.
- Runtime NVRAM binaries.
- Container runtime state.

Obtain proprietary software from authorized sources and follow the applicable
license and entitlement requirements. Review [SECURITY.md](SECURITY.md) before
publishing a fork.

## Contributing

Contributions must preserve profile isolation, source-of-truth boundaries,
runtime safety, documentation accuracy, and licensed-image exclusions.

Run the validations appropriate to the files intentionally changed. Do not run
generators as a reflex when the active lab contains manual study state.

```bash
python3 -m compileall -q tools
python3 tools/validate_master_structure.py
python3 tools/validate_documentation.py
git diff --check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete workflow.

## License

Repository-authored documentation, diagrams, configurations, and supporting
scripts are available under the
[Creative Commons Attribution 4.0 International license](LICENSE). Vendor
software and network operating-system images are not covered by this license.

---

<div align="center">

Built as a reproducible study environment for serious CCIE Service Provider
practice, controlled experimentation, manual learning, and documented
engineering work.

</div>
