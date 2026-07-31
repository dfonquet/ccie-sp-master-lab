# Troubleshooting — Lab 1 Master

## Duplicate Prefix-SID

**Symptom:** `Nodal sid is already in use`.

**Cause:** XRd 24.2.11 rejected reuse of the same index for IPv4 and IPv6.

**Solution:** use IDs 1-18 for IPv4 and 601-618 for IPv6. Verify with:

```text
show isis segment-routing label table
show mpls forwarding prefix 10.0.0.18/32
```

## IS-IS remains in Init with BFD

**Cause:** XRd Control Plane accepts the BFD CLI but does not create BFD
sessions on these virtual links.

**Solution:** remove `bfd fast-detect` from the XRd baseline and retain
LFA/per-prefix FRR. Practice BFD on a platform whose data plane supports it.

## SSH banner timeout

**Cause:** too many simultaneous sessions to the same XRd node.

**Solution:** reuse one connection per router for IPv4 and IPv6, and keep
`--workers` at `1` or `2` during startup and convergence.

## Containerlab reports that the lab already exists

Do not deploy another node with the same lab name through `--node-filter`.
Use `labctl`, which prevents simultaneous profiles. If only AUTO1 is missing,
follow the controlled procedure in `OPERATIONS.md`.

## AUTO1 cannot find Ansible or its collections

Check:

```bash
which ansible
ansible-galaxy collection list
echo "$ANSIBLE_COLLECTIONS_PATH"
```

The image installs shared collections under
`/usr/share/ansible/collections`.

## A link is Up/Up but does not pass traffic

Check both namespaces and then IOS XR:

```bash
docker exec clab-ccie-sp-master-P1 ip -br link
```

```text
show ipv4 interface brief
show ipv6 interface brief
show interfaces accounting
```

A hot-added veth can be visible in Linux without being attached to the XRd
data plane. Use `containerlab restart --node <node>`, never
`docker stop/start`, to preserve and restore links.

Additional common findings are recorded in
[`docs/TROUBLESHOOTING.md`](../../docs/TROUBLESHOOTING.md).
