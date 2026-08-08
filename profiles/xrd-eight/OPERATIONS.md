# XRd Eight v2 — Detailed Operating Guide

> **Operational runbook for building, validating, deploying, operating, troubleshooting and destroying the XRd Eight v2 full-dataplane Service Provider laboratory.**
>
> This guide distinguishes the repository Source of Truth, generated artifacts, Containerlab runtime state and the configuration currently running inside each router.

XRd Eight v2 is designed to be reproducible.

A successful deployment should always be traceable back to a known Git revision and a deterministic set of generated repository artifacts.

The operational lifecycle therefore follows:

```text
Repository Source of Truth
          |
          v
Artifact Generation
          |
          v
Static Validation
          |
          v
Git Review / Clean State
          |
          v
Containerlab Deployment
          |
          v
Runtime Validation
          |
          v
Protocol / Service Work
          |
          v
Evidence / Backups
          |
          v
Clean Destruction
```

The most important operational rule is:

> **Do not confuse generated repository configuration with Containerlab runtime files or the running configuration inside a live router.**

They are three different states and must be managed independently.

---

# Operational State Model

XRd Eight v2 has four relevant configuration layers.

| Layer | Description | Persistent in Git? |
| --- | --- | --- |
| Repository Source of Truth | Builder logic and explicit addressing data | Yes |
| Generated artifacts | Startup configs, inventories and topology generated from the repository model | Yes |
| Containerlab runtime copy | Disposable files created during deployment | No |
| Router running configuration | Configuration currently active inside XRd/IOL-XE | No, unless intentionally promoted |

Conceptually:

```text
Source of Truth
      |
      v
Generated Startup Configuration
      |
      v
Containerlab Runtime Copy
      |
      v
Router Running Configuration
```

A change made at the bottom of this chain does **not** automatically propagate upward.

For example:

```text
IOS XR commit
```

changes the live router but does not automatically modify:

```text
tools/build_xrd_eight.py
```

or:

```text
configs/xrd-eight/00-foundation/
```

Similarly, editing a generated startup file manually does not modify the authoritative builder logic.

---

# Repository Directory Model

The principal XRd Eight v2 files and directories are shown below.

| Path | Purpose | Edit directly? |
| --- | --- | --- |
| `tools/build_xrd_eight.py` | Authoritative topology logic, node model and generated foundation | Yes, after review |
| `profiles/xrd-eight/links-v2.csv` | Explicit v2 endpoint and P2P addressing Source of Truth | Yes, after review |
| `tools/validate_xrd_eight_addressing.py` | Static addressing validator | Yes, after review |
| `tools/render_xrd_eight.py` | Generates the SVG topology from repository inventories | Yes, after review |
| `profiles/xrd-eight/nodes.csv` | Generated node inventory | No |
| `profiles/xrd-eight/links.csv` | Generated normalized link/address inventory | No |
| `configs/xrd-eight/00-foundation/` | Generated startup configuration candidates | No |
| `topology/ccie-sp-xrd-eight.clab.yml` | Generated Containerlab topology | No |
| `profiles/xrd-eight/topology.svg` | Generated architecture diagram | No |
| `profiles/xrd-eight/labctl` | Profile lifecycle wrapper | Review before changing |
| `automation/xrd-eight/workspace/` | Persistent automation playbooks, templates and scripts | Yes |
| `automation/xrd-eight/data/` | Persistent AAA/RPKI/service data | Runtime data |
| `automation/xrd-eight/evidence/` | Validation evidence and collected state | Runtime evidence |
| `automation/xrd-eight/backups/` | Device configuration backups | Never commit secrets |
| `topology/clab-ccie-sp-xrd-eight/` | Containerlab runtime directory | Never edit; disposable |

---

# Source of Truth

The repository is intentionally generator-driven.

The main infrastructure definition is:

```text
tools/build_xrd_eight.py
```

Explicit v2 link addressing is maintained in:

```text
profiles/xrd-eight/links-v2.csv
```

Generated inventories are:

```text
profiles/xrd-eight/nodes.csv
profiles/xrd-eight/links.csv
```

Generated startup configurations are stored under:

```text
configs/xrd-eight/00-foundation/
```

The generated Containerlab topology is:

```text
topology/ccie-sp-xrd-eight.clab.yml
```

The important distinction is:

```text
build_xrd_eight.py + links-v2.csv
              |
              | authoritative input
              v
         Generated Files
```

Do not fix a permanent infrastructure problem by manually editing a generated file.

Instead:

1. modify the Source of Truth;
2. regenerate;
3. validate;
4. inspect the Git diff;
5. test;
6. commit through the normal Git workflow.

---

# Generated Foundation

The current generated foundation contains:

```text
P1.cfg
P2.cfg
P3.cfg
P4.cfg
PE1.cfg
PE2.cfg
PE3.cfg
RR.cfg
CE1.cfg
CE2.cfg
CE3.cfg
```

The eight XRd configurations contain the provider foundation.

The three CE configurations intentionally remain minimal so customer services can be built according to the exercise being studied.

The generated provider foundation includes:

- hostnames;
- login/MOTD banners;
- management integration;
- deterministic Node IDs;
- IPv4 Loopback0 addresses;
- IPv6 Loopback0 addresses;
- IPv4 `/31` infrastructure addressing;
- IPv6 `/127` infrastructure addressing;
- IS-IS Level 2 process `500-SP`;
- deterministic IS-IS NETs;
- SR-MPLS;
- IPv4 Prefix-SIDs;
- IPv6 Prefix-SIDs;
- BFD intent;
- per-prefix fast-reroute foundation.

Higher-layer services remain intentionally outside the generated baseline.

---

# Container Images

XRd Eight v2 currently uses the following local images.

| Function | Nodes | Local Image |
| --- | --- | --- |
| Provider Core | `P1-P4` | `vrnetlab/cisco_xrd-vrouter:26.2.1` |
| Provider Edge | `PE1-PE3` | `vrnetlab/cisco_xrd-vrouter:26.2.1` |
| Control Plane | `RR` | `vrnetlab/cisco_xrd-vrouter:26.2.1` |
| Customer Edge | `CE1-CE3` | `vrnetlab/cisco_iol:17.12.01` |
| Automation | `AUTO1` | `ccie-sp-automation:1.0` |

Cisco software images are not stored in this repository.

The XRd image used during local development was independently obtained and verified using Cisco-provided verification material before being loaded locally.

Example verification workflow:

```bash
python3 cisco_x509_verify_release.py3 \
  -e IOS-XR-SW-XRd.crt \
  -i xrd-vrouter-container-x64.dockerv1.tgz \
  -s xrd-vrouter-container-x64.dockerv1.tgz.signature \
  -v smime \
  --container xr \
  --sig_type DER
```

Load the vendor image:

```bash
docker load -i xrd-vrouter-container-x64.dockerv1.tgz
```

Inspect the source and local vrnetlab images:

```bash
docker image inspect ios-xr/xrd-vrouter:26.2.1
docker image inspect vrnetlab/cisco_xrd-vrouter:26.2.1
```

XRd Eight uses:

```text
XRD_NIC_TYPE=igb
```

because this interface model was validated against the local XRd dataplane environment.

The generated topology therefore includes:

```yaml
kinds:
  cisco_xrd_vrouter:
    image: vrnetlab/cisco_xrd-vrouter:26.2.1
    env:
      XRD_NIC_TYPE: igb
```

---

# Image Preflight

Before a deployment, verify that all required images exist locally.

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

All three images must return an image ID.

Do not begin deployment if any required image reports:

```text
IMAGE NOT FOUND
```

---

# Laboratory Credentials

These credentials are disposable defaults for the isolated laboratory environment.

They must not be reused for production infrastructure.

| Platform | Username | Password |
| --- | --- | --- |
| XRd vRouter | `clab` | `clab@123` |
| IOL-XE | `admin` | `admin` |
| AUTO1 | `student` | supplied through `CCIE_AUTO_PASSWORD` |

AUTO1's runtime password is intentionally not stored in Git.

---

# AUTO1 Password Handling

Load the AUTO1 password interactively without displaying it:

```bash
read -rsp "CCIE_AUTO_PASSWORD: " CCIE_AUTO_PASSWORD
echo
export CCIE_AUTO_PASSWORD
```

Verify that the variable exists without displaying its value:

```bash
if [ -n "${CCIE_AUTO_PASSWORD:-}" ]; then
  echo "CCIE_AUTO_PASSWORD: SET"
else
  echo "CCIE_AUTO_PASSWORD: NOT SET"
fi
```

Expected output:

```text
CCIE_AUTO_PASSWORD: SET
```

Do not print the password into logs.

Do not place it inside:

```text
README files
YAML topology files
Git commits
playbooks
inventory files
shell scripts
```

The profile lifecycle wrapper preserves the variable when invoking Containerlab through `sudo`.

---

# Management Network

The dedicated management subnet is:

```text
10.207.255.0/24
```

Containerlab management network:

```text
ccie-sp-xrd-eight-mgmt
```

Current management allocation:

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

The management network must remain available independently from the Service Provider transport plane.

---

# Git Pre-Deployment Gate

Full-dataplane deployment should normally occur from a synchronized and clean `main`.

Enter the repository:

```bash
cd /srv/netlab/labs/ccie-sp-master
```

Switch to `main`:

```bash
git switch main
```

Synchronize:

```bash
git pull --ff-only origin main
```

Verify repository state:

```bash
git status --short --branch
git rev-parse --short HEAD
git rev-parse --short origin/main
```

The local and remote commit IDs should match.

A clean state should look conceptually like:

```text
## main
<commit>
<commit>
```

Unexpected working-tree modifications should be investigated before deployment.

---

# Generate Before Deployment

Regenerate the complete XRd Eight v2 foundation:

```bash
cd /srv/netlab/labs/ccie-sp-master

python3 tools/build_xrd_eight.py
```

Expected summary:

```text
Generated topology: /srv/netlab/labs/ccie-sp-master/topology/ccie-sp-xrd-eight.clab.yml
Generated ISP configs: 8
Generated CE configs: 3
Generated links: 19
Repository profile: profiles/xrd-eight
```

---

# Deterministic Build Gate

An unchanged Source of Truth must regenerate identical artifacts.

Immediately after running the builder:

```bash
git status --short
```

Expected result:

```text
<no output>
```

If generated files appear modified after an unchanged build, stop and inspect the diff.

Use:

```bash
git diff
```

Generated artifacts should only change when the underlying Source of Truth changes.

---

# Addressing Validation

Run the permanent dual-stack validator:

```bash
python3 tools/validate_xrd_eight_addressing.py
```

Expected output:

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

Do not deploy if this validator fails.

---

# Regenerate the Topology Diagram

Generate the current SVG topology:

```bash
python3 tools/render_xrd_eight.py
```

Generated diagram:

```text
profiles/xrd-eight/topology.svg
```

The renderer consumes the same profile inventories used by the rest of the lab.

This keeps topology documentation aligned with the repository model.

---

# Repository Integrity Check

Run:

```bash
git diff --check
```

The command should return no errors.

Then confirm:

```bash
git status --short
```

For an unchanged repository baseline, no generated modification should remain.

---

# Host Preflight Safety Gate

XRd Eight v2 is a resource-intensive full-dataplane profile.

Before deployment, verify that no conflicting heavy lab is active.

Check for existing Containerlab containers:

```bash
docker ps --format '{{.Names}}' | grep '^clab-' || echo "PASS: no active lab"
```

For an XRd Eight-specific stale deployment check:

```bash
docker ps -a --format '{{.Names}}' | \
  grep '^clab-ccie-sp-xrd-eight-' || \
  echo "PASS: no existing XRd Eight containers"
```

---

# Host Resource Check

Inspect memory:

```bash
free -h
```

Inspect CPU count:

```bash
nproc
```

Inspect load:

```bash
uptime
```

Inspect KVM:

```bash
ls -l /dev/kvm
```

If the host uses AMD virtualization, nested virtualization can also be inspected with:

```bash
cat /sys/module/kvm_amd/parameters/nested
```

For Intel hosts, use the appropriate `kvm_intel` equivalent.

Do not start another heavy profile concurrently with XRd Eight.

---

# Pre-Deployment Stop Conditions

Do not proceed with the full deployment if any of the following is true:

- another heavy Containerlab topology is already running;
- required Docker images are missing;
- `CCIE_AUTO_PASSWORD` is not set;
- the repository is unexpectedly dirty;
- static addressing validation fails;
- generated artifacts differ unexpectedly from Git;
- `/dev/kvm` is unavailable;
- virtualization support is not functioning;
- the host is already under severe memory pressure;
- stale XRd Eight runtime containers remain from an earlier deployment.

---

# Startup Topology

XRd nodes use staggered startup delays to reduce simultaneous CPU and memory pressure.

Current startup schedule:

| Node | Startup Delay |
| --- | ---: |
| `P1` | `0 s` |
| `P2` | `120 s` |
| `P3` | `240 s` |
| `P4` | `360 s` |
| `PE1` | `480 s` |
| `PE2` | `600 s` |
| `PE3` | `720 s` |
| `RR` | `840 s` |
| `CE1` | `960 s` |
| `CE2` | `970 s` |
| `CE3` | `980 s` |

`AUTO1` does not require the XRd staggered boot sequence and may start immediately.

A complete startup therefore takes significant time.

The presence of a delayed later node is not itself a failure.

---

# Start the Complete Profile

Enter the repository:

```bash
cd /srv/netlab/labs/ccie-sp-master
```

Ensure AUTO1 credentials are loaded:

```bash
if [ -n "${CCIE_AUTO_PASSWORD:-}" ]; then
  echo "CCIE_AUTO_PASSWORD: SET"
else
  echo "CCIE_AUTO_PASSWORD: NOT SET"
fi
```

Deploy:

```bash
./profiles/xrd-eight/labctl deploy-full
```

The lifecycle wrapper performs the equivalent full Containerlab deployment while preserving:

```text
CCIE_AUTO_PASSWORD
```

through the `sudo` boundary.

Do not start a second deployment while the first one is still progressing.

---

# Provider-Only Deployment

For transport-only work, the provider XRd infrastructure can be started independently.

```bash
./profiles/xrd-eight/labctl deploy-isp
```

The provider node filter contains:

```text
P1,P2,P3,P4,PE1,PE2,PE3,RR
```

This mode is useful for work involving:

- IS-IS;
- SR-MPLS;
- BFD;
- fast reroute;
- BGP;
- Route Reflection;
- PCE;
- provider convergence;

without consuming CE/AUTO1 resources unnecessarily.

---

# Observe Container Status

Use the profile wrapper:

```bash
./profiles/xrd-eight/labctl status
```

The full deployment should eventually contain:

```text
12 containers
```

Expected logical composition:

```text
8 XRd vRouters
3 IOL-XE routers
1 AUTO1 Linux node
```

---

# Observe Resource Consumption

Run:

```bash
./profiles/xrd-eight/labctl resources
```

The command reports:

- host memory;
- host uptime/load;
- Docker resource consumption for active XRd Eight containers.

Because XRd vRouter provides a full dataplane, elevated CPU and memory consumption during startup is expected.

---

# XRd Health Validation

Inspect all eight XRd nodes:

```bash
for node in P1 P2 P3 P4 PE1 PE2 PE3 RR; do
  docker inspect "clab-ccie-sp-xrd-eight-$node" \
    --format '{{.Name}} health={{if .State.Health}}{{.State.Health.Status}}{{end}} restart={{.RestartCount}} oom={{.State.OOMKilled}}'
done
```

The desired steady state is:

```text
health=healthy
restart=0
oom=false
```

for all eight XRd instances.

---

# Runtime Stop Conditions

Investigate immediately if an XRd node:

- becomes OOM-killed;
- repeatedly restarts;
- exits unexpectedly;
- remains unhealthy beyond its expected boot period;
- consumes abnormal resources compared with its peers;
- fails to expose management services after boot;
- shows persistent startup failures.

Also investigate if the host begins using unexpected swap or enters severe sustained memory pressure.

---

# Check Container Count

Count XRd Eight containers:

```bash
docker ps -a \
  --filter name=clab-ccie-sp-xrd-eight \
  --format '{{.Names}}' | wc -l
```

Expected full deployment:

```text
12
```

---

# Connect to Devices

## Provider Core

```bash
ssh clab@10.207.255.101
```

Target:

```text
P1
```

Additional provider management addresses:

```text
P2   10.207.255.102
P3   10.207.255.104
P4   10.207.255.106

PE1  10.207.255.107
PE2  10.207.255.108
PE3  10.207.255.103

RR   10.207.255.105
```

---

## Route Reflector

```bash
ssh clab@10.207.255.105
```

Target:

```text
RR
```

---

## Customer Edge

Example:

```bash
ssh admin@10.207.255.141
```

Target:

```text
CE1
```

Other CE addresses:

```text
CE2  10.207.255.143
CE3  10.207.255.146
```

---

## AUTO1

```bash
ssh student@10.207.255.150
```

AUTO1 provides the automation and operations workspace.

---

# Runtime Acceptance Sequence

Do not validate the entire protocol stack at once.

Acceptance should proceed layer by layer.

---

## Stage 1 — Container Acceptance

Validate:

```text
12 expected containers exist
8 XRd instances eventually become healthy
XRd restart count remains zero
XRd OOM state remains false
3 IOL-XE nodes remain running
AUTO1 remains running
```

---

## Stage 2 — Management Acceptance

Verify management reachability to:

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

The management plane should be validated before protocol troubleshooting begins.

---

## Stage 3 — Physical Interface Acceptance

Validate all:

```text
19 physical links
38 physical endpoints
```

Provider links:

```text
6 core
6 provider
2 control
```

Customer links:

```text
5 customer
```

---

## Stage 4 — IPv4/IPv6 Acceptance

Validate:

```text
19 IPv4 /31 networks
19 IPv6 /127 networks
8 IPv4 provider loopbacks
8 IPv6 provider loopbacks
```

Confirm physical-neighbor reachability before moving to IS-IS.

---

## Stage 5 — IS-IS Acceptance

Validate:

- IS-IS process `500-SP`;
- Level-2-only operation;
- expected infrastructure interfaces;
- absence of CE-facing interfaces in provider IS-IS;
- IPv4 adjacencies;
- IPv6 topology behavior;
- Loopback0 advertisement;
- expected shortest paths.

---

## Stage 6 — BFD Acceptance

Validate BFD sessions on provider infrastructure links.

Expected scope:

```text
core
provider
control
```

Customer-facing service interfaces remain outside the provider foundation unless the exercise explicitly adds BFD.

---

## Stage 7 — SR-MPLS Acceptance

Validate:

- SRGB `16000-23999`;
- IPv4 Prefix-SIDs `1-8`;
- IPv6 Prefix-SIDs `601-608`;
- MPLS forwarding entries;
- expected SID reachability;
- forwarding behavior between provider loopbacks.

---

## Stage 8 — Convergence Acceptance

Introduce controlled failures only after the baseline is stable.

Examples:

```text
P1-P2 failure
PE1-P1 failure
RR-P1 failure
P4 node failure
```

Observe:

- IS-IS convergence;
- BFD response;
- FRR behavior;
- MPLS forwarding changes;
- alternate path selection.

---

## Stage 9 — Service Acceptance

Only after transport is stable should higher-layer services be introduced.

Examples:

```text
BGP
Route Reflection
L3VPN
VPNv6
VPWS
VPLS
EVPN
EVPN Multihoming
SR Policy
PCE
Multicast
QoS
RPKI
```

---

# Manual Configuration and Persistence

A manual configuration change inside a live router affects that container only.

On IOS XR:

```text
commit
```

persists the change within the live router/container lifecycle.

On IOS-XE:

```text
write memory
```

persists the live device state.

Neither action automatically updates the Git repository.

---

## Important Persistence Rule

This:

```text
Router running-config
```

does not automatically become:

```text
Repository Source of Truth
```

Destroying the lab can remove runtime configuration that was never exported or promoted.

---

# Manual Backup Before Destructive Operations

Create a private backup directory if required:

```bash
mkdir -p automation/xrd-eight/backups/manual
```

Example provider backup:

```bash
ssh clab@10.207.255.101 'show running-config' \
  > automation/xrd-eight/backups/manual/P1.cfg
```

Example RR backup:

```bash
ssh clab@10.207.255.105 'show running-config' \
  > automation/xrd-eight/backups/manual/RR.cfg
```

Backups may contain:

- credentials;
- community strings;
- keys;
- tokens;
- AAA data;
- topology state.

Treat them as private runtime artifacts.

Do not commit sensitive backups.

---

# Promoting a Manual Change into the Baseline

If a manual experiment produces a configuration that should become part of the permanent generated foundation, do not simply copy the running configuration over a generated file.

Use this workflow:

```text
Running Configuration
        |
        v
Review Intended Change
        |
        v
Modify Source of Truth
        |
        v
Run Builder
        |
        v
Static Validation
        |
        v
Inspect Git Diff
        |
        v
Test
        |
        v
Pull Request / Merge
```

For generated XR infrastructure, the permanent change normally belongs in:

```text
tools/build_xrd_eight.py
```

or the relevant explicit Source-of-Truth inventory.

---

# AUTO1 Workflow

AUTO1 is intended to provide repeatable automation without bypassing engineering review.

A recommended workflow is:

1. load inventory and runtime credentials;
2. perform read-only discovery;
3. collect baseline state;
4. back up affected devices;
5. render candidate configuration;
6. review generated configuration;
7. perform dry/check validation where supported;
8. select one canary device;
9. deploy to the canary;
10. validate expected state;
11. continue serially to additional devices;
12. run post-checks;
13. store evidence;
14. roll back if an acceptance gate fails.

Conceptually:

```text
Inventory
   |
   v
Discovery
   |
   v
Backup
   |
   v
Render
   |
   v
Review
   |
   v
Canary
   |
   v
Validate
   |
   v
Serial Deployment
   |
   v
Postcheck
   |
   v
Evidence
```

---

# AUTO1 Workspace

Persistent automation development belongs under:

```text
automation/xrd-eight/workspace/
```

Typical content includes:

```text
Ansible playbooks
Python scripts
Jinja2 templates
inventory definitions
validation scripts
service exercises
rollback logic
```

For example, an EVPN or L2VPN exercise can be authored under the workspace while the physical topology and infrastructure addressing remain controlled by the repository profile.

---

# AUTO1 Persistent Data

The current Containerlab profile mounts:

```text
automation/xrd-eight/workspace
        ->
/workspace/xrd-eight
```

```text
automation/xrd-eight/data
        ->
/var/lib/ccie-sp
```

```text
automation/xrd-eight/evidence
        ->
/evidence
```

```text
automation/xrd-eight/backups
        ->
/backups
```

The mounts are deliberately separated by purpose.

---

# AAA and RPKI on AUTO1

AUTO1 can also support experiments involving centralized operations services.

Potential roles include:

- FreeRADIUS;
- TACACS+;
- Routinator;
- validation services;
- telemetry tooling.

Persistent service data belongs under:

```text
/var/lib/ccie-sp
```

Evidence belongs under:

```text
/evidence
```

Backups belong under:

```text
/backups
```

Enabling a service on AUTO1 does not automatically configure the routers to consume that service.

For example:

```text
Start Routinator on AUTO1
```

does not automatically mean:

```text
RPKI origin validation enabled on P/PE/RR
```

Router-side integration remains an explicit study phase.

The same applies to AAA.

---

# Evidence Collection

Runtime validation output should be stored under:

```text
automation/xrd-eight/evidence/
```

Useful evidence can include:

```text
container health
resource usage
interface state
IS-IS neighbors
IS-IS database
IPv4 routes
IPv6 routes
MPLS forwarding table
Prefix-SID state
BFD state
BGP summaries
VPN routes
EVPN routes
failure-test results
```

Evidence should identify the relevant lab state or exercise so it can be correlated with the configuration under test.

---

# Containerlab Runtime Directory

During deployment, Containerlab creates:

```text
topology/clab-ccie-sp-xrd-eight/
```

This directory is **runtime state**.

It is not the repository Source of Truth.

Typical runtime content may include device-specific startup copies such as:

```text
topology/clab-ccie-sp-xrd-eight/<node>/config/startup-config.cfg
```

Do not edit these files as a permanent configuration method.

---

# Stale Runtime Configuration Risk

A previous runtime copy can become dangerous when:

1. repository startup artifacts are regenerated;
2. an old Containerlab runtime directory survives;
3. Containerlab reuses runtime state;
4. a router boots with an older startup copy.

This can create the appearance that:

```text
the builder generated the wrong configuration
```

when the real problem is:

```text
Containerlab booted stale runtime state
```

For this reason, proper cleanup is part of the normal lifecycle.

---

# Troubleshooting Configuration Mismatches

If a live router does not match the expected generated foundation, compare the three states independently.

## Repository Generated Candidate

Example:

```bash
sed -n '1,240p' configs/xrd-eight/00-foundation/P1.cfg
```

## Containerlab Runtime Copy

Inspect the corresponding runtime file under:

```text
topology/clab-ccie-sp-xrd-eight/
```

if it exists.

## Live Running Configuration

Example:

```bash
ssh clab@10.207.255.101 'show running-config'
```

Compare:

```text
Repository candidate
        vs
Containerlab runtime copy
        vs
Live running configuration
```

Do not assume they are identical.

---

# Git Workflow for Permanent Changes

Permanent changes should use a normal Git workflow.

Example:

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/<change-name>
```

Make the Source-of-Truth change.

Then:

```bash
python3 tools/build_xrd_eight.py
python3 tools/validate_xrd_eight_addressing.py
python3 tools/render_xrd_eight.py
git diff --check
git status --short
```

Inspect:

```bash
git diff
```

Then commit and push through the normal Pull Request process.

Avoid editing `main` directly for substantial topology or infrastructure changes.

---

# Check Runtime Resources During Study

At any point:

```bash
./profiles/xrd-eight/labctl resources
```

For a more direct Docker view:

```bash
docker stats --no-stream \
  $(docker ps \
    --filter name=clab-ccie-sp-xrd-eight \
    --format '{{.Names}}')
```

Resource consumption should be interpreted in the context of the eight full-dataplane XRd nodes.

---

# Runtime Envelope

The eight-XRd topology was selected based on previous full-dataplane host measurements.

Observed reference values:

| Measurement | Observed Result |
| --- | ---: |
| XRd vRouter nodes | `8` |
| IOL-XE nodes | `3` |
| AUTO1 nodes | `1` |
| Total containers | `12` |
| VM allocation during measurement | `16 vCPU / 86 GiB RAM` |
| RAM used | approximately `70 GiB` |
| RAM remaining available | approximately `16 GiB` |
| Swap | `0 B` |
| XRd restarts | `0` |
| XRd OOM | `false` |

These are reference observations, not guaranteed fixed values.

Actual resource usage can change depending on:

- active protocols;
- number of routes;
- VPN scale;
- multicast state;
- traffic generation;
- telemetry;
- automation workloads.

---

# Heavy-Lab Concurrency Policy

Do not run another resource-intensive dataplane lab concurrently with XRd Eight unless the host has been deliberately revalidated for that workload.

Examples of heavy profiles include:

```text
XRd Eight
Master
Inter-AS
SRv6
Full Dataplane
JNCIE-SP
```

Preferred workflow:

```text
Run one heavy lab
        |
        v
Study / Validate
        |
        v
Collect Evidence
        |
        v
Backup Required State
        |
        v
Destroy with Cleanup
        |
        v
Start Next Lab
```

---

# Normal Shutdown

Destroy XRd Eight with the profile lifecycle wrapper:

```bash
cd /srv/netlab/labs/ccie-sp-master

./profiles/xrd-eight/labctl destroy
```

The wrapper uses Containerlab cleanup semantics.

Equivalent underlying operation:

```bash
sudo containerlab destroy \
  -t topology/ccie-sp-xrd-eight.clab.yml \
  --cleanup
```

---

# Why `--cleanup` Is Required

The cleanup option is not cosmetic.

It removes disposable runtime artifacts associated with the deployment.

Without cleanup, files under:

```text
topology/clab-ccie-sp-xrd-eight/
```

may survive.

A surviving runtime startup configuration can cause newly generated repository artifacts to be ignored during a later deployment.

For XRd Eight, clean destruction is therefore part of configuration correctness.

---

# Verify Destruction

Check that XRd Eight containers no longer exist:

```bash
docker ps -a --format '{{.Names}}' | \
  grep '^clab-ccie-sp-xrd-eight-' || \
  echo "PASS: containers removed"
```

Check that the runtime directory was removed:

```bash
test ! -e topology/clab-ccie-sp-xrd-eight && \
  echo "PASS: runtime cleaned"
```

Review memory:

```bash
free -h
```

Review host load:

```bash
uptime
```

---

# Emergency Shutdown

If the lifecycle wrapper cannot be used, destroy the topology directly:

```bash
sudo containerlab destroy \
  -t /srv/netlab/labs/ccie-sp-master/topology/ccie-sp-xrd-eight.clab.yml \
  --cleanup
```

Then verify:

```bash
docker ps -a --format '{{.Names}}' | \
  grep '^clab-ccie-sp-xrd-eight-' || \
  echo "PASS: removed"
```

---

# Recovery After Interrupted Deployment

If a deployment is interrupted or partially fails:

1. do not immediately rerun deployment;
2. inspect existing containers;
3. inspect Containerlab runtime state;
4. collect useful logs if troubleshooting is required;
5. destroy the partial topology with cleanup;
6. verify that containers and runtime files are gone;
7. verify host memory recovery;
8. regenerate the repository artifacts;
9. rerun static validation;
10. redeploy from a known clean state.

The recovery principle is:

```text
Unknown Runtime State
        |
        v
Collect Evidence
        |
        v
Destroy + Cleanup
        |
        v
Known Clean State
        |
        v
Regenerate
        |
        v
Validate
        |
        v
Redeploy
```

---

# Pre-Deployment Checklist

Before executing `deploy-full`, verify:

| Check | Required |
| --- | --- |
| Repository on expected branch | Yes |
| Local `HEAD` synchronized with `origin/main` | Yes |
| Working tree clean | Yes |
| Builder completes successfully | Yes |
| Address validator passes | Yes |
| SVG renderer completes successfully | Yes |
| `git diff --check` clean | Yes |
| XRd image present | Yes |
| IOL-XE image present | Yes |
| AUTO1 image present | Yes |
| `CCIE_AUTO_PASSWORD` set | Yes |
| No stale XRd Eight containers | Yes |
| No conflicting heavy lab | Yes |
| KVM available | Yes |
| Sufficient host memory | Yes |

---

# Post-Deployment Checklist

After the full topology has completed its startup window:

| Check | Expected |
| --- | --- |
| Total containers | `12` |
| XRd containers | `8` |
| IOL-XE containers | `3` |
| AUTO1 | `1` |
| XRd health | `healthy` |
| XRd restart count | `0` |
| XRd OOM | `false` |
| Management reachability | `12/12` |
| Physical topology | `19 links` |
| IPv4 P2P addressing | `19 /31 networks` |
| IPv6 P2P addressing | `19 /127 networks` |
| Provider IPv4 loopbacks | `8/8` |
| Provider IPv6 loopbacks | `8/8` |

Only after these checks should protocol-level validation proceed.

---

# Operational Rules

XRd Eight v2 should be operated according to the following rules:

1. Treat `main` as the deployable repository baseline.
2. Keep permanent infrastructure changes in the Source of Truth.
3. Never treat Containerlab runtime files as authoritative.
4. Do not manually edit generated artifacts as the permanent solution.
5. Regenerate before deployment.
6. Run static validation before starting expensive XRd nodes.
7. Keep AUTO1 credentials outside Git.
8. Use management connectivity independently from the provider data plane.
9. Validate the lab incrementally rather than all at once.
10. Back up valuable manual work before destruction.
11. Promote successful experiments through reviewed Source-of-Truth changes.
12. Always destroy the profile with `--cleanup`.
13. Never assume that a running container means the routing protocol is healthy.
14. Never assume that a successful configuration generation means the runtime state is correct.
15. Keep evidence from meaningful validation and failure tests.

---

# Recommended Operational Lifecycle

The complete normal lifecycle can be summarized as:

```text
+-----------------------------+
| 1. Synchronize Git          |
+-------------+---------------+
              |
              v
+-----------------------------+
| 2. Generate Artifacts       |
+-------------+---------------+
              |
              v
+-----------------------------+
| 3. Validate Addressing      |
+-------------+---------------+
              |
              v
+-----------------------------+
| 4. Check Git Determinism    |
+-------------+---------------+
              |
              v
+-----------------------------+
| 5. Validate Host / Images   |
+-------------+---------------+
              |
              v
+-----------------------------+
| 6. Load Runtime Secret      |
+-------------+---------------+
              |
              v
+-----------------------------+
| 7. Deploy                   |
+-------------+---------------+
              |
              v
+-----------------------------+
| 8. Validate Containers      |
+-------------+---------------+
              |
              v
+-----------------------------+
| 9. Validate Management      |
+-------------+---------------+
              |
              v
+-----------------------------+
| 10. Validate IGP / SR       |
+-------------+---------------+
              |
              v
+-----------------------------+
| 11. Add Services            |
+-------------+---------------+
              |
              v
+-----------------------------+
| 12. Failure / Automation    |
+-------------+---------------+
              |
              v
+-----------------------------+
| 13. Collect Evidence        |
+-------------+---------------+
              |
              v
+-----------------------------+
| 14. Backup Valuable State   |
+-------------+---------------+
              |
              v
+-----------------------------+
| 15. Destroy + Cleanup       |
+-----------------------------+
```

The objective is to keep every deployment **reproducible, inspectable and recoverable**.

XRd Eight v2 should never depend on undocumented runtime state.

The repository defines the baseline.

Containerlab creates the disposable runtime environment.

The routers provide the live engineering workspace.

AUTO1 provides repeatable automation and validation.

Git records the intentional evolution of the lab.
