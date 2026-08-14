<h1 align="center">

Professional CCIE SP Multi-Profile Lab Operating Guide
</h1>

<div align="center">

**Step-by-step operations for the Master ISP, Inter-AS, and SRv6 profiles**

[Preparation](#6-server-readiness) —
[Generation](#7-reproducible-generation) —
[Deployment](#8-safe-lifecycle) —
[Configuration](#10-phase-based-configuration) —
[Validation](#12-validation) —
[Recovery](#16-troubleshooting-and-recovery)

</div>

---

This is the operational entry point for understanding, preparing, deploying,
validating, modifying, recovering, and safely retiring the lab profiles. The
repository is not merely a collection of topology files. It implements a
reproducible engineering workflow in which inventories and generators produce
reviewable configurations, diagrams, and Containerlab artifacts.

> [!IMPORTANT]
> Follow the sections in order for the first deployment. A stable interface,
> addressing, IGP, and transport foundation must exist before BGP or customer
> services can be meaningfully validated.

> [!WARNING]
> Run only one heavy profile at a time. The three profiles share the same host
> CPU, RAM, KVM acceleration, Docker storage, and licensed network images.

## 1. Purpose

The project supports CCIE Service Provider blueprint practice and realistic
service-provider scenarios without running several resource-heavy labs at the
same time.

| Profile | Status | Purpose |
|---|---|---|
| `master` | Runnable; infrastructure baseline validated | Redundant ISP backbone with dual-stack IS-IS, SR-MPLS, RR/PCE roles, and progressive services |
| `inter-as` | Runnable; baseline validated | Three autonomous systems, multiple IGPs, route reflectors, eBGP, and Options A/B/C practice |
| `srv6` | Runnable; 21-node baseline validated | IPv6 IS-IS underlay, operational locators, and progressive SRv6 services |

The primary operational rule is simple: **only one heavy profile may be active
at a time**. This preserves resources, prevents overlapping names and networks,
and ensures that every exercise starts from a known state.

### 1.1 How to use this guide

| Situation | Start with |
|---|---|
| First installation | [Containerlab Host, Image, and AUTO1 Build Guide](CONTAINERLAB-INSTALLATION.md) |
| First deployment | Sections 6 through 12 of this guide |
| Daily operation | [Operations quick reference](../OPERATIONS.md) |
| Personal workflow and persistence | [Personal Three-Profile Lab Workflow](PERSONAL-LAB-WORKFLOW.md) |
| Changing topology or addressing | Sections 3, 7, 10, and 11 |
| Investigating a failure | Section 16 and the profile troubleshooting guide |
| Checking what has actually passed | [Deployment Status](../STATUS.md) |
| Mapping practice to the exam | [CCIE SP Blueprint Matrix](../BLUEPRINT-MATRIX.md) |

### 1.2 Operating principles

1. **Inventory before configuration:** inventory defines the intended nodes,
   links, interfaces, and addresses.
2. **Generate before deployment:** rendered artifacts must match their source.
3. **Validate before expansion:** begin with a canary or small node batch.
4. **One change domain at a time:** do not mix underlay, BGP, VPN, and failure
   changes in one unreviewed action.
5. **Evidence before claims:** record expected and observed state.
6. **Recoverability before experimentation:** create a known-good checkpoint
   before destructive exercises.

## 2. Repository layout

```text
ccie-sp-master-lab/
|-- README.md                    Project entry point and summary
|-- labctl                       Safe lifecycle and IOL persistence controller
|-- inventory/                   Authoritative Master node/link inventory
|-- profiles/
|   |-- master/                  Master design and operating documentation
|   |-- inter-as/                Inter-AS inventory and operating guide
|   `-- srv6/                    SRv6 profile and acceptance gates
|-- tools/                       Generators, validators, readiness, and NVRAM tools
|-- templates/                   Jinja2 templates
|-- configs/                     Phase-based rendered configurations
|-- topology/                    Containerlab topologies, startup bootstrap, runtime labdirs
|-- automation/                  AUTO1 image and examples
`-- docs/                        Architecture, operations, persistence, and troubleshooting
```

Profile-specific entry points:

- [Lab 1 â€” Master ISP](../profiles/master/README.md)
- [Lab 2 â€” Inter-AS](../profiles/inter-as/README.md)
- [Lab 3 â€” SRv6](../profiles/srv6/README.md)
- [Acceptance status](../STATUS.md)
- [Blueprint matrix](../BLUEPRINT-MATRIX.md)
## 3. Source of truth and change flow

The Master uses two complementary authorities:

| State | Authority | Meaning |
|---|---|---|
| **REPO** | Topology, inventories, addressing, scripts, bootstrap, validators, and documentation | Structural source of truth |
| **RUNTIME ACTUAL** | Running configuration on the active routers | Source of truth for manual study state |
| **IOL NVRAM** | Complete binary startup state saved by IOS | Persistent IOL configuration across destroy/deploy |

The structural design follows this chain:

```text
Inventories + generator + templates
                 â†“
       reviewable repository artifacts
                 â†“
       Containerlab topology
                 â†“
       controlled deployment and validation
```

For `master`, the structural sources include `inventory/nodes.csv`,
`inventory/links.csv`, `tools/build_lab.py`, `tools/render_topology.py`, and
the related templates. Inter-AS and SRv6 use their profile-specific inventory
and generator files.

> [!IMPORTANT]
> The active Master may contain manual EVPN, multicast, BSR/RP, L3VPN, VRF,
> MP-BGP, eBGP PE-CE, dual-homing, route-policy, Local Preference,
> `as-override`, IPv4, and IPv6 study configuration that has not been promoted
> into generators or startup files.

Do not run `tools/build_lab.py`, regenerate Master startup configurations, or
deploy generated protocol phases merely to preserve live study work. A
generator is a deliberate offline repository operation, not a runtime backup
mechanism.

When structural automation is intentionally changed, update its authoritative
input, render offline, inspect the complete diff, and deploy only during an
approved window. This keeps diagrams, topology, addressing, interfaces,
configuration artifacts, and documentation aligned without treating generated
files as a complete copy of runtime.
## 4. Profiles and architecture

### 4.1 Lab 1 â€” Master ISP

Lab 1 contains **38 nodes and 57 links** split into two provider domains.

#### ISP-1 / AS500

- `P1-P8`: provider transit routers.
- `PE1-PE8`: provider edge and service termination.
- `RR1-RR2`: redundant Route Reflectors and PCE nodes.
- `CE1-CE9` and `C1-C2`: customer routers and endpoints.
- `AUTO1`: Linux automation workstation.
- Dual-stack IS-IS Level 2 and SR-MPLS foundation.
- Progressive MP-BGP, L3VPN, EVPN, multicast, and failure study.

`RR1` retains its RR, PCE, BSR, and RP study roles. CE2 uses PE1 as its eBGP
primary and PE2 as backup; CE5 uses PE4 as primary and PE3 as backup.

#### ISP-2 / AS65002

- `ASBR-ISP2`: XRd Control Plane ASBR.
- `RR-ISP2`: XRd Control Plane future route reflector.
- `ISP2-P1` and `ISP2-P2`: Cisco IOL P routers.
- `ISP2-P3` and `ISP2-P4`: Cisco IOL transit routers.
- `ISP2-P5`: Cisco IOL PE/service edge.
- `SOURCE1`: Linux IPv4/IPv6 traffic generator connected to `ISP2-P5`.
- Links `L048-L057`.
- OSPFv2 and OSPFv3 Area 0, configured manually during the first study phase.

The ISP-2 expansion uses no XRd vRouter/full dataplane. Its protocols are not
automatically generated: internal OSPF, eBGP, iBGP/RR, labeled unicast, and
Inter-AS services remain explicit manual study phases.

Platform totals:

```text
20 XRd Control Plane
16 Cisco IOL
 2 Linux containers (AUTO1 and SOURCE1)
---------------------------------------
38 nodes / 57 links
```

See the [Master diagram and addressing guide](../profiles/master/README.md).
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

The delivered baseline includes operational interfaces, an IPv6 IS-IS Level 2
underlay, management access, direct-link validation, and operational SRv6
locators. SRv6-TE policies, VPN services, advanced endpoint behaviors, TI-LFA,
and uSID scenarios remain progressive student work on top of that known-good
foundation.

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
Management:              10.201.255.0/24
ISP-1 IPv4 loopbacks:    10.0.0.<id>/32
ISP-1 IPv4 links:        10.255.0.0/31 onward
ISP-1 IPv6 loopbacks:    2001:db8:500:abcd::<id>/128
ISP-1 IPv6 core links:   2001:db8:1000:<link-id>::/127

ISP-2 ASN:               65002
ISP-2 IPv4 loopbacks:    10.65.2.1/32 through 10.65.2.7/32
ISP-2 IPv4 P2P links:    /31
ISP-2 IPv6 aggregate:    2001:db8:6502::/48
ISP-2 IPv6 P2P links:    /127
ISP-2 IGP:               OSPFv2 + OSPFv3 Area 0
```

Management additions are `10.201.255.151-158` for `ASBR-ISP2`, `RR-ISP2`,
`ISP2-P1-P5`, and `SOURCE1`. The `/31` and `/127` prefixes represent efficient
point-to-point links. Loopbacks remain stable router IDs and protocol endpoints.
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

### 6.1 Confirm the working copy

Operate from a clean, known repository revision:

```bash
cd /srv/netlab/labs/ccie-sp-startup-repair
pwd
git status --short --branch
git branch --show-current
git log -1 --oneline
```

Stop if unexpected modifications or untracked device backups appear. Existing
work must be reviewed or preserved before generation because a generator can
legitimately update many files.

### 6.2 Confirm platform and virtualization

```bash
uname -a
cat /etc/os-release
nproc
systemd-detect-virt
ls -l /dev/kvm

test -r /sys/module/kvm_amd/parameters/nested && \
  echo "kvm_amd nested=$(cat /sys/module/kvm_amd/parameters/nested)"

test -r /sys/module/kvm_intel/parameters/nested && \
  echo "kvm_intel nested=$(cat /sys/module/kvm_intel/parameters/nested)"
```

Expected results:

- `/dev/kvm` exists and is accessible to the runtime.
- Nested virtualization is enabled on a virtualized host.
- The CPU count matches the VM configuration.
- No unexpected hypervisor change has occurred.

### 6.3 Confirm software and images

```bash
docker version
containerlab version
docker info --format 'root={{.DockerRootDir}} driver={{.Driver}}'

docker image ls --format '{{.Repository}}:{{.Tag}} | {{.ID}} | {{.Size}}' | \
  grep -E 'ios-xr/xrd-control-plane:24.2.11|vrnetlab/cisco_iol:17.12.01|ccie-sp-automation:1.0'
```

The expected image references are:

```text
ios-xr/xrd-control-plane:24.2.11
vrnetlab/cisco_iol:17.12.01
ccie-sp-automation:1.0
```

If an image is missing, stop and follow the
[installation and image-build guide](CONTAINERLAB-INSTALLATION.md). Network
operating-system images are local licensed prerequisites and are not downloaded
by this repository.

### 6.4 Create the Python environment

Use an isolated virtual environment for automation dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

test -f automation/requirements.txt && \
  python -m pip install -r automation/requirements.txt

python -c 'import netmiko; print("Netmiko", netmiko.__version__)'
```

Reusing a previously validated `.venv` is acceptable. The virtual environment
is local runtime state and must not be committed.

### 6.5 Load runtime credentials

Create and load the local credential file before deployment:

```bash
cp .env.example .env
# Replace every placeholder in .env, then:
set -a
source .env
set +a
```

The real `.env` file is ignored by Git. Never place production credentials or
provider tokens in it. Confirm that the required variables exist without
printing their values:

```bash
for variable in \
  CCIE_XRD_USERNAME CCIE_XRD_PASSWORD \
  CCIE_IOL_USERNAME CCIE_IOL_PASSWORD \
  CCIE_AUTO_USERNAME CCIE_AUTO_PASSWORD; do
  [[ -n "${!variable:-}" ]] || echo "MISSING: $variable"
done
```

### 6.6 Check active labs and host capacity

Run the host checks:

```bash
cd /srv/netlab/labs/ccie-sp-startup-repair
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

Treat those measurements as observed planning data, not universal guarantees.
Image release, hypervisor scheduling, startup concurrency, and host workload can
change resource demand.

### 6.7 Go/no-go decision

Proceed only when all checks below pass:

| Check | Go condition |
|---|---|
| Active lab | No other `clab-ccie-sp-*` nodes are running |
| KVM | `/dev/kvm` exists and nested virtualization is enabled if required |
| Images | Every image required by the chosen profile exists locally |
| Credentials | Required variables are loaded without exposing their values |
| Memory | Available memory is above the selected profile's operating gate |
| Swap | No active swap pressure |
| Load | Host load is stable before deployment |
| Storage | `/srv/netlab` has adequate working space |
| Repository | No unexplained local changes |

## 7. Reproducible generation

Generation is an **offline structural workflow**, not part of normal daily
startup and not a method for preserving manual runtime configuration.

> [!WARNING]
> If the Master is active and contains manual study configuration, do not run
> `tools/build_lab.py` or regenerate its startup configurations. First capture
> evidence and backups, schedule a controlled window, and review the intended
> structural scope.

When generation is explicitly intended:

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

For unchanged inputs, generation should be deterministic. Review every file;
never use reset/restore merely to hide an unexplained difference.

### 7.1 Generation acceptance

| Artifact | Questions to answer |
|---|---|
| Node inventory | Are names, roles, platforms, IDs, and management addresses unique? |
| Link inventory | Are endpoints, interfaces, link IDs, `/31`, and `/127` allocations correct? |
| Topology YAML | Do images, mounts, bootstrap, management, and links match the profile? |
| Bootstrap | Does it contain only the intended minimum or accepted automated baseline? |
| Protocol phase | Is it approved for automation, or must it remain manual? |
| Diagram | Does the visual topology match inventory and link IDs? |

> [!CAUTION]
> A successful generator exit code proves only that generation completed.
> Human semantic review remains an acceptance requirement.
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

For the Master profile, the controller also loads the ignored local `.env`,
passes only the required `CCIE_*` variables through `sudo`, and runs
`tools/wait_ready.py`. Readiness means authenticated CLI access on every node;
an open TCP port alone is insufficient. The default deadline is 900 seconds,
but the command returns as soon as all nodes are ready.

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

Destroying a lab removes its ephemeral containers and links. Source files and
documentation remain in the repository. For `master`, `labctl` first captures
and backs up complete IOL NVRAM, allowing IOS configuration saved with
`write memory` to survive the next controlled deploy.


### 8.1 Complete Cisco IOL persistence

The Master preserves complete binary NVRAM for `CE1-CE9`, `C1-C2`, and
`ISP2-P1-P5`. Save normally from IOS:

```text
CE2# copy running-config startup-config
```

Containerlab stores native IOL NVRAM under a PID-based filename. Because that
PID may change after topology edits, the repository wrapper mirrors each
binary to a stable node-centric location:

```text
topology/persistent/iol/<node>/nvram
```

Before Master destroy, `labctl` captures and backs up the complete NVRAM.
Before deploy, it restores the binary using the PID expected by Containerlab.
This preserves usernames, management, interfaces, SSH/HTTP, routing protocols,
ACLs, route maps, VRFs, and every other saved IOS configuration without
filtering `show running-config`.

```bash
python3 tools/iol_nvram.py status
python3 tools/iol_nvram.py backup --label before-study-change
```

Files under `topology/startup/*.partial.cfg` are first-boot bootstrap only.
Never use `containerlab destroy --cleanup` when persistent state must survive.
Use `labctl` rather than raw Containerlab lifecycle commands for the Master.

## 9. First deployment runbook

Use this procedure for the first boot of any profile.

### Step 1 — Select exactly one profile

```bash
PROFILE=master
# Valid values: master, inter-as, srv6
```

The variable is only a convenience for this shell session. Confirm it before
every destructive lifecycle command:

```bash
printf 'Selected profile: %s\n' "$PROFILE"
```

### Step 2 — Confirm the topology parses

```bash
sudo containerlab apply \
  -t "topology/ccie-sp-${PROFILE}.clab.yml" \
  --dry-run
```

For a new deployment, the expected plan is `deploy lab`. For an existing lab,
read every proposed node recreation or link modification before continuing.

### Step 3 — Capture the pre-deployment state

```bash
date -Is
free -h
uptime
df -h /srv/netlab
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
```

Keep this output with the exercise notes. It provides the reference for later
resource and stability comparisons.

### Step 4 — Deploy through the lifecycle controller

```bash
./labctl deploy "$PROFILE"
```

Do not start a second deployment terminal. XRd and vrnetlab nodes have long
boot sequences, and duplicate deployment attempts make the resulting state
harder to interpret.

### Step 5 — Observe the startup window

For `master`, `labctl` already performs the authoritative readiness loop and
prints each node as it becomes ready. The following command is optional visual
observation, not a timer or acceptance gate:

```bash
watch -n 15 "docker ps \
  --filter name=clab-ccie-sp-${PROFILE} \
  --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'"
```

Exit `watch` with `Ctrl+C` after the expected nodes are running. Some vrnetlab
nodes transition through `health: starting` or temporary `unhealthy` states
while their nested VM boots. Judge readiness using sustained health, TCP/22,
and CLI access rather than one early snapshot.

### Step 6 — Check container health

```bash
for container in $(docker ps \
  --filter "name=clab-ccie-sp-${PROFILE}" \
  --format '{{.Names}}'); do
  docker inspect "$container" \
    --format '{{.Name}} status={{.State.Status}} restart={{.RestartCount}} oom={{.State.OOMKilled}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}n/a{{end}}'
done
```

Stop the rollout when a node repeatedly restarts, reports an OOM event, or
never reaches its expected management state.

### Step 7 — Check post-boot resources

```bash
free -h
uptime
docker stats --no-stream \
  $(docker ps --filter "name=clab-ccie-sp-${PROFILE}" --format '{{.Names}}')
```

High CPU during initial boot is expected. Persistent saturation after all nodes
are ready requires investigation before configuration deployment.

### Step 8 — Validate management and CLI

Choose the matching inventory:

```bash
case "$PROFILE" in
  master)   INVENTORY=inventory/nodes.csv ;;
  inter-as) INVENTORY=profiles/inter-as/nodes.csv ;;
  srv6)     INVENTORY=profiles/srv6/nodes.csv ;;
esac

python3 tools/validate_nodes.py \
  --inventory "$INVENTORY" \
  --workers 4
```

A TCP/22 success without a CLI success is not an accepted node. It normally
indicates an incomplete boot, incorrect username/password, or platform-specific
authentication mismatch.

### Step 9 — Save the deployment evidence

Record at minimum:

- Repository revision.
- Profile and topology filename.
- Docker and Containerlab versions.
- Image references and IDs.
- Node count and health state.
- CLI validation summary.
- Host CPU, RAM, swap, load, and disk state.
- Any warning, workaround, or platform limitation.

For a Master redeployment, saved IOL NVRAM is restored by `labctl`. XRd and
Linux bootstrap behavior follows the topology and documented profile workflow.
Generated startup files must not be assumed to contain every manual runtime
study configuration. Validate the actual runtime before applying any
additional phase. Inter-AS and SRv6 retain their documented staged workflows.

## 10. Phase-based and manual configuration

Never apply every advanced phase at once. The existing ISP-1 automated
foundation and the new ISP-2 manual workflow have different boundaries.

| Scope | Operating boundary |
|---|---|
| ISP-1 structural/accepted baseline | Repository-managed where documented |
| ISP-1 EVPN, multicast, L3VPN, PE-CE, and policy studies | May exist only in runtime; verify before automation |
| ISP-2 nodes, links, management, and minimum bootstrap | Repository-managed structure |
| ISP-2 OSPFv2/OSPFv3 | Manual phase 1 |
| ISP-2 eBGP IPv4/IPv6 and policies | Manual phase 2 |
| ISP-2 iBGP/RR, LU, and Inter-AS L3VPN | Future independent manual sessions |
| AUTO1 | Preserved; no automatic ISP-2 protocol deployment yet |

The ISP-2 workflow is:

```text
design â†’ offline validation â†’ controlled deploy â†’ manual configuration
       â†’ troubleshooting â†’ write memory â†’ validation â†’ later automation review
```

For other profiles, continue to use documented phase-based canaries.
Inter-AS example:Inter-AS example:

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

## 11. Controlled change procedure

Use the same workflow for a configuration phase, a personal study exercise, or
a topology refinement.

### Step 1 — Define the change

Write down:

- Intended profile and node scope.
- Current state.
- Desired state.
- Expected protocol or service effect.
- Validation commands.
- Rollback method.

If these items cannot be stated clearly, the change is not ready to apply.

### Step 2 — Back up the target nodes

```bash
python3 tools/backup_provider.py \
  --inventory profiles/srv6/nodes.csv \
  --nodes P1,P2 \
  --workers 2 \
  --label before-change
```

Select the inventory and nodes that match the real scope. Backups are runtime
evidence and may contain sensitive data; keep them outside Git.

### Step 3 — Render and inspect

Regenerate the relevant artifacts and inspect both syntax and semantics:

```bash
git status --short
git diff --check
git diff -- configs topology inventory profiles
```

### Step 4 — Apply to a canary

```bash
python3 tools/apply_phase.py 00-base \
  --profile srv6 \
  --nodes P1 \
  --workers 1
```

Use one node when testing syntax or node-local behavior. Use two directly
connected nodes when the acceptance condition requires an adjacency or link.

### Step 5 — Validate the canary

Check all layers affected by the change:

```text
configuration accepted
        -> interface state
        -> addressing
        -> adjacency or session
        -> route/label/SID installation
        -> end-to-end service
```

Do not expand a phase merely because the configuration command returned
successfully.

### Step 6 — Expand in controlled batches

Recommended order:

1. Core P nodes.
2. PE and RR nodes.
3. CE or customer nodes.
4. Service-specific nodes.

Keep worker counts conservative on a nested-virtualization host. Parallelism
reduces elapsed time but can also create CPU contention and misleading timeouts.

### Step 7 — Run post-change validation

Repeat the pre-change commands and compare:

- Adjacency and session counts.
- Route, label, and SID state.
- Direct-link and end-to-end reachability.
- Container restart and OOM state.
- Host resource state.
- Configuration failure output.

### Step 8 — Roll back or preserve

If acceptance fails:

1. Stop expansion.
2. Preserve the failing output.
3. Identify the last accepted configuration commit or backup.
4. Roll back only the affected scope.
5. Re-run baseline validation.
6. Document the cause and resolution.

If acceptance passes, update the relevant status or validation document and
commit only reproducible source artifacts.

## 12. Validation

Validation proceeds from infrastructure to services. A higher-layer success
does not remove the requirement to understand lower-layer state.

### 12.1 Node management and CLI

Master:

```bash
python3 tools/validate_nodes.py \
  --inventory inventory/nodes.csv \
  --workers 4
```

Inter-AS:

```bash
python3 tools/validate_nodes.py \
  --inventory profiles/inter-as/nodes.csv --workers 4
```

SRv6:

```bash
python3 tools/validate_nodes.py \
  --inventory profiles/srv6/nodes.csv \
  --workers 4
```

Interpret the summary carefully:

- `tcp22=open` proves transport reachability only.
- `cli=ok` proves authentication and prompt detection.
- The reported software version must match the documented image.
- A failure on every node of one platform usually indicates credentials or
  platform parameters rather than simultaneous device failure.

### 12.2 Directly connected links

Master:

```bash
python3 tools/validate_links.py \
  --profile master \
  --family both \
  --workers 2
```

Inter-AS:

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

These validators test directed reachability. A physical link normally produces
one test from each endpoint and for each selected address family. A single
failed direction may indicate an interface, address, ACL, source-selection, or
parser issue and must not be silently ignored.

### 12.3 Control-plane checks

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

Recommended validation order:

| Layer | Evidence |
|---|---|
| Container | Running state, health, restart count, OOM state |
| Management | TCP/22, authentication, prompt, and software version |
| Interface | Administrative and operational state |
| Addressing | Expected IPv4/IPv6 addresses and connected routes |
| IGP | Expected neighbor count, levels/areas, metrics, and loopback routes |
| Transport | MPLS labels, Prefix-SIDs, locators, and next-hop resolution |
| BGP | Session state, address-family activation, policy, and prefixes |
| Service | VRF/bridge state, route import/export, and end-to-end traffic |
| Resiliency | Failure detection, alternate path, convergence, and recovery |

### 12.4 Accepted evidence

The current Master structural baseline includes:

- 38 declared nodes and 57 links.
- 20 XRd Control Plane, 16 Cisco IOL, and two Linux containers.
- ISP-1 `P1-P8`, `PE1-PE8`, `RR1-RR2`, `CE1-CE9`, `C1-C2`, and `AUTO1`.
- ISP-2 `ASBR-ISP2`, `RR-ISP2`, `ISP2-P1-P5`, and `SOURCE1`.
- ISP-2 structural links `L048-L057` and management `.151-.158`.
- Complete node-centric IOL NVRAM capture for all 16 IOL nodes.
- Established ISP-1 IS-IS/SR-MPLS, RR, EVPN, multicast, L3VPN, and PE-CE
  study milestones, some of which may remain manual runtime state.

Do not interpret structural presence as automatic protocol completion in
ISP-2. OSPF, eBGP, iBGP/RR, LU, and Inter-AS services follow the approved
manual phases and require their own evidence.

The Inter-AS and SRv6 acceptance evidence remains profile-specific and is
maintained in `STATUS.md` and their validation documents.
## 13. Inter-AS practice workflow

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

## 14. SRv6 practice workflow

Start every SRv6 exercise from the validated IPv6 underlay:

1. Verify links, loopbacks, and all expected IS-IS adjacencies.
2. Allocate and advertise one locator per provider node.
3. Inspect locally allocated End and End.X SIDs.
4. Build an explicit SRv6-TE policy between selected PE nodes.
5. Add VPNv4/VPNv6 services and validate DT4/DT6 behavior.
6. Introduce a link failure and measure convergence or TI-LFA behavior.
7. Repeat with uSID only after the classic SRv6 behavior is understood.
8. Restore or redeploy the baseline before starting a different scenario.

## 15. AUTO1 and synchronization

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

## 16. Troubleshooting and recovery

Troubleshoot from the lowest layer upward:

```text
container ? interface ? addressing ? IGP ? labels/next hop
? iBGP/RR ? eBGP/policy ? VPN/service
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

### 16.1 First-response collection

Before restarting or destroying anything, collect evidence:

```bash
date -Is
free -h
uptime
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
docker stats --no-stream
./labctl status
git status --short --branch
```

For one failing container:

```bash
docker inspect <container-name> \
  --format 'status={{.State.Status}} restart={{.RestartCount}} oom={{.State.OOMKilled}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}n/a{{end}}'

docker logs --since 10m <container-name> 2>&1 | tail -200
```

Do not expose passwords, environment variables, private keys, or full
configurations containing secrets in public evidence.

### 16.2 Recovery decision

| Condition | Preferred response |
|---|---|
| One rejected configuration | Inspect `show configuration failed`, abort the candidate, and correct syntax |
| One bad committed change | Use the platform configuration rollback for that change |
| One node incomplete after boot | Preserve logs, confirm resources, and use the documented Containerlab lifecycle |
| Link missing after an unmanaged restart | Destroy and redeploy the profile so Containerlab recreates the wiring |
| Widespread authentication failure | Verify per-platform credentials before touching configurations |
| Widespread timeout under high load | Reduce workers, wait for boot stabilization, and recheck host resources |
| Unknown multi-node state | Back up evidence, destroy the selected profile, regenerate, and redeploy |

### 16.3 Clean redeployment

Use clean redeployment only when the selected profile lifecycle is understood
and relevant evidence has been preserved. For Master IOL nodes, first save IOS:

```text
copy running-config startup-config
```

Then use the wrapper:

```bash
PROFILE=master

python3 tools/iol_nvram.py status
./labctl destroy "$PROFILE"

docker ps --format '{{.Names}}' | grep '^clab-' || \
  echo 'PASS: no active Containerlab nodes'

free -h
uptime

./labctl deploy "$PROFILE"
python3 tools/iol_nvram.py status
```

Do not use `--cleanup`. Destroy/redeploy is not a substitute for understanding
a configuration failure, and XRd/Linux manual runtime state requires its own
documented backup strategy.
## 17. Professional Git workflow

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

## 18. Completion criteria

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
