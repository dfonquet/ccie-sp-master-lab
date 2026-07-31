# Inter-AS dual-stack profile

## Provider domains

| Domain | ASN | IGP | RR | Provider nodes |
|---|---:|---|---|---|
| Metro/Core | 500 | IS-IS L2 IPv4/IPv6 | RR500 | P1-P4, PE1-PE4 |
| North ISP | 65100 | OSPFv2 IPv4 + OSPFv3 IPv6 | RR65100 | P5/P7, PE5/PE7 |
| South ISP | 65200 | OSPFv2 IPv4 + OSPFv3 IPv6 | RR65200 | P6/P8, PE6/PE8 |

Each domain has a complete iBGP hierarchy: PE and ASBR clients peer to their
local RR. Direct RR-to-RR eBGP multihop sessions are an optional exercise for
Option C and labeled-unicast; they are never required for Option A.

## Interconnection matrix

- Two physically diverse AS500-AS65100 links.
- Two physically diverse AS500-AS65200 links.
- One AS65100-AS65200 settlement-free/private-peering link.
- IPv4 and IPv6 eBGP on every external link.
- Independent inbound/outbound route policies and communities.

## Exercise phases

1. Global IPv4/IPv6 eBGP and policy control.
2. Inter-AS Option A using per-VRF subinterfaces.
3. Option B using VPNv4/VPNv6 between ASBRs with RT filtering.
4. Option C using labeled-unicast, RR reachability and multihop MP-BGP.
5. Failure, loop-prevention, SoO, graceful restart and convergence tests.

The profile has its own addressing and generated configurations; it never
overwrites the master profile.

## Generated implementation

`tools/build_inter_as.py` generates:

- `topology/ccie-sp-inter-as.clab.yml`
- `profiles/inter-as/nodes.csv` and `links.csv`
- `configs/inter-as/00-base`
- `configs/inter-as/10-igp`
- `configs/inter-as/20-bgp`

The implementation deliberately separates the phases. OSPFv2, OSPFv3 and BGP syntax
are canary-tested on XRd before being expanded to all nodes.
