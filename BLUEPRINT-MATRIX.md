# CCIE SP v5.1 Coverage Matrix

This matrix follows the official Cisco CCIE Service Provider v5.1 practical
exam domains.

## 1. Core Routing — 25%

| Topic | Master-lab use |
|---|---|
| IS-IS, OSPFv2, OSPFv3 | P/PE/RR underlay; multi-area and redistribution variants |
| IBGP, EBGP, MP-BGP | RR1/RR2, PE clients, CE eBGP, VPNv4/v6, BGP-LU and BGP-LS |
| Route policies and scale | Prefix sets, community sets, RPL, ORF, add-path and PIC |
| Multicast | PIM-SM/SSM/BIDIR, Anycast-RP, BSR, MSDP, IGMP/MLD |
| MPLS and LDP | LDP, targeted LDP, synchronization, graceful restart and mLDP |
| RSVP-TE | Explicit/dynamic tunnels, FRR, affinities, MAM/RDM and PBTS |
| Segment Routing | SR-MPLS, SR-TE, Flex-Algo, PCE/PCEP, SRv6 and uSID |

## 2. Architectures and Services — 25%

| Topic | Master-lab use |
|---|---|
| Unified MPLS | Convert the two backbone planes into separate IGP domains |
| Multi-domain SR-PCE | RR1/RR2 act as redundant PCEs |
| SLA/disjoint paths | Metrics, affinities and predefined SRLG values in `links.csv` |
| Carrier Ethernet | VPWS, VPLS, H-VPLS, EVPN-VPWS, ELAN and IRB |
| L3VPN | IPv4/IPv6 VRFs, OSPF/BGP PE-CE, inter-AS and shared services |
| Internet services | Peering policy, RTBH, FlowSpec and translation design |
| Multicast VPN | NG-mVPN profiles, PIM and mLDP core trees |
| QoS | Classification, marking, scheduling, MPLS QoS models and TE QoS |
| Mobile/optical architecture | Design exercises; hardware behavior is not emulated |

## 3. Access Connectivity — 10%

| Topic | Master-lab use |
|---|---|
| Dual-homed access | CE2, CE5 and CE8 attach to two PEs for access-failure and loop-prevention drills |
| Ethernet access | Q-in-Q, E-Line, VPWS and service-delimiting tag exercises |
| EVPN multihoming | Ethernet Segment, ESI, Designated Forwarder and all-active/single-active practice |
| MC-LAG | Control-plane design, split-brain analysis and comparison with EVPN multihoming |
| PE-CE routing | Static, OSPF, eBGP, multihop and Site-of-Origin loop-prevention scenarios |
| BNG and subscriber access | PPPoE/IPoE, DHCP, subscriber policy and scale treated as design modules until a suitable BNG image is available |
| CUPS and timing | Architecture and troubleshooting exercises; hardware timing behavior is not emulated |

## 4. High Availability and Fast Convergence — 10%

| Topic | Master-lab use |
|---|---|
| Stateful control-plane resiliency | NSR, NSF and graceful-restart behavior and verification |
| IGP convergence | IS-IS/OSPF timer tuning, overload behavior and deterministic link/node failures |
| MPLS convergence | LDP synchronization, graceful restart and label-path verification |
| BGP convergence | BGP-PIC, next-hop tracking, multipath and RR failure scenarios |
| Failure detection | BFD configuration and comparison with XRd Control Plane platform limitations |
| IP fast reroute | LFA, remote LFA and TI-LFA coverage over rings, rungs and diagonal paths |
| RSVP-TE protection | Link/node protection and fast-reroute design exercises |
| SR-TE/PCE resiliency | Candidate-path fallback, disjointness and PCE failover between RR1 and RR2 |
| Service resiliency | Dual-homed CE, PE failure and end-to-end VPN recovery measurements |

## 5. Security — 10%

| Topic | Master-lab use |
|---|---|
| Control-plane authentication | IS-IS, OSPF, BGP, LDP and PCEP authentication exercises |
| Infrastructure protection | LPTS/CoPP, MPP, SSH, VTY and management-plane hardening |
| AAA | Central RADIUS and TACACS+ services with local fallback and authorization testing |
| Routing security | RPKI origin validation with Routinator, prefix filtering and policy enforcement |
| DDoS response | uRPF, RTBH, FlowSpec, ACL object groups and mitigation workflows |
| Secure operations | Secure syslog, SNMPv3, role separation and auditable configuration changes |
| Model-driven security | TLS/mTLS for NETCONF, gNMI and gRPC management channels |
| Data-link security | MACsec configuration and design coverage where virtual interfaces permit |

## 6. Assurance and Automation — 20%

| Topic | Master-lab use |
|---|---|
| Python and data formats | Python 3.12, Jinja2, YAML, JSON, XML and pytest on `AUTO1` |
| Configuration automation | Ansible 2.21 with IOS, IOS XR, NSO and network-common collections |
| Device access frameworks | Netmiko, Scrapli, Nornir and NTC templates |
| Model-driven interfaces | ncclient for NETCONF and pyGNMI/grpcio for gNMI |
| State validation | Cisco pyATS and Genie 26.6 parsers and reusable verification jobs |
| Source-of-truth workflow | Inventory, variables, Jinja2 render, validation, check/diff, canary deployment and post-check |
| Change safety | Pre-checks, explicit confirmation, serial deployment, backups and rollback evidence |
| Monitoring | Syslog, SNMP, NetFlow/IPFIX and model-driven telemetry collector exercises |
| Performance assurance | SR performance measurement and TWAMP design and validation |
| Service orchestration | Authorized Cisco NSO installation and service-package exercises |
| Provisioning and faults | Secure ZTP and automated fault-injection workflows |

## Recommended study order

```text
IPv4/IPv6 addressing
  -> IS-IS/OSPF
  -> MPLS/LDP
  -> SR-MPLS and TI-LFA
  -> MP-BGP and L3VPN
  -> SR-TE and PCE
  -> Multicast and mVPN
  -> L2VPN/EVPN
  -> SRv6
  -> Security
  -> Assurance and automation
  -> Full eight-hour failure scenario
```
