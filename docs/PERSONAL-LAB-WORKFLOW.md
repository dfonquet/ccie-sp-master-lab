# Personal Three-Profile Lab Workflow

This guide explains how to safely operate, modify, automate, preserve, back up,
recover, and extend the **Master**, **Inter-AS**, and **SRv6** lab profiles.

It also defines the separation of responsibilities between:

- The Ubuntu NetLab host.
- Containerlab.
- The generated infrastructure baseline.
- XRd and IOL persistent configuration.
- The AUTO1 automation workstation.
- Personal study scenarios.
- Git and GitHub.

> [!IMPORTANT]
> Run only one heavy profile at a time. Always use `labctl` for normal lifecycle
> operations. Use `commit` on IOS XR, `write memory` on IOL-XE, and create a
> backup before every important exercise.

> [!WARNING]
> Do not use `containerlab destroy --cleanup`, manually delete a Containerlab
> lab directory, or remove containers with `docker rm` during normal study.
> Those actions can bypass the supported lifecycle and remove persistent state.

---

## Table of contents

1. [Core operating model](#1-core-operating-model)
2. [NetLab directory structure](#2-netlab-directory-structure)
3. [Current operational repository](#3-current-operational-repository)
4. [Why the Master currently uses the repair worktree](#4-why-the-master-currently-uses-the-repair-worktree)
5. [First login after starting the VM](#5-first-login-after-starting-the-vm)
6. [Credential management](#6-credential-management)
7. [Profile overview](#7-profile-overview)
8. [Starting a lab](#8-starting-a-lab)
9. [What happens during deployment](#9-what-happens-during-deployment)
10. [Inspecting a running lab](#10-inspecting-a-running-lab)
11. [Stopping a lab safely](#11-stopping-a-lab-safely)
12. [Configuration persistence](#12-configuration-persistence)
13. [Where XRd and IOL state is stored](#13-where-xrd-and-iol-state-is-stored)
14. [NetLab host and AUTO1 responsibilities](#14-netlab-host-and-auto1-responsibilities)
15. [Where each type of change belongs](#15-where-each-type-of-change-belongs)
16. [Developing an L2VPN exercise](#16-developing-an-l2vpn-exercise)
17. [Recommended automation workflow](#17-recommended-automation-workflow)
18. [Backups and evidence](#18-backups-and-evidence)
19. [Personal study scenarios](#19-personal-study-scenarios)
20. [Daily study workflow](#20-daily-study-workflow)
21. [Recovery and rollback](#21-recovery-and-rollback)
22. [Returning to a clean baseline](#22-returning-to-a-clean-baseline)
23. [Git and GitHub workflow](#23-git-and-github-workflow)
24. [Common mistakes](#24-common-mistakes)
25. [Quick decision tables](#25-quick-decision-tables)
26. [Command reference](#26-command-reference)

---

## 1. Core operating model

The project contains different types of state. Understanding these layers
prevents accidental loss of configuration.

| Layer | Purpose | Stored where | Survives the supported normal lifecycle? |
|---|---|---|---:|
| Source of Truth | Defines topology, roles, addressing and generated baselines | Git repository and Python generators | Yes |
| Generated baseline | Reproducible initial infrastructure | `configs/`, inventories and `topology/startup/` | Yes |
| Device persistent state | Manual and automated committed router configuration | XRd storage and IOL NVRAM | Yes |
| AUTO1 workspace | Templates, playbooks, scripts, backups and evidence | Host `automation/`, mounted as `/workspace` | Yes |
| Container runtime | Running processes, virtual links and volatile memory | Docker and Containerlab runtime | No |

```text
Source of Truth
       |
       | generate
       v
Topology + inventory + startup baseline
       |
       | deploy
       v
XRd and IOL nodes
       |
       +------------------------------+
       |                              |
       | manual CLI                   | AUTO1 automation
       v                              v
IOS XR commit                 Ansible/Python deployment
IOL write memory                      |
       |                              |
       +--------------+---------------+
                      |
                      v
              Persistent node state
                      |
                      v
             Backup and evidence
```

The generated baseline is not a continuous controller. It does not constantly
connect to the routers and overwrite every manual command.

It establishes the reproducible infrastructure foundation. Later study changes
remain router state until they are:

- Removed manually.
- Rolled back.
- Replaced by another automation workflow.
- Removed during an intentional clean reset.
- Lost because they were not committed or saved.

---

## 2. NetLab directory structure

The Ubuntu NetLab storage root is:

```text
/srv/netlab/
```

Its relevant structure is:

```text
/srv/netlab/
├── backups/                       Host-level operational backups
├── docker/                        Docker persistent storage
├── images/                        Authorized local vendor images
├── labs/                          Lab repositories and Git worktrees
├── venvs/                         Python virtual environments
└── ...
```

Important lab paths include:

```text
/srv/netlab/labs/
├── ccie-sp-startup-repair/        Current validated Master worktree
├── ccie-sp-study/                 Canonical repository copy
├── ccie-sp-inter-as-rollout/      Historical/controlled Inter-AS worktree
├── ccie-sp-srv6/                  SRv6 capability worktree
└── ccie-sp-srv6-full/             Full SRv6 study worktree
```

> [!NOTE]
> A Git worktree is another working directory associated with the same project.
> It can contain a different branch or revision. A worktree name does not
> necessarily describe the current quality or status of the code.

---

## 3. Current operational repository

The currently validated 30-node Master was deployed from:

```bash
/srv/netlab/labs/ccie-sp-startup-repair
```

Enter it with:

```bash
cd /srv/netlab/labs/ccie-sp-startup-repair
```

Confirm the path:

```bash
pwd
```

Expected:

```text
/srv/netlab/labs/ccie-sp-startup-repair
```

Before every important session, verify the repository:

```bash
git status --short --branch
git log -1 --oneline
./labctl status
```

Do not operate the same running profile from multiple worktrees.

The correct rule is:

> The worktree that starts a lab must also be used to inspect and stop that
> running lab.

---

## 4. Why the Master currently uses the repair worktree

The name `ccie-sp-startup-repair` does not mean that the Master remains broken.

This worktree was used to develop and validate:

- The cumulative Master startup baseline.
- XRd startup generation.
- Partial IOL startup generation.
- Credential-aware CLI readiness polling.
- Controlled Containerlab concurrency.
- Extended deployment timeouts.
- Staggered IOL startup.
- AUTO1 UID/GID alignment.
- The redundant BGP automation workflow.
- The three-profile personal operating workflow.

These changes were merged into GitHub `main` through pull request **#22**.

The active 30-node lab was created from this worktree. Therefore, the current
running deployment must continue to be operated from:

```bash
cd /srv/netlab/labs/ccie-sp-startup-repair
```

### Transition to the canonical repository

Perform this only after ending the current study session.

Stop the Master from its current worktree:

```bash
cd /srv/netlab/labs/ccie-sp-startup-repair
./labctl destroy master
```

Confirm that no Containerlab profile remains active:

```bash
docker ps --format '{{.Names}}' |
  grep '^clab-' ||
  echo "PASS: no active Containerlab nodes"
```

Inspect the canonical repository:

```bash
cd /srv/netlab/labs/ccie-sp-study
git status --short --branch
```

If it is clean, synchronize it with GitHub:

```bash
git fetch --prune origin
git switch main
git pull --ff-only origin main
```

Confirm the revision:

```bash
git status --short --branch
git log -1 --oneline
```

From the next cold deployment onward, the canonical procedure becomes:

```bash
cd /srv/netlab/labs/ccie-sp-study
./labctl deploy master
```

> [!CAUTION]
> Do not delete the repair worktree while its Master deployment is still
> running. Its topology path and persistent lab directory may still be required
> to stop the active deployment safely.

---

## 5. First login after starting the VM

After starting the VMware Ubuntu VM, connect through SSH:

```bash
ssh daniel@192.168.192.10
```

Replace the address if the VM management address changes.

### Step 1 — Confirm host identity

```bash
whoami
hostname
date -Is
```

### Step 2 — Check host resources

```bash
free -h
nproc
uptime
df -h /srv/netlab
```

### Step 3 — Check active labs

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
```

Specific Containerlab guard:

```bash
docker ps --format '{{.Names}}' |
  grep '^clab-' ||
  echo "PASS: no active Containerlab nodes"
```

### Step 4 — Enter the active repository

For the current repair-based deployment:

```bash
cd /srv/netlab/labs/ccie-sp-startup-repair
```

After completing the canonical transition:

```bash
cd /srv/netlab/labs/ccie-sp-study
```

### Step 5 — Confirm repository state

```bash
pwd
git status --short --branch
git log -1 --oneline
```

### Step 6 — Check lifecycle status

```bash
./labctl status
```

---

## 6. Credential management

Credentials must exist only in the ignored `.env` file.

Create it when necessary:

```bash
cp .env.example .env
chmod 600 .env
```

Edit it:

```bash
nano .env
```

Expected variables:

```dotenv
CCIE_XRD_USERNAME=clab
CCIE_XRD_PASSWORD=REPLACE_ME

CCIE_IOL_USERNAME=admin
CCIE_IOL_PASSWORD=REPLACE_ME

CCIE_AUTO_USERNAME=student
CCIE_AUTO_PASSWORD=REPLACE_ME
```

Confirm that Git ignores it:

```bash
git check-ignore -v .env
```

Expected result: Git must identify an ignore rule for `.env`.

> [!WARNING]
> Never place credentials in topology YAML, generated configurations, Jinja2
> templates, Python code, Git commits, screenshots, GitHub Issues, pull
> requests, study evidence, `group_vars`, or `host_vars` in plaintext.

### What `labctl` does with credentials

When this command is executed:

```bash
./labctl deploy master
```

`labctl`:

1. Reads the local ignored `.env`.
2. Loads the approved `CCIE_*` variables.
3. Preserves only the necessary lab credentials through the privileged command.
4. Uses them for startup substitutions and readiness validation.
5. Does not require storing plaintext credentials in tracked files.

---

## 7. Profile overview

| Profile | Primary purpose | Lifecycle name | Main baseline |
|---|---|---|---|
| Master | Main 30-node CCIE SP environment | `master` | IPv4/IPv6, IS-IS, provider standard and SR-MPLS |
| Inter-AS | Multi-AS and Inter-AS services | `inter-as` | Base, per-AS IGP and staged BGP |
| SRv6 | IPv6 and SRv6 study environment | `srv6` | IPv6 addressing, IS-IS and SRv6 locators |

### Master generated phases

| Phase | Purpose |
|---|---|
| `00-base` | Hostnames, management, interfaces, loopbacks and addressing |
| `10-isis` | Dual-stack IS-IS Level 2 |
| `15-provider-standard` | Common P, PE and RR operational standards |
| `20-sr-mpls` | SRGB, IPv4/IPv6 Prefix-SIDs and SR-MPLS foundation |

Master startup artifacts are generated beneath:

```text
topology/startup/
```

Example:

```text
topology/startup/
├── P1.cfg
├── P2.cfg
├── ...
├── PE1.cfg
├── ...
├── RR1.cfg
├── RR2.cfg
├── CE1.partial.cfg
├── ...
├── C1.partial.cfg
└── C2.partial.cfg
```

IOL uses `.partial.cfg` startup files so that Containerlab/vrnetlab can preserve
its management VRF, SSH and management bootstrap behavior.

### Intentionally incremental technologies

The following are not permanently pre-solved in the infrastructure baseline:

- MP-BGP services.
- L2VPN.
- L3VPN.
- EVPN and EVPN multihoming.
- Multicast and mVPN.
- SR-TE and PCE.
- Advanced SRv6 services.
- AAA.
- RPKI.
- QoS.
- Failure and convergence exercises.
- Assurance and automation scenarios.

---

## 8. Starting a lab

### 8.1 Required prechecks

Enter the active repository:

```bash
cd /srv/netlab/labs/ccie-sp-startup-repair
```

Check repository state:

```bash
git status --short --branch
git log -1 --oneline
```

Check that `.env` exists:

```bash
test -f .env &&
  echo "PASS: .env exists" ||
  echo "FAIL: .env is missing"
```

Check that no other lab is active:

```bash
docker ps --format '{{.Names}}' |
  grep '^clab-' ||
  echo "PASS: no active Containerlab nodes"
```

Check resources:

```bash
free -h
uptime
df -h /srv/netlab
```

### 8.2 Start Master

```bash
./labctl deploy master
```

Do not start its routers individually.

Do not interrupt the command merely because XRd and IOL need several minutes
to initialize.

### 8.3 Start Inter-AS

Only when no other profile is active:

```bash
./labctl deploy inter-as
```

### 8.4 Start SRv6

Only when no other profile is active:

```bash
./labctl deploy srv6
```

### 8.5 Check deployment status

```bash
./labctl status
```

Container view:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
```

---

## 9. What happens during deployment

When this command runs:

```bash
./labctl deploy master
```

the project performs the following sequence:

1. Selects the Master profile.
2. Loads credentials from the ignored `.env`.
3. Selects the generated Master topology.
4. Creates the Containerlab management network.
5. Creates the profile lab directory.
6. Starts XRd nodes using controlled concurrency.
7. Staggers IOL startup to avoid a simultaneous first-boot race.
8. Creates the virtual provider and customer links.
9. Assigns management addresses.
10. Presents generated startup configurations.
11. Loads the cumulative provider baseline on XRd.
12. Loads partial platform-safe startup configuration on IOL.
13. Completes Containerlab platform-specific post-deployment actions.
14. Checks management TCP/22.
15. Checks real CLI authentication and prompts.
16. Reports lifecycle completion.

### Why startup is intentionally controlled

The Master runs many nested virtual network operating systems.

Starting every node simultaneously can produce:

- Extreme host CPU load.
- Delayed Docker API responses.
- XRd freeze-monitor warnings.
- IOL initial configuration dialogs.
- Post-deployment timeouts.
- Temporary SSH failures.
- Incorrect assumptions that a running container means a ready router.

The project therefore uses:

- Limited Containerlab workers.
- Extended deployment timeout.
- Individual IOL startup delays.
- Real SSH/CLI readiness polling.

> [!NOTE]
> `docker ps` reporting `Up` means the container process is running. It does not
> always mean that IOS XR or IOS-XE is fully ready for configuration.

---

## 10. Inspecting a running lab

General status:

```bash
./labctl status
```

Inspect Master:

```bash
./labctl inspect master
```

Inspect Inter-AS:

```bash
./labctl inspect inter-as
```

Inspect SRv6:

```bash
./labctl inspect srv6
```

View containers:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
```

Check resources:

```bash
free -h
uptime
docker stats --no-stream
```

Connect to an XRd node:

```bash
ssh clab@10.201.255.101
```

Connect to an IOL-XE node:

```bash
ssh admin@10.201.255.131
```

Connect to AUTO1:

```bash
ssh student@10.201.255.150
```

---

## 11. Stopping a lab safely

Stop a profile from the same repository used to start it.

### Master

```bash
cd /srv/netlab/labs/ccie-sp-startup-repair
./labctl destroy master
```

### Inter-AS

```bash
./labctl destroy inter-as
```

### SRv6

```bash
./labctl destroy srv6
```

Confirm that the profile stopped:

```bash
docker ps --format '{{.Names}}' |
  grep '^clab-' ||
  echo "PASS: no active Containerlab nodes"
```

Check released resources:

```bash
free -h
uptime
```

### Lifecycle comparison

| Operation | Intended purpose | Persistent state |
|---|---|---|
| `./labctl destroy <profile>` | Normal daily shutdown | Preserved by the supported project lifecycle |
| `containerlab destroy --cleanup` | Intentional clean reset | May be deleted |
| Manual lab-directory deletion | Destructive manual reset | Deleted |
| `docker rm -f` | Emergency troubleshooting | Can leave lifecycle inconsistent |

---

## 12. Configuration persistence

There are two unrelated meanings of the word `commit`.

| Commit type | Location | Purpose |
|---|---|---|
| IOS XR configuration commit | XRd router | Saves a candidate configuration into the IOS XR configuration database |
| Git commit | Repository | Saves source code, documentation, templates and generated artifacts |

An IOS XR `commit` does not create a Git commit.

A Git commit does not automatically configure a router.

### 12.1 IOS XR / XRd

Enter configuration mode:

```text
configure
```

Make the required change:

```text
router bgp 500
 address-family vpnv4 unicast
 !
!
```

Commit it with a meaningful comment:

```text
commit comment STUDY-L2VPN-001
```

Exit:

```text
end
```

Verify:

```text
show configuration commit list
show running-config
show configuration failed
```

> [!IMPORTANT]
> An uncommitted IOS XR candidate configuration is not safely persistent.

### 12.2 IOS-XE / IOL

Enter configuration mode:

```text
configure terminal
```

Make the change and exit:

```text
end
```

Save the running configuration:

```text
write memory
```

Alternative:

```text
copy running-config startup-config
```

Verify:

```text
show running-config
show startup-config
```

> [!IMPORTANT]
> An IOL configuration that was not saved to NVRAM can disappear when the node
> is recreated.

---

## 13. Where XRd and IOL state is stored

### 13.1 XRd live configuration

IOS XR configuration commits are stored in XRd persistent storage associated
with the node.

For the Master profile, runtime node data is associated with:

```text
topology/clab-ccie-sp-master/
```

Do not edit XR storage files directly.

Inspect the actual mounted directories for P1:

```bash
docker inspect clab-ccie-sp-master-P1 \
  --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}'
```

Use IOS XR CLI for:

- Configuration commits.
- Commit history.
- Rollback.
- Configuration verification.

### 13.2 IOL saved configuration

IOL startup configuration is stored through its NVRAM/persistent vrnetlab
state.

Inspect CE1 mounts:

```bash
docker inspect clab-ccie-sp-master-CE1 \
  --format '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}'
```

Do not manually modify its NVRAM files.

Use:

```text
write memory
```

### 13.3 Generated Git baseline

Generated startup files are stored beneath:

```text
topology/startup/
```

These files provide reproducible bootstrap configuration. They are not
automatically updated every time a manual command is entered on a router.

### State comparison

| State | Example | Storage |
|---|---|---|
| Generated XRd baseline | `P1.cfg` | Git `topology/startup/` |
| Generated IOL baseline | `CE1.partial.cfg` | Git `topology/startup/` |
| XRd live configuration | IS-IS/BGP/L2VPN committed through CLI | XRd persistent storage |
| IOL live configuration | CE routing saved with `write memory` | IOL NVRAM |
| Router backup | Captured running configuration | Ignored backup directory |
| Automation source | Playbook or Jinja2 template | Git `automation/` |

---

## 14. NetLab host and AUTO1 responsibilities

### 14.1 NetLab Ubuntu host

The Ubuntu host owns:

- Docker.
- Containerlab.
- Network images.
- Topology lifecycle.
- Repository worktrees.
- Python topology generators.
- Addressing Source of Truth.
- Generated startup configurations.
- Persistent node directories.
- Host-side backup utilities.
- Git and GitHub workflows.

### 14.2 AUTO1

AUTO1 is the automation and assurance workstation.

AUTO1 is used for:

- Ansible inventory.
- Jinja2 templates.
- Configuration rendering.
- Prechecks and postchecks.
- Controlled deployments.
- Netmiko.
- pyATS and Genie.
- Nornir.
- Scrapli.
- NETCONF.
- gNMI.
- Backups.
- Rollback workflows.
- Sanitized validation evidence.

### 14.3 Responsibility table

| Task | NetLab host | AUTO1 |
|---|:---:|:---:|
| Start or stop Containerlab | Yes | No |
| Add or remove nodes | Yes | No |
| Add or remove links | Yes | No |
| Change official addressing | Yes | No |
| Generate startup baseline | Yes | No |
| Store vendor images | Yes | No |
| Create service templates | Source stored here | Visible through `/workspace` |
| Run service playbooks | Possible | Preferred |
| Configure L2VPN/L3VPN/EVPN | Through scripts if required | Preferred automation execution point |
| Store router NVRAM | Through persistent node directories | No |
| Save every manual CLI command automatically | No | No |
| Capture router backups | Yes | Yes |
| Store permanent automation source | Host `automation/` | Mounted as `/workspace` |

> [!IMPORTANT]
> AUTO1 is not router NVRAM. It does not automatically capture manual CLI
> commands. A backup workflow must be executed explicitly.

### 14.4 AUTO1 persistent workspace

The host directory:

```text
automation/
```

is mounted inside AUTO1 as:

```text
/workspace/
```

Path mapping:

| AUTO1 path | Ubuntu host path |
|---|---|
| `/workspace/inventory/` | `automation/inventory/` |
| `/workspace/templates/` | `automation/templates/` |
| `/workspace/playbooks/` | `automation/playbooks/` |
| `/workspace/scripts/` | `automation/scripts/` |
| `/workspace/rendered/` | `automation/rendered/` |
| `/workspace/artifacts/` | `automation/artifacts/` |

Files created under `/workspace` survive AUTO1 container destruction because
the host directory is the persistent source.

---

## 15. Where each type of change belongs

| Change | Correct location |
|---|---|
| Add or remove a node | Profile Python generator |
| Add or remove a link | Profile Python generator |
| Change official addressing | Profile Python generator |
| Change the infrastructure baseline | Generator and phase source |
| Create a personal exercise | `studies/<profile>/<scenario-id>/` |
| Create a Jinja2 service template | `automation/templates/` |
| Create an Ansible playbook | `automation/playbooks/` |
| Create an automation Python script | `automation/scripts/` |
| Create a repository-wide generator/validator | `tools/` |
| Store rendered candidates | `automation/rendered/` |
| Store automation backups | `automation/artifacts/backups/` |
| Store sanitized exercise results | Scenario `evidence/` |
| Store secrets | Ignored `.env` or approved vault |
| Save XRd live configuration | IOS XR `commit` |
| Save IOL live configuration | `write memory` |
| Preserve reusable source | Git commit and pull request |

### Generated files must not be edited directly

| Profile | Source of Truth |
|---|---|
| Master | `tools/build_lab.py` |
| Inter-AS | `tools/build_inter_as.py` |
| SRv6 | `tools/build_srv6_capability.py` |

After changing a generator:

```bash
python tools/build_lab.py
git status --short
git diff --check
git diff
```

Only commit generated changes when they are intentional.

---

## 16. Developing an L2VPN exercise

Assume that the objective is to build an L2VPN service between PE1 and PE6.

### 16.1 Where L2VPN should not be placed

Do not permanently insert the full exercise into:

```text
configs/00-base/
configs/10-isis/
configs/15-provider-standard/
configs/20-sr-mpls/
```

Those directories define the infrastructure foundation.

Adding study services to the baseline would:

- Pre-solve the exercise.
- Mix infrastructure and services.
- Increase startup complexity.
- Make troubleshooting harder.
- Make clean recovery less predictable.
- Hide configuration dependencies.

### 16.2 Correct project structure

```text
studies/master/L2VPN-001/
├── README.md
├── initial/
├── faults/
├── checks/
├── cleanup/
├── solution/
└── evidence/

automation/
├── inventory/
├── templates/
│   └── l2vpn/
│       └── xconnect_iosxr.j2
├── playbooks/
│   └── l2vpn/
│       ├── precheck.yml
│       ├── render.yml
│       ├── deploy.yml
│       ├── postcheck.yml
│       └── cleanup.yml
├── rendered/
└── artifacts/
```

### 16.3 Step 1 — Create the scenario

From the NetLab repository:

```bash
mkdir -p studies/master/L2VPN-001/initial
mkdir -p studies/master/L2VPN-001/faults
mkdir -p studies/master/L2VPN-001/checks
mkdir -p studies/master/L2VPN-001/cleanup
mkdir -p studies/master/L2VPN-001/solution
mkdir -p studies/master/L2VPN-001/evidence
```

The scenario `README.md` should define:

- Objective.
- Nodes involved.
- Required starting baseline.
- Customer attachment circuits.
- VLANs.
- Pseudowire identifiers.
- Expected control-plane state.
- Expected data-plane result.
- Failure conditions.
- Cleanup procedure.
- Success criteria.

### 16.4 Step 2 — Capture a checkpoint

From the host:

```bash
python tools/backup_provider.py \
  --label before-l2vpn-001 \
  --workers 2
```

Or from AUTO1:

```bash
ssh student@10.201.255.150
cd /workspace
ansible-playbook playbooks/backup.yml
```

### 16.5 Step 3 — Create non-secret variables

Example:

```yaml
l2vpn_services:
  - name: CUSTOMER-A-EPL
    vpn_id: 100
    pe_a: PE1
    pe_b: PE6
    interface_a: GigabitEthernet0/0/0/4
    interface_b: GigabitEthernet0/0/0/4
    pseudowire_id: 100
```

Reusable variables belong beneath:

```text
automation/inventory/group_vars/
automation/inventory/host_vars/
```

Do not place passwords in those files.

### 16.6 Step 4 — Create the Jinja2 template

Create:

```text
automation/templates/l2vpn/xconnect_iosxr.j2
```

The template should produce candidate configuration. It should not contain
credentials or unrelated infrastructure configuration.

### 16.7 Step 5 — Render without deployment

Connect to AUTO1:

```bash
ssh student@10.201.255.150
cd /workspace
```

Render:

```bash
ansible-playbook playbooks/l2vpn/render.yml
```

Review the generated candidates:

```bash
find rendered/ -maxdepth 3 -type f -print
```

### 16.8 Step 6 — Run prechecks

```bash
ansible-playbook playbooks/l2vpn/precheck.yml \
  --limit PE1,PE6
```

Prechecks should confirm:

- SSH/CLI reachability.
- Required interfaces exist.
- Interfaces are not unexpectedly in use.
- IS-IS underlay is operational.
- PE loopbacks are reachable.
- MPLS forwarding is available.
- No conflicting L2VPN service exists.
- A configuration backup exists.

### 16.9 Step 7 — Check mode

```bash
ansible-playbook playbooks/l2vpn/deploy.yml \
  --limit PE1,PE6 \
  --check
```

Review the expected configuration difference before applying it.

### 16.10 Step 8 — Canary deployment

```bash
ansible-playbook playbooks/l2vpn/deploy.yml \
  --limit PE1,PE6
```

The playbook should apply the change to a limited node set first.

### 16.11 Step 9 — Postchecks

```bash
ansible-playbook playbooks/l2vpn/postcheck.yml \
  --limit PE1,PE6
```

Postchecks should inspect:

- L2VPN state.
- Pseudowire state.
- Attachment circuits.
- Label exchange.
- MAC learning where applicable.
- CE-to-CE connectivity.
- Failure and recovery behavior.

### 16.12 Step 10 — Evidence

Store sanitized results in:

```text
studies/master/L2VPN-001/evidence/
```

Do not store:

- Passwords.
- Tokens.
- Private keys.
- Vendor images.
- Unsanitized full router configurations.

### 16.13 Step 11 — Cleanup or preservation

To remove the exercise:

```bash
ansible-playbook playbooks/l2vpn/cleanup.yml \
  --limit PE1,PE6
```

To preserve the exercise:

- Commit the XRd configuration.
- Save IOL configuration with `write memory`.
- Create a backup.
- Record the scenario state.
- Preserve reusable source through Git.

### L2VPN responsibility summary

| Component | Correct location |
|---|---|
| Physical/logical topology | NetLab generator |
| Base IS-IS/SR-MPLS | Generated Master baseline |
| Exercise description | `studies/master/L2VPN-001/` |
| Variables | `automation/inventory/` |
| Jinja2 template | `automation/templates/l2vpn/` |
| Deployment playbook | `automation/playbooks/l2vpn/` |
| Playbook execution | AUTO1 |
| Live configuration | PE routers |
| Backup | AUTO1 or host backup tool |
| Sanitized evidence | Scenario `evidence/` |
| Reusable source | Git and GitHub |

---

## 17. Recommended automation workflow

```text
Source of Truth
       |
       v
Inventory and variables
       |
       v
Jinja2 template
       |
       v
Rendered candidate configuration
       |
       v
Static validation
       |
       v
Device prechecks
       |
       v
Check/diff mode
       |
       v
Configuration backup
       |
       v
Canary deployment
       |
       v
Canary postchecks
       |
       v
Controlled expansion
       |
       v
Full postchecks
       |
       v
Sanitized evidence
       |
       v
Cleanup or intentional preservation
```

Connect to AUTO1:

```bash
ssh student@10.201.255.150
cd /workspace
```

Confirm inventory:

```bash
ansible-inventory --graph
```

Inspect the workspace:

```bash
pwd
find . -maxdepth 2 -type d | sort
```

Run a precheck:

```bash
ansible-playbook playbooks/precheck.yml --limit P1
```

---

## 18. Backups and evidence

### Host-side provider backup

```bash
python tools/backup_provider.py \
  --label before-my-exercise \
  --workers 2
```

Typical location:

```text
artifacts/backups/<timestamp>-before-my-exercise/
```

### AUTO1 backup

```bash
ssh student@10.201.255.150
cd /workspace
ansible-playbook playbooks/backup.yml
```

AUTO1 location:

```text
/workspace/artifacts/backups/
```

Host location:

```text
automation/artifacts/backups/
```

Backups should normally be ignored by Git because they can contain:

- Password hashes.
- SNMP communities.
- AAA keys.
- BGP authentication.
- Management addresses.
- Other sensitive configuration.

Check ignore behavior:

```bash
git check-ignore -v automation/artifacts/backups/*
```

---

## 19. Personal study scenarios

Create personal exercises beneath:

```text
studies/<profile>/<scenario-id>/
```

Standard structure:

```text
studies/<profile>/<scenario-id>/
├── README.md
├── initial/
├── faults/
├── checks/
├── cleanup/
├── solution/
└── evidence/
```

| Directory | Purpose |
|---|---|
| `initial/` | Starting assumptions and additive setup |
| `faults/` | Controlled fault-injection commands |
| `checks/` | Read-only verification commands and scripts |
| `cleanup/` | Exact rollback/removal procedure |
| `solution/` | Reference solution separated from the task |
| `evidence/` | Sanitized output demonstrating results |

Examples:

```text
studies/master/L2VPN-001/
studies/master/L3VPN-001/
studies/master/EVPN-MH-001/
studies/inter-as/INTER-AS-B-001/
studies/srv6/SRV6-TE-001/
```

---

## 20. Daily study workflow

### Start

```bash
cd /srv/netlab/labs/ccie-sp-startup-repair

pwd
git status --short --branch
git log -1 --oneline

./labctl status

docker ps --format '{{.Names}}' |
  grep '^clab-' ||
  echo "PASS: no active Containerlab nodes"

free -h
uptime
df -h /srv/netlab

./labctl deploy master
```

Replace `master` with the selected profile when necessary.

Never start a second heavy profile.

### Establish a checkpoint

```bash
python tools/backup_provider.py \
  --label before-session-topic \
  --workers 2
```

### Study

1. Read the scenario objective.
2. Confirm the required starting baseline.
3. Capture prechecks.
4. Make one logical change at a time.
5. Commit IOS XR changes.
6. Save IOL-XE changes with `write memory`.
7. Validate control-plane state.
8. Validate data-plane behavior.
9. Introduce a controlled fault.
10. Troubleshoot the fault.
11. Restore the service.
12. Save sanitized evidence.
13. Run cleanup or preserve the configuration intentionally.

### Stop

```bash
cd /srv/netlab/labs/ccie-sp-startup-repair
./labctl destroy master
```

Confirm:

```bash
docker ps --format '{{.Names}}' |
  grep '^clab-' ||
  echo "PASS: no active Containerlab nodes"

free -h
uptime
```

---

## 21. Recovery and rollback

| Objective | Correct action |
|---|---|
| Keep manual work for tomorrow | XRd `commit`, IOL `write memory`, then normal destroy |
| Undo one XRd change | Use IOS XR commit history and controlled rollback |
| Remove a study service | Use the scenario cleanup workflow |
| Restore known router configuration | Use AUTO1 or host backup |
| Recover automation source | Use Git |
| Restore generated baseline | Regenerate and perform intentional clean reset |
| Modify official baseline | Change the generator, validate and create a PR |

### IOS XR commit inspection

```text
show configuration commit list
show configuration commit changes <commit-id>
```

Preview rollback:

```text
show configuration rollback changes last 1
```

Perform a controlled rollback only after reviewing the affected change:

```text
rollback configuration last 1
```

Verify:

```text
show configuration failed
show running-config
```

### Before major recovery

```bash
git rev-parse HEAD
git status --short --branch

python tools/backup_provider.py \
  --label before-recovery \
  --workers 2
```

---

## 22. Returning to a clean baseline

A clean reset is different from a normal daily shutdown.

Use a clean reset only when intentionally discarding accumulated device state.

Before resetting:

1. Stop making changes.
2. Commit XRd configuration that must survive.
3. Save IOL configuration that must survive.
4. Capture host or AUTO1 backups.
5. Record the Git revision.
6. Confirm the selected profile.
7. Confirm that no other profile is active.
8. Review the exact lab directory.
9. Use the documented reset workflow.
10. Regenerate the baseline.
11. Deploy one profile only.

> [!DANGER]
> Never issue a recursive deletion against `/srv/netlab`,
> `/srv/netlab/labs`, the home directory, or a path built from an unresolved
> variable.

Generate Master:

```bash
python tools/build_lab.py
```

Generate Inter-AS:

```bash
python tools/build_inter_as.py
```

Generate SRv6:

```bash
python tools/build_srv6_capability.py
```

Review generated changes:

```bash
git status --short
git diff --check
git diff
```

---

## 23. Git and GitHub workflow

Create a focused branch:

```bash
git switch -c study/<short-topic>
```

Example:

```bash
git switch -c study/l2vpn-xconnect
```

Review modifications:

```bash
git status --short
git diff --check
git diff
```

Run repository tests:

```bash
python -m pytest -q -p no:cacheprovider tests
```

Add explicit files:

```bash
git add studies/master/L2VPN-001/README.md
git add automation/templates/l2vpn/xconnect_iosxr.j2
git add automation/playbooks/l2vpn/
```

Commit:

```bash
git commit -m "study: add L2VPN xconnect scenario"
```

Push:

```bash
git push -u origin study/l2vpn-xconnect
```

Then create a pull request.

> [!CAUTION]
> Avoid `git add .` until you have confirmed that credentials, backups,
> generated runtime files and evidence are correctly ignored.

### Appropriate Git content

- Source of Truth changes.
- Templates.
- Playbooks.
- Python scripts.
- Tests.
- Documentation.
- Intentional generated artifacts.
- Sanitized educational evidence.

### Content that must not enter Git

- `.env`.
- Vendor images.
- Router persistent storage.
- IOL NVRAM.
- Plaintext credentials.
- Private keys.
- Unsanitized router backups.
- Docker runtime files.
- Temporary rendered configurations unless intentionally required.

---

## 24. Common mistakes

### Starting multiple profiles

Consequences:

- CPU and RAM exhaustion.
- Port conflicts.
- Management-network confusion.
- Unreliable validation.

Prevention:

```bash
./labctl status
docker ps --format '{{.Names}}' | grep '^clab-'
```

### Operating from the wrong worktree

Consequences:

- Wrong topology revision.
- Wrong generated startup files.
- Wrong `.env`.
- Wrong persistent lab directory.

Prevention:

```bash
pwd
git log -1 --oneline
```

### Assuming AUTO1 records manual CLI automatically

AUTO1 does not automatically capture manual commands.

Run an explicit backup workflow.

### Editing generated files directly

The next generator execution can overwrite the edit.

Modify the profile generator instead.

### Forgetting IOS XR `commit`

The configuration remains candidate state and may be lost.

### Forgetting IOL `write memory`

The running configuration may not survive recreation.

### Placing study services in the infrastructure baseline

This pre-solves the exercise and makes clean recovery more difficult.

Use:

```text
studies/
automation/templates/
automation/playbooks/
```

### Using cleanup as normal shutdown

Cleanup is a reset operation. It is not the normal daily stop procedure.

---

## 25. Quick decision tables

### Where should the work happen?

| Question | Answer |
|---|---|
| Where do I start and stop the lab? | Ubuntu NetLab host |
| Where do I modify topology? | Profile Python generator |
| Where do I modify official addressing? | Profile Python generator |
| Where do I create a personal exercise? | `studies/<profile>/<scenario-id>/` |
| Where do Jinja2 templates go? | `automation/templates/` |
| Where do playbooks go? | `automation/playbooks/` |
| Where do automation Python scripts go? | `automation/scripts/` |
| Where do repository generators and validators go? | `tools/` |
| Where do rendered configurations go? | `automation/rendered/` |
| Where do AUTO1 backups go? | `automation/artifacts/backups/` |
| Where do secrets go? | Ignored `.env` or approved vault |
| Where is XRd live configuration saved? | IOS XR commit database and persistent XR storage |
| Where is IOL live configuration saved? | IOL NVRAM after `write memory` |
| Does AUTO1 automatically save CLI work? | No |
| Should L2VPN be part of `00-base`? | No |
| Should L2VPN automation run from AUTO1? | Preferably yes |
| Should topology generation run from AUTO1? | No |
| Does normal destroy mean factory reset? | No |
| Can cleanup remove configuration state? | Yes |

### What must be saved?

| Content | Save mechanism |
|---|---|
| XRd configuration | IOS XR `commit` |
| IOL-XE configuration | `write memory` |
| Automation source | Git commit |
| Study documentation | Git commit |
| Router backups | AUTO1 or host backup workflow |
| Sanitized evidence | Scenario `evidence/` and Git when appropriate |
| Credentials | Ignored `.env` or vault, never Git |

---

## 26. Command reference

### Enter the current operational repository

```bash
cd /srv/netlab/labs/ccie-sp-startup-repair
```

### Check status

```bash
./labctl status
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
```

### Start Master

```bash
./labctl deploy master
```

### Inspect Master

```bash
./labctl inspect master
```

### Stop Master

```bash
./labctl destroy master
```

### Start Inter-AS

```bash
./labctl deploy inter-as
```

### Inspect Inter-AS

```bash
./labctl inspect inter-as
```

### Stop Inter-AS

```bash
./labctl destroy inter-as
```

### Start SRv6

```bash
./labctl deploy srv6
```

### Inspect SRv6

```bash
./labctl inspect srv6
```

### Stop SRv6

```bash
./labctl destroy srv6
```

### Enter AUTO1

```bash
ssh student@10.201.255.150
cd /workspace
```

### Inspect Ansible inventory

```bash
ansible-inventory --graph
```

### Run a precheck

```bash
ansible-playbook playbooks/precheck.yml --limit P1
```

### Create a provider backup

```bash
python tools/backup_provider.py \
  --label before-study \
  --workers 2
```

### Save XRd configuration

```text
commit comment STUDY-CHECKPOINT
```

### Save IOL-XE configuration

```text
write memory
```

### Check repository changes

```bash
git status --short
git diff --check
git diff
```

---

## Final operating principle

> [!TIP]
> **NetLab builds and operates the infrastructure. AUTO1 renders, validates,
> deploys and verifies controlled service changes. Routers hold the live
> committed configuration. Git preserves reproducible engineering source.
> Backups preserve recoverable operational state.**




