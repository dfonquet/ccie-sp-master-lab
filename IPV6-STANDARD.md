# Provider IPv6 and Control-Plane Standard

## Design decisions

The supplied configuration was used as the functional standard, while
preserving the working identifiers already assigned to this lab:

| Supplied example | Master-lab implementation | Reason |
|---|---|---|
| `Loopback600` | `Loopback0` | Keeps every deployed IPv4 router ID unchanged |
| IS-IS `500-SP` | IS-IS `CORE` | Avoids replacing a healthy IGP instance |
| IPv4 example addresses | Existing `10.0.0.0/32` and `10.255.0.0/31` plan | Explicitly protected |
| IPv6 loopback block | `2001:db8:500:abcd::/64` | Matches the requested convention |
| IPv6 core link block | `2001:db8:1000:<link-id>::/127` | Deterministic P/PE/RR addressing |

## Common P, PE and RR/PCE behavior

- Login banner and consistent loopback descriptions.
- IS-IS Level 2 only with wide metrics.
- Dual-stack single topology.
- Passive-prefix advertisement control.
- Point-to-point circuits with disabled hello padding.
- Per-prefix LFA/FRR for IPv4 and IPv6.
- SR-MPLS preferred for IPv4 and enabled for IPv6.
- Separate deterministic IPv4 and IPv6 Prefix-SID ranges.
- SRGB `16000-23999`.
- MPLS traffic-engineering extensions and SR-TE hierarchy.

## Address plan

```text
P1-P6:    2001:db8:500:abcd::1-6/128
PE1-PE6:  2001:db8:500:abcd::7-12/128
RR1-RR2:  2001:db8:500:abcd::13-14/128

L001-L025:
2001:db8:1000:101::/127 through
2001:db8:1000:125::/127

IPv4 Prefix-SID indexes: 1-14     (labels 16001-16014)
IPv6 Prefix-SID indexes: 601-614  (labels 16601-16614)
```

`inventory/links.csv` is authoritative for the exact endpoint assignments.

The supplied example reuses one Prefix-SID index for both address families.
XRd 24.2.11 rejects that as a duplicate nodal SID, so this lab uses the
separate IPv6 range above while preserving every existing IPv4 SID.

## XRd BFD boundary

The supplied configuration enables IS-IS BFD for IPv4 and IPv6. XRd Control
Plane 24.2.11 accepts the commands but does not instantiate BFD sessions on
these virtual links; enabling them leaves the IS-IS three-way state in `Init`.
The active XRd baseline therefore removes `bfd fast-detect` and retains
per-prefix LFA/FRR. BFD drills should use the IOL nodes, an XRv9k data-plane
image, or physical IOS XR equipment.

## SR-MPLS IPv6 versus SRv6

This baseline configures SR-MPLS control-plane support for IPv6 prefixes. It
does not yet turn the IPv6 IS-IS address family into an SRv6 locator domain.
IOS XR supports either SR-MPLS or SRv6 for one IS-IS address family at a time,
so the future SRv6 exercise must be a deliberate alternate phase that removes
`segment-routing mpls` from the IPv6 AF before adding SRv6 locators.
