# Lab design catalog

This catalog explains the purpose and routing model of each mutually exclusive
profile. Detailed per-node assignments remain in each profile's CSV inventory.

| Profile | Scale | Management | Provider IGP | Primary study purpose |
|---|---:|---|---|---|
| Master | 30 nodes | `10.201.255.0/24` | IS-IS Level 2, IPv4/IPv6 | CCIE SP integrated services, SR-MPLS, VPN, multicast, HA and automation |
| Inter-AS | 23 nodes | `10.202.255.0/24` | AS500 IS-IS; AS65100/65200 OSPFv2 + OSPFv3 | Inter-AS Options A/B/C, eBGP, per-AS RR design and policy boundaries |
| SRv6 | 21 nodes | `10.203.255.0/24` | IPv6-only IS-IS Level 2 | SRv6 locators, policies, services, uSID, convergence and automation |
| XRd Eight | 12 nodes | `10.207.255.0/24` | Student-selected dual-stack IS-IS/SR-MPLS foundation | Resource-bounded real forwarding, P/PE redundancy, PCE, multicast, VPN, EVPN, AAA and RPKI practice |

## Why the profiles are separate

The profiles represent different operational questions and intentionally use
different management subnets. Keeping them separate prevents configuration
leakage, makes evidence attributable to one design, and keeps CPU/RAM inside
the validated envelope. `labctl` enforces the one-heavy-profile-at-a-time rule.

## Master profile

The Master profile is the broadest CCIE SP environment. Its provider core uses
IS-IS Level 2 because one protocol can carry both address families and SR-MPLS
extensions consistently. It keeps stable IPv4 router IDs while adding a
structured IPv6 plan. See [architecture](ARCHITECTURE.md),
[addressing](ADDRESSING.md), [build history](BUILD-GUIDE.md) and
[validation](VALIDATION.md).

## Inter-AS profile

The Inter-AS profile deliberately mixes IGPs to create realistic domain
boundaries: IS-IS in AS500 and OSPFv2/OSPFv3 in AS65100 and AS65200. Each AS has
its own RR candidate, and external links are visually and operationally
separate from internal links. See the
[Inter-AS profile guide](../profiles/inter-as/README.md) and
[diagram](../profiles/inter-as/topology.svg).

## SRv6 profile

The SRv6 profile is IPv6-first and uses full-length SIDs. The operational
baseline stops at working interfaces and provider IS-IS so students configure
locators, SRv6-TE, BGP and services themselves. See the
[SRv6 design](../profiles/srv6/DESIGN.md),
[validation record](../profiles/srv6/VALIDATION.md) and
[diagram](../profiles/srv6/topology.svg).

## Common operating model

1. Confirm no other `clab-*` profile is active.
2. Load credentials from local environment variables.
3. Generate and statically validate artifacts.
4. Deploy with profile-specific topology.
5. Validate management and resources before configuration.
6. Back up before each phase.
7. Apply small batches and record evidence.
8. Destroy the profile before starting another.

Installation and host rationale are documented in
[CONTAINERLAB-INSTALLATION.md](CONTAINERLAB-INSTALLATION.md).

## XRd Eight profile

XRd Eight is the accepted compact forwarding profile: eight XRd vRouter nodes,
three IOL-XE customer nodes and AUTO1. Its four-node P layer is a complete graph,
each PE is dual-attached to the provider core, and R2 is reserved for RR, PCE and
multicast-RP exercises. See the [profile guide](../profiles/xrd-eight/README.md),
[operations](../profiles/xrd-eight/OPERATIONS.md) and
[topology](../profiles/xrd-eight/topology.svg).
