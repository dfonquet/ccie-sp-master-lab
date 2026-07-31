# SRv6 readiness assessment

This document records the capability gates that must pass before the SRv6
profile is deployed. A parser-accepted command is not treated as proof of
control-plane or data-plane support.

## Assessment scope

- Host: `netlab-core`
- Assessment date: 2026-07-31
- Target image: `ios-xr/xrd-control-plane:24.2.11`
- Containerlab: `0.77.0`
- Docker client/server: `29.1.3`
- Intended first stage: one-node parser and commit canary
- Intended second stage: P1-P2-PE1 capability mini-lab
- Full SRv6 profile: blocked until the capability gates pass

## Host baseline

| Gate | Observed state | Result |
|---|---|---|
| Concurrent labs | No running Docker containers or Containerlab nodes | PASS |
| Guest operating system | Ubuntu 26.04 LTS, kernel 7.0.0-28-generic | PASS |
| Compute assigned to VM | 12 vCPU | PASS for canary |
| Memory | 60 GiB total, approximately 59 GiB available | PASS for canary |
| Swap | 2 GiB, unused | PASS |
| Root filesystem | 19 GiB total, approximately 11 GiB available | PASS; Docker uses a separate filesystem |
| Docker filesystem | 196 GiB total, approximately 153 GiB available at `/srv/netlab` | PASS |
| Hypervisor | VMware on AMD-V | PASS |
| KVM device | `/dev/kvm` present | PASS |
| Nested virtualization | `kvm_amd nested=1` | PASS |
| XRd image | `ios-xr/xrd-control-plane:24.2.11`, image ID `sha256:f160dc83ee7e6ef3c9e66254d32237c8d62052f91539da0defc38ddfcc2f36af` | PASS |
| XRd repository digest | Not recorded because the image was imported from TAR | ACCEPTED; pin local image ID in evidence |
| Existing management networks | Docker bridge `172.30.0.0/24`; empty residual network `10.200.255.0/24` | PASS after avoiding both ranges |
| Capability management network | Reserved `10.203.255.0/24` | PASS |
| VM repository | Old feature branch with unclassified local changes | BLOCKED |

## Repository safety finding

The VM checkout is currently on `agent/multi-profile-lab` at commit `66eeba3`.
The only tracked difference is the executable bit on `labctl`. Untracked data
includes `automation/.dockerignore` and three device configuration backups under
`automation/playbooks/backup/`. These files must be classified and backed up
before any fetch, checkout, pull, reset, clean, or replacement operation.

The authoritative GitHub `main` includes later profile, documentation, and
credential-hardening work. The VM checkout must not be described as synchronized
until the local work has been preserved and compared with that branch.

The local files were preserved on 2026-07-31 under
`/srv/netlab/backups/repo-reconcile-20260731T151208Z`. The backup includes a
binary Git patch, status evidence, the executable `labctl`, `.dockerignore`,
three device configurations, and SHA-256 checksums. All three device
configurations matched common secret indicators and are therefore excluded from
the public repository. Their contents and checksum values are intentionally not
duplicated here.

The original checkout remains untouched. SRv6 work will use a separate Git
worktree at `/srv/netlab/labs/ccie-sp-srv6`, created only after this readiness
branch is published. This avoids destructive reconciliation of the older
feature branch.

## Remaining readiness evidence

- publish this readiness branch and create the isolated VM worktree
- create an explicit rollback point before synchronizing the VM checkout
- confirm required runtime credential variables without recording their values

## Initial decision

**GO** for continued read-only preparation and repository reconciliation.

**NO-GO** for deploying the XRd canary until the management-network and VM Git
gates above are closed. This is an operational safety gate, not a host-capacity
failure.
