# Deployment Status

Date: 2026-07-28

## Deployed

- 26 of 26 master-lab containers running.
- 14 Cisco XRd nodes running IOS XR 24.2.11.
- 11 Cisco IOL nodes running IOS XE Dublin 17.12.1.
- One Ubuntu 24.04 automation workstation, `AUTO1`, at `10.201.255.150`.
- 39 of 39 directly connected links passed IPv4 ping.
- 39 of 39 directly connected links passed IPv6 ping.
- Zero container restarts.
- Zero OOM events.
- Zero failed systemd units.

## Baselines applied

- `00-base`: dual-stack loopbacks and point-to-point addressing.
- `10-isis`: dual-stack Level-2 IS-IS on P, PE and RR/PCE nodes.
- `15-provider-standard`: banner, standardized provider IPv6 plan, IS-IS
  single topology, LFA/FRR, MPLS TE extensions and SR-TE hierarchy.
- `20-sr-mpls`: SRGB `16000-23999`, IPv4 Prefix-SIDs `16001-16014` and
  IPv6 Prefix-SIDs `16601-16614`.

## Control-plane validation

- P1 has five expected IS-IS neighbors.
- IS-IS LSDB contains 14 active Level-2 router LSPs.
- IPv4 and IPv6 loopback reachability between P1 and RR2 passed 5/5.
- P1 learned all 14 IPv4 SR Prefix-SIDs, labels `16001-16014`.
- P1 learned all 14 IPv6 SR Prefix-SIDs, labels `16601-16614`.
- MPLS traceroute from P1 to RR2 used label `16014`.
- IPv6 SR label `16614` is installed for RR2.

## Automation validation

- Python 3.12.3.
- Ansible Core 2.21.2 with IOS, IOS XR, NSO and supporting collections.
- Cisco pyATS and Genie 26.6.
- Netmiko 4.7.0, Nornir, Scrapli, ncclient and pyGNMI.
- 26 of 26 management SSH/CLI validations passed.
- Netmiko from `AUTO1` to P1 passed.
- The Ansible provider pre-check against P1 completed with zero failures.
- Windows reachability to `10.201.255.150`: ping 3/3 and TCP/22 open.

## Platform findings

- XRd 24.2.11 rejects reuse of one nodal Prefix-SID index by IPv4 and IPv6;
  IPv6 therefore uses indexes `601-614`.
- XRd Control Plane accepts IS-IS BFD commands but does not instantiate BFD
  sessions on these virtual links. The active baseline omits BFD and keeps
  LFA/FRR; BFD practice should use IOL, XRv9k or physical IOS XR.
- Pre-change running configurations for all 14 XRd nodes are stored under
  `artifacts/backups/20260728T235747Z-before-ipv6-standard`.

## Host resources with the lab running

- 60 GiB total RAM.
- Approximately 35 GiB used.
- Approximately 25 GiB available.
- 158 GB free on `/srv/netlab`.
- `AUTO1` uses approximately 8 MiB RAM while idle; its image is about 1.01 GB.

The separate two-node IOL validation topology is also still running.
