# Troubleshooting — Lab 1 Master

## Prefix-SID duplicado

**Síntoma:** `Nodal sid is already in use`.

**Causa:** XRd 24.2.11 rechazó reutilizar el mismo índice para IPv4 e IPv6.

**Solución:** IDs 1–18 para IPv4 y 601–618 para IPv6. Verifique con:

```text
show isis segment-routing label table
show mpls forwarding prefix 10.0.0.18/32
```

## IS-IS permanece en Init con BFD

**Causa:** XRd Control Plane acepta el CLI de BFD, pero no crea sesiones BFD
en estos enlaces virtuales.

**Solución:** retire `bfd fast-detect` del baseline XRd y conserve
LFA/per-prefix FRR. Practique BFD en una plataforma cuyo dataplane lo soporte.

## Timeout del banner SSH

**Causa:** demasiadas sesiones simultáneas contra el mismo XRd.

**Solución:** reutilizar una conexión por router para IPv4/IPv6 y mantener
`--workers 1` o `2` durante arranque y convergencia.

## Containerlab indica que el lab ya existe

No despliegue otro nodo con el mismo nombre de lab mediante `--node-filter`.
Use `labctl`, que impide dos perfiles simultáneos. Si sólo AUTO1 falta, siga el
procedimiento controlado de `OPERATIONS.md`.

## AUTO1 no encuentra Ansible o colecciones

Compruebe:

```bash
which ansible
ansible-galaxy collection list
echo "$ANSIBLE_COLLECTIONS_PATH"
```

La imagen instala las colecciones compartidas bajo
`/usr/share/ansible/collections`.

## Un enlace aparece Up/Up pero no pasa tráfico

Compruebe ambos namespaces y luego IOS XR:

```bash
docker exec clab-ccie-sp-master-P1 ip -br link
```

```text
show ipv4 interface brief
show ipv6 interface brief
show interfaces accounting
```

Un veth agregado en caliente puede ser visible en Linux pero no quedar unido
al dataplane XRd. Use `containerlab restart --node <nodo>`, nunca
`docker stop/start`, para conservar y restaurar enlaces.

Los hallazgos comunes adicionales están en
[`docs/TROUBLESHOOTING.md`](../../docs/TROUBLESHOOTING.md).
