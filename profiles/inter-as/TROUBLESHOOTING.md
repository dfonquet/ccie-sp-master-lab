# Troubleshooting — Lab 2 Inter-AS

Este registro conserva errores encontrados durante el despliegue real y la
forma segura de resolverlos.

## Faltan enlaces después del deploy

**Síntoma:** el contenedor está running, pero faltan `eth1/eth2` o interfaces
`Gi0-0-0-x`.

**Diagnóstico:**

```bash
docker exec clab-ccie-sp-inter-as-CE-C ip -br link
sudo containerlab apply -t topology/ccie-sp-inter-as.clab.yml --dry-run
```

Use siempre el `dry-run`. Si el plan recrea nodos adicionales, calcule el
impacto y use `--max-workers 1`.

## XRd muestra Up/Up, pero no reenvía

Un veth agregado en caliente puede aparecer en Linux y IOS XR sin quedar
operativo en el dataplane. Reinicie el nodo afectado con Containerlab:

```bash
sudo containerlab restart \
  -t topology/ccie-sp-inter-as.clab.yml \
  --node P5
```

No use `docker stop/start`: Containerlab debe aparcar y restaurar los veth.

## IOL queda en “System Configuration Dialog”

La NVRAM vacía puede tener prioridad sobre `boot_config.txt`. Conserve una
copia, limpie sólo la NVRAM del CE afectado y use el ciclo de vida de
Containerlab. Nunca use `--cleanup` para todo el lab.

Compruebe después:

```text
show ip interface brief
show ip route vrf clab-mgmt
ping vrf clab-mgmt 10.202.255.1
```

## OSPFv3 IPv4 rechazado

XRd 24.2.11 no dejó `address-family ipv4` dentro de `router ospfv3`.
La implementación validada usa:

- `router ospf <ASN>` para IPv4.
- `router ospfv3 <ASN>` para IPv6.

Además, `area 0` es hermana de `address-family ipv6`, no hija de la AF.

## `exit` rompe una jerarquía IOS XR

En varios submodos XR, `exit` vuelve a configuración global. El aplicador
reingresa el path completo para cada comando XR. Si aparece `% Invalid input`,
ejecute un canario y revise `show configuration failed` antes de expandir.

## Route-policy deja la sesión en el editor RPL

`route-policy ... end-policy` debe enviarse como un bloque atómico. No inserte
`root` dentro del editor RPL.

## BGP: “The address family has not been initialized”

Inicialice la AF global antes de asociarla al vecino:

```text
router bgp <ASN>
 address-family ipv4 unicast
 address-family ipv6 unicast
```

IOS XR también exige route-policy de entrada y salida para eBGP.

## Falso negativo en resumen BGP IPv6

IOS XR parte las filas IPv6 largas en dos líneas. Un parser que busque todos
los campos en la línea de la dirección reportará `FAIL`. Valide con:

```text
show bgp ipv6 unicast neighbors <peer>
```

La prueba correcta busca `BGP state = Established`.
