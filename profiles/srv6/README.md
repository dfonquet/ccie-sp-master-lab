# SRv6 capability profile

This profile determines what `ios-xr/xrd-control-plane:24.2.11` actually
supports before a full SRv6 lab is designed. It is not evidence that the image
provides SRv6 packet forwarding merely because commands parse or commit.

## Scope

- P1, P2 and PE1 running IOS XRd Control Plane.
- IPv6-only IS-IS Level 2 underlay.
- One /64 SRv6 locator per node from the common `2001:db8:600::/40` block.
- Dedicated management network `10.203.255.0/24`.
- One-node P1 canary before the three-node capability deployment.
- No CE service, SRv6-TE policy, uSID or resiliency claim at this stage.

## Generated artifacts

| Artifact | Purpose |
|---|---|
| `nodes.csv` | Node, management, loopback and locator Source of Truth |
| `links.csv` | Interface and IPv6 /127 Source of Truth |
| `../../topology/ccie-sp-srv6.clab.yml` | Containerlab topology |
| `../../configs/srv6/00-canary/` | Link-independent one-node baseline |
| `../../configs/srv6/00-base/` | IPv6 loopbacks and interfaces |
| `../../configs/srv6/10-isis-ipv6/` | IS-IS Level 2 IPv6 underlay |
| `../../configs/srv6/20-srv6-locator/` | Experimental locator and IS-IS advertisement phase |

Regenerate and validate without deploying:

```bash
python3 tools/build_srv6_capability.py
python3 tools/validate_srv6_artifacts.py
git diff --exit-code
```

## Controlled canary

Confirm `./labctl status` returns no nodes. Then deploy only P1:

```bash
./labctl canary srv6
python3 tools/validate_nodes.py --inventory profiles/srv6/nodes.csv --nodes P1 --workers 1
python3 tools/backup_provider.py --inventory profiles/srv6/nodes.csv --nodes P1 --workers 1 --label before-srv6-canary
python3 tools/apply_phase.py 00-canary --profile srv6 --nodes P1 --workers 1
python3 tools/apply_phase.py 20-srv6-locator --profile srv6 --nodes P1 --workers 1
```

Do not apply `00-base` or `10-isis-ipv6` in the one-node canary. Node filtering
omits the peer links, so only the link-independent `00-canary` phase is valid.

Destroy the canary after evidence collection:

```bash
./labctl destroy srv6
```

## Capability classification

Every tested feature receives exactly one classification:

1. `UNSUPPORTED_PARSER`
2. `UNSUPPORTED_COMMIT`
3. `CONTROL_PLANE_ONLY`
4. `DATA_PLANE_SUPPORTED`
5. `NOT_TESTED`

Proceed to the three-node profile only if management, base IPv6, locator parser,
commit, rollback and restart gates pass. See [ACCEPTANCE.md](ACCEPTANCE.md).
