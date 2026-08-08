# XRd Eight v2 — Validation and Acceptance

> **Validation framework for the XRd Eight v2 full-dataplane Service Provider laboratory.**
>
> This document defines the acceptance boundaries between repository correctness, generated configuration, Containerlab runtime state, router protocol state and service-level behavior.

XRd Eight v2 uses a layered validation model.

A successful Python build does not prove that Containerlab can deploy the topology.

A successful Containerlab deployment does not prove that the routers are healthy.

Healthy routers do not prove that IS-IS is converged.

A converged IGP does not prove that SR-MPLS forwarding is correct.

Likewise, correct transport does not prove that BGP, VPN, EVPN or other services are operational.

For that reason, validation is performed incrementally.

The intended acceptance chain is:

```text
Repository Integrity
        |
        v
Deterministic Generation
        |
        v
Static Addressing Validation
        |
        v
Topology Validation
        |
        v
Container Runtime
        |
        v
Management Reachability
        |
        v
Physical Interfaces
        |
        v
IPv4 / IPv6 Transport
        |
        v
IS-IS
        |
        v
BFD / Convergence
        |
        v
SR-MPLS
        |
        v
BGP
        |
        v
VPN / EVPN / Services
        |
        v
Failure and Recovery Validation
```

Each stage has its own acceptance criteria.

---

## Validation Philosophy

XRd Eight v2 distinguishes four different kinds of correctness.

| Validation Domain | Question |
| --- | --- |
| Repository validation | Is the Source of Truth internally consistent? |
| Generation validation | Does the builder reproducibly generate the expected artifacts? |
| Runtime validation | Can the complete topology operate successfully on the host? |
| Protocol validation | Do routing, MPLS and service protocols actually behave as intended? |

These domains must not be confused.

For example:

```text
python3 tools/build_xrd_eight.py
```

returning successfully means that the generator completed.

It does **not** mean:

```text
IS-IS is converged
```

or:

```text
SR-MPLS forwarding works
```

Those require independent runtime evidence.

---

# Acceptance Status Model

Every capability should be considered one of the following:

| Status | Meaning |
| --- | --- |
| `DESIGNED` | Architecture exists in the repository |
| `STATICALLY VALIDATED` | Generated files and structural checks pass |
| `RUNTIME VALIDATED` | Behavior has been observed successfully in the running lab |
| `SERVICE VALIDATED` | End-to-end protocol/service behavior has been demonstrated |
| `NOT YET VALIDATED` | No sufficient evidence has been collected |

The distinction matters because XRd Eight is intentionally developed in phases.

---

# Historical Runtime Evidence

A previous full-dataplane deployment of the XRd Eight lab family was successfully operated on the Ubuntu virtualization host on **2026-08-06**.

That deployment demonstrated that the host is capable of simultaneously running:

```text
8 XRd vRouters
3 IOL-XE routers
1 AUTO1 Linux container
-------------------------
12 total containers
```

Observed runtime evidence included:

- `12/12` containers running;
- `8/8` XRd vRouters reporting `healthy`;
- every XRd container reporting restart count `0`;
- every XRd container reporting `oom=false`;
- all three IOL-XE CE containers remaining operational;
- `AUTO1` remaining operational;
- no XRd container terminating unexpectedly;
- no OOM event observed;
- no swap usage observed;
- no final eight-node deployment indication of `UnicodeDecodeError`;
- no fatal Python traceback associated with the completed deployment;
- no XR panic observed during the accepted runtime window;
- approximately `70 GiB` RAM consumed from an `86 GiB` VM allocation;
- approximately `16 GiB` RAM remaining available.

Reference host envelope:

| Measurement | Observed Result |
| --- | ---: |
| XRd vRouter nodes | `8` |
| IOL-XE nodes | `3` |
| Automation nodes | `1` |
| Total containers | `12` |
| VM allocation during observation | `16 vCPU / 86 GiB RAM` |
| RAM used | approximately `70 GiB` |
| RAM available | approximately `16 GiB` |
| Swap | `0 B` |
| XRd restart count | `0` |
| XRd OOM state | `false` |

---

# Historical Evidence Boundary

The previous runtime evidence validates the **host capacity, container images and ability to operate eight XRd full-dataplane nodes simultaneously**.

It does **not** constitute final runtime acceptance of the current XRd Eight v2 generated protocol foundation.

During the earlier runtime, Containerlab reused startup files that had been copied into:

```text
topology/clab-ccie-sp-xrd-eight/
```

during a previous deployment.

As a consequence, the routers observed during that runtime retained the historical IS-IS process:

```text
XR8-SP
```

while the current v2 Source of Truth generates:

```text
500-SP
```

Therefore:

```text
Historical Runtime
        |
        +-- Host capacity              ACCEPTED
        |
        +-- 8 XRd full dataplanes      ACCEPTED
        |
        +-- Container stability        ACCEPTED
        |
        +-- Current v2 IS-IS config    NOT ACCEPTED FROM THAT RUN
```

This distinction is intentional.

The repository must never claim live protocol acceptance for configuration that was not actually running during the observed validation window.

---

# Current XRd Eight v2 Acceptance Boundary

The current v2 repository introduces a redesigned:

- node naming model;
- Node-ID model;
- loopback allocation;
- point-to-point addressing plan;
- physical-link model;
- CE multihoming layout;
- IS-IS process `500-SP`;
- IS-IS NET allocation;
- SR-MPLS Prefix-SID model;
- topology renderer;
- addressing validator;
- deterministic CSV generation.

The current Source of Truth has already undergone static validation.

The clean v2 deployment must independently prove the runtime layers.

Current conceptual status:

| Area | Current Acceptance |
| --- | --- |
| Repository topology | `STATICALLY VALIDATED` |
| Node inventory | `STATICALLY VALIDATED` |
| Link inventory | `STATICALLY VALIDATED` |
| IPv4 P2P addressing | `STATICALLY VALIDATED` |
| IPv6 P2P addressing | `STATICALLY VALIDATED` |
| Provider loopbacks | `STATICALLY VALIDATED` |
| Node-ID model | `STATICALLY VALIDATED` |
| IS-IS `500-SP` generation | `STATICALLY VALIDATED` |
| SR-MPLS Prefix-SID generation | `STATICALLY VALIDATED` |
| 12-container host capacity | `HISTORICALLY RUNTIME VALIDATED` |
| Current v2 clean deployment | `RUNTIME VALIDATION REQUIRED` |
| Current v2 IS-IS adjacency state | `RUNTIME VALIDATION REQUIRED` |
| Current v2 SR-MPLS forwarding | `RUNTIME VALIDATION REQUIRED` |
| BGP | `NOT YET VALIDATED` |
| VPN services | `NOT YET VALIDATED` |
| EVPN | `NOT YET VALIDATED` |
| EVPN multihoming | `NOT YET VALIDATED` |

---

# Repository Integrity Validation

Before any runtime validation, confirm that the repository is synchronized and clean.

```bash
cd /srv/netlab/labs/ccie-sp-master

git switch main
git pull --ff-only origin main

git status --short --branch
git rev-parse --short HEAD
git rev-parse --short origin/main
```

Expected conditions:

```text
local HEAD == origin/main
working tree clean
```

Runtime validation should normally be performed against an identifiable Git commit.

This allows collected evidence to be associated with a specific repository state.

---

# Deterministic Generation Validation

Generate the profile:

```bash
python3 tools/build_xrd_eight.py
```

Expected summary:

```text
Generated topology: topology/ccie-sp-xrd-eight.clab.yml
Generated ISP configs: 8
Generated CE configs: 3
Generated links: 19
Repository profile: profiles/xrd-eight
```

After generation:

```bash
git status --short
```

should show no unexpected modifications when the Source of Truth has not changed.

This validates build determinism.

---

## CSV Determinism

Generated CSV files use explicit LF line endings.

The builder must not cause:

```text
nodes.csv
links.csv
```

to appear modified solely because of CRLF/LF conversion.

A no-change regeneration should therefore leave Git clean.

This behavior is part of the repository acceptance criteria.

---

# Python Static Validation

Compile the Python tooling:

```bash
python3 -m py_compile \
  tools/build_xrd_eight.py \
  tools/render_xrd_eight.py \
  tools/validate_xrd_eight_addressing.py
```

Expected result:

```text
<no output>
```

Any syntax error is a deployment blocker.

---

# Addressing Validation

Run:

```bash
python3 tools/validate_xrd_eight_addressing.py
```

The current v2 addressing model is expected to report:

```text
ADDRESSING VALIDATION: PASSED

Links validated        : 19
IPv4 /31 networks      : 19
IPv6 /127 networks     : 19
IPv4 endpoint addresses: 38
IPv6 endpoint addresses: 38
IPv4 loopbacks         : 8
IPv6 loopbacks         : 8
Overlapping networks   : 0
Duplicate addresses    : 0
```

The validator checks:

- expected link definitions;
- IPv4 `/31` prefix length;
- IPv6 `/127` prefix length;
- endpoint membership in the same IPv4 network;
- endpoint membership in the same IPv6 network;
- duplicate IPv4 addresses;
- duplicate IPv6 addresses;
- overlapping IPv4 networks;
- overlapping IPv6 networks;
- IPv4 `/32` loopbacks;
- IPv6 `/128` loopbacks;
- duplicate loopbacks;
- loopback/link overlap.

Deployment should not continue when this validator fails.

---

# Topology Rendering Validation

Generate the topology diagram:

```bash
python3 tools/render_xrd_eight.py
```

Expected output should confirm rendering of:

```text
profiles/xrd-eight/topology.svg
```

The generated SVG should represent:

```text
12 nodes
8 XRd vRouters
3 IOL-XE CE routers
1 AUTO1 node
19 physical links
```

The topology must not contain historical aliases such as:

```text
XR1
XR2
XR3
XR4
R1
R2
R3
R4
R5
R7
R10
```

The current architecture uses only:

```text
P1
P2
P3
P4
PE1
PE2
PE3
RR
CE1
CE2
CE3
AUTO1
```

---

# Generated Configuration Static Checks

The generated foundation must contain eight provider IS-IS instances using:

```text
500-SP
```

Check:

```bash
grep -h '^router isis 500-SP$' \
  configs/xrd-eight/00-foundation/*.cfg | wc -l
```

Expected:

```text
8
```

---

## Segment Routing AF Checks

The generated provider configuration contains Segment Routing under both IPv4 and IPv6 address families.

Check:

```bash
grep -hE '^  segment-routing mpls( sr-prefer)?$' \
  configs/xrd-eight/00-foundation/*.cfg | wc -l
```

Expected:

```text
16
```

This represents:

```text
8 IPv4 AF SR-MPLS statements
+
8 IPv6 AF SR-MPLS statements
=
16
```

---

## Prefix-SID Checks

Each provider node receives:

```text
1 IPv4 Prefix-SID
1 IPv6 Prefix-SID
```

Check:

```bash
grep -h '^   prefix-sid index' \
  configs/xrd-eight/00-foundation/*.cfg | wc -l
```

Expected:

```text
16
```

---

# Expected Prefix-SID Allocation

IPv4 Prefix-SID indices:

| Node | Index |
| --- | ---: |
| `P1` | `1` |
| `P2` | `2` |
| `P3` | `3` |
| `P4` | `4` |
| `PE1` | `5` |
| `PE2` | `6` |
| `PE3` | `7` |
| `RR` | `8` |

IPv6 Prefix-SID indices:

| Node | Index |
| --- | ---: |
| `P1` | `601` |
| `P2` | `602` |
| `P3` | `603` |
| `P4` | `604` |
| `PE1` | `605` |
| `PE2` | `606` |
| `PE3` | `607` |
| `RR` | `608` |

With SRGB:

```text
16000-23999
```

the expected index-to-label correlation begins as:

```text
IPv4 P1 SID 1   -> 16001
IPv4 RR SID 8   -> 16008

IPv6 P1 SID 601 -> 16601
IPv6 RR SID 608 -> 16608
```

Actual runtime label installation must still be independently validated.

---

# Node-ID Validation

The provider identity model must remain:

| Node | Node ID |
| --- | ---: |
| `P1` | `1` |
| `P2` | `2` |
| `P3` | `3` |
| `P4` | `4` |
| `PE1` | `5` |
| `PE2` | `6` |
| `PE3` | `7` |
| `RR` | `8` |

The Node ID correlates with:

```text
IPv4 Loopback
IPv6 Loopback
IS-IS System ID
IPv4 Prefix-SID
IPv6 Prefix-SID
```

Any unintended divergence should be treated as a static validation failure.

---

# IS-IS NET Validation

Expected NET allocation:

| Node | IS-IS NET |
| --- | --- |
| `P1` | `49.0001.0000.0000.0001.00` |
| `P2` | `49.0001.0000.0000.0002.00` |
| `P3` | `49.0001.0000.0000.0003.00` |
| `P4` | `49.0001.0000.0000.0004.00` |
| `PE1` | `49.0001.0000.0000.0005.00` |
| `PE2` | `49.0001.0000.0000.0006.00` |
| `PE3` | `49.0001.0000.0000.0007.00` |
| `RR` | `49.0001.0000.0000.0008.00` |

All eight must remain unique.

---

# Physical Topology Acceptance

The static topology contains:

```text
19 physical links
```

distributed as:

| Link Type | Expected |
| --- | ---: |
| Provider Core | `6` |
| Provider Edge | `6` |
| Control Plane | `2` |
| Customer Edge | `5` |
| **Total** | **19** |

Provider Core:

```text
P1-P2
P1-P3
P1-P4
P2-P3
P2-P4
P3-P4
```

Provider Edge:

```text
PE1-P1
PE1-P3
PE2-P2
PE2-P4
PE3-P1
PE3-P4
```

Control Plane:

```text
RR-P1
RR-P4
```

Customer Edge:

```text
CE1-PE1
CE1-PE2
CE2-PE2
CE3-PE3
CE3-PE2
```

Any generated topology containing a different link count requires review before deployment.

---

# Pre-Deployment Image Acceptance

Verify required local images:

```bash
for image in \
  vrnetlab/cisco_xrd-vrouter:26.2.1 \
  vrnetlab/cisco_iol:17.12.01 \
  ccie-sp-automation:1.0
do
  echo "===== $image ====="

  docker image inspect "$image" \
    --format 'ID={{.Id}} SIZE={{.Size}}' 2>/dev/null \
    || echo "IMAGE NOT FOUND"
done
```

Expected:

```text
XRd image present
IOL-XE image present
AUTO1 image present
```

Missing images block deployment.

---

# AUTO1 Secret Acceptance

The full profile requires:

```text
CCIE_AUTO_PASSWORD
```

Verify without printing the value:

```bash
if [ -n "${CCIE_AUTO_PASSWORD:-}" ]; then
  echo "CCIE_AUTO_PASSWORD: SET"
else
  echo "CCIE_AUTO_PASSWORD: NOT SET"
fi
```

Required:

```text
CCIE_AUTO_PASSWORD: SET
```

---

# Stale Runtime Protection

Before deployment:

```bash
docker ps -a --format '{{.Names}}' | \
  grep '^clab-ccie-sp-xrd-eight-' || \
  echo "PASS: no existing XRd Eight containers"
```

Expected:

```text
PASS: no existing XRd Eight containers
```

Also verify that stale runtime state is not unintentionally being reused.

The normal lifecycle uses:

```text
containerlab destroy --cleanup
```

specifically to prevent previous runtime startup configuration from overriding regenerated repository artifacts.

---

# Runtime Acceptance Stage 1 — Container Creation

After `deploy-full`, the complete profile must eventually contain:

```text
12 containers
```

Composition:

| Type | Expected |
| --- | ---: |
| XRd vRouter | `8` |
| IOL-XE | `3` |
| AUTO1 | `1` |
| **Total** | **12** |

Check:

```bash
docker ps -a \
  --filter name=clab-ccie-sp-xrd-eight \
  --format '{{.Names}}' | wc -l
```

Expected:

```text
12
```

---

# Runtime Acceptance Stage 2 — XRd Health

Inspect:

```bash
for node in P1 P2 P3 P4 PE1 PE2 PE3 RR; do
  docker inspect "clab-ccie-sp-xrd-eight-$node" \
    --format '{{.Name}} health={{if .State.Health}}{{.State.Health.Status}}{{end}} restart={{.RestartCount}} oom={{.State.OOMKilled}}'
done
```

Target steady state:

```text
health=healthy
restart=0
oom=false
```

for all eight XRd nodes.

A node still starting within its normal startup window is not automatically considered failed.

Persistent unhealthy state requires investigation.

---

# Runtime Acceptance Stage 3 — Host Resources

Observe:

```bash
./profiles/xrd-eight/labctl resources
```

and:

```bash
free -h
uptime
```

Reference historical envelope:

```text
approximately 70 GiB used
approximately 16 GiB available
0 B swap
```

These are reference measurements rather than hard fixed values.

Protocol scale and automation workload may change actual usage.

---

## Runtime Resource Stop Conditions

Stop and investigate if:

- an XRd instance is OOM-killed;
- XRd containers restart repeatedly;
- one or more routers exit;
- sustained host memory exhaustion occurs;
- unexpected swap pressure appears;
- the host becomes unstable;
- another heavy topology is consuming significant resources concurrently.

---

# Runtime Acceptance Stage 4 — Management Reachability

All twelve management addresses must be reachable.

| Node | Management IPv4 |
| --- | --- |
| `P1` | `10.207.255.101` |
| `P2` | `10.207.255.102` |
| `P3` | `10.207.255.104` |
| `P4` | `10.207.255.106` |
| `PE1` | `10.207.255.107` |
| `PE2` | `10.207.255.108` |
| `PE3` | `10.207.255.103` |
| `RR` | `10.207.255.105` |
| `CE1` | `10.207.255.141` |
| `CE2` | `10.207.255.143` |
| `CE3` | `10.207.255.146` |
| `AUTO1` | `10.207.255.150` |

Management reachability must be validated before diagnosing higher protocol layers.

---

# Runtime Acceptance Stage 5 — Startup Configuration Identity

Before accepting protocol state, verify that the live routers are actually using the current v2 foundation.

The most important check is:

```text
router isis 500-SP
```

The historical process:

```text
XR8-SP
```

must not appear as the active intended baseline on a clean v2 deployment.

This check protects against stale Containerlab startup state.

---

## Configuration Comparison Model

If a discrepancy is found, compare:

```text
Repository Generated Candidate
            |
            v
Containerlab Runtime Copy
            |
            v
Router Running Configuration
```

These are separate states.

Example repository candidate:

```text
configs/xrd-eight/00-foundation/P1.cfg
```

Possible Containerlab runtime copy:

```text
topology/clab-ccie-sp-xrd-eight/P1/config/startup-config.cfg
```

Live router:

```text
show running-config
```

Do not assume they are identical.

---

# Runtime Acceptance Stage 6 — Physical Interfaces

Validate all physical endpoints.

Expected:

```text
19 physical links
38 physical endpoints
```

Provider links expected to participate in infrastructure protocols:

```text
6 core links
6 provider links
2 control links
```

Customer-facing links:

```text
5 customer links
```

Customer links must not accidentally become part of the provider IS-IS foundation.

---

# Runtime Acceptance Stage 7 — IPv4 and IPv6

Expected runtime infrastructure:

```text
19 IPv4 /31 networks
19 IPv6 /127 networks
```

Provider identities:

```text
8 IPv4 /32 loopbacks
8 IPv6 /128 loopbacks
```

Validation should first confirm directly connected neighbor reachability.

Only then should routing-protocol behavior be evaluated.

---

# Runtime Acceptance Stage 8 — IS-IS

The provider infrastructure is expected to run:

```text
router isis 500-SP
```

with:

```text
is-type level-2-only
```

and area:

```text
49.0001
```

Runtime acceptance should verify:

- all expected provider interfaces participate;
- no CE-facing interface participates unintentionally;
- all expected L2 adjacencies reach `Up`;
- IPv4 topology is present;
- IPv6 topology is present;
- Loopback0 prefixes are advertised;
- transit prefix policy matches design;
- expected shortest paths exist;
- no duplicate system IDs exist.

---

# Expected IS-IS Interface Scope

Infrastructure purposes:

```text
core
provider
control
```

must participate.

Customer links:

```text
customer
```

must remain outside the provider IS-IS baseline.

Expected provider-side interface participation count:

| Node | Infrastructure Links |
| --- | ---: |
| `P1` | `6` |
| `P2` | `4` |
| `P3` | `4` |
| `P4` | `6` |
| `PE1` | `2` |
| `PE2` | `2` |
| `PE3` | `2` |
| `RR` | `2` |

This count represents physical provider/control infrastructure memberships, not necessarily unique adjacency count after protocol interpretation.

---

# Runtime Acceptance Stage 9 — BFD

Provider infrastructure links are generated with BFD intent.

Validation should confirm BFD operation across:

```text
core
provider
control
```

links.

BFD should be evaluated before deliberate convergence testing.

---

# Runtime Acceptance Stage 10 — SR-MPLS

SR-MPLS acceptance should verify:

- SRGB configuration;
- Prefix-SID advertisement;
- Prefix-SID uniqueness;
- IPv4 SID indices `1-8`;
- IPv6 SID indices `601-608`;
- MPLS label installation;
- LFIB entries;
- forwarding reachability between provider loopbacks;
- consistency between IS-IS SID advertisement and forwarding state.

The expected SRGB is:

```text
16000-23999
```

---

# Runtime Acceptance Stage 11 — Fast Reroute

The generated baseline includes:

```text
fast-reroute per-prefix
```

Runtime acceptance should verify the behavior supported by the current XRd image.

TI-LFA is not assumed to be globally accepted until its syntax and runtime behavior are tested directly against:

```text
XRd vRouter 26.2.1
```

Any future TI-LFA promotion into the generated baseline must have explicit evidence.

---

# Runtime Acceptance Stage 12 — Failure Testing

Failure testing begins only after the baseline is healthy.

Suggested tests include:

```text
P1-P2 link failure
PE1-P1 uplink failure
RR-P1 control-link failure
P1 node failure
P4 node failure
CE1-PE1 customer-link failure
CE3-PE3 customer-link failure
```

For each controlled failure, record:

```text
pre-failure state
failure timestamp
protocol reaction
alternate path
convergence behavior
forwarding impact
recovery behavior
post-recovery state
```

---

# BGP Acceptance Boundary

BGP is intentionally outside the generated transport foundation.

Therefore, successful IS-IS and SR-MPLS validation does not imply BGP acceptance.

Future BGP acceptance should independently validate:

- iBGP sessions;
- Route Reflection;
- IPv4 unicast;
- IPv6 unicast;
- VPNv4;
- VPNv6;
- EVPN;
- next-hop behavior;
- route-policy behavior;
- BGP-LS if enabled.

---

# VPN Acceptance Boundary

L3VPN, VPNv6, VPWS, VPLS and EVPN require independent service acceptance.

Examples:

```text
Transport Reachable
        !=
VPN Service Working
```

and:

```text
EVPN Routes Present
        !=
EVPN Dataplane Working
```

Control-plane and forwarding-plane behavior must both be demonstrated before a service is declared accepted.

---

# EVPN Multihoming Acceptance Boundary

The topology provides physical readiness for:

```text
CE1 -> PE1 + PE2
CE3 -> PE3 + PE2
```

This means the physical design is suitable for EVPN multihoming.

It does not mean EVPN multihoming is already operational.

Future acceptance must validate:

- Ethernet Segment Identifier;
- ES routes;
- DF election;
- all-active or single-active behavior;
- aliasing;
- split horizon;
- mass withdrawal;
- MAC/IP Advertisement routes;
- PE failure behavior;
- CE-link failure behavior.

---

# AUTO1 Acceptance

AUTO1 should remain operational as the external operations plane.

Validate:

```bash
docker inspect clab-ccie-sp-xrd-eight-AUTO1 \
  --format 'status={{.State.Status}} restart={{.RestartCount}} oom={{.State.OOMKilled}}'
```

Expected:

```text
status=running
restart=0
oom=false
```

Persistent mounts should exist:

```bash
ls -ld \
  /workspace/xrd-eight \
  /var/lib/ccie-sp \
  /evidence \
  /backups
```

AUTO1 service capabilities such as AAA and RPKI have their own acceptance boundaries.

---

# AAA Acceptance Boundary

Starting a FreeRADIUS or TACACS+ service on AUTO1 is not sufficient to claim AAA acceptance.

AAA acceptance requires both:

```text
AAA Server Operational
        +
Router AAA Integration
        +
Successful Authentication / Authorization / Accounting
```

Fallback behavior should also be tested before centralized AAA is considered safely implemented.

---

# RPKI Acceptance Boundary

Starting Routinator does not constitute RPKI routing-policy acceptance.

The full chain is:

```text
Routinator Operational
        |
        v
RTR Session Established
        |
        v
ROA State Received
        |
        v
Validation State Visible
        |
        v
Routing Policy Applied
        |
        v
Expected Routing Impact
```

Each stage should have evidence.

---

# Validation Evidence

Runtime evidence should be stored under:

```text
automation/xrd-eight/evidence/
```

Suggested structure:

```text
evidence/
|
+-- platform/
|
+-- management/
|
+-- interfaces/
|
+-- isis/
|
+-- bfd/
|
+-- segment-routing/
|
+-- bgp/
|
+-- l3vpn/
|
+-- l2vpn/
|
+-- evpn/
|
+-- multicast/
|
+-- aaa/
|
+-- rpki/
|
+-- failures/
```

Useful evidence includes:

- Docker health output;
- memory/resource snapshots;
- interface state;
- IS-IS neighbors;
- IS-IS database;
- routing tables;
- BFD sessions;
- SR Prefix-SIDs;
- MPLS forwarding entries;
- BGP summaries;
- VPN routes;
- EVPN routes;
- failure timestamps;
- convergence measurements;
- automation logs;
- pre/post configuration diffs.

---

# PASS / FAIL Model

Validation should produce explicit acceptance results.

Preferred output:

```text
[PASS] Container count = 12
[PASS] XRd healthy = 8/8
[PASS] XRd restart count = 0
[PASS] XRd OOM = false
[PASS] IS-IS process = 500-SP
[PASS] IPv4 loopbacks = 8/8
[PASS] IPv6 loopbacks = 8/8
[PASS] Prefix-SIDs unique
```

Avoid relying solely on statements such as:

```text
Looks good
```

or:

```text
Seems stable
```

The long-term objective is to convert more validation into repeatable machine-verifiable acceptance tests through AUTO1.

---

# Failure Handling

When a validation stage fails:

```text
FAIL
 |
 v
Stop dependent deployment
 |
 v
Collect evidence
 |
 v
Identify failure domain
 |
 v
Correct or rollback
 |
 v
Re-run failed validation
 |
 v
Continue only after PASS
```

A failed infrastructure dependency should prevent higher-layer automation from continuing.

For example:

```text
IS-IS FAIL
```

should block:

```text
BGP service deployment
```

when BGP depends on loopback transport through IS-IS.

---

# Destruction Acceptance

After finishing the lab:

```bash
./profiles/xrd-eight/labctl destroy
```

Verify containers are removed:

```bash
docker ps -a --format '{{.Names}}' | \
  grep '^clab-ccie-sp-xrd-eight-' || \
  echo "PASS: containers removed"
```

Verify runtime state is removed:

```bash
test ! -e topology/clab-ccie-sp-xrd-eight && \
  echo "PASS: runtime cleaned"
```

This validation is important because stale Containerlab startup files previously demonstrated that runtime state can influence future deployments.

---

# Clean Redeployment Requirement

A configuration is considered runtime-valid for the current v2 baseline only when it has been observed after:

```text
Current Source of Truth
        |
        v
Fresh Generation
        |
        v
Static Validation PASS
        |
        v
Old Runtime Removed
        |
        v
Clean Containerlab Deployment
        |
        v
Running Configuration Verified
        |
        v
Protocol Validation
```

This prevents an old runtime configuration from being mistaken for current repository behavior.

---

# Static Validation Command Set

A complete static validation sequence is:

```bash
cd /srv/netlab/labs/ccie-sp-master

python3 -m py_compile \
  tools/build_xrd_eight.py \
  tools/render_xrd_eight.py \
  tools/validate_xrd_eight_addressing.py

python3 tools/build_xrd_eight.py

python3 tools/validate_xrd_eight_addressing.py

python3 tools/render_xrd_eight.py

git diff --check

git status --short
```

Protocol-generation counters:

```bash
grep -h '^router isis 500-SP$' \
  configs/xrd-eight/00-foundation/*.cfg | wc -l
```

Expected:

```text
8
```

Segment Routing AF statements:

```bash
grep -hE '^  segment-routing mpls( sr-prefer)?$' \
  configs/xrd-eight/00-foundation/*.cfg | wc -l
```

Expected:

```text
16
```

Prefix-SID statements:

```bash
grep -h '^   prefix-sid index' \
  configs/xrd-eight/00-foundation/*.cfg | wc -l
```

Expected:

```text
16
```

---

# Static Acceptance Summary

Before deployment, the following must be true:

| Validation | Expected |
| --- | --- |
| Python compile | PASS |
| Builder execution | PASS |
| Generated XR configs | `8` |
| Generated CE configs | `3` |
| Generated links | `19` |
| IPv4 `/31` networks | `19` |
| IPv6 `/127` networks | `19` |
| IPv4 loopbacks | `8` |
| IPv6 loopbacks | `8` |
| Duplicate addresses | `0` |
| Overlapping networks | `0` |
| IS-IS `500-SP` instances | `8` |
| SR-MPLS AF statements | `16` |
| Prefix-SID statements | `16` |
| Git whitespace check | PASS |
| Deterministic regeneration | PASS |

---

# Runtime Acceptance Summary

A clean XRd Eight v2 runtime should eventually demonstrate:

| Validation | Expected |
| --- | --- |
| Containers | `12/12` |
| XRd nodes | `8/8` |
| IOL-XE nodes | `3/3` |
| AUTO1 | `1/1` |
| XRd health | `8/8 healthy` |
| XRd restart count | `0` |
| XRd OOM | `false` |
| Management reachability | `12/12` |
| Physical links | `19/19` |
| IPv4 point-to-point networks | `19/19` |
| IPv6 point-to-point networks | `19/19` |
| IPv4 provider loopbacks | `8/8` |
| IPv6 provider loopbacks | `8/8` |
| Active IS-IS process | `500-SP` |
| Provider IS-IS scope | core/provider/control only |
| Customer links in provider IS-IS | `0` |
| Prefix-SID uniqueness | PASS |
| SRGB consistency | PASS |

Higher-layer protocols have separate acceptance criteria.

---

# Current Validation Summary

XRd Eight v2 currently has a strong static acceptance baseline.

Confirmed repository properties include:

```text
12-node architecture
8 XRd vRouter provider/control nodes
3 IOL-XE CE nodes
1 AUTO1 node
19 deterministic physical links
19 IPv4 /31 networks
19 IPv6 /127 networks
38 IPv4 physical endpoints
38 IPv6 physical endpoints
8 IPv4 /32 provider loopbacks
8 IPv6 /128 provider loopbacks
0 duplicate addresses
0 overlapping networks
IS-IS process 500-SP generated on 8 XRd nodes
IPv4 Prefix-SIDs 1-8
IPv6 Prefix-SIDs 601-608
deterministic generated CSV output
```

Historical runtime evidence additionally demonstrates that the host can operate the complete twelve-container full-dataplane footprint without swap or OOM events under the previously measured conditions.

The remaining acceptance requirement is to validate the **current v2 repository state through a clean deployment**, ensuring that the routers boot the regenerated foundation rather than stale Containerlab runtime files.

---

# Final Acceptance Principle

XRd Eight v2 should only claim a capability as validated when there is evidence from the appropriate layer.

The rule is:

```text
Designed
   !=
Generated

Generated
   !=
Deployed

Deployed
   !=
Converged

Converged
   !=
Forwarding Correctly

Forwarding Correctly
   !=
Service Accepted
```

The project therefore prefers explicit evidence over assumptions.

A capability moves from design to acceptance only when its expected state has been generated, deployed, observed and validated at the appropriate layer.

This model keeps the repository technically accurate while allowing XRd Eight v2 to evolve incrementally from a deterministic infrastructure foundation into a fully validated Service Provider engineering environment.
