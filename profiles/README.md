# Laboratory profiles

Only one heavy profile runs at a time. Images and the AUTO1 workstation are
shared; topology, addressing, protocol intent and generated configurations are
profile-specific.

| Profile | Main purpose | IGP/BGP model |
|---|---|---|
| `master` | Stable ISP services, AAA, RPKI, EVPN and multicast | AS 500, IS-IS, dual RR/PCE |
| `inter-as` | Runnable foundation for Options A/B/C and policy practice | Three AS, one RR per AS, IS-IS plus OSPFv2/OSPFv3 |
| `srv6` | Generated capability profile; live validation pending | IPv6-first IS-IS and SRv6 locators |

Profile guides:

- [Lab 1 — Master ISP](master/README.md)
- [Lab 2 — Inter-AS](inter-as/README.md)
- [Lab 3 — SRv6 capability](srv6/README.md)
- [Professional end-to-end operating guide](../docs/LAB-OPERATING-GUIDE.md)

Lifecycle is controlled with `labctl`; it refuses to deploy a second profile
while another Containerlab profile is running.
