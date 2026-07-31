# AUTO1: Source of Truth and BGP Automation

This module formalizes the workflow built in `AUTO1` for RR2 and the six PEs:

```text
Source of Truth → Jinja2 → Render → Validate → Check/Diff
                → Controlled Deploy → BGP Post-check
```

The implementation comes from the files used in
`Automation-Notes/LAB-Container`. Names and folders were normalized to avoid
duplicates: `group_vars-pe.yml` became `inventory/group_vars/pe.yml`,
`host_varsRR2.yml` became `inventory/host_vars/RR2.yml`, and files prefixed
with `playbooks-` or `templates-` now live in their native directories.

Data resides next to the inventory under `automation/inventory/group_vars/`
and `automation/inventory/host_vars/` so Ansible loads it automatically.
Templates are stored in `automation/templates/`. The `rendered/` directory
contains local candidates and is excluded from Git: source files are versioned,
not their derivatives.

## Existing AUTO1 capabilities

The reproducible image already included Ansible, Cisco IOS/IOS XR collections,
Python, Jinja2, pyATS/Genie, Netmiko, Nornir, Scrapli, ncclient, and pyGNMI.
Inventory, pre-checks, and backups also existed. This module adds a
data-driven BGP change cycle with templates and pre-deployment controls.

## Run from `/workspace/automation`

```bash
ansible-inventory -i inventory/hosts.yml --host RR2
ansible-inventory -i inventory/hosts.yml --host PE1

ansible-playbook -i inventory/hosts.yml playbooks/validate_bgp_data.yml
ansible-playbook -i inventory/hosts.yml playbooks/validate_pe_loopbacks.yml
ansible-playbook -i inventory/hosts.yml playbooks/discover_loopbacks.yml
ansible-playbook -i inventory/hosts.yml playbooks/render_rr2_bgp.yml
ansible-playbook -i inventory/hosts.yml playbooks/render_pe_bgp.yml

cat rendered/RR2_bgp.cfg
grep -H "bgp router-id" rendered/PE*_bgp.cfg

ansible-playbook -i inventory/hosts.yml playbooks/check_rr2_bgp.yml --check --diff
ansible-playbook -i inventory/hosts.yml playbooks/check_pe_bgp.yml --check --diff
```

No real change should exist at this point. After human review:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_rr2_bgp.yml \
  --diff -e deploy_confirm=true
ansible-playbook -i inventory/hosts.yml playbooks/deploy_pe_bgp.yml \
  --diff -e deploy_confirm=true
ansible-playbook -i inventory/hosts.yml playbooks/postcheck_bgp.yml
```

The design preserves the values verified in the lab: AS 500, RR2
`10.0.0.14`, cluster ID `10.0.0.100`, PE1-PE6 `10.0.0.7-12`, and
`Loopback0` as the update source. PEs deploy with `serial: 1`; both playbooks
require explicit confirmation and create a backup.

## Startup and shutdown

```bash
cd /srv/netlab/labs/ccie-sp-master/topology
sudo containerlab deploy -t ccie-sp-master.clab.yml
sudo containerlab destroy -t ccie-sp-master.clab.yml
sudo docker ps -a --filter "name=clab-ccie-sp-master"
sudo shutdown -h now
```

Do not run `containerlab destroy` without `-t` from an ambiguous directory.
Rendered artifacts, backups, logs, keys, and proprietary Cisco images must not
be published.
