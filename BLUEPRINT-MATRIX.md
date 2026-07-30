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

CE2, CE5 and CE8 are dual-homed. They are used for Q-in-Q, E-Line access,
EVPN multihoming, MC-LAG design, PE-CE loop prevention and access failure
drills. Cloud-native BNG, CUPS and timing are treated as design modules unless
a suitable BNG image is added later.

## 4. High Availability and Fast Convergence — 10%

The two-plane P core provides deterministic failure points for:

- NSR, NSF and graceful restart.
- IGP/LDP convergence tuning.
- BGP-PIC.
- BFD.
- LFA, remote LFA and TI-LFA.
- RSVP-TE FRR.
- PCE and route-reflector failure.

## 5. Security — 10%

Planned services:

- IS-IS, OSPF, BGP, LDP and PCEP authentication.
- LPTS/CoPP, MPP, SSH and VTY hardening.
- Central AAA with RADIUS and TACACS+ test services.
- Secure syslog and SNMP.
- RPKI origin validation with Routinator.
- uRPF, RTBH, FlowSpec, ACL object groups and router hardening.
- TLS/mTLS for gNMI and gRPC.
- MACsec as configuration/design coverage where virtual interfaces permit.

## 6. Assurance and Automation — 20%

Deployed on `AUTO1`:

- Python 3.12 with Jinja2, YAML, JSON, XML and pytest.
- Ansible 2.21 with IOS, IOS XR, NSO and network-common collections.
- Netmiko, Scrapli, Nornir and NTC templates.
- ncclient for NETCONF and pyGNMI/grpcio for model-driven interfaces.
- Cisco pyATS and Genie 26.6.
- Reusable inventory, pre-check, backup and verification examples.

Next assurance services:

- Syslog, SNMP, NetFlow/IPFIX and model-driven telemetry collectors.
- SR performance measurement and TWAMP.
- An authorized Cisco NSO installation for service-package exercises.
- Secure ZTP and automated fault-injection workflows.

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
