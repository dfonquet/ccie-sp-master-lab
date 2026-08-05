# Personal Three-Profile Lab Workflow

This guide explains how to operate, modify, preserve, back up, and recover the
Master, Inter-AS, and SRv6 labs without confusing generated baselines, router
persistence, personal exercises, and AUTO1 automation.

> [!IMPORTANT]
> Run only one heavy profile at a time. Use `labctl` for lifecycle operations,
> `commit` on IOS XR, `write memory` on IOL-XE, and AUTO1 or the host backup
> tools before important exercises.

## 1. Mental model

The project has four different state layers:

| Layer | Purpose | Survives normal `destroy`? | Stored where? |
|---|---|---:|---|
| Generated baseline | Reproducible initial infrastructure | Yes, in Git | Generators, inventories, `configs/`, `topology/startup/` |
| Device persistent state | Manual and automated committed changes | Yes | XRd `xr-storage`; IOL NVRAM |
| AUTO1 workspace | Templates, playbooks, scripts, backups, evidence | Yes | Host `automation/`, mounted as `/workspace` |
| Container runtime | Processes, links, transient memory | No | Docker containers and networks |

```text
Source of Truth ──generate──> Baseline artifacts ──deploy──> Routers
                                                           │
Manual CLI or AUTO1 ─────────────commit/write memory───────┤
                                                           │
AUTO1/host backup <────────────────read running config─────┘
```

The generated baseline is not a continuous controller. It initializes a clean
lab. Existing persistent router state takes precedence during a normal
destroy/deploy cycle, which preserves study changes instead of overwriting
them every time the lab starts.

## 2. Repository used for operations

The validated repair worktree is:

```bash
cd /srv/netlab/labs/ccie-sp-startup-repair
```

Confirm the revision and local state before every important session:

```bash
git status --short --branch
git log -1 --oneline
./labctl status
```

Do not operate simultaneously from multiple worktrees. Choose one worktree as
the active operational copy for the complete session.

## 3. Credentials

Create credentials only in the ignored `.env` file:

```bash
cp .env.example .env
chmod 600 .env
```

Required variables:

```text
CCIE_XRD_USERNAME
CCIE_XRD_PASSWORD
CCIE_IOL_USERNAME
CCIE_IOL_PASSWORD
CCIE_AUTO_USERNAME
CCIE_AUTO_PASSWORD
```

Never place passwords in topology YAML, generated configurations, playbooks,
inventory, templates, shell history, Git commits, or screenshots.

## 4. Safe lifecycle for all profiles

Check active labs:

```bash
./labctl status
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
```

### Master

```bash
./labctl deploy master
./labctl inspect master
./labctl destroy master
```

### Inter-AS

```bash
./labctl deploy inter-as
./labctl inspect inter-as
./labctl destroy inter-as
```

### SRv6

```bash
./labctl deploy srv6
./labctl inspect srv6
./labctl destroy srv6
```

Normal `destroy` removes containers and links but preserves the node lab
directories used for XRd configuration databases and IOL NVRAM.

Do not use either of these during normal study:

```bash
sudo containerlab destroy --cleanup ...
rm -rf topology/clab-ccie-sp-...
```

They remove the persistent node state. Use cleanup only when intentionally
returning to a completely fresh generated baseline and only after a backup.

## 5. Profile-specific baseline behavior

| Profile | Fresh-deploy behavior | Generated phases |
|---|---|---|
| Master | Cumulative baseline is loaded automatically and `labctl` polls all 30 CLIs | `00-base`, `10-isis`, `15-provider-standard`, `20-sr-mpls` |
| Inter-AS | Use the staged phase workflow after management readiness | `00-base`, `10-igp`, `20-bgp` |
| SRv6 | Use canary and staged rollout after management readiness | `00-base`, `10-isis-ipv6`, `20-srv6-locator`, `21-srv6-isis` |

The Master startup artifacts are generated under:

```text
topology/startup/<XRd-node>.cfg
topology/startup/<IOL-node>.partial.cfg
```

IOL uses a partial startup file so Containerlab retains its management VRF,
SSH service, and default management behavior.

### Inter-AS phase application

Start with a canary pair and then expand only after validation:

```bash
python tools/apply_phase.py 00-base \
  --profile inter-as --nodes P1,P3 --workers 1

python tools/apply_phase.py 10-igp \
  --profile inter-as --nodes P1,P3 --workers 1
```

Apply `20-bgp` only when the exercise requires the generated BGP baseline.

### SRv6 phase application

Start with the documented canary:

```bash
python tools/apply_phase.py 00-base \
  --profile srv6 --nodes P1,P2,PE1 --workers 1

python tools/apply_phase.py 10-isis-ipv6 \
  --profile srv6 --nodes P1,P2,PE1 --workers 1
```

Locator and SRv6 IS-IS phases must follow the acceptance gates in
`profiles/srv6/ACCEPTANCE.md`.

## 6. Preserving manual router configuration

### IOS XR / XRd

```text
configure
 ! configuration
commit comment MY-STUDY-CHANGE
end
```

Verify:

```text
show configuration commit list
show running-config
show configuration failed
```

An uncommitted candidate configuration is not persistent.

### IOS-XE / IOL

```text
configure terminal
 ! configuration
end
write memory
```

Verify:

```text
show running-config
show startup-config
```

An IOL change that was not saved to NVRAM may disappear when the node is
recreated.

## 7. Where to create each kind of change

### 7.1 Permanent topology or baseline change

Do not edit generated YAML, CSV, or CFG files directly. Edit the generator:

| Profile | Source of Truth |
|---|---|
| Master | `tools/build_lab.py` |
| Inter-AS | `tools/build_inter_as.py` |
| SRv6 | `tools/build_srv6_capability.py` |

Then regenerate and review:

```bash
python tools/build_lab.py
python tools/build_inter_as.py
python tools/build_srv6_capability.py
git status --short
git diff --check
git diff
```

Only commit when the generated output is intentional and validators pass.

### 7.2 Personal study scenario

Create scenarios outside generated directories:

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

Recommended contents:

| Directory | Content |
|---|---|
| `initial/` | Required starting assumptions and optional additive configuration |
| `faults/` | Controlled fault injection commands |
| `checks/` | Read-only validation commands or scripts |
| `cleanup/` | Exact commands required to remove the exercise |
| `solution/` | Reference solution kept separate from the task |
| `evidence/` | Sanitized outputs; never credentials or full private configs |

Do not place a personal experiment inside `configs/00-base` or another
generated phase unless it is intentionally becoming part of the product
baseline.

### 7.3 Reusable automation

Use the AUTO1 source directories:

```text
automation/inventory/             Device groups and connection metadata
automation/inventory/group_vars/  Shared, non-secret variables
automation/inventory/host_vars/   Per-node, non-secret variables
automation/templates/             Jinja2 configuration templates
automation/playbooks/             Orchestration and validation workflows
automation/scripts/               Python utilities
automation/rendered/              Generated candidate configs; ignored
automation/artifacts/             Backups and evidence; ignored
```

Secrets remain environment variables or Ansible Vault material excluded from
Git. Do not hardcode them in `group_vars` or `host_vars`.

## 8. AUTO1 responsibilities

AUTO1 is an automation and evidence workstation. It is not the router's NVRAM
and does not automatically capture every manual command.

AUTO1 should contain:

- Inventory and variable hierarchy.
- Jinja2 templates.
- Prechecks and postchecks.
- Controlled deployment playbooks.
- Read-only operational commands.
- Backup and rollback workflows.
- Sanitized acceptance evidence.

AUTO1 should not contain:

- Vendor images.
- Plaintext passwords or tokens.
- Private SSH keys committed to Git.
- Unsanitized production-style configuration backups in Git.
- Generated runtime directories.

The host directory `automation/` is bind-mounted at `/workspace`, so files
written below `/workspace` persist after the AUTO1 container is destroyed.

Connect to AUTO1:

```bash
ssh student@10.201.255.150
cd /workspace
ansible-inventory --graph
```

Run a precheck before a change:

```bash
ansible-playbook playbooks/precheck.yml --limit P1
```

Create configuration backups:

```bash
ansible-playbook playbooks/backup.yml
```

The backup playbook writes to:

```text
/workspace/artifacts/backups/
```

On the Ubuntu host that is:

```text
automation/artifacts/backups/
```

The directory is ignored by Git because router backups may contain sensitive
configuration.

## 9. Host-side provider backup

For XRd provider nodes:

```bash
python tools/backup_provider.py \
  --label before-my-exercise \
  --workers 2
```

Backups are stored below:

```text
artifacts/backups/<timestamp>-before-my-exercise/
```

Record the checksum and Git revision with important checkpoints.

## 10. Daily study workflow

### Start

```bash
cd /srv/netlab/labs/ccie-sp-startup-repair
git status --short --branch
./labctl status
free -h
uptime
./labctl deploy master
```

Replace `master` with the chosen profile. Never deploy a second heavy profile.

### Establish a checkpoint

```bash
python tools/backup_provider.py \
  --label before-session-topic \
  --workers 2
```

### Study

1. Read the scenario objective.
2. Capture prechecks.
3. Make one logical change at a time.
4. Commit XRd changes or save IOL NVRAM.
5. Validate protocol state and data-plane reachability.
6. Save sanitized evidence.
7. Practice failure and recovery.
8. Run cleanup or keep the committed state intentionally.

### Stop

```bash
./labctl destroy master
docker ps --format '{{.Names}}' | grep '^clab-' || \
  echo 'PASS: no active Containerlab nodes'
free -h
```

## 11. Recovery choices

| Objective | Correct action |
|---|---|
| Keep manual work for tomorrow | Commit/save, then normal `labctl destroy` |
| Undo one XRd change | Use commit history and a controlled rollback |
| Restore from recorded configuration | Use AUTO1 or host backup after prechecks |
| Return to generated baseline | Back up, destroy with intentional cleanup, regenerate, deploy |
| Change the official baseline | Edit generator, regenerate, validate, commit through a PR |

Before a full reset, capture:

```bash
git rev-parse HEAD
git status --short --branch
python tools/backup_provider.py --label before-clean-reset --workers 2
```

Never delete a broad directory based on an unresolved variable or wildcard.

## 12. Git workflow

Create a focused branch:

```bash
git switch -c study/<short-topic>
```

After editing:

```bash
git status --short
git diff --check
git diff
python -m pytest -q -p no:cacheprovider tests
```

Commit only intentional source, documentation, tests, and generated artifacts:

```bash
git add <explicit-files>
git commit -m "study: add <topic> scenario"
git push -u origin study/<short-topic>
```

Never use `git add .` before confirming that backups, evidence, credentials,
and runtime artifacts are correctly ignored.

## 13. Quick decision table

| Question | Answer |
|---|---|
| Where do I change topology/addressing? | The profile generator |
| Where do I create a personal exercise? | `studies/<profile>/<scenario-id>/` |
| Where do Jinja2 templates go? | `automation/templates/` |
| Where do playbooks go? | `automation/playbooks/` |
| Where do Python automation tools go? | `automation/scripts/` or repository `tools/`, depending on scope |
| Where do secrets go? | Ignored `.env` or approved vault mechanism |
| How do XRd changes persist? | `commit` plus retained `xr-storage` |
| How do IOL changes persist? | `write memory` plus retained NVRAM |
| Does AUTO1 automatically save manual CLI work? | No; run a backup workflow |
| Does normal `destroy` erase configurations? | No, provided cleanup and lab-directory deletion are not used |
| What restores a completely clean Master? | Regenerate and deploy from `topology/startup/` after intentional cleanup |
