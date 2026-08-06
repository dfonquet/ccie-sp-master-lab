# XRd Eight Detailed Operating Guide
This runbook distinguishes the repository Source of Truth, Containerlab runtime files and the configuration currently running inside each router.

## Directory model

| Path | Purpose | Edit directly? |
|---|---|---|
| `tools/build_xrd_eight.py` | Authoritative topology, roles, addresses and generated foundation | Yes, after review |
| `profiles/xrd-eight/nodes.csv` | Generated node inventory | No |
| `profiles/xrd-eight/links.csv` | Generated link/address inventory | No |
| `configs/xrd-eight/00-foundation/` | Generated startup candidates | No |
| `topology/ccie-sp-xrd-eight.clab.yml` | Generated Containerlab topology | No |
| `profiles/xrd-eight/topology.svg` | Generated architecture diagram | No |
| `automation/xrd-eight/workspace/` | Persistent student playbooks, templates and scripts | Yes |
| `automation/xrd-eight/data/` | Persistent AAA/RPKI data | Runtime only |
| `automation/xrd-eight/evidence/` | Validation output | Runtime only |
| `automation/xrd-eight/backups/` | Device configuration backups | Runtime only; never commit |
| `topology/clab-ccie-sp-xrd-eight/` | Containerlab runtime copy | Never; disposable |

## Images

| Function | Local image |
|---|---|
| P, PE, RR/PCE/RP | `vrnetlab/cisco_xrd-vrouter:26.2.1` |
| CE | `vrnetlab/cisco_iol:17.12.01` |
| Operations | `ccie-sp-automation:1.0` |

Cisco images are not stored in Git. The XRd archive used during development was verified with Cisco's supplied X.509 certificate and detached signature before `docker load`. The base image was then wrapped locally for Containerlab/vrnetlab.

```bash
python3 cisco_x509_verify_release.py3 \
  -e IOS-XR-SW-XRd.crt \
  -i xrd-vrouter-container-x64.dockerv1.tgz \
  -s xrd-vrouter-container-x64.dockerv1.tgz.signature \
  -v smime --container xr --sig_type DER

docker load -i xrd-vrouter-container-x64.dockerv1.tgz
docker image inspect ios-xr/xrd-vrouter:26.2.1
docker image inspect vrnetlab/cisco_xrd-vrouter:26.2.1
```

## Laboratory credentials

These are disposable defaults for the isolated lab, not production credentials.

| Platform | Username | Password |
|---|---|---|
| XRd vRouter | `clab` | `clab@123` |
| IOL-XE | `admin` | `admin` |
| AUTO1 | `student` | value supplied through `CCIE_AUTO_PASSWORD` |

AUTO1's selected password is intentionally not committed. Set it for each shell session:

```bash
read -rsp "AUTO1 password: " CCIE_AUTO_PASSWORD
echo
export CCIE_AUTO_PASSWORD
```

## Generate before deployment

```bash
cd /srv/netlab/labs/ccie-sp-master
python3 tools/build_xrd_eight.py
python3 tools/render_xrd_eight.py
git diff --check
sudo --preserve-env=CCIE_AUTO_PASSWORD containerlab apply \
  -t topology/ccie-sp-xrd-eight.clab.yml --dry-run
```

## Preflight safety gate

```bash
docker ps --format '{{.Names}}' | grep '^clab-' || echo "PASS: no active lab"
free -h
nproc
uptime
ls -l /dev/kvm
cat /sys/module/kvm_amd/parameters/nested
```

Do not continue if another Containerlab profile is running, swap is active before deployment, `/dev/kvm` is unavailable or nested virtualization is disabled.

## Start the complete profile

```bash
cd /srv/netlab/labs/ccie-sp-master
profiles/xrd-eight/labctl deploy-full
```

XRd nodes start 120 seconds apart. A full deployment can take 16-20 minutes. Do not launch another heavy profile or interrupt the terminal merely because a later node is delayed.

## Observe status and resources

```bash
profiles/xrd-eight/labctl status
profiles/xrd-eight/labctl resources

for node in XR1 XR2 XR3 XR4 R1 R2 R3 R5; do
  docker inspect "clab-ccie-sp-xrd-eight-$node" \
    --format '{{.Name}} health={{if .State.Health}}{{.State.Health.Status}}{{end}} restart={{.RestartCount}} oom={{.State.OOMKilled}}'
done
```

Stop if swap is used, an XR node is OOM-killed, restarts repeatedly, exits, or remains unhealthy after its normal boot window.

## Connect to devices

```bash
ssh clab@10.207.255.101       # XR1 / P1
ssh clab@10.207.255.105       # R2 / RR-PCE-RP
ssh admin@10.207.255.141      # R4 / CE1
ssh student@10.207.255.150    # AUTO1
```

## Manual configuration and persistence

A manual `commit` on IOS XR or `write memory` on IOS-XE persists while that container exists. It is **not** automatically written back to Git or to the generated startup files. Destroying the lab removes that state.

Before destructive lifecycle operations, back up configuration from AUTO1 or the Ubuntu host. Store private backups outside Git:

```bash
mkdir -p automation/xrd-eight/backups/manual
ssh clab@10.207.255.101 'show running-config' \
  > automation/xrd-eight/backups/manual/XR1.cfg
```

To make an intentional baseline permanent, update `tools/build_xrd_eight.py`, regenerate, review the diff and then commit. Do not copy an unreviewed running configuration over a generated artifact.

## AUTO1 workflow

Use AUTO1 for repeatable operations:

1. inventory and credential loading;
2. read-only discovery and prechecks;
3. backups;
4. Jinja2 rendering into a review directory;
5. `--check --diff` or commit-check;
6. one-node canary;
7. controlled serial deployment;
8. postchecks and evidence;
9. rollback when an acceptance gate fails.

For example, an L2VPN exercise should be authored under `automation/xrd-eight/workspace/` and rendered on AUTO1. The permanent topology and addressing model remain in the repository; AUTO1 executes and validates changes against the running lab.

## AAA and RPKI on AUTO1

AUTO1 is reserved for FreeRADIUS/TACACS+ and Routinator experiments in addition to automation. Keep service databases under `/var/lib/ccie-sp`, evidence under `/evidence`, and configuration backups under `/backups`. Enabling a daemon on AUTO1 does not automatically enable AAA or origin validation on routers; those remain explicit study phases.

## Destroy correctly

```bash
cd /srv/netlab/labs/ccie-sp-master
profiles/xrd-eight/labctl destroy
```

The command uses:

```bash
containerlab destroy -t topology/ccie-sp-xrd-eight.clab.yml --cleanup
```

`--cleanup` is essential. Without it, `topology/clab-ccie-sp-xrd-eight/*/config/startup-config.cfg` can survive and override newly generated startup artifacts during the next deployment.

Verify shutdown:

```bash
docker ps -a --format '{{.Names}}' | grep '^clab-ccie-sp-xrd-eight-' || echo "PASS: removed"
test ! -e topology/clab-ccie-sp-xrd-eight && echo "PASS: runtime cleaned"
free -h
uptime
```

## Emergency shutdown

```bash
sudo containerlab destroy \
  -t /srv/netlab/labs/ccie-sp-master/topology/ccie-sp-xrd-eight.clab.yml \
  --cleanup
```
