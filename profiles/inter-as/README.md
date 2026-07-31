# Inter-AS operations

This profile is isolated from `master` and uses its own management network,
inventory, addressing and configuration phases.

## Scale

- 19 IOS XRd nodes, three IOL customer routers and `AUTO1`.
- AS500: four P/ASBR, four PE and RR500; dual-stack IS-IS Level 2.
- AS65100: two ASBR, two PE and RR65100; OSPFv2 for IPv4 and OSPFv3 for IPv6.
- AS65200: two ASBR, two PE and RR65200; OSPFv2 for IPv4 and OSPFv3 for IPv6.
- 35 links: 24 internal, five inter-provider and six customer links.

![Inter-AS topology](topology.svg)

## Documentation map

- [Design and protocol intent](DESIGN.md)
- [Addressing, loopbacks and identifiers](ADDRESSING.md)
- [Observed errors and solutions](TROUBLESHOOTING.md)
- [Cisco and IETF references](REFERENCES.md)

## Controlled lifecycle

Never deploy this profile while another `clab-ccie-sp-*` lab is running.

```bash
./labctl status
./labctl deploy inter-as
```

Apply phases serially from `AUTO1`, initially with one or two nodes:

```bash
python3 tools/apply_phase.py 00-base --profile inter-as --nodes P1,P3
python3 tools/apply_phase.py 10-igp --profile inter-as --nodes P1,P3
python3 tools/apply_phase.py 20-bgp --profile inter-as --nodes P3,RR500
```

After each canary succeeds, expand the same phase to the full profile. Validate
all directly connected links with:

```bash
python3 tools/validate_links.py --profile inter-as --family both --workers 2
```

The phase priority is deliberate: base addressing, then IGP, then local iBGP,
then external eBGP, and only afterwards Options A/B/C. A service phase must not
be used to hide an underlay failure.

## Acceptance gates

1. 23/23 containers running, zero restarts and zero OOM events.
2. No swap use; at least 12 GiB available inside the VM.
3. All 70 directly connected IPv4/IPv6 tests pass.
4. IS-IS, OSPFv2 and OSPFv3 adjacencies match the inventory.
5. Every PE/ASBR has redundant reachability to its local RR.
6. IPv4/IPv6 eBGP is established on the five external links.
7. Options A, B and C are introduced separately, with rollback between them.

## Last validated baseline

The latest integral test of this profile confirmed:

- 23/23 nodes running.
- 70/70 directional tests over directly connected links.
- AS500: ten operational IS-IS links and 16/16 loopback reachability tests.
- AS65100 and AS65200: 14/14 directional OSPFv2 adjacencies and 14/14
  OSPFv3 adjacencies per domain; 8/8 loopback tests in each AS.
- RR-based iBGP: 6/6, 4/4 and 4/4 sessions per VPN address family.
- Inter-AS eBGP: 10/10 IPv4 endpoints and 10/10 IPv6 endpoints established.

This is the known-good baseline, not a replacement for testing after each
change. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for commands, symptoms and
recovery procedures.
