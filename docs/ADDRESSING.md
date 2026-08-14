# Addressing and identifiers

## Management

```text
Docker network: ccie-sp-master-mgmt
Subnet:         10.201.255.0/24
Windows route:  10.201.255.0/24 via 192.168.192.10
AUTO1:          10.201.255.150
ISP-2 planned:  10.201.255.151-158
```

Management addresses for every node are recorded in `inventory/nodes.csv`.

## Provider loopbacks

```text
IPv4: 10.0.0.<node-id>/32
IPv6: 2001:db8:500:abcd::<node-id>/128
```

Node IDs:

```text
P1-P6      -> 1-6
PE1-PE6    -> 7-12
P7-P8      -> 15-16
PE7-PE8    -> 17-18
RR1-RR2    -> 13-14
```

## Customer loopbacks

```text
IPv4: 10.100.0.<node-id>/32
IPv6: 2001:db8:100::<node-id>/128
```

## ISP-2 loopbacks (offline structural plan)

ISP-2 is AS65002 and remains separate from the AS500 IS-IS/SR-MPLS domain.

| Node | IPv4 / OSPF router ID | IPv6 |
|---|---|---|
| ASBR-ISP2 | `10.65.2.1/32` | `2001:db8:6502::1/128` |
| ISP2-P1 | `10.65.2.2/32` | `2001:db8:6502::2/128` |
| ISP2-P2 | `10.65.2.3/32` | `2001:db8:6502::3/128` |
| ISP2-P3 | `10.65.2.4/32` | `2001:db8:6502::4/128` |
| ISP2-P4 | `10.65.2.5/32` | `2001:db8:6502::5/128` |
| ISP2-P5 | `10.65.2.6/32` | `2001:db8:6502::6/128` |
| RR-ISP2 | `10.65.2.7/32` | `2001:db8:6502::7/128` |

The ISP-2 IPv6 loopback allocation belongs to `2001:db8:6502::/48`.

## Point-to-point links

Provider IPv4 links use consecutive `/31` networks beginning at:

```text
10.255.0.0/31
```

Provider IPv6 links L001-L025 use:

```text
2001:db8:1000:101::/127
...
2001:db8:1000:125::/127
```

Customer/access IPv6 links keep their separate deterministic
`2001:db8:0:<link-id>::/127` plan.

The authoritative endpoint-level table is `inventory/links.csv`.

The offline ISP-2 expansion continues the point-to-point plan with L048-L057:

```text
IPv4: 10.255.0.94/31 through 10.255.0.112/31
IPv6: 2001:db8:1000:148::/127 through 2001:db8:1000:157::/127
```

These links are declared structurally but are not active yet. L048 is excluded
from ISP-1 IS-IS/SR-MPLS. ISP-2 OSPFv2/OSPFv3 configuration is manual.

## IS-IS

```text
Instance: CORE
Level:    Level 2 only
Area:     49.0001
```

NETs follow:

```text
49.0001.0000.0000.<node-id>.00
```

## Segment Routing

```text
SRGB: 16000-23999

IPv4 Prefix-SID indexes: 1-18
IPv4 labels:             16001-16018

IPv6 Prefix-SID indexes: 601-618
IPv6 labels:             16601-16618
```
