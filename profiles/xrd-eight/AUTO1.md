# AUTO1 Workspace for XRd Eight

AUTO1 is the management and service workstation for the local XRd lab.

Planned responsibilities:

- Ansible, Python, Netmiko and pyATS/Genie automation.
- Configuration rendering and validation.
- Device backups and evidence collection.
- FreeRADIUS authentication and accounting.
- TACACS+ authentication, authorization and accounting.
- Routinator RPKI validator and RTR cache.
- Controlled prechecks, deployment and postchecks.

Persistent host directories:

- `/workspace/xrd-eight`
- `/var/lib/ccie-sp`
- `/evidence`
- `/backups`

AAA and RPKI are not automatically enabled on routers. They remain controlled study phases.

The selected `student` password is injected with `CCIE_AUTO_PASSWORD` at deployment and must never be committed. Lab-only device defaults are documented in [OPERATIONS.md](OPERATIONS.md).
