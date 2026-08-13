# Validation and Acceptance Runbook

> Reproducible validation procedure for the CCIE SP Master profile. This runbook
> separates inventory-derived cardinality from live acceptance evidence.

## 1. Scope

The currently active Master runtime baseline contains:

| Component | Inventory source | Current count |
|---|---|---:|
| All managed nodes | `inventory/nodes.csv` | 30 |
| IOS XRd provider nodes | `inventory/nodes.csv` | 18 |
| Directly connected links | `inventory/links.csv` | 47 |
| Address families tested per link | Validator argument | 2 |
| Directions tested per link | Validator behavior | 2 |

For a complete dual-stack link-validation run, the calculated test cardinality
is therefore:

```text
47 active links × 2 directions × 2 address families = 188 directed tests
```

The offline structural inventory additionally declares ISP-2. It must not be
counted as runtime acceptance before the approved deployment and manual
configuration phases:

```text
structural_nodes=38
structural_links=57
active_nodes=30
active_links=47
active_directed_dual_stack_tests=188
```

This number verifies test **coverage**, not reachability. Do not publish a pass
result until the live output reports all 188 tests successful.

## 2. Acceptance policy

Use the following terminology consistently:

| Term | Meaning |
|---|---|
| **Calculated target** | Count derived from committed source-of-truth files |
| **Observed result** | Summary produced by a live validator execution |
| **Accepted** | Observed result matches the target and reports zero failures |
| **Evidence** | Timestamped command output retained outside Git or sanitized before publication |

An expected count must never be presented as observed evidence. Capture the
actual output from the deployed lab and record its timestamp, Git revision,
profile, image versions, and validator return code.

## 3. Preconditions

Run from the Ubuntu `netlab-core` host:

```bash
cd /srv/netlab/labs/ccie-sp-master
```

Confirm the repository revision and ensure that only the Master profile is
active:

```bash
git status --short --branch
git rev-parse HEAD

docker ps --format '{{.Names}}' |
  grep '^clab-' ||
  echo 'FAIL: no Containerlab nodes are active'
```

Activate the project environment and load credentials without printing them:

```bash
source /srv/netlab/venvs/ccie-sp/bin/activate

test -n "${CCIE_XRD_PASSWORD:-}" || {
  read -rsp 'XRd password: ' CCIE_XRD_PASSWORD
  echo
  export CCIE_XRD_PASSWORD
}

test -n "${CCIE_IOL_PASSWORD:-}" || {
  read -rsp 'IOL password: ' CCIE_IOL_PASSWORD
  echo
  export CCIE_IOL_PASSWORD
}

test -n "${CCIE_AUTO_PASSWORD:-}" || {
  read -rsp 'AUTO1 password: ' CCIE_AUTO_PASSWORD
  echo
  export CCIE_AUTO_PASSWORD
}
```

Do not paste credentials, `.env` content, private keys, or raw configuration
backups into evidence files committed to Git.

## 4. Verify source-of-truth cardinality

Calculate the current counts instead of trusting documentation copied from an
older topology:

```bash
python3 - <<'PY'
import csv
from pathlib import Path

root = Path('.')
with (root / 'inventory/nodes.csv').open(encoding='utf-8', newline='') as f:
    nodes = list(csv.DictReader(f))
with (root / 'inventory/links.csv').open(encoding='utf-8', newline='') as f:
    links = list(csv.DictReader(f))

xrd = [node for node in nodes if node['kind'] == 'cisco_xrd']
families = 2
directions = 2

print(f'nodes={len(nodes)}')
print(f'xrd_nodes={len(xrd)}')
print(f'links={len(links)}')
print(f'directed_dual_stack_tests={len(links) * families * directions}')
PY
```

Calculated target for the committed 30-node Master topology:

```text
nodes=30
xrd_nodes=18
links=47
directed_dual_stack_tests=188
```

If these values change, regenerate the documentation target and investigate the
topology diff before running acceptance.

## 5. Management and software validation

Validate TCP/22, authentication, CLI prompt detection, and reported software
version for all XRd, IOL-XE, and AUTO1 nodes:

```bash
python tools/validate_nodes.py --workers 4 |
  tee /tmp/ccie-sp-master-validate-nodes.txt
```

Current calculated acceptance target:

```text
SUMMARY total=30 tcp22_open=30 cli_ok=30
```

Acceptance requires the live summary to match the target. `tcp22=open` alone is
not sufficient: it proves transport reachability but not valid credentials,
prompt detection, or CLI execution.

## 6. Provider-standard validation

Validate every P, PE, and RR/PCE XRd node against the provider baseline:

```bash
python tools/validate_provider_standard.py --workers 2 |
  tee /tmp/ccie-sp-master-provider-standard.txt
```

Current calculated acceptance target:

```text
SUMMARY nodes=18 passed=18 failed=0
```

The validator checks expected provider IPv6 addressing, IS-IS configuration,
and adjacency cardinality. Its `bfd_up` field is diagnostic only because XRd
Control Plane may accept BFD configuration without creating operational BFD
sessions over the virtual links.

## 7. Bidirectional directly connected link validation

`validate_links.py` builds two directed tests for every inventory link:

```text
endpoint_a -> endpoint_b
endpoint_b -> endpoint_a
```

It repeats those tests for each selected address family. Connections are grouped
by source node so that one SSH session can validate all outbound links from that
node.

Run the complete Master validation:

```bash
python tools/validate_links.py \
  --profile master \
  --family both \
  --workers 2 |
  tee /tmp/ccie-sp-master-validate-links.txt
```

Current calculated acceptance target:

```text
SUMMARY tests=188 families=ipv4,ipv6 passed=188 failed=0
```

Each result identifies the link, family, source node, destination node/address,
status, and device-reported success rate:

```text
L001|ipv4|P1->P2(10.255.0.1)|ok|Success rate is 100 percent (...)
L001|ipv4|P2->P1(10.255.0.0)|ok|Success rate is 100 percent (...)
```

The exact addresses above are illustrative; the committed `links.csv` and live
output are authoritative.

### 7.1 Targeted diagnostics

Test one family only:

```bash
python tools/validate_links.py --profile master --family ipv6 --workers 2
```

Test outbound directions from selected nodes only:

```bash
python tools/validate_links.py \
  --profile master \
  --family both \
  --sources P1,PE1 \
  --workers 2
```

`--sources` deliberately limits the run to tests sourced by those nodes. It does
not imply full bidirectional coverage unless both endpoints are selected.

### 7.2 Failure interpretation

| Pattern | Probable area to investigate |
|---|---|
| Both families fail in both directions | Link state, interface mapping, container link, or missing base configuration |
| One direction fails | Source interface/routing, ACL, return path, or platform-specific ping behavior |
| IPv4 passes and IPv6 fails | IPv6 address, `/127`, ND, interface family activation, or command syntax |
| IPv6 passes and IPv4 fails | IPv4 `/31`, source selection, interface family activation, or ACL |
| Every test from one node fails | Management/CLI session, credentials, node health, or configuration batch failure |
| First attempt fails but retry passes | Boot convergence, control-plane load, transient neighbor discovery, or host pressure |

The validator retries a failed ping once. A retry success should still prompt a
resource and convergence review if it occurs repeatedly.

## 8. IOS XR control-plane checks

Use CLI verification to corroborate the automated results:

```text
show ipv4 interface brief
show ipv6 interface brief
show isis neighbors
show isis database summary
show route isis
show isis segment-routing label table
show mpls forwarding
show segment-routing mpls connected-prefix-sid-map ipv4
show configuration failed
show configuration commit list
```

Example end-to-end IPv6 test from P1 to a provider loopback:

```text
ping ipv6 2001:db8:500:abcd::14 \
  source 2001:db8:500:abcd::1 count 5 timeout 1
```

Do not treat one end-to-end ping as a substitute for the complete adjacency,
route, label, and directed-link validation set.

## 9. AUTO1 validation

Connect to the automation workstation:

```bash
ssh student@10.201.255.150
cd /workspace
```

Validate its mounted source, inventory, Python environment, and read-only
automation path:

```bash
pwd
git status --short --branch
ansible --version
ansible-inventory --graph
python3 --version
python3 scripts/hello_netmiko.py
ansible-playbook playbooks/precheck.yml --limit P1 --check
```

The pre-check must remain read-only. Do not use a configuration playbook merely
to prove that AUTO1 is reachable.

## 10. Host-resource and container-health evidence

Collect health after the network has reached a stable state:

```bash
date -Is
free -h
uptime

docker ps \
  --filter name=clab-ccie-sp-master \
  --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'

docker stats --no-stream \
  $(docker ps \
    --filter name=clab-ccie-sp-master \
    --format '{{.Names}}')
```

Inspect XRd restart and OOM state:

```bash
for node in P{1..8} PE{1..8} RR1 RR2; do
  docker inspect "clab-ccie-sp-master-${node}" \
    --format '{{.Name}} restart={{.RestartCount}} oom={{.State.OOMKilled}}'
done
```

Acceptance requires no unexpected restart, no OOM kill, sufficient available
memory, zero swap pressure attributable to the lab, and a host load that has
stabilized after the staggered XRd boot sequence.

## 11. Capture a complete acceptance record

Create a timestamped directory outside the Git working tree:

```bash
evidence_dir="/srv/netlab/evidence/ccie-sp-master-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$evidence_dir"

git rev-parse HEAD > "$evidence_dir/git-revision.txt"
docker ps --format '{{.Names}}|{{.Status}}|{{.Image}}' \
  > "$evidence_dir/containers.txt"
free -h > "$evidence_dir/free-h.txt"
uptime > "$evidence_dir/uptime.txt"

python tools/validate_nodes.py --workers 4 \
  | tee "$evidence_dir/validate-nodes.txt"
python tools/validate_provider_standard.py --workers 2 \
  | tee "$evidence_dir/provider-standard.txt"
python tools/validate_links.py --profile master --family both --workers 2 \
  | tee "$evidence_dir/validate-links.txt"

sha256sum "$evidence_dir"/* > "$evidence_dir/SHA256SUMS"
echo "$evidence_dir"
```

Review and sanitize evidence before publishing it. Raw evidence remains local by
default and must not contain passwords, environment dumps, device secrets,
private keys, or proprietary configuration content.

## 12. Final acceptance gate

The current Master profile is accepted only when the live run demonstrates:

- [ ] Inventory calculation reports 30 nodes, 18 XRd nodes, and 47 links.
- [ ] All 30 management endpoints have TCP/22 and valid CLI access.
- [ ] All 18 provider nodes pass the provider-standard validator.
- [ ] All 188 directed dual-stack link tests pass.
- [ ] IOS XR reports no hidden configuration failures.
- [ ] Expected IS-IS adjacencies and SR-MPLS state are present.
- [ ] AUTO1 inventory and read-only pre-checks succeed.
- [ ] No container has an unexpected restart or OOM event.
- [ ] Host memory, swap, and load remain inside the operational safety gate.
- [ ] Evidence records the Git revision, timestamp, images, commands, and output.

If any check fails, record the failure, isolate the affected layer, correct the
source of truth or implementation, rerun the smallest relevant test, and then
repeat the complete acceptance suite. Never edit a summary line manually to make
the evidence match the calculated target.
