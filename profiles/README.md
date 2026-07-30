# Laboratory profiles

Only one heavy profile runs at a time. Images and the AUTO1 workstation are
shared; topology, addressing, protocol intent and generated configurations are
profile-specific.

| Profile | Main purpose | IGP/BGP model |
|---|---|---|
| `master` | Stable ISP services, AAA, RPKI, EVPN and multicast | AS 500, IS-IS, dual RR/PCE |
| `inter-as` | Runnable foundation for Options A/B/C and policy practice | Three AS, one RR per AS, IS-IS plus OSPFv3 |
| `srv6` | SRv6 capabilities, policies and VPN services | IPv6-first IS-IS and SRv6 locators |

Lifecycle is controlled with `labctl`; it refuses to deploy a second profile
while another Containerlab profile is running.
