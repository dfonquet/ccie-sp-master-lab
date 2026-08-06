# XRd Eight Architecture and Design
![Authoritative XRd Eight topology](topology.svg)

## Design objective

The profile concentrates the forwarding-plane topics of the CCIE Service Provider journey into the largest topology accepted on the measured host without swap or OOM events. Eight XRd vRouters are the normal ceiling for this VM. IOL-XE and Linux provide economical customer and operations roles.

## Redundancy model

The P fabric is a four-node complete graph: six internal links provide several equal- and unequal-cost paths without depending on a single ring or diagonal. PE1, PE2 and PE3 each terminate on two different P routers. R2 has two core attachments so it can later become an RR, stateful/stateless PCE candidate and multicast RP candidate.

| Logical role | Containerlab node | Attachments |
|---|---|---|
| P1 | XR1 | P2, P3, P4, PE1, PE3, RR |
| P2 | XR2 | P1, P3, P4, PE2 |
| P3 | R1 | P1, P2, P4, PE1 |
| P4 | R3 | P1, P2, P3, PE2, PE3, RR |
| PE1 | R5 | P1, P3, CE1 x2 |
| PE2 | XR4 | P2, P4, CE2 x2 |
| PE3 | XR3 | P1, P4, CE3 x2 |
| RR/PCE/RP | R2 | P1, P4 |

## Why XRd vRouter 26.2.1

The vRouter variant provides a real forwarding plane required for packet-level SR, VPN, EVPN, multicast and convergence exercises. The image was cryptographically verified with Cisco's supplied certificate, signature and verification script before it was loaded and wrapped for Containerlab. The local vrnetlab wrapper uses `igb` interfaces because that mapping was validated in the single-node dataplane canary.

## Study boundary

The topology provides infrastructure and address planning. It deliberately does not solve:

- MP-BGP route reflection or VPN address families;
- L3VPN, VPWS, VPLS, EVPN or EVPN multihoming;
- PCE/PCEP, SR policies or disjointness constraints;
- multicast RP, mLDP, Tree-SID or mVPN;
- SRv6 locators, policies or endpoint behaviors;
- centralized AAA or RPKI origin validation;
- QoS, telemetry and failure scoring.

These features should be added manually or through reviewed AUTO1 playbooks, one phase at a time.

## Runtime envelope

| Measurement | Observed result |
|---|---:|
| XRd vRouter nodes | 8 |
| Total containers | 12 |
| VM allocation | 16 vCPU / 86 GiB RAM |
| RAM used after deployment | approximately 70 GiB |
| RAM available | approximately 16 GiB |
| Swap | 0 B |
| XR restarts / OOM | 0 / false |

Do not add another XRd node or run another heavy profile concurrently. Destroy this profile before starting Master, Inter-AS, SRv6, Full Dataplane or JNCIE-SP.
