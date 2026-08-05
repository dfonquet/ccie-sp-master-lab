# Laboratory profiles

Only one heavy profile runs at a time. Images and the AUTO1 workstation are
shared; topology, addressing, protocol intent and generated configurations are
profile-specific.

| Profile | Main purpose | IGP/BGP model |
|---|---|---|
| `master` | Stable ISP services, AAA, RPKI, EVPN and multicast | AS 500, IS-IS, dual RR/PCE |
| `inter-as` | Runnable foundation for Options A/B/C and policy practice | Three AS, one RR per AS, IS-IS plus OSPFv2/OSPFv3 |
| `srv6` | 21-node full study profile; staged rollout required | IPv6 IS-IS, SRv6 locators, RR/PE/CE practice |
| `full-dataplane` | Prepared 30-node forwarding profile; live acceptance pending | XRd vRouter, dual-stack IS-IS and SR-MPLS foundation |

Profile guides:

- [Lab 1 — Master ISP](master/README.md)
- [Lab 2 — Inter-AS](inter-as/README.md)
- [Lab 3 — SRv6 capability](srv6/README.md)
- [Professional end-to-end operating guide](../docs/LAB-OPERATING-GUIDE.md)
- [Lab 4 — Full Dataplane](full-dataplane/README.md)

Lifecycle is controlled with `labctl`; it refuses to deploy a second profile
while another Containerlab profile is running.
