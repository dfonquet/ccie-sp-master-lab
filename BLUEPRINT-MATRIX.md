# CCIE Service Provider v5.1 Coverage Matrix

> Blueprint-aligned study map for the three isolated Containerlab profiles in
> this repository. It distinguishes verified functionality from exercises,
> planned work, and subjects that require design study or another platform.

[![Blueprint](https://img.shields.io/badge/Blueprint-CCIE%20SP%20v5.1-0B5CAB?style=flat-square)](https://learningcontent.cisco.com/documents/marketing/exam-topics/CCIE_Service_Provider_v5.1_Exam_Topics_v4_edited-kz.pdf)
![Profiles](https://img.shields.io/badge/Profiles-Master%20%7C%20Inter--AS%20%7C%20SRv6-2F855A?style=flat-square)
![Scope](https://img.shields.io/badge/Scope-Study%20environment-orange?style=flat-square)

## Purpose and interpretation

The official CCIE Service Provider v5.1 practical exam evaluates the ability to
plan, design, implement, operate, and optimize complex dual-stack service
provider networks. This document maps those domains to the reusable foundations
and exercise opportunities provided by this repository.

This is a **coverage map**, not a claim that every blueprint objective is
preconfigured or fully emulated. The repository intentionally delivers a stable
base and leaves advanced services for the student to implement, validate,
troubleshoot, remove, and rebuild.

## Coverage legend

| State | Meaning |
|---|---|
| **Validated baseline** | Generated, deployed, and verified on the stated virtual platform |
| **Runnable exercise** | The topology and addressing support the exercise; the student supplies and validates the feature configuration |
| **Incremental** | Repository phase or design exists, but complete acceptance evidence is still being developed |
| **Design-only** | Study, configuration review, or troubleshooting is possible, but faithful data-plane or hardware behavior is not emulated |
| **External platform** | Requires a suitable image, Cisco NSO installation, physical equipment, or another authorized environment |

## Profile map

| Profile | Primary purpose | Current acceptance boundary |
|---|---|---|
| **Master** | Dual-stack provider core, SR-MPLS, redundant RR/PCE roles, services, security, and automation | Expanded IS-IS, SR-MPLS, and route-reflector foundation validated |
| **Inter-AS** | Multi-AS IGP/BGP design and Inter-AS Options A, B, and C | Runnable dual-stack baseline; advanced Inter-AS services remain student exercises |
| **SRv6** | IPv6 underlay, IS-IS, locators, endpoint behavior, and later SRv6 policy work | 21-node infrastructure, IPv6 IS-IS, and locator baseline validated; advanced SRv6 services remain incremental |

---

## 1. Core Routing — 25%

| Blueprint capability | Repository application | Profile | State |
|---|---|---|---|
| IS-IS | Dual-stack Level 2 provider underlay, point-to-point links, wide metrics, passive loopbacks, and deterministic failure tests | Master, SRv6 | **Validated baseline** |
| OSPFv2 and OSPFv3 | Alternate IGP domains, multi-area design, route filtering, summarization, and redistribution scenarios | Inter-AS | **Runnable exercise** |
| IGP scale and performance | Metrics, overload behavior, timer analysis, ECMP, LFA/TI-LFA topology evaluation, and controlled node/link failures | Master, Inter-AS, SRv6 | **Runnable exercise** |
| IBGP, EBGP, and MP-BGP | Redundant RR design, PE clients, CE eBGP, VPN address families, labeled-unicast, and BGP-LS study | Master, Inter-AS | **Incremental** |
| BGP policy and attributes | IOS XR route-policy language, prefix/community/as-path sets, local preference, MED, communities, and AS-path control | Master, Inter-AS | **Runnable exercise** |
| BGP scale and convergence | Add-path, ORF, next-hop tracking, multipath, graceful restart, and PIC analysis | Master, Inter-AS | **Runnable exercise** |
| Multicast | PIM-SM, SSM, BIDIR-PIM, static/BSR/Anycast-RP, MSDP, IGMP, MLD, mLDP, and Tree-SID study | Master | **Incremental** |
| MPLS forwarding and LDP | Label forwarding, LDP, targeted LDP, IGP synchronization, graceful restart, and mLDP | Master | **Runnable exercise** |
| MPLS traffic engineering | RSVP-TE, explicit/dynamic paths, affinities, FRR, bandwidth constraints, and policy steering | Master | **Incremental** |
| Segment Routing | SRGB, Prefix-SIDs, SR-MPLS, SR-TE, mapping/interworking, Flex-Algo, PCE/PCEP, and policy study | Master | **Validated baseline** for SR-MPLS; advanced functions are **incremental** |
| SRv6 | Locator allocation, IS-IS advertisement, endpoint behaviors, uSID, encapsulation, policies, and interworking-gateway study | SRv6 | **Incremental** |

### Engineering intent

The Master profile uses IS-IS as its authoritative provider underlay. OSPF is
kept for explicit comparative or Inter-AS exercises instead of enabling two IGPs
everywhere and hiding protocol boundaries. This preserves a realistic failure
domain and makes redistribution an intentional task.

---

## 2. Architectures and Services — 25%

| Blueprint capability | Repository application | Profile | State |
|---|---|---|---|
| Mobile infrastructure architecture | 5G transport, vRAN/O-RAN, MEC, slicing, and telco cloud design exercises mapped onto the provider topology | Master | **Design-only** |
| Clocking and synchronization | PTP/SyncE design, failure analysis, and verification-command study | Master | **Design-only** |
| Routed optical networking | Routed optical architecture, controller integration, and operational-failure analysis | Master | **External platform** |
| Unified MPLS | Repartition the provider into access/core IGP domains and practice BGP-LU reachability and label continuity | Master, Inter-AS | **Runnable exercise** |
| Multi-domain SR and PCE | Redundant RR/PCE roles, PCEP sessions, affinity, SRLG, disjointness, and candidate-path fallback | Master | **Incremental** |
| Carrier Ethernet | E-Line, E-LAN, E-Tree, VPWS, VPLS, H-VPLS, EVPN-VPWS, EVPN ELAN, and IRB | Master | **Runnable exercise** subject to image capabilities |
| EVPN multihoming | Ethernet Segment, ESI, DF election, aliasing, mass withdrawal, and all-active/single-active comparison | Master | **Runnable exercise** subject to virtual data-plane support |
| L3VPN | IPv4/IPv6 VRFs, route distinguishers/targets, PE-CE routing, shared services, extranets, and route leaking | Master, Inter-AS | **Runnable exercise** |
| Inter-AS VPN | Options A, B, and C, including control-plane boundaries, labels, next-hop behavior, and RR interaction | Inter-AS | **Runnable exercise** |
| Internet services | Transit/peering policy, RTBH, FlowSpec, default routing, NAT/translation design, and origin validation | Master, Inter-AS | **Runnable exercise** |
| Multicast VPN | Rosen/NG-mVPN concepts, PIM and mLDP core trees, profiles, and service verification | Master | **Incremental** |
| QoS and traffic management | Classification, marking, policing, shaping, scheduling, MPLS QoS models, and TE-aware design | Master | **Design-only** where XRd lacks faithful hardware queuing |

### Engineering intent

The topology provides redundant P, PE, RR/PCE, and dual-homed customer roles,
but does not ship every service already solved. Each service should be introduced
as a controlled change with a pre-check, candidate diff, post-check, and rollback
record.

---

## 3. Access Connectivity — 10%

| Blueprint capability | Repository application | Profile | State |
|---|---|---|---|
| Dual-homed customer access | CE2, CE5, and CE8 attach to two PEs for failure, loop-prevention, and service-recovery drills | Master | **Runnable exercise** |
| Ethernet access | VLAN encapsulation, Q-in-Q, E-Line, VPWS, and service-delimiting tag exercises | Master | **Runnable exercise** subject to image capabilities |
| EVPN multihoming | ESI, DF election, split-horizon, all-active/single-active operation, and failure convergence | Master | **Runnable exercise** subject to virtual data-plane support |
| MC-LAG | Design, split-brain analysis, state synchronization, and comparison with EVPN multihoming | Master | **Design-only** unless a supported image is added |
| PE-CE routing | Static routing, OSPF, eBGP, multihop, BFD evaluation, and Site-of-Origin loop prevention | Master, Inter-AS | **Runnable exercise** |
| BNG and subscriber services | PPPoE/IPoE, DHCP, subscriber policy, accounting, redundancy, and scale workflows | Master | **External platform** until a suitable authorized BNG image is integrated |
| CUPS, timing, and access architecture | Control/user-plane separation, timing design, and fault analysis | Master | **Design-only** |

---

## 4. High Availability and Fast Convergence — 10%

| Blueprint capability | Repository application | Profile | State |
|---|---|---|---|
| Stateful control-plane resiliency | NSR, NSF, graceful restart, route preservation, and control-plane restart analysis | Master | **Runnable exercise** within virtual-platform limits |
| IGP convergence | Timer tuning, overload bit, ECMP, deterministic link/node failures, and convergence measurement | Master, Inter-AS, SRv6 | **Runnable exercise** |
| MPLS convergence | LDP synchronization, graceful restart, label-path inspection, and black-hole analysis | Master | **Runnable exercise** |
| BGP convergence | BGP PIC, next-hop tracking, multipath, graceful restart, and RR/PE failure scenarios | Master, Inter-AS | **Runnable exercise** |
| Failure detection | BFD configuration, operational verification, and comparison with XRd Control Plane limitations | Master, SRv6 | **Design-only on affected XRd virtual links** |
| IP fast reroute | LFA, remote LFA, and TI-LFA over backbone rings, rungs, and diagonal paths | Master | **Runnable exercise** |
| RSVP-TE protection | Link/node protection, FRR, path-option fallback, and failure measurement | Master | **Incremental** |
| SR-TE/PCE resiliency | Candidate-path fallback, affinity/SRLG constraints, disjointness, and RR1/RR2 PCE failover | Master | **Incremental** |
| Service resiliency | Dual-homed CE, PE failure, RR failure, VPN recovery, and end-to-end loss/convergence measurement | Master, Inter-AS | **Runnable exercise** |

> **XRd boundary:** accepting a BFD configuration does not prove that the virtual
> platform instantiates a usable BFD session. Validate operational state and use
> IOL-XE, XRv9k, or physical equipment when the exercise requires real BFD
> behavior.

---

## 5. Security — 10%

| Blueprint capability | Repository application | Profile | State |
|---|---|---|---|
| Routing-protocol authentication | IS-IS, OSPF, BGP, LDP, and PCEP authentication, key rotation, and failure verification | Master, Inter-AS | **Runnable exercise** |
| Infrastructure protection | LPTS/CoPP, MPP, SSH, VTY, ACLs, control-plane exposure review, and management hardening | Master | **Runnable exercise** |
| AAA | Central RADIUS/TACACS+, local fallback, command authorization, accounting, role separation, and outage drills | Master | **Incremental** |
| Routing security | RPKI origin validation with an authorized validator, ROA-state policy, prefix limits, and route filtering | Master, Inter-AS | **Incremental** |
| DDoS response | uRPF, RTBH, FlowSpec, ACL/object-group policy, diversion, and mitigation validation | Master, Inter-AS | **Runnable exercise** |
| Secure operations | SNMPv3, protected syslog, configuration accountability, backups, and least-privilege workflows | Master | **Runnable exercise** |
| Model-driven security | TLS/mTLS and authorization for NETCONF, RESTCONF where supported, gNMI, and gRPC | Master | **Incremental** |
| Data-link security | MACsec configuration and design analysis | Master | **External platform** when faithful link encryption is required |

---

## 6. Assurance and Automation — 20%

| Blueprint capability | Repository application | Profile | State |
|---|---|---|---|
| Python and structured data | Python, Jinja2, YAML, JSON, XML, CSV source-of-truth data, and automated tests on `AUTO1` | All profiles | **Runnable exercise** |
| Configuration automation | Ansible collections for IOS/IOS XR, inventory-driven rendering, check mode, serial rollout, and idempotence testing | All profiles | **Runnable exercise** |
| Programmatic device access | Netmiko, Scrapli, Nornir, and NTC templates for controlled collection and change workflows | All profiles | **Runnable exercise** |
| Model-driven management | NETCONF with `ncclient`, gNMI with pyGNMI/grpcio, YANG-aware validation, and capability discovery | Master | **Incremental** |
| State validation | pyATS/Genie parsing, assertions, reusable test jobs, pre/post snapshots, and evidence generation | Master | **Incremental**; confirm the local AUTO1 image contains the complete toolchain |
| Source-of-truth workflow | CSV/inventory and variables → Jinja2 render → lint/validate → diff → canary → serial rollout → post-check | All profiles | **Validated workflow foundation** |
| Change safety | Active-lab guard, backups, explicit scope, check mode, commit confirmation, rollback, and acceptance evidence | All profiles | **Validated workflow foundation** |
| Monitoring and telemetry | Syslog, SNMP, NetFlow/IPFIX, streaming telemetry, collectors, dashboards, and alert validation | Master | **Runnable exercise** |
| Performance assurance | TWAMP, delay/loss measurement, SR performance measurement, and baseline comparison | Master | **Incremental** |
| Service orchestration | Cisco NSO installation, device onboarding, service models, dry-run, commit, and rollback | Master | **External platform**; authorized NSO software required |
| Provisioning and fault injection | Secure ZTP, generated configurations, deterministic failure injection, recovery checks, and reporting | All profiles | **Runnable exercise** |

## Recommended progression

```text
Foundation
  Addressing and interface verification
    -> IS-IS / OSPF underlay
    -> MPLS / LDP
    -> SR-MPLS and fast convergence

Control plane and services
  MP-BGP and routing policy
    -> L3VPN
    -> SR-TE and PCE
    -> Multicast and mVPN
    -> L2VPN and EVPN
    -> Inter-AS Options A / B / C

Advanced transport and operations
  SRv6 foundation and policies
    -> Security, AAA, and RPKI
    -> Assurance and automation
    -> Timed design / deploy / operate / optimize scenario
```

## Evidence model

A topic should be promoted to **Validated baseline** only when the repository
contains reproducible evidence for all applicable gates:

1. Static generation and schema checks pass.
2. The intended profile deploys without another lab running.
3. Every required node reaches a healthy state.
4. Management access and CLI authentication succeed.
5. The candidate configuration commits without hidden failures.
6. Protocol and forwarding state match the expected result.
7. Negative and failure-path tests behave as designed.
8. Resource consumption remains within the host safety gate.
9. Destroy removes the containers, links, and management network.
10. Documentation records commands, results, limitations, and rollback steps.

## Platform and scope boundaries

- Cisco images, licenses, secrets, private keys, and generated device backups are
  not distributed by this repository.
- XRd Control Plane is strong for provider control-plane practice but does not
  reproduce every physical forwarding, queuing, timing, optical, MACsec, or
  line-card behavior.
- IOL-XE is used for customer/access roles where its verified feature set is
  appropriate; it is not treated as a universal substitute for physical IOS XE.
- Advanced phases remain deliberately unsolved so the repository functions as a
  study environment rather than a collection of completed answers.
- The official Cisco blueprint remains authoritative if its wording or scope
  differs from this repository mapping.

## Authoritative references

- [Cisco CCIE Service Provider v5.1 practical exam topics](https://learningcontent.cisco.com/documents/marketing/exam-topics/CCIE_Service_Provider_v5.1_Exam_Topics_v4_edited-kz.pdf)
- [Cisco CCIE Service Provider certification](https://www.cisco.com/site/us/en/learn/training-certifications/certifications/service-provider/ccie-service-provider/index.html)
- [Deployment and acceptance status](STATUS.md)
- [Professional lab operating guide](docs/LAB-OPERATING-GUIDE.md)
- [Containerlab host, image, and AUTO1 build guide](docs/CONTAINERLAB-INSTALLATION.md)

---

> **Repository position:** this lab extends beyond the blueprint where doing so
> improves operational realism, but it does not represent itself as an official
> Cisco exam environment or as a replacement for authorized Cisco training.
