# Complete build guide

This document records how the lab was built, why each decision was made and
how to reproduce it without relying on hidden state.

## 1. Objective

The target was a reusable CCIE Service Provider v5.1 practice environment with:

- A redundant P backbone.
- Dual-homed PEs and selected dual-homed customer sites.
- Redundant route-reflector/PCE nodes.
- IPv4 and IPv6 underlay operation.
- IS-IS, SR-MPLS, SR-TE and future SRv6 exercises.
- L2VPN, L3VPN, multicast, security and failure-injection capacity.
- A dedicated automation workstation for the 20% Assurance and Automation
  portion of the blueprint.

## 2. Platform choice

The routing lab was placed on the existing Ubuntu Server VM instead of the
Arch Linux desktop VM.

Reasons:

- Containerlab and Docker are easier to operate as persistent services.
- Ubuntu provides a stable host for a long-running 25-router topology.
- The VM already had direct storage under `/srv/netlab`.
- Router startup, persistence, validation and automation can be scripted.
- Arch remains useful as a desktop/security workstation but is not required
  in the control path of the service-provider lab.

## 3. Confirmed resources

The figures below were measured while the final lab was running.

| Resource | Confirmed value | Design use |
|---|---:|---|
| Ubuntu VM vCPU | 12 vCPU | Parallel XRd control planes and validation |
| Ubuntu VM memory | 60 GiB | 14 XRd, 11 IOL and AUTO1 |
| Memory used | Approximately 35 GiB | Final running topology |
| Memory available | Approximately 25 GiB | Failure drills and future services |
| `/srv/netlab` filesystem | 196 GB | Images, persistence and projects |
| Free storage after build | Approximately 158 GB | Future artifacts and labs |
| AUTO1 idle memory | Approximately 8 MiB | Lightweight automation control node |
| Windows-visible logical CPUs | 16 | Host observation; physical model was not recorded |

The exact physical Windows RAM and CPU model were not captured, so they are
not guessed here. The allocation that matters to reproducibility is the
12-vCPU/60-GiB Ubuntu VM.

## 4. Software images

```text
ios-xr/xrd-control-plane:24.2.11
vrnetlab/cisco_iol:17.12.01
ccie-sp-automation:1.0
```

The supplied IOL folder name suggested `17.15.01`, but CLI verification showed
IOS XE Dublin 17.12.1. The Docker tag was corrected to represent the actual
software version.

Cisco images are intentionally excluded from Git for licensing and size
reasons.

## 5. Project generation

`tools/build_lab.py` is the source of truth. It defines:

- Nodes and management addresses.
- Point-to-point links and groups.
- IPv4 and IPv6 addressing.
- IS-IS NETs and metrics.
- Prefix-SID indexes.
- Containerlab topology.
- Configuration phases and inventories.

Generate everything with:

```bash
python3 tools/build_lab.py
```

Do not hand-edit files under `configs/`, `inventory/` or the generated
Containerlab topology unless the generator is changed at the same time.

## 6. Initial deployment

```bash
cd /srv/netlab/labs/ccie-sp-master

sudo containerlab deploy \
  -t topology/ccie-sp-master.clab.yml \
  --max-workers 4
```

The staggered startup delays prevent all XRd/IOL nodes from competing for CPU
and memory at the same instant.

## 7. Configuration phases

Apply phases in order on a clean deployment:

```bash
/srv/netlab/venvs/ccie-sp/bin/python tools/apply_phase.py 00-base --workers 2
/srv/netlab/venvs/ccie-sp/bin/python tools/apply_phase.py 10-isis --workers 2
/srv/netlab/venvs/ccie-sp/bin/python tools/apply_phase.py 20-sr-mpls --workers 2
```

The already-running lab originally used a different IPv6 plan. Its safe
in-place migration was:

```bash
/srv/netlab/venvs/ccie-sp/bin/python tools/backup_provider.py \
  --label before-ipv6-standard --workers 2

/srv/netlab/venvs/ccie-sp/bin/python tools/apply_phase.py \
  15-provider-standard --workers 2
```

The migration contains no IPv4 address removal or replacement.

## 8. IPv6 refinement

The requested convention was adapted without replacing the working IPv4
router IDs:

```text
Provider loopbacks: 2001:db8:500:abcd::<node-id>/128
Provider links:     2001:db8:1000:<101-125>::/127
```

`Loopback0` and IS-IS process `CORE` were retained. Renaming them to
`Loopback600` and `500-SP` would have created an unnecessary IGP migration
without adding protocol capability.

## 9. SR-MPLS refinement

The original 14-node IPv4 Prefix-SIDs were retained and extended for P7, P8,
PE7, and PE8:

```text
Current indexes 1-18 -> labels 16001-16018
```

XRd rejected reuse of the same nodal SID index for IPv6. A separate,
deterministic range was therefore selected:

```text
Current indexes 601-618 -> labels 16601-16618
```

This keeps both address families inside SRGB `16000-23999`.

## 10. XRd BFD finding

XRd Control Plane accepted:

```text
bfd fast-detect ipv4
bfd fast-detect ipv6
```

However, it did not instantiate BFD sessions on these virtual links and IS-IS
adjacencies remained in `Init`. The commands were removed atomically and every
adjacency returned to `Up`.

The final XRd baseline retains per-prefix LFA/FRR. BFD practice should use IOL,
XRv9k with a suitable data plane, or physical IOS XR.

## 11. Adding AUTO1

`AUTO1` was built from `automation/Dockerfile`. Because the main Containerlab
lab already existed, Containerlab 0.77 refused to extend the same lab name
with `--node-filter`. The running lab was not destroyed. AUTO1 was attached
directly to the existing management Docker network:

```bash
docker run -d \
  --name clab-ccie-sp-master-AUTO1 \
  --hostname AUTO1 \
  --network ccie-sp-master-mgmt \
  --ip 10.201.255.150 \
  --restart unless-stopped \
  --volume /srv/netlab/labs/ccie-sp-master/automation:/workspace \
  ccie-sp-automation:1.0
```

On a future clean deployment, AUTO1 is already present in the topology and
Containerlab creates it normally.

## 12. Final validation

The original 26-node acceptance evidence was:

- 26/26 management SSH/CLI checks passed.
- 14/14 provider nodes passed the standard audit.
- 39/39 directly connected IPv4 tests passed.
- 39/39 directly connected IPv6 tests passed.
- P1 to RR2 IPv6 loopback ping passed 5/5.
- P1 learned 14 IPv4 and 14 IPv6 Prefix-SIDs.
- Netmiko from AUTO1 to P1 passed.
- Ansible pre-check from AUTO1 to P1 completed with zero failures.

Those results are retained as historical expansion evidence. They do not
replace the current 30-node acceptance gate. The current targets are 30
management sessions, 18 provider-standard checks, and 188 bidirectional
dual-stack link tests; record them as validated only after observing a complete
live run.

See [VALIDATION.md](VALIDATION.md) for the repeatable commands.
