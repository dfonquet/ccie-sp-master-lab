# Addressing and identifiers

## Management

```text
Docker network: ccie-sp-master-mgmt
Subnet:         10.201.255.0/24
Windows route:  10.201.255.0/24 via 192.168.192.10
AUTO1:          10.201.255.150
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

IPv4 Prefix-SID indexes: 1-14
IPv4 labels:             16001-16014

IPv6 Prefix-SID indexes: 601-614
IPv6 labels:             16601-16614
```
