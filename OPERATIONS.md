# Operations and Quick Start

## Current access

| Nodes | Management addresses | Username source | Password source |
|---|---|---|---|
| P1-P8 | `10.201.255.101-108` | `CCIE_XRD_USERNAME` | `CCIE_XRD_PASSWORD` |
| PE1-PE8 | `10.201.255.111-118` | `CCIE_XRD_USERNAME` | `CCIE_XRD_PASSWORD` |
| RR1-RR2 | `10.201.255.121-122` | `CCIE_XRD_USERNAME` | `CCIE_XRD_PASSWORD` |
| CE1-CE9 | `10.201.255.131-139` | `CCIE_IOL_USERNAME` | `CCIE_IOL_PASSWORD` |
| C1-C2 | `10.201.255.141-142` | `CCIE_IOL_USERNAME` | `CCIE_IOL_PASSWORD` |
| AUTO1 | `10.201.255.150` | `CCIE_AUTO_USERNAME` | `CCIE_AUTO_PASSWORD` |

The following entries are declared offline and are not reachable until a
separately approved deployment window:

| Planned nodes | Management addresses | Username source | Password source |
|---|---|---|---|
| ASBR-ISP2, RR-ISP2 | `10.201.255.151-152` | `CCIE_XRD_USERNAME` | `CCIE_XRD_PASSWORD` |
| ISP2-P1–ISP2-P5 | `10.201.255.153-157` | `CCIE_IOL_USERNAME` | `CCIE_IOL_PASSWORD` |
| SOURCE1 | `10.201.255.158` | `CCIE_AUTO_USERNAME` | `CCIE_AUTO_PASSWORD` |

Create the ignored runtime credential file before operating the lab:

```bash
cp .env.example .env
# Replace every placeholder, then load it:
set -a
source .env
set +a
```

These variables supply credentials to automation clients; they do not modify
accounts on XRd or IOL. Rotate the live node credentials separately and keep
the management networks isolated from untrusted hosts.

Examples from Windows:

```powershell
ssh clab@10.201.255.101
ssh clab@10.201.255.111
ssh admin@10.201.255.131
ssh student@10.201.255.150
```

The persistent Windows route is:

```text
10.201.255.0/24 via 192.168.192.10
```

## Lab directory

```bash
cd /srv/netlab/labs/ccie-sp-master
```

Inspect the topology:

```bash
containerlab inspect -t topology/ccie-sp-master.clab.yml
```

Validate all management sessions:

```bash
/srv/netlab/venvs/ccie-sp/bin/python tools/validate_nodes.py --workers 2
```

Validate the 47 active ISP-1 links with IPv4 and IPv6 before the expansion.
After manual ISP-2 addressing, the same validator targets all 57 links:

```bash
/srv/netlab/venvs/ccie-sp/bin/python tools/validate_links.py --family both
```

## Rebuild the generated files

Do not run the Master generator while runtime-only study configuration has not
been captured and reconciled. It can regenerate topology and startup artifacts
that are intentionally not authoritative for the current runtime.

```bash
/srv/netlab/venvs/ccie-sp/bin/python tools/build_lab.py
```

## Baseline restoration and manual phases

Historically, `python3 tools/build_lab.py` generates deploy-safe files under
`topology/startup/`. `./labctl deploy master` uses them automatically and
waits for all 30 nodes to pass real SSH/CLI readiness. XRd receives the final
cumulative provider baseline; IOL receives a partial startup configuration so
Containerlab retains its management VRF and SSH defaults.

The lifecycle controller limits deployment to four workers, gives Docker API
operations a five-minute deadline, and staggers each IOL node by 15 seconds.
This prevents IOL from reaching its initial configuration dialog before
Containerlab completes postdeploy configuration during an XRd boot storm.

The commands below remain useful for controlled canaries, repair of an already
running node, and phase-by-phase study. They are not required after a clean
Master deployment.

Apply the phases in order:

```bash
/srv/netlab/venvs/ccie-sp/bin/python tools/apply_phase.py 00-base --workers 2
/srv/netlab/venvs/ccie-sp/bin/python tools/apply_phase.py 10-isis --workers 2
/srv/netlab/venvs/ccie-sp/bin/python tools/apply_phase.py 15-provider-standard --workers 2
/srv/netlab/venvs/ccie-sp/bin/python tools/apply_phase.py 20-sr-mpls --workers 2
```

For an already running lab created with the older IPv6 plan, take a backup and
apply the in-place provider refinement instead:

```bash
/srv/netlab/venvs/ccie-sp/bin/python tools/backup_provider.py \
  --label before-ipv6-standard --workers 2
/srv/netlab/venvs/ccie-sp/bin/python tools/apply_phase.py \
  15-provider-standard --workers 2
/srv/netlab/venvs/ccie-sp/bin/python tools/validate_provider_standard.py \
  --workers 2
/srv/netlab/venvs/ccie-sp/bin/python tools/validate_links.py --family both
```

The migration contains no `no ipv4 address` or `ipv4 address` changes. It
replaces only the provider IPv6 addresses and adds the common IS-IS, LFA, SR
and SR-TE control-plane standard. XRd Control Plane does not establish BFD
sessions on these links, so BFD is intentionally removed from this baseline.

Apply a phase to one or more nodes:

```bash
/srv/netlab/venvs/ccie-sp/bin/python tools/apply_phase.py \
  10-isis --nodes P1,P2 --workers 1
```

XRd commits are persistent under each node's `xr-storage` directory. IOL
baselines are saved with `write memory`.

## Useful verification

On an XRd node:

```text
show isis neighbors
show isis database summary
show route isis
show isis segment-routing label table
show mpls forwarding prefix 10.0.0.14/32
traceroute 10.0.0.14 source 10.0.0.1 numeric timeout 1
```

On an IOL node:

```text
show version
show ip interface brief
show ipv6 interface brief
show cdp neighbors
```

## Lifecycle

Build the lightweight automation workstation:

```bash
docker build -t ccie-sp-automation:1.0 automation
```

On a clean full deployment, Containerlab creates `AUTO1` from the topology.
When adding it to an already running lab, Containerlab 0.77 refuses to extend
the existing lab name. Attach the container directly without restarting the
25 routers:

```bash
docker run -d \
  --name clab-ccie-sp-master-AUTO1 \
  --hostname AUTO1 \
  --network ccie-sp-master-mgmt \
  --ip 10.201.255.150 \
  --restart unless-stopped \
  --label containerlab=ccie-sp-master \
  --label clab-node-name=AUTO1 \
  --label clab-node-longname=clab-ccie-sp-master-AUTO1 \
  --label clab-node-kind=linux \
  --label clab-owner=daniel \
  --env AUTO1_PASSWORD="$CCIE_AUTO_PASSWORD" \
  --volume /srv/netlab/labs/ccie-sp-master/automation:/workspace \
  ccie-sp-automation:1.0
```

Do not run the following against an already deployed lab; Containerlab will
correctly reject it because that lab name already exists:

```bash
sudo containerlab deploy \
  -t topology/ccie-sp-master.clab.yml \
  --node-filter AUTO1
```

Deploy:

```bash
sudo containerlab deploy \
  -t topology/ccie-sp-master.clab.yml \
  --max-workers 4
```

Destroy while keeping the persisted node state:

```bash
sudo containerlab destroy -t topology/ccie-sp-master.clab.yml
```

Do not use `--cleanup` unless a completely clean reset is intended, because it
removes the persisted lab directories.

## AUTO1 quick start

```bash
ssh student@10.201.255.150
cd /workspace
ansible-inventory --graph
ansible-playbook playbooks/precheck.yml
python3 scripts/hello_netmiko.py
ansible-playbook playbooks/backup.yml
```

## Recommended practice workflow

1. Load or verify the required baseline.
2. Capture pre-check outputs.
3. Perform the task without consulting the answer.
4. Test IPv4 and IPv6 service reachability.
5. Inject one failure.
6. Record convergence and control-plane behavior.
7. Compare the running configuration with the solution.
8. Restore the baseline before starting the next task.
