# Addressing — Lab 2 Inter-AS

The generated CSV files are the source of truth:

- `profiles/inter-as/nodes.csv`
- `profiles/inter-as/links.csv`

## Management

```text
Network:    10.202.255.0/24
Gateway:    10.202.255.1
AUTO1:      10.202.255.250
AS500:      10.202.255.101-114 and .150
AS65100:    10.202.255.105/.107/.115/.117/.151
AS65200:    10.202.255.106/.108/.116/.118/.152
CE-A/B/C:   10.202.255.201-203
```

## Loopbacks

| Domain | IPv4 | IPv6 |
|---|---|---|
| AS500 | `10.50.0.<ID>/32` | `2001:db8:500::<ID>/128` |
| AS65100 | `10.65.100.<ID>/32` | `2001:db8:6510::<ID>/128` |
| AS65200 | `10.65.200.<ID>/32` | `2001:db8:6520::<ID>/128` |
| Customers | `10.200.0.<ID>/32` | `2001:db8:ce::<ID>/128` |

The RRs use IDs 50, 51, and 52. Each loopback is used as the router ID and
iBGP source.

## Links

The 35 links use sequential `/31` and `/127` networks:

```text
IPv4: 10.240.0.0/31 ... 10.240.0.68/31
IPv6: 2001:db8:2400:1::/127 ... 2001:db8:2400:23::/127
```

In every `links.csv` row, endpoint A receives the first address and endpoint B
receives the second. This makes the topology reproducible without an external
IPAM system.

## Inter-AS links

| ID | Interconnection | IPv4 | IPv6 |
|---|---|---|---|
| IAS025 | P3-P5 | `10.240.0.48/31` | `2001:db8:2400:19::/127` |
| IAS026 | P4-P7 | `10.240.0.50/31` | `2001:db8:2400:1a::/127` |
| IAS027 | P3-P6 | `10.240.0.52/31` | `2001:db8:2400:1b::/127` |
| IAS028 | P4-P8 | `10.240.0.54/31` | `2001:db8:2400:1c::/127` |
| IAS029 | P7-P8 | `10.240.0.56/31` | `2001:db8:2400:1d::/127` |

## Protocol identifiers

| Domain | IGP | Process | Router ID |
|---|---|---|---|
| AS500 | IS-IS L2 | `AS500` | IPv4 loopback |
| AS65100 | OSPFv2/OSPFv3 | `65100` | IPv4 loopback |
| AS65200 | OSPFv2/OSPFv3 | `65200` | IPv4 loopback |

IOS XR in this lab uses OSPFv2 for IPv4 and OSPFv3 for IPv6, matching the
documented Cisco IOS XR implementation.
