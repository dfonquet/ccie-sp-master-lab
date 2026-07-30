# Troubleshooting and design findings

## Duplicate IPv4/IPv6 nodal SID

Symptom:

```text
Feature not supported: Nodal sid is already in use,
duplicates are not supported.
```

Cause: XRd 24.2.11 rejected the same Prefix-SID index on IPv4 and IPv6.

Resolution:

```text
IPv4 indexes: 1-14
IPv6 indexes: 601-614
```

## IS-IS neighbors remain in Init

Symptom:

```text
State Init
show bfd session -> no sessions
```

Cause: XRd Control Plane accepted IS-IS BFD configuration but did not create
BFD sessions on these virtual links.

Resolution: remove `bfd fast-detect ipv4/ipv6` from the XRd baseline and retain
per-prefix LFA/FRR. Use another platform for BFD exercises.

## Containerlab refuses to add AUTO1

Symptom:

```text
The 'ccie-sp-master' lab has already been deployed.
Destroy the lab before deploying a lab with the same name.
```

Cause: Containerlab 0.77 does not extend an already deployed lab under the
same name through `--node-filter`.

Resolution: do not destroy the routers. Attach AUTO1 directly to
`ccie-sp-master-mgmt`, as documented in `BUILD-GUIDE.md`.

## SSH banner timeout during parallel validation

Symptom:

```text
Error reading SSH protocol banner
```

Cause: the first link validator opened simultaneous IPv4 and IPv6 sessions to
the same XRd daemon.

Resolution: reuse one SSH session per source router for both families.

## AUTO1 cannot find Ansible over SSH

Symptom:

```text
ansible: command not found
```

Cause: an interactive SSH shell did not inherit `/opt/venv/bin`.

Resolution: export the virtualenv path from the student user's `.bashrc` and
`.profile`, rebuild AUTO1 and verify through a real SSH session.
