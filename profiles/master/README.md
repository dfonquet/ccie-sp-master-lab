# Lab 1 — CCIE SP Master ISP

El perfil `master` es el laboratorio principal de servicios de un ISP. Está
pensado para practicar el blueprint de CCIE Service Provider y extenderlo con
operación realista: redundancia, automatización, AAA, RPKI, observabilidad y
pruebas de fallo.

![Topología del Lab 1](../../docs/topology.svg)

## Resumen

| Elemento | Implementación |
|---|---|
| Escala | 30 nodos y 47 enlaces |
| Core | P1–P8, dos planos longitudinales, rungs y diagonales |
| Edge | PE1–PE8 con doble conexión al core |
| Control plane | RR1/RR2 como RR y PCE redundantes |
| Clientes | CE1–CE9, C1/C2 |
| Automatización | AUTO1 |
| IGP | IS-IS Level 2 dual-stack |
| Transporte | SR-MPLS, SR-TE y base para TI-LFA |
| Servicios | L3VPN, L2VPN/EVPN, multicast y PE-CE |

La descripción completa de roles y grupos de enlaces está en
[`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md). El inventario
`inventory/nodes.csv` y `inventory/links.csv` es la fuente de verdad.

## Direccionamiento e identificadores

| Uso | Plan |
|---|---|
| Gestión | `10.201.255.0/24` |
| Loopback provider IPv4 | `10.0.0.<ID>/32` |
| Loopback provider IPv6 | `2001:db8:500:abcd::<ID>/128` |
| Loopback cliente IPv4 | `10.100.0.<ID>/32` |
| Loopback cliente IPv6 | `2001:db8:100::<ID>/128` |
| P2P provider IPv4 | `/31` desde `10.255.0.0/31` |
| P2P provider IPv6 | `2001:db8:1000:<link-id>::/127` |
| SRGB | `16000–23999` |

Los IDs 1–18 identifican P, PE y RR. El Prefix-SID IPv4 usa el ID; el
Prefix-SID IPv6 usa `600 + ID`, evitando la colisión observada en XRd.
Consulta la tabla completa en
[`docs/ADDRESSING.md`](../../docs/ADDRESSING.md).

## Cómo funciona

1. IS-IS Level 2 descubre la topología dual-stack y anuncia loopbacks.
2. SR-MPLS asigna un Node-SID estable a cada loopback provider.
3. RR1/RR2 eliminan la necesidad de un full mesh MP-BGP entre PEs.
4. Cada PE tiene dos caminos hacia el core; las métricas distinguen camino
   primario, rung y diagonal.
5. Los CE multihomed permiten practicar SoO, sham-links, BGP multipath,
   EVPN multihoming y fallos de acceso.
6. AUTO1 renderiza, aplica, verifica y respalda cambios de forma repetible.

## Prioridad de configuración

No se aplican servicios antes de estabilizar el transporte:

1. `00-base`: hostname, loopbacks y enlaces.
2. `10-isis`: IS-IS dual-stack.
3. `15-provider-standard`: estándar IPv6, LFA y SR.
4. `20-sr-mpls`: SRGB y Prefix-SIDs.
5. MP-BGP/RR y políticas.
6. L3VPN, L2VPN/EVPN, multicast y servicios de gestión.
7. Fallos controlados y validación de convergencia.

Use uno o dos nodos canario antes de expandir una fase:

```bash
python3 tools/apply_phase.py 10-isis --nodes P1,P3 --workers 1
python3 tools/validate_links.py --family both --workers 2
```

## Operación segura

```bash
./labctl status
./labctl deploy master
./labctl inspect master
./labctl destroy master
```

Sólo un perfil pesado puede estar activo. No use `--cleanup` salvo que quiera
eliminar también el estado persistente de los routers.

## Validación mínima

- 30/30 contenedores ejecutándose y sin OOM.
- Todos los enlaces directos pasan IPv4 e IPv6.
- Adyacencias IS-IS iguales al inventario.
- Loopbacks provider alcanzables dual-stack.
- Node-SIDs únicos e instalados.
- PEs con sesiones VPNv4/VPNv6 redundantes hacia RR1/RR2.
- Cero swap y al menos 12 GiB disponibles en la VM.

El runbook detallado está en
[`docs/VALIDATION.md`](../../docs/VALIDATION.md).

## Troubleshooting y referencias

- [Errores conocidos y soluciones](TROUBLESHOOTING.md)
- [Referencias Cisco y RFC](REFERENCES.md)
- [Operación general](../../OPERATIONS.md)
- [Automatización desde AUTO1](../../docs/AUTO1-SOURCE-OF-TRUTH.md)
