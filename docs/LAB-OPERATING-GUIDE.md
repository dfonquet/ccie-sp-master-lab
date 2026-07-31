# Professional CCIE SP Master Lab Operating Guide

This is the entry point for understanding, deploying, validating, modifying,
and recovering the lab. The repository is not merely a collection of
topologies: it implements a reproducible workflow in which inventories and
generators produce verifiable configurations, diagrams, and Containerlab files.

## 1. Purpose

The project supports CCIE Service Provider blueprint practice and realistic
service-provider scenarios without running several resource-heavy labs at the
same time.

| Profile | Status | Purpose |
|---|---|---|
| `master` | Runnable and validated | Redundant ISP backbone, SR-MPLS, RR/PCE, VPN, multicast, EVPN, AAA, and RPKI |
| `inter-as` | Runnable and validated | Three autonomous systems, multiple IGPs, eBGP, and Options A/B/C |
| `srv6` | Runnable 21-node profile; functional underlay validated | Redundant IPv6 IS-IS and SRv6 study environment |

The primary operational rule is simple: **only one heavy profile may be active
at a time**. This preserves RAM for XRd, prevents overlapping names and
networks, and ensures that every exercise starts from a known state.

## 2. Repository layout

```text
ccie-sp-master-lab/
├── README.md                    Project entry point and summary
├── labctl                       Safe lifecycle controller
├── inventory/                   Authoritative Lab 1 inventory
├── profiles/
│   ├── master/                  Lab 1 design and operating guide
│   ├── inter-as/                Lab 2 inventory and operating guide
│   └── srv6/                    Lab 3 full study profile and acceptance gates
├── tools/                       Generators and validators
├── templates/                   Jinja2 templates
├── configs/                     Phase-based rendered configurations
├── topology/                    Generated Containerlab topologies
├── automation/                  AUTO1 image and examples
└── docs/                        Architecture, operations, and troubleshooting
```

Profile-specific entry points:

- [Lab 1 — Master ISP](../profiles/master/README.md)
- [Lab 2 — Inter-AS](../profiles/inter-as/README.md)
- [Lab 3 — SRv6](../profiles/srv6/README.md)
- [Acceptance status](../STATUS.md)
- [Blueprint matrix](../BLUEPRINT-MATRIX.md)

## 3. Source of truth and change flow

The design follows this chain:

```text
Inventories + generator + templates
                 ↓
       rendered configurations
                 ↓
       Containerlab topology
                 ↓
       deployment and validation
```

For `master`, the primary sources are `tools/build_lab.py`,
`inventory/nodes.csv`, and `inventory/links.csv`. For `inter-as`, they are
`tools/build_inter_as.py`, `profiles/inter-as/nodes.csv`, and
`profiles/inter-as/links.csv`. For `srv6`, they are
`tools/build_srv6_capability.py`, `profiles/srv6/nodes.csv`, and
`profiles/srv6/links.csv`.

Do not manually edit generated files to make a persistent change. Update the
inventory, generator, or template, then render and inspect the diff. This keeps
the following artifacts aligned:

- Diagram.
- Topology.
- Addressing.
- Interface descriptions.
- Phase-based configurations.
- Documentation.

## 4. Profiles and architecture

### 4.1 Lab 1 — Master ISP

Lab 1 contains 30 nodes and 47 links:

- P1-P8: transit routers.
- PE1-PE8: provider edge and service termination.
- RR1-RR2: redundant Route Reflectors and PCE nodes.
- CE1-CE9 and C1-C2: customers and test endpoints.
- AUTO1: Ubuntu automation workstation.

Its underlay uses dual-stack IS-IS Level 2 and SR-MPLS. Separating the
underlay, RR/iBGP, and services makes it possible to practice failures without
mixing root causes. See the
[Master diagram and addressing guide](../profiles/master/README.md).

### 4.2 Lab 2 — Inter-AS

Lab 2 contains 23 nodes and 35 links:

- AS500: dual-stack IS-IS, RR500, four P/ASBR nodes, and four PEs.
- AS65100: OSPFv2/OSPFv3, RR65100, two P/ASBR nodes, and two PEs.
- AS65200: OSPFv2/OSPFv3, RR65200, two P/ASBR nodes, and two PEs.
- Five external links provide routing-policy and physical-diversity exercises.
- Three CEs support end-to-end service validation.

The exact topology and networks are documented in:

- [Inter-AS operations](../profiles/inter-as/README.md)
- [Inter-AS addressing](../profiles/inter-as/ADDRESSING.md)
- [Design and options](../profiles/inter-as/DESIGN.md)

### 4.3 Lab 3 — SRv6

Lab 3 contains 21 nodes and 33 links:

- P1-P6: redundant provider transit fabric.
- PE1-PE6: provider edges with six customer sites.
- RR1-RR2: redundant route reflectors attached to different core nodes.
- CE1-CE6: customer routers; CE2 and CE5 are dual-homed.
- AUTO1: automation and validation workstation.

The delivered baseline includes dual-stack-capable interfaces, an operational
IPv6 IS-IS Level 2 underlay, management access, and direct-link validation.
SRv6 locators, SRv6-TE policies, VPN services, TI-LFA, and uSID exercises are
intentionally left as student work on top of that known-good foundation.

- [SRv6 operations and addressing](../profiles/srv6/README.md)
- [SRv6 design](../profiles/srv6/DESIGN.md)
- [SRv6 validation evidence](../profiles/srv6/VALIDATION.md)
- [SRv6 topology diagram](../profiles/srv6/topology.svg)

## 5. Addressing model

Each profile has an independent management network and data-plane addressing
plan. Management addresses must not be reused by simultaneously active
profiles.

The `master` profile uses:

```text
Management:          10.201.255.0/24
IPv4 loopbacks:      10.0.0.<id>/32
IPv4 links:          10.255.0.0/31 onward
IPv6 loopbacks:      2001:db8:500:abcd::<id>/128
IPv6 core links:     2001:db8:1000:<link-id>::/127
```

The `/31` and `/127` prefixes represent point-to-point links without wasting
addresses. Loopbacks remain stable and serve as router IDs, BGP endpoints,
Prefix-SIDs, and convergence-test destinations.

The `srv6` profile uses:

```text
Management:          10.203.255.0/24
Provider loopbacks:  2001:db8:500:abcd::/64, allocated as /128
CE loopbacks:        2001:db8:700:ce::/64, allocated as /128
Provider links:      2001:db8:1000::/40, allocated as /127
PE-CE access links:  2001:db8:2000::/40, allocated as /127
SRv6 locator pool:   2001:db8:600::/40, one /64 per XRd node
```

The separate locator block keeps routable loopbacks distinct from local SID
space and makes locator summarization, policy, and troubleshooting explicit.

## 6. Server readiness

Create and load the local credential file before deployment:

```bash
cp .env.example .env
# Replace every placeholder in .env, then:
set -a
source .env
set +a
```

The real `.env` file is ignored by Git. Never place production credentials or
provider tokens in it. Then run the host checks:

```bash
cd /srv/netlab/labs/ccie-sp-master
docker ps --format '{{.Names}}' | grep '^clab-ccie-sp-' || \
  echo "No active labs"
free -h
uptime
df -h /srv/netlab
./labctl status
```

Do not deploy when another `clab-ccie-sp-*` lab exists, swap is in use,
available memory is below the profile gate, or host load remains abnormal.
The recommended Inter-AS gate is at least 12 GiB of available RAM. For the
full SRv6 profile, start with at least 45 GiB available RAM, 12 vCPUs, and
100 GiB of free lab storage. The validated 21-node steady state used about
32 GiB of RAM, left about 28 GiB available, and did not use swap.

## 7. Reproducible generation

### Master

```bash
python3 tools/build_lab.py
python3 tools/render_topology.py
```

### Inter-AS

```bash
python3 tools/build_inter_as.py
python3 tools/render_inter_as.py
```

### SRv6

```bash
python3 tools/build_srv6_capability.py
python3 tools/render_srv6.py
python3 tools/validate_srv6_artifacts.py
```

Inspect all generated changes:

```bash
git status --short
git diff --check
git diff -- inventory profiles topology configs docs
```

An unexpected change across many files usually indicates a modified global
rule. Review the diff before applying any configuration.

## 8. Safe lifecycle

### Check active profiles

```bash
./labctl status
```

### Deploy one profile

```bash
./labctl deploy master
# or, after destroying Master:
./labctl deploy inter-as
# or, after destroying Inter-AS:
./labctl deploy srv6
```

`labctl` rejects deployment when another profile is active.

### Inspect

```bash
./labctl inspect master
./labctl inspect inter-as
./labctl inspect srv6
```

### Destroy

```bash
./labctl destroy master
# or:
./labctl destroy inter-as
# or:
./labctl destroy srv6
```

Destroying a lab removes its ephemeral containers and links. Source files,
generated configurations, and documentation remain in the repository.

## 9. Phase-based configuration

Never apply every phase at once. Start with one or two canary nodes, validate
them, and only then expand the same phase.

Inter-AS example:

```bash
python3 tools/apply_phase.py 00-base \
  --profile inter-as --nodes P1,P3

python3 tools/apply_phase.py 10-igp \
  --profile inter-as --nodes P1,P3

python3 tools/apply_phase.py 20-bgp \
  --profile inter-as --nodes P3,RR500
```

SRv6 baseline example:

```bash
python3 tools/apply_phase.py 00-base \
  --profile srv6 --nodes P1,P2

python3 tools/apply_phase.py 10-isis-ipv6 \
  --profile srv6 --nodes P1,P2
```

After validating the canaries, expand those two baseline phases to the
remaining provider nodes. The locator and SRv6 control-plane phases are
optional study exercises, not prerequisites for the delivered underlay.

Operational order:

1. `00-base`: hostname, loopbacks, interfaces, and addressing.
2. IGP: IS-IS or OSPF according to the domain.
3. Transport: SR-MPLS, labels, and loopback reachability.
4. iBGP/RR: required address families and redundancy.
5. eBGP: external sessions and explicit routing policies.
6. Services: L3VPN, L2VPN/EVPN, multicast, or Inter-AS.
7. Security and assurance: AAA, RPKI, telemetry, and tests.
8. Failure drills: convergence, rollback, and recovery.

This order prevents troubleshooting BGP when the actual problem is an
interface, IGP adjacency, label, or next-hop reachability failure.

## 10. Validation

### Node management and CLI

```bash
python3 tools/validate_nodes.py \
  --inventory profiles/inter-as/nodes.csv --workers 4
```

### Directly connected links

```bash
python3 tools/validate_links.py \
  --profile inter-as --family both --workers 2
```

For Lab 3:

```bash
python3 tools/validate_nodes.py \
  --inventory profiles/srv6/nodes.csv --workers 4

python3 tools/validate_srv6_links.py
```

### Control-plane checks

Useful IOS XR commands:

```text
show interfaces brief
show route ipv4
show route ipv6
show isis adjacency
show ospf neighbor
show ospfv3 neighbor
show bgp summary
show bgp vpnv4 unicast summary
show bgp vpnv6 unicast summary
show mpls forwarding
```

Expected output depends on the profile and phase. Always compare results with
the inventory rather than a memorized count from another topology.

The current validated Inter-AS baseline is:

- 23/23 running nodes.
- 70/70 directional IPv4/IPv6 tests.
- IS-IS, OSPFv2, and OSPFv3 counts matching the inventory.
- RR-based iBGP at 6/6, 4/4, and 4/4 per VPN address family.
- eBGP at 10/10 IPv4 and 10/10 IPv6 endpoints.

The current validated SRv6 baseline is:

- 21/21 running nodes: 14 XRd, six IOL-XE, and AUTO1.
- 20/20 router management and CLI sessions operational.
- 66/66 directional IPv6 directly connected link tests passed.
- IPv6 IS-IS applied successfully to all 14 provider and RR nodes.
- Zero container restarts, OOM events, or swap use during validation.

## 11. Inter-AS practice workflow

Preserve a known-good logical baseline before testing each option:

1. Validate interfaces, loopbacks, IGP, and iBGP.
2. Configure IPv4/IPv6 eBGP and prefix/community policies.
3. Practice Option A and document VRFs, RDs, RTs, and PE-CE routes.
4. Remove Option A or restore the baseline.
5. Practice Option B with VPNv4/VPNv6 between ASBRs.
6. Restore the baseline.
7. Practice Option C with labeled unicast and multihop MP-BGP.
8. Introduce link, RR, and ASBR failures individually.
9. Record previous state, hypothesis, commands, and result.

Do not mix Options A, B, and C during initial validation. The objective is to
understand which information each model exchanges and where its control plane
resides.

## 11.1 SRv6 practice workflow

Start every SRv6 exercise from the validated IPv6 underlay:

1. Verify links, loopbacks, and all expected IS-IS adjacencies.
2. Allocate and advertise one locator per provider node.
3. Inspect locally allocated End and End.X SIDs.
4. Build an explicit SRv6-TE policy between selected PE nodes.
5. Add VPNv4/VPNv6 services and validate DT4/DT6 behavior.
6. Introduce a link failure and measure convergence or TI-LFA behavior.
7. Repeat with uSID only after the classic SRv6 behavior is understood.
8. Restore or redeploy the baseline before starting a different scenario.

## 12. AUTO1 and synchronization

AUTO1 runs Ansible, Python, pyATS/Genie, Netmiko, Nornir, Scrapli, NETCONF,
and gNMI. The recommended workflow is:

1. Synchronize or mount the repository in AUTO1.
2. Modify inventory, variables, or templates.
3. Render candidates.
4. Inspect the diff.
5. Run check mode or a pre-check.
6. Apply to canaries.
7. Run the post-check.
8. Expand to the remaining scope.
9. Commit only reproducible source files to Git.

The detailed process is documented in
[AUTO1 Source of Truth](AUTO1-SOURCE-OF-TRUTH.md).

## 13. Troubleshooting and recovery

Troubleshoot from the lowest layer upward:

```text
container → interface → addressing → IGP → labels/next hop
→ iBGP/RR → eBGP/policy → VPN/service
```

Documented failure modes include:

- A lab already deployed under the same name.
- An added link that requires XRd/IOL node recreation.
- IOL interfaces left `administratively down`.
- IOL initial dialog or NVRAM state.
- XRd Control Plane BFD limitations.
- IPv4/IPv6 Prefix-SID collision.
- OSPFv2/OSPFv3 applied to the wrong address family.
- A missing RPL policy that blocks BGP.
- BGP neighbor without its address family activated.
- False negatives in IPv6 parsers.

See:

- [General troubleshooting](TROUBLESHOOTING.md)
- [Master troubleshooting](../profiles/master/TROUBLESHOOTING.md)
- [Inter-AS troubleshooting](../profiles/inter-as/TROUBLESHOOTING.md)
- [SRv6 validation and troubleshooting](../profiles/srv6/VALIDATION.md)

## 14. Professional Git workflow

From AUTO1 or the server:

```bash
git status --short --branch
git pull --ff-only
git switch -c agent/change-name
```

After modifying and validating:

```bash
git diff --check
git status --short
git add <files-in-scope>
git commit -m "Brief concrete description"
git push -u origin agent/change-name
```

Do not commit Cisco images, private keys, passwords, tokens, configuration
backups containing secrets, or heavy artifacts. Review
[`SECURITY.md`](../SECURITY.md) and `.gitignore` before publishing.

## 15. Completion criteria

An exercise is complete when:

- The intended profile is the only active profile.
- Host memory, CPU, and swap remain within the gate.
- The source of truth reproduces every generated artifact.
- Links, IGP, and BGP match the inventory.
- The service works end to end.
- Failure and rollback have been tested.
- Documentation reflects the actual state.
- Git contains no secrets or proprietary binaries.

Official technical references are listed in
[Master REFERENCES](../profiles/master/REFERENCES.md) and
[Inter-AS REFERENCES](../profiles/inter-as/REFERENCES.md). SRv6 standards and
platform references are maintained in the
[SRv6 design guide](../profiles/srv6/DESIGN.md).
