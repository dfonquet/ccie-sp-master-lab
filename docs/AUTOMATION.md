# Automation workstation

## Why a container instead of another VM

AUTO1 is a Linux container on the existing management network. This design:

- Uses very little idle memory.
- Starts and stops quickly.
- Is reproducible from a Dockerfile.
- Shares a persistent workspace with the Ubuntu host.
- Reaches every router by its management address.
- Avoids contaminating the Containerlab host Python environment.

## Confirmed software

| Tool | Validated version/use |
|---|---|
| Python | 3.12.3 |
| Ansible Core | 2.21.2 |
| Cisco pyATS/Genie | 26.6 |
| Netmiko | 4.7.0 |
| Nornir | Installed |
| Scrapli | Installed |
| ncclient | NETCONF client |
| pyGNMI/grpcio | gNMI and gRPC clients |
| Cisco collections | IOS, IOS XR and NSO |

## Access

```bash
ssh student@10.201.255.150
cd /workspace
```

Credentials are loaded from the `CCIE_*` environment variables documented in
`.env.example`; no functional password is committed. Review `SECURITY.md`
before sharing or deploying outside an isolated lab network.

## First exercises

```bash
ansible-inventory --graph
python3 scripts/hello_netmiko.py
ansible-playbook playbooks/precheck.yml --limit P1
ansible-playbook playbooks/backup.yml
```

## Recommended automation progression

1. Read-only CLI collection with Netmiko.
2. Jinja2 configuration rendering.
3. Ansible command and configuration modules.
4. Structured parsing with Genie/pyATS.
5. NETCONF/YANG discovery with ncclient.
6. gNMI capabilities and telemetry subscriptions.
7. Pre-check/change/post-check pipelines.
8. Fault injection and automated convergence reports.
9. NSO service packages when an authorized NSO installation is available.
