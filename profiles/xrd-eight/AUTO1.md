# AUTO1 — Automation and Operations Workspace

> **Dedicated automation, validation and service-integration node for the XRd Eight v2 Service Provider lab.**
>
> AUTO1 provides an isolated Linux-based operations environment for configuration management, validation, evidence collection, AAA, RPKI and NetDevOps workflows without mixing automation tooling with the provider forwarding infrastructure.

AUTO1 is the management and automation workstation for XRd Eight v2.

It is intentionally separated from the provider forwarding topology.

The P, PE and RR nodes are responsible for the Service Provider control and forwarding planes, while AUTO1 provides the external operational plane used to configure, validate, observe and automate them.

Conceptually:

```text
                    XRd Eight v2

              Service Provider Network
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
      P Core          PE Edge         RR
        |              |              |
        +--------------+--------------+
                       |
                       |
                Management Plane
                       |
                       v
                    AUTO1
                       |
      +----------------+----------------+
      |                |                |
      v                v                v
 Automation        Validation       Services
 Ansible/Python    Evidence         AAA/RPKI
```

AUTO1 is therefore not another Service Provider router.

It is the operational system used to interact with the lab.

---

## Role in XRd Eight v2

AUTO1 is designed to support several operational functions.

| Function | Responsibility |
| --- | --- |
| Automation | Execute Ansible, Python and network automation workflows |
| Configuration rendering | Generate candidate configuration from templates |
| Validation | Perform prechecks, postchecks and state verification |
| Backups | Collect device configurations before changes |
| Evidence | Store command output and validation artifacts |
| AAA | Host lab FreeRADIUS and TACACS+ services |
| RPKI | Host Routinator and provide an RTR validation cache |
| NetDevOps | Support repeatable configuration and validation pipelines |
| Troubleshooting | Collect and compare operational state |
| Experimentation | Provide a safe environment for API, NETCONF and automation studies |

AUTO1 should be considered the **operations and automation plane** of the XRd Eight profile.

---

## Platform

AUTO1 uses the local image:

```text
ccie-sp-automation:1.0
```

Containerlab node:

```text
AUTO1
```

Management IPv4:

```text
10.207.255.150
```

AUTO1 connects to the same dedicated management network used by the routers:

```text
10.207.255.0/24
```

Containerlab management network:

```text
ccie-sp-xrd-eight-mgmt
```

The automation node therefore reaches network devices through management connectivity rather than depending on the Service Provider IGP or forwarding plane.

This is an intentional design decision.

If IS-IS, SR-MPLS, BGP, VPN or EVPN is broken during an exercise, AUTO1 should still be capable of reaching the devices through management.

---

## Operational Separation

XRd Eight v2 separates the network into two logical planes.

### Provider Plane

The provider routers contain:

```text
P1
P2
P3
P4

PE1
PE2
PE3

RR
```

These nodes provide:

- forwarding;
- IS-IS;
- SR-MPLS;
- BGP;
- VPN;
- EVPN;
- multicast;
- QoS;
- Segment Routing;
- service-provider control-plane functions.

### Operations Plane

AUTO1 provides:

- automation;
- configuration generation;
- backups;
- validation;
- evidence collection;
- AAA;
- RPKI;
- tooling;
- orchestration.

Conceptually:

```text
+-------------------------------------------------------+
|               SERVICE PROVIDER PLANE                  |
|                                                       |
|  P1 --- P2 --- P3 --- P4                             |
|   \      \      /      /                             |
|       PE1   PE2   PE3                                |
|              |                                        |
|              RR                                       |
+-------------------------------------------------------+

                        |
                        |
                  Management Network
                        |
                        v

+-------------------------------------------------------+
|                 OPERATIONS PLANE                      |
|                                                       |
|                     AUTO1                             |
|                                                       |
|  Automation | Validation | AAA | RPKI | Evidence     |
+-------------------------------------------------------+
```

---

## Persistent Directory Model

AUTO1 uses persistent host directories mounted into the container.

| Repository / Host Path | AUTO1 Path | Purpose |
| --- | --- | --- |
| `automation/xrd-eight/workspace/` | `/workspace/xrd-eight` | Automation code, playbooks, templates and utilities |
| `automation/xrd-eight/data/` | `/var/lib/ccie-sp` | Persistent AAA/RPKI and supporting service data |
| `automation/xrd-eight/evidence/` | `/evidence` | Validation and operational evidence |
| `automation/xrd-eight/backups/` | `/backups` | Device configuration backups |

Containerlab defines these mounts as:

```yaml
binds:
  - ../automation/xrd-eight/workspace:/workspace/xrd-eight
  - ../automation/xrd-eight/data:/var/lib/ccie-sp
  - ../automation/xrd-eight/evidence:/evidence
  - ../automation/xrd-eight/backups:/backups
```

The separation is intentional.

Each directory has a different lifecycle and security requirement.

---

# Workspace

The primary automation development directory is:

```text
/workspace/xrd-eight
```

Host-side equivalent:

```text
automation/xrd-eight/workspace/
```

This directory is intended for reusable automation assets.

Typical content can include:

```text
Ansible playbooks
Python scripts
Jinja2 templates
inventory files
validation utilities
Netmiko scripts
NETCONF tooling
pyATS/Genie exercises
rollback logic
service-specific automation
```

A possible structure is:

```text
automation/xrd-eight/workspace/
|
+-- inventory/
|
+-- playbooks/
|   |
|   +-- prechecks/
|   +-- transport/
|   +-- bgp/
|   +-- l3vpn/
|   +-- l2vpn/
|   +-- evpn/
|   +-- multicast/
|   +-- security/
|   +-- validation/
|
+-- python/
|
+-- templates/
|
+-- filters/
|
+-- vars/
|
+-- validation/
|
+-- rollback/
|
+-- README.md
```

This structure is not mandatory, but automation should remain organized by function or study phase rather than accumulating as unrelated scripts.

---

# Automation Tooling

AUTO1 is intended to support several complementary automation models.

## Ansible

Ansible can be used for:

- configuration deployment;
- configuration rendering;
- controlled serial changes;
- prechecks;
- postchecks;
- backup workflows;
- state validation;
- idempotency experiments;
- failure handling.

Typical workflow:

```text
Inventory
   |
   v
Variables
   |
   v
Jinja2
   |
   v
Candidate Configuration
   |
   v
Review
   |
   v
Canary Deployment
   |
   v
Validation
   |
   v
Serial Deployment
```

---

## Python

Python provides more direct control over custom workflows.

Potential uses include:

- inventory processing;
- topology validation;
- configuration generation;
- parsing operational output;
- API interaction;
- failure injection;
- state comparison;
- automated acceptance tests;
- evidence normalization.

Python should complement the repository generators rather than duplicate them unnecessarily.

---

## Netmiko

Netmiko can provide SSH-based automation for tasks such as:

- command execution;
- configuration pushes;
- output collection;
- backups;
- targeted troubleshooting;
- canary changes.

It is particularly useful for quick operational workflows where NETCONF or structured APIs are unnecessary.

---

## NETCONF and `ncclient`

NETCONF can be used for structured configuration and state-management exercises.

Potential study areas include:

- capability discovery;
- configuration retrieval;
- candidate configuration;
- commit operations;
- structured validation;
- YANG-oriented workflows.

NETCONF exercises should remain isolated from baseline generation unless explicitly promoted into the permanent automation model.

---

## pyATS / Genie

pyATS and Genie can be introduced for structured operational validation.

Potential use cases include:

- interface state verification;
- routing table checks;
- BGP neighbor validation;
- protocol-state comparison;
- pre/post snapshots;
- automated failure acceptance.

Where supported, structured parsers are preferable to fragile regular-expression parsing for larger validation workflows.

---

# Recommended Automation Lifecycle

Automation should not immediately configure the entire topology.

A controlled workflow is preferred.

The recommended sequence is:

```text
1. Inventory
      |
      v
2. Credential Loading
      |
      v
3. Read-Only Discovery
      |
      v
4. Baseline Evidence
      |
      v
5. Configuration Backup
      |
      v
6. Candidate Rendering
      |
      v
7. Review / Diff
      |
      v
8. Canary Device
      |
      v
9. Canary Validation
      |
      v
10. Controlled Serial Deployment
      |
      v
11. Postchecks
      |
      v
12. Evidence Collection
      |
      v
13. Acceptance / Rollback
```

This mirrors a production-style NetDevOps change model more closely than an uncontrolled push to every router simultaneously.

---

# Prechecks

Before changing a device, AUTO1 should ideally verify the current state.

Examples include:

```text
management reachability
SSH availability
device hostname
software version
interface state
IS-IS adjacency state
BFD state
BGP state
current configuration
available resources
expected topology neighbors
```

The exact prechecks depend on the exercise.

For example, before deploying BGP:

```text
Management Reachability
        |
        v
IS-IS Reachability
        |
        v
Loopback Reachability
        |
        v
SR-MPLS Transport
        |
        v
BGP Candidate Deployment
```

Higher-layer configuration should not be deployed if its required infrastructure dependencies are already broken.

---

# Candidate Configuration

Configuration should preferably be rendered before deployment.

Example workflow:

```text
Jinja2 Template
      +
Variables
      |
      v
Rendered Candidate
      |
      v
Review Directory
      |
      v
Diff / Validation
      |
      v
Deployment
```

The candidate should be inspectable before it reaches the router.

This makes it easier to identify:

- incorrect variables;
- missing neighbors;
- incorrect route targets;
- wrong interfaces;
- syntax errors;
- unintended policy changes.

---

# Canary Deployment

Significant automation changes should initially target one device.

Example:

```text
PE1
```

The canary process should verify:

1. configuration acceptance;
2. protocol stability;
3. expected routing changes;
4. expected forwarding behavior;
5. absence of unintended side effects.

Only then should the workflow continue to other nodes.

Conceptually:

```text
Candidate
   |
   v
  PE1
   |
   v
Validation
   |
   +---- FAIL ----> Rollback / Stop
   |
  PASS
   |
   v
PE2 / PE3 / Remaining Nodes
```

---

# Controlled Serial Deployment

Where possible, avoid simultaneously changing every provider router.

For infrastructure changes, a serial deployment provides better failure containment.

Example:

```text
P1
 |
 v
Validate

P2
 |
 v
Validate

P3
 |
 v
Validate

P4
 |
 v
Validate
```

The exact order depends on the technology and failure domain being tested.

---

# Postchecks

After deployment, AUTO1 should confirm that the intended state was achieved.

Possible postchecks include:

- configuration presence;
- interface state;
- IS-IS adjacency count;
- loopback reachability;
- BFD sessions;
- SR-MPLS Prefix-SIDs;
- BGP neighbor state;
- VPN route presence;
- EVPN routes;
- MPLS labels;
- multicast state;
- RPKI status;
- AAA authentication;
- telemetry state.

Postchecks should verify **state**, not merely configuration acceptance.

A command being accepted does not prove that the network operates correctly.

---

# Evidence Collection

Operational evidence belongs under:

```text
/evidence
```

Host equivalent:

```text
automation/xrd-eight/evidence/
```

Evidence can include:

```text
precheck results
postcheck results
show commands
protocol state
routing tables
MPLS tables
BGP summaries
EVPN routes
interface state
resource consumption
failure-test results
automation logs
configuration diffs
```

A useful evidence hierarchy could be:

```text
evidence/
|
+-- transport/
|
+-- isis/
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

Evidence should be associated with a specific exercise or validation event whenever practical.

---

# Configuration Backups

Backups belong under:

```text
/backups
```

Host equivalent:

```text
automation/xrd-eight/backups/
```

The purpose of this directory is to preserve device state before potentially destructive changes.

Example structure:

```text
backups/
|
+-- manual/
|
+-- pre-change/
|
+-- rollback/
|
+-- snapshots/
```

A typical process is:

```text
Current Device
      |
      v
Configuration Backup
      |
      v
Candidate Change
      |
      v
Validation
      |
      +---- FAIL ----> Restore / Rollback
      |
     PASS
```

Backups can contain sensitive information.

They should therefore be treated differently from normal automation code.

---

# Backup Security Boundary

Configuration backups may contain:

- passwords;
- encrypted secrets;
- TACACS+ keys;
- RADIUS keys;
- SNMP communities;
- certificates;
- private keys;
- routing-policy information;
- customer addressing;
- service configuration.

Do not automatically commit backup directories to Git.

The repository should contain automation logic, not uncontrolled copies of live device configurations containing secrets.

---

# AAA Services

AUTO1 is reserved for centralized AAA experiments.

Potential services include:

```text
FreeRADIUS
TACACS+
```

AAA can be used to study:

- centralized authentication;
- authorization;
- accounting;
- fallback behavior;
- local-user recovery;
- command authorization;
- operational logging.

AAA service data belongs under:

```text
/var/lib/ccie-sp
```

---

## FreeRADIUS

Potential FreeRADIUS exercises include:

- user authentication;
- authentication policy;
- accounting;
- network-device client definitions;
- fallback testing;
- centralized login validation.

Starting FreeRADIUS on AUTO1 does **not** automatically enable RADIUS on the routers.

Router integration must be explicitly configured as a separate study phase.

---

## TACACS+

Potential TACACS+ exercises include:

- login authentication;
- command authorization;
- accounting;
- role separation;
- local fallback;
- failure behavior.

Again:

```text
TACACS+ running on AUTO1
```

does not imply:

```text
TACACS+ enabled on P/PE/RR
```

The service side and network-device side remain deliberately independent.

---

# RPKI and Routinator

AUTO1 is also reserved for RPKI exercises.

The intended validator is:

```text
Routinator
```

Potential roles include:

- local RPKI validator;
- RTR cache;
- origin-validation source;
- RPKI lab data collection.

Conceptually:

```text
RPKI Repositories
       |
       v
   Routinator
     AUTO1
       |
       | RTR
       v
 Provider Routers
```

The validator can be configured independently from router policy.

This permits phased study.

---

## RPKI Study Phases

A controlled RPKI exercise could progress through:

```text
1. Start validator
      |
      v
2. Validate RTR availability
      |
      v
3. Establish router-to-cache session
      |
      v
4. Observe validation states
      |
      v
5. Build route policy
      |
      v
6. Apply policy
      |
      v
7. Validate routing impact
```

Starting Routinator should never automatically activate origin-validation policy on routers.

The routing policy remains an explicit configuration phase.

---

# Persistent Service Data

Service state belongs under:

```text
/var/lib/ccie-sp
```

Host equivalent:

```text
automation/xrd-eight/data/
```

Potential contents include:

```text
AAA databases
RADIUS configuration
TACACS+ service data
Routinator data
service state
local test artifacts
```

This directory should be treated as runtime/service data rather than general source code.

---

# Credential Model

AUTO1 uses:

```text
Username: student
```

Its password is supplied at deployment using:

```text
CCIE_AUTO_PASSWORD
```

The password is intentionally not stored in the repository.

Load it interactively:

```bash
read -rsp "CCIE_AUTO_PASSWORD: " CCIE_AUTO_PASSWORD
echo
export CCIE_AUTO_PASSWORD
```

Verify only its presence:

```bash
if [ -n "${CCIE_AUTO_PASSWORD:-}" ]; then
  echo "CCIE_AUTO_PASSWORD: SET"
else
  echo "CCIE_AUTO_PASSWORD: NOT SET"
fi
```

The actual value should not be printed.

---

# Secret Handling

Runtime credentials must never be committed.

Do not store `CCIE_AUTO_PASSWORD` in:

```text
Git
README.md
AUTO1.md
inventory files
plain-text vars files
topology YAML
Python source
Ansible playbooks
Jinja2 templates
shell history
```

The topology references the environment variable rather than embedding the password.

Conceptually:

```text
Shell Environment
       |
       | CCIE_AUTO_PASSWORD
       v
Containerlab Deployment
       |
       v
AUTO1 Runtime
```

The secret should remain outside the repository lifecycle.

---

# Containerlab Integration

AUTO1 is defined in the XRd Eight Containerlab topology.

Conceptually:

```yaml
AUTO1:
  kind: linux
  mgmt-ipv4: 10.207.255.150
  image: ccie-sp-automation:1.0
  cmd: sleep infinity
  env:
    AUTO1_PASSWORD: ${CCIE_AUTO_PASSWORD}
  binds:
    - ../automation/xrd-eight/workspace:/workspace/xrd-eight
    - ../automation/xrd-eight/data:/var/lib/ccie-sp
    - ../automation/xrd-eight/evidence:/evidence
    - ../automation/xrd-eight/backups:/backups
```

The lifecycle wrapper preserves `CCIE_AUTO_PASSWORD` across `sudo` during a full deployment.

---

# Connecting to AUTO1

AUTO1 management address:

```text
10.207.255.150
```

SSH example:

```bash
ssh student@10.207.255.150
```

Once connected:

```bash
cd /workspace/xrd-eight
```

This is the primary working directory for XRd Eight automation.

---

# Reachability Model

AUTO1 should be capable of reaching all managed nodes through the management network.

Current targets include:

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

AUTO1 itself:

```text
10.207.255.150
```

Automation should normally use management addresses unless an exercise specifically requires in-band access.

---

# Read-Only Discovery First

Before AUTO1 performs configuration changes, it should first establish what is currently running.

Example discovery sequence:

```text
Device reachable?
      |
      v
Correct hostname?
      |
      v
Expected software?
      |
      v
Interfaces operational?
      |
      v
IGP healthy?
      |
      v
SR transport healthy?
      |
      v
Safe to modify?
```

This principle prevents automation from applying a higher-layer service on top of an already unhealthy infrastructure state.

---

# Transport Validation from AUTO1

AUTO1 can later automate transport checks such as:

```text
8 expected provider nodes
expected management reachability
expected interface count
expected IS-IS adjacencies
8 IPv4 loopbacks
8 IPv6 loopbacks
SRGB consistency
Prefix-SID uniqueness
BFD state
MPLS forwarding state
```

The exact validation workflow can evolve independently from the generated startup foundation.

---

# Service Automation

Once transport acceptance is complete, AUTO1 can be used for higher-layer exercises.

Examples include:

## BGP

```text
iBGP
Route Reflection
VPNv4
VPNv6
BGP-LS
BGP-LU
```

## MPLS VPN

```text
VRFs
RDs
RTs
PE-CE routing
L3VPN
VPNv6
```

## L2VPN

```text
VPWS
VPLS
pseudowires
bridge domains
attachment circuits
```

## EVPN

```text
EVPN address family
EVPN Route Reflection
EVI
MAC/IP Advertisement
EVPN VPWS
EVPN Multihoming
```

## Segment Routing

```text
SR Policy
candidate paths
segment lists
PCE/PCC
affinity constraints
disjointness
```

## Multicast

```text
PIM
RP
BSR
mLDP
mVPN
```

## Security / Operations

```text
AAA
RPKI
telemetry
QoS
validation
```

---

# EVPN Multihoming Automation

XRd Eight v2 provides two physical dual-homing scenarios:

```text
CE1
 +-- PE1
 +-- PE2
```

and:

```text
CE3
 +-- PE3
 +-- PE2
```

AUTO1 can eventually automate and validate concepts such as:

```text
ESI generation
Ethernet Segment configuration
DF election
all-active operation
single-active operation
EVPN route types
aliasing
mass withdrawal
failure convergence
```

The physical topology exists in the baseline.

The EVPN multihoming service itself remains explicit study work.

---

# Failure Automation

AUTO1 can also be used to automate controlled failure experiments.

Potential tests include:

```text
shutdown a P-P link
shutdown a PE uplink
remove an RR uplink
disable a CE attachment
change an IS-IS metric
withdraw a BGP route
remove a service policy
```

Each test should follow:

```text
Baseline
   |
   v
Inject Failure
   |
   v
Measure Reaction
   |
   v
Collect Evidence
   |
   v
Restore
   |
   v
Validate Recovery
```

The goal is not simply to create failures, but to measure convergence and prove recovery.

---

# Evidence-Driven Validation

AUTO1 should help convert manual observation into repeatable evidence.

Instead of:

```text
"It looks correct."
```

the target model is:

```text
Expected State
      |
      v
Collected State
      |
      v
Comparison
      |
      +---- PASS
      |
      +---- FAIL
```

Examples:

```text
Expected IS-IS neighbors: N
Observed IS-IS neighbors: N
Result: PASS
```

or:

```text
Expected EVPN Route Type 2: present
Observed: missing
Result: FAIL
```

This approach becomes increasingly useful as the lab grows in complexity.

---

# AUTO1 and the Repository Source of Truth

AUTO1 should not silently redefine the physical infrastructure.

The repository remains authoritative for:

```text
node names
node roles
physical links
management addressing
provider loopbacks
P2P addressing
IS-IS identity
Prefix-SID identity
Containerlab topology
```

AUTO1 operates **against** that infrastructure.

Conceptually:

```text
Git Repository
      |
      | defines infrastructure
      v
XRd Eight Topology
      |
      | managed by
      v
AUTO1
```

This prevents automation logic from becoming a hidden second topology definition.

---

# Permanent Change vs Runtime Exercise

A useful distinction is:

### Permanent Infrastructure Change

Example:

```text
Add another physical provider link
```

This belongs in the repository Source of Truth.

Workflow:

```text
Modify Source of Truth
      |
      v
Generate
      |
      v
Validate
      |
      v
Git Review
      |
      v
Merge
      |
      v
Deploy
```

### Runtime Study Change

Example:

```text
Configure EVPN EVI 500
```

This can be:

```text
manual configuration
```

or:

```text
AUTO1 automation
```

without necessarily becoming part of the permanent foundation.

---

# Rollback Philosophy

Automation should define what happens when validation fails.

A failed postcheck should not automatically be ignored.

Preferred model:

```text
Deploy
   |
   v
Postcheck
   |
   +---- PASS ----> Continue
   |
   +---- FAIL
           |
           v
        Stop
           |
           v
      Collect Evidence
           |
           v
        Rollback
```

Rollback can be:

- configuration removal;
- replacement with saved candidate;
- restore from backup;
- Containerlab redeployment for disposable exercises.

The appropriate mechanism depends on the technology under study.

---

# Safety Rules

AUTO1 should follow several operating rules.

1. Perform read-only discovery before changing devices.
2. Back up important configurations before destructive changes.
3. Render candidate configuration before deployment where practical.
4. Review diffs before pushing large changes.
5. Use a canary device for significant new automation.
6. Prefer serial deployment for infrastructure changes.
7. Validate protocol state after configuration.
8. Store meaningful validation output as evidence.
9. Stop automation when acceptance criteria fail.
10. Keep runtime credentials outside Git.
11. Never treat backups as normal source files.
12. Keep AAA and RPKI activation as explicit study phases.
13. Do not use AUTO1 as an alternative Source of Truth for the physical topology.
14. Preserve management-plane reachability independently from the SP forwarding plane.
15. Promote successful permanent changes through the normal repository workflow.

---

# AAA and RPKI Boundary

AUTO1 provides the infrastructure required to host these services.

It does **not** automatically activate them on routers.

The distinction is:

```text
Service Available
      !=
Router Integration Enabled
```

For AAA:

```text
FreeRADIUS / TACACS+ running
        |
        X
        |
Router AAA configuration
```

Router configuration remains an explicit action.

For RPKI:

```text
Routinator running
        |
        X
        |
RTR session + routing policy
```

RPKI origin validation remains an explicit routing exercise.

This prevents enabling security functions unintentionally across the whole topology.

---

# Recommended Study Progression

AUTO1 can evolve alongside the network.

A practical progression is:

```text
Phase 1
Basic SSH discovery
        |
        v
Phase 2
Configuration backups
        |
        v
Phase 3
Read-only validation
        |
        v
Phase 4
Jinja2 rendering
        |
        v
Phase 5
Ansible deployment
        |
        v
Phase 6
NETCONF / YANG
        |
        v
Phase 7
Protocol validation
        |
        v
Phase 8
Failure automation
        |
        v
Phase 9
AAA / RPKI
        |
        v
Phase 10
End-to-end NetDevOps workflows
```

This keeps automation complexity aligned with the networking complexity being studied.

---

# Example End-to-End Workflow

A future EVPN exercise could follow:

```text
1. Validate transport
        |
        v
2. Backup PE configuration
        |
        v
3. Render BGP/EVPN candidate
        |
        v
4. Review candidate
        |
        v
5. Apply to RR
        |
        v
6. Validate EVPN AF
        |
        v
7. Apply to PE1
        |
        v
8. Canary validation
        |
        v
9. Apply to PE2 / PE3
        |
        v
10. Configure EVI
        |
        v
11. Validate EVPN routes
        |
        v
12. Configure CE multihoming
        |
        v
13. Inject failure
        |
        v
14. Measure convergence
        |
        v
15. Save evidence
```

The same operational model can be reused for BGP, VPN, multicast, QoS or Segment Routing policy studies.

---

# Data Retention Model

Different AUTO1 data types have different retention expectations.

| Data | Location | Retention |
| --- | --- | --- |
| Automation source | `/workspace/xrd-eight` | Persistent / version-controlled when appropriate |
| Service databases | `/var/lib/ccie-sp` | Persistent runtime data |
| Validation evidence | `/evidence` | Persistent as required |
| Device backups | `/backups` | Persistent, private |
| Container-local temporary files | Other container paths | Disposable |

This separation helps prevent runtime state from becoming mixed with source code.

---

# Git Boundary

Items normally appropriate for Git include:

```text
Ansible playbooks
Python scripts
Jinja2 templates
validation logic
documentation
non-secret inventory structure
test definitions
```

Items that should generally remain outside Git include:

```text
passwords
tokens
private keys
device backups containing secrets
AAA shared secrets
RPKI private material
temporary runtime state
generated sensitive evidence
```

Before committing automation changes:

```bash
git status
git diff
```

should always be reviewed.

---

# Operational Validation

After deployment, verify that AUTO1 exists:

```bash
docker ps -a \
  --filter name=clab-ccie-sp-xrd-eight-AUTO1
```

Inspect its state:

```bash
docker inspect clab-ccie-sp-xrd-eight-AUTO1 \
  --format 'status={{.State.Status}} restart={{.RestartCount}} oom={{.State.OOMKilled}}'
```

Expected steady state:

```text
status=running
restart=0
oom=false
```

---

# Workspace Validation

Inside AUTO1:

```bash
cd /workspace/xrd-eight
pwd
```

Expected:

```text
/workspace/xrd-eight
```

Validate persistent mounts:

```bash
ls -ld \
  /workspace/xrd-eight \
  /var/lib/ccie-sp \
  /evidence \
  /backups
```

All four paths should exist.

---

# Automation Tool Validation

Installed automation tools can be validated independently.

Examples:

```bash
ansible --version
```

```bash
python3 --version
```

```bash
python3 -c 'import netmiko; print(netmiko.__version__)'
```

```bash
python3 -c 'import ncclient; print(ncclient.__version__)'
```

Additional frameworks should be checked before an exercise depends on them.

The existence of AUTO1 does not imply that every optional framework is permanently installed.

---

# Failure Recovery

If AUTO1 itself becomes unusable, the provider topology should remain independently operational.

AUTO1 can be recreated because its important data is stored through persistent bind mounts.

Recovery model:

```text
AUTO1 Failure
     |
     v
Destroy / Recreate Container
     |
     v
Remount Persistent Directories
     |
     v
Restore Operations Environment
```

The network should therefore never depend on transient container-local AUTO1 data for permanent topology identity.

---

# Lifecycle

AUTO1 is created and destroyed as part of the full XRd Eight profile.

Deploy:

```bash
./profiles/xrd-eight/labctl deploy-full
```

Destroy:

```bash
./profiles/xrd-eight/labctl destroy
```

The profile uses Containerlab cleanup semantics during destruction.

Persistent bind-mounted workspace, data, evidence and backup directories remain on the host according to their own lifecycle.

---

# Responsibility Matrix

| Capability | Repository | AUTO1 | Routers |
| --- | ---: | ---: | ---: |
| Physical topology | ✓ | — | — |
| Deterministic addressing | ✓ | Validate | Apply |
| Generated foundation | ✓ | Validate | Run |
| Manual protocol study | — | Optional | ✓ |
| Automation | Store | ✓ | Target |
| Configuration rendering | Templates | ✓ | — |
| Backups | Location defined | ✓ | Source |
| Evidence | Location defined | ✓ | Source |
| AAA server | — | ✓ | Client |
| RPKI validator | — | ✓ | RTR client |
| Route policy | Optional automation | Deploy | ✓ |
| Runtime forwarding | — | Observe | ✓ |

This division of responsibility keeps the architecture understandable.

---

# AUTO1 Design Intent

AUTO1 exists to make the XRd Eight lab **repeatable without making it automatic by default**.

The goal is not:

```text
Press one button and configure everything.
```

The goal is:

```text
Understand the intended state
        |
        v
Represent it as code
        |
        v
Render it deterministically
        |
        v
Review it
        |
        v
Deploy it safely
        |
        v
Validate the actual network state
        |
        v
Collect evidence
        |
        v
Rollback when required
```

AUTO1 therefore becomes the bridge between traditional Service Provider engineering and NetDevOps.

The routers remain the network.

The repository remains the infrastructure Source of Truth.

AUTO1 provides the tools used to operate, validate and automate that network.

---

# Summary

AUTO1 currently provides the operational foundation for the following roles:

| Area | Intended Capability |
| --- | --- |
| Management | Dedicated management-plane access |
| Automation | Ansible, Python, Netmiko and structured workflows |
| NETCONF | `ncclient` / YANG experimentation |
| Validation | Prechecks, postchecks and acceptance gates |
| Configuration | Candidate rendering and controlled deployment |
| Backups | Persistent pre-change and rollback snapshots |
| Evidence | Persistent operational validation output |
| AAA | FreeRADIUS and TACACS+ experiments |
| RPKI | Routinator and RTR cache experiments |
| Failure testing | Automated fault injection and recovery validation |
| NetDevOps | Reproducible end-to-end workflows |

The central design principle is:

> **AUTO1 automates and validates the network, but it does not replace the network's Source of Truth or automatically enable advanced services.**

AAA, RPKI, EVPN, VPN, BGP, PCE, multicast, QoS and other advanced capabilities remain explicit study phases.

This keeps XRd Eight v2 useful both as a manual certification lab and as a progressively automated Service Provider engineering environment.
