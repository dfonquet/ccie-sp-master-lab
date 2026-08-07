# XRd Eight Addressing Plan

The CSV files are authoritative: [nodes.csv](nodes.csv) and [links.csv](links.csv).

## Address blocks

| Purpose | Allocation |
|---|---|
| Management | `10.207.255.0/24` |
| Provider loopbacks | `10.70.0.<node-id>/32` |
| Provider IPv6 loopbacks | `2001:db8:570:abcd::<node-id>/128` |
| Provider links | sequential `/31` from `10.70.255.0/24` |
| Provider IPv6 links | `2001:db8:1700:<link>::/127` |
| Customer exercise links | sequential `/31` from `10.71.255.0/24` |
| Customer IPv6 links | `2001:db8:2700:<link>::/127` |
| IS-IS process / area | `500-SP` / `49.0001` |
| SRGB | `16000-23999` |
| IPv4 Prefix-SID index | node ID `1-8` |
| IPv6 Prefix-SID index | `600 + node ID`, producing `601-608` |

## Node addressing

| Node | Role | Management | IPv4 loopback | IPv6 loopback |
|---|---|---|---|---|
| XR1 | P1 | `10.207.255.101` | `10.70.0.1/32` | `2001:db8:570:abcd::1/128` |
| XR2 | P2 | `10.207.255.102` | `10.70.0.2/32` | `2001:db8:570:abcd::2/128` |
| R1 | P3 | `10.207.255.104` | `10.70.0.4/32` | `2001:db8:570:abcd::4/128` |
| R3 | P4 | `10.207.255.106` | `10.70.0.6/32` | `2001:db8:570:abcd::6/128` |
| R5 | PE1 | `10.207.255.107` | `10.70.0.7/32` | `2001:db8:570:abcd::7/128` |
| XR4 | PE2 | `10.207.255.108` | `10.70.0.8/32` | `2001:db8:570:abcd::8/128` |
| XR3 | PE3 | `10.207.255.103` | `10.70.0.3/32` | `2001:db8:570:abcd::3/128` |
| R2 | RR/PCE/RP | `10.207.255.105` | `10.70.0.5/32` | `2001:db8:570:abcd::5/128` |
| R4 | CE1 | `10.207.255.141` | student work | student work |
| R7 | CE2 | `10.207.255.143` | student work | student work |
| R10 | CE3 | `10.207.255.146` | student work | student work |
| AUTO1 | Operations | `10.207.255.150` | n/a | n/a |

## Link addressing

All 20 endpoint/interface/address assignments are maintained in [links.csv](links.csv). Links L001-L014 are provider links. Links L015-L020 are intentionally unconfigured customer service edges in the generated startup baseline.
