# AUTO1 Automation Workstation

`AUTO1` is a disposable but reproducible Linux automation workstation attached
to the lab management network at `10.201.255.150`.

Access from Windows:

```powershell
ssh student@10.201.255.150
```

Credentials are never stored in the repository. Before deploying, copy the
root `.env.example` file to `.env`, replace every placeholder, and load the
variables into the current shell:

```bash
set -a
source .env
set +a
```

`CCIE_AUTO_PASSWORD` is passed to the container at runtime. The same file
provides the XRd and IOL credentials consumed by Ansible and the Python tools.
The `.env` file is ignored by Git and must never be committed.

First checks:

```bash
cd /workspace
ansible-inventory --graph
ansible-playbook playbooks/precheck.yml
python3 scripts/hello_netmiko.py
ansible-playbook playbooks/backup.yml
```

The reviewed Source of Truth/Jinja2 BGP workflow is documented in
[`../docs/AUTO1-SOURCE-OF-TRUTH.md`](../docs/AUTO1-SOURCE-OF-TRUTH.md).

Installed tool families:

- Python, Jinja2, YAML, JSON, XML and pytest.
- Ansible with IOS, IOS XR, NSO and network-common collections.
- Netmiko, Scrapli, Nornir and NTC templates.
- NETCONF with ncclient.
- gNMI/gRPC with pyGNMI and grpcio.
- Cisco pyATS and Genie.

NSO itself is not included because Cisco distributes it separately. `AUTO1`
already includes the Ansible NSO collection and can act as an NSO northbound
client when an authorized NSO installation is added later.
