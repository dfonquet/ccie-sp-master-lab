# ISP-2 offline structural design

## Authority boundary

The repository is authoritative for physical structure, node identity,
management addressing and link addressing. The active routers are authoritative
for study configuration. Generated Master startup files must not be used to
replace uncaptured runtime EVPN, multicast, VPN or policy configuration.

ISP-2 is declared but not deployed. Its routing configuration is intentionally
manual and no generator supplies OSPF or BGP.

## Nodes and roles

| Node | Platform | Initial role |
|---|---|---|
| ASBR-ISP2 | XRd Control Plane | AS65002 boundary; eBGP belongs to phase 2 |
| RR-ISP2 | XRd Control Plane | Reachability target in phase 1; RR configuration is later |
| ISP2-P1, ISP2-P2 | IOL-XE | Core P routers |
| ISP2-P3, ISP2-P4 | IOL-XE | Transit routers and separate RR attachments |
| ISP2-P5 | IOL-XE | PE/service edge for SOURCE1 |
| SOURCE1 | Linux | Traffic source and capture host |

All IOL endpoints are restricted to `Ethernet0/1-3`. L055 attaches RR-ISP2 to
ISP2-P3, L056 attaches it to ISP2-P4, and L057 attaches SOURCE1 to ISP2-P5.

## Manual study sequence

1. Manually configure interfaces, loopbacks, OSPFv2 and OSPFv3 area 0.
2. Validate internal dual-stack connectivity, RR reachability and SOURCE1.
3. In a separate phase, configure IPv4/IPv6 eBGP between AS500 and AS65002.
4. Study iBGP/RR, labeled-unicast and Inter-AS VPN options independently.

L048 must never participate in ISP-1 IS-IS or SR-MPLS. AUTO1 remains unchanged.

## Deployment boundary

No deploy, destroy or restart is authorized by this structural change. Before a
future deployment, capture the active running configurations and reconcile them
with persistent startup state. XRd Control Plane forwarding and SOURCE1 tool
availability remain explicit acceptance gates.
