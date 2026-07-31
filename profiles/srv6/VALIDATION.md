# Full-profile validation record

## Environment

| Item | Observed value |
|---|---|
| Host | Ubuntu 26.04 LTS VM on VMware |
| Compute | 12 vCPU, AMD-V nested virtualization |
| Memory | 60 GiB, 2 GiB swap |
| Storage | `/srv/netlab`, 196 GB, approximately 153 GB free before deployment |
| Containerlab | 0.77.0 |
| Docker | 29.1.3 |
| XRd | `ios-xr/xrd-control-plane:24.2.11` |
| IOL-XE | `vrnetlab/cisco_iol:17.12.01` |

## Evidence collected on 2026-07-31

| Gate | Result | Evidence |
|---|---|---|
| Static generation | PASS | 21 nodes, 33 links, 14 unique `/64` locator assignments |
| Containerlab parser | PASS | `containerlab apply --dry-run` accepted the topology |
| Deployment | PASS | 21/21 containers running |
| Management | PASS | TCP/22 open on 20/20 network devices |
| CLI | PASS | 14/14 XRd and 6/6 IOL authenticated successfully |
| Base configuration | PASS | P, PE, RR and CE batches applied without CLI failure |
| Direct links | PASS | 66/66 directional IPv6 tests passed |
| Stability | PASS | Zero OOM kills, zero unexpected restarts, zero swap use |
| Stable footprint | PASS | About 32 GiB used and 28 GiB available |

The first link-validation run reported eight false failures because IOS XR uses
`count` while IOS XE uses `repeat` for extended ping repetition. All eight were
CE-to-PE directions. The adaptive validator corrected the command per platform
and every direction passed. This is a tooling portability finding, not a link
failure.

## SRv6 capability evidence inherited from the canary

The earlier P1-P2-PE1 capability stages proved locator commit, IS-IS locator
advertisement, local End and End.X allocation, remote `/64` learning and basic
reachability to remote End SIDs. They did not install an SRv6-TE policy or VPN
service in the full profile. See [FINDINGS.md](FINDINGS.md).

## Operational boundary

The full topology was intentionally stopped at a functional underlay. A green
baseline does not claim that BGP, SRv6-TE, VPN, multicast, TI-LFA or uSID is
preconfigured. Those features require separate student acceptance evidence.
