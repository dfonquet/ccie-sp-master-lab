# Direccionamiento — Lab 2 Inter-AS

Los CSV generados son la fuente de verdad:

- `profiles/inter-as/nodes.csv`
- `profiles/inter-as/links.csv`

## Gestión

```text
Red:        10.202.255.0/24
Gateway:    10.202.255.1
AUTO1:      10.202.255.250
AS500:      10.202.255.101-114 y .150
AS65100:    10.202.255.105/.107/.115/.117/.151
AS65200:    10.202.255.106/.108/.116/.118/.152
CE-A/B/C:   10.202.255.201-203
```

## Loopbacks

| Dominio | IPv4 | IPv6 |
|---|---|---|
| AS500 | `10.50.0.<ID>/32` | `2001:db8:500::<ID>/128` |
| AS65100 | `10.65.100.<ID>/32` | `2001:db8:6510::<ID>/128` |
| AS65200 | `10.65.200.<ID>/32` | `2001:db8:6520::<ID>/128` |
| Clientes | `10.200.0.<ID>/32` | `2001:db8:ce::<ID>/128` |

Los RRs usan IDs 50, 51 y 52. Cada loopback es el router ID y origen de iBGP.

## Enlaces

Los 35 enlaces usan `/31` y `/127` consecutivos:

```text
IPv4: 10.240.0.0/31 ... 10.240.0.68/31
IPv6: 2001:db8:2400:1::/127 ... 2001:db8:2400:23::/127
```

En cada fila de `links.csv`, endpoint A recibe la primera dirección y endpoint
B la segunda. Esto hace que la topología sea reproducible sin IPAM externo.

## Enlaces Inter-AS

| ID | Interconexión | IPv4 | IPv6 |
|---|---|---|---|
| IAS025 | P3–P5 | `10.240.0.48/31` | `2001:db8:2400:19::/127` |
| IAS026 | P4–P7 | `10.240.0.50/31` | `2001:db8:2400:1a::/127` |
| IAS027 | P3–P6 | `10.240.0.52/31` | `2001:db8:2400:1b::/127` |
| IAS028 | P4–P8 | `10.240.0.54/31` | `2001:db8:2400:1c::/127` |
| IAS029 | P7–P8 | `10.240.0.56/31` | `2001:db8:2400:1d::/127` |

## Identificadores de protocolo

| Dominio | IGP | Proceso | Router ID |
|---|---|---|---|
| AS500 | IS-IS L2 | `AS500` | Loopback IPv4 |
| AS65100 | OSPFv2/OSPFv3 | `65100` | Loopback IPv4 |
| AS65200 | OSPFv2/OSPFv3 | `65200` | Loopback IPv4 |

IOS XR en este lab usa OSPFv2 para IPv4 y OSPFv3 para IPv6. Esto coincide con
el soporte documentado por Cisco para IOS XR.
