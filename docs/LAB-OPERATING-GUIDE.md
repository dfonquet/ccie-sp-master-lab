# Guía profesional de operación del CCIE SP Master Lab

Esta es la guía de entrada para comprender, desplegar, validar, modificar y
recuperar el laboratorio. El repositorio no es solamente un conjunto de
topologías: implementa un flujo reproducible donde inventarios y generadores
producen configuraciones, diagramas y archivos de Containerlab verificables.

## 1. Objetivo

El proyecto permite practicar el blueprint de CCIE Service Provider y
escenarios más cercanos a una red real sin encender varios laboratorios pesados
simultáneamente.

| Perfil | Estado | Propósito |
|---|---|---|
| `master` | Ejecutable y validado | Backbone ISP redundante, SR-MPLS, RR/PCE, VPN, multicast, EVPN, AAA y RPKI |
| `inter-as` | Ejecutable y validado | Tres sistemas autónomos, varios IGP, eBGP y Options A/B/C |
| `srv6` | Diseño aprobado | Locators, SRv6, políticas y servicios IPv6-first |

La regla operativa principal es sencilla: **solo un perfil pesado puede estar
activo a la vez**. Así se conserva RAM para XRd, se evitan nombres y redes
solapadas y cada práctica empieza desde un estado conocido.

## 2. Cómo está organizado el repositorio

```text
ccie-sp-master-lab/
├── README.md                    Portada y estado resumido
├── labctl                       Control seguro del ciclo de vida
├── inventory/                   Inventario autoritativo del Lab 1
├── profiles/
│   ├── master/                  Diseño y manual específico del Lab 1
│   ├── inter-as/                Inventarios y manual del Lab 2
│   └── srv6/                    Diseño del futuro Lab 3
├── tools/                       Generadores y validadores
├── templates/                   Plantillas Jinja2
├── configs/                     Configuraciones renderizadas por fases
├── topology/                    Topologías Containerlab generadas
├── automation/                  Imagen y ejemplos para AUTO1
└── docs/                        Arquitectura, operación y troubleshooting
```

Los documentos específicos están en:

- [Lab 1 — Master ISP](../profiles/master/README.md)
- [Lab 2 — Inter-AS](../profiles/inter-as/README.md)
- [Estado de aceptación](../STATUS.md)
- [Matriz del blueprint](../BLUEPRINT-MATRIX.md)

## 3. Fuente de verdad y flujo de cambios

El diseño sigue esta cadena:

```text
Inventarios + generador + plantillas
                 ↓
      configuraciones renderizadas
                 ↓
       topología Containerlab
                 ↓
      despliegue y validación
```

Para `master`, la fuente principal está en `tools/build_lab.py`,
`inventory/nodes.csv` e `inventory/links.csv`. Para `inter-as`, se utiliza
`tools/build_inter_as.py`, `profiles/inter-as/nodes.csv` y
`profiles/inter-as/links.csv`.

No se deben editar manualmente los archivos generados para hacer permanente un
cambio. La modificación correcta se realiza en el inventario, generador o
plantilla; después se renderiza y se revisa el diff. Esto mantiene alineados:

- Diagrama.
- Topología.
- Direccionamiento.
- Descripciones de interfaces.
- Configuraciones por fase.
- Documentación.

## 4. Perfiles y arquitectura

### 4.1 Lab 1 — Master ISP

El Lab 1 contiene 30 nodos y 47 enlaces:

- P1-P8: routers de tránsito.
- PE1-PE8: borde del proveedor y terminación de servicios.
- RR1-RR2: Route Reflectors redundantes y PCE.
- CE1-CE9 y C1-C2: clientes y extremos para pruebas.
- AUTO1: estación Ubuntu de automatización.

Su underlay usa IS-IS Level 2 dual-stack y SR-MPLS. La separación entre
underlay, RR/iBGP y servicios permite practicar fallos sin mezclar causas.
Consulte el [diagrama y direccionamiento del Master](../profiles/master/README.md).

### 4.2 Lab 2 — Inter-AS

El Lab 2 contiene 23 nodos y 35 enlaces distribuidos así:

- AS500: IS-IS dual-stack, RR500 y cuatro P/ASBR más cuatro PE.
- AS65100: OSPFv2/OSPFv3, RR65100, dos P/ASBR y dos PE.
- AS65200: OSPFv2/OSPFv3, RR65200, dos P/ASBR y dos PE.
- Cinco enlaces externos permiten practicar política y diversidad física.
- Tres CE permiten validar servicios extremo a extremo.

La topología y las redes exactas están en:

- [Operación Inter-AS](../profiles/inter-as/README.md)
- [Direccionamiento Inter-AS](../profiles/inter-as/ADDRESSING.md)
- [Diseño y opciones](../profiles/inter-as/DESIGN.md)

## 5. Direccionamiento

Cada perfil tiene una red de gestión independiente y direccionamiento de datos
propio. No se deben reutilizar direcciones de gestión entre perfiles activos.

En `master`:

```text
Gestión:             10.201.255.0/24
Loopbacks IPv4:      10.0.0.<id>/32
Enlaces IPv4:        10.255.0.0/31 en adelante
Loopbacks IPv6:      2001:db8:500:abcd::<id>/128
Enlaces IPv6 core:   2001:db8:1000:<id-enlace>::/127
```

Los prefijos `/31` y `/127` representan enlaces punto a punto y evitan
desperdicio de direcciones. Los loopbacks permanecen estables y sirven como
router-id, endpoint BGP, Prefix-SID y destino de pruebas de convergencia.

## 6. Preparación del servidor

Antes de desplegar:

```bash
cd /srv/netlab/labs/ccie-sp-master
docker ps --format '{{.Names}}' | grep '^clab-ccie-sp-' || \
  echo "No hay labs activos"
free -h
uptime
df -h /srv/netlab
./labctl status
```

No despliegue si existe otro `clab-ccie-sp-*`, hay swap activa, la memoria
disponible está por debajo del gate del perfil o el host mantiene una carga
anormal. El gate recomendado para Inter-AS es un mínimo de 12 GiB disponibles.

## 7. Generación reproducible

### Master

```bash
python3 tools/build_lab.py
python3 tools/render_topology.py
```

### Inter-AS

```bash
python3 tools/build_inter_as.py
python3 tools/render_inter_as.py
```

Después de generar:

```bash
git status --short
git diff --check
git diff -- inventory profiles topology configs docs
```

Un cambio inesperado en numerosos archivos suele indicar que se modificó una
regla global. Revise el diff antes de aplicar configuraciones.

## 8. Ciclo de vida seguro

### Consultar el estado

```bash
./labctl status
```

### Desplegar un perfil

```bash
./labctl deploy master
# o, con el Master destruido:
./labctl deploy inter-as
```

`labctl` rechaza el despliegue cuando detecta otro perfil activo.

### Inspeccionar

```bash
./labctl inspect master
./labctl inspect inter-as
```

### Destruir

```bash
./labctl destroy master
# o:
./labctl destroy inter-as
```

Destruir un lab elimina sus contenedores y enlaces efímeros. Las fuentes,
configuraciones generadas y documentación permanecen en el repositorio.

## 9. Aplicación de configuraciones por fases

Nunca aplique todo de una vez. Primero use uno o dos nodos canario, valide y
después amplíe la misma fase.

Ejemplo para Inter-AS:

```bash
python3 tools/apply_phase.py 00-base \
  --profile inter-as --nodes P1,P3

python3 tools/apply_phase.py 10-igp \
  --profile inter-as --nodes P1,P3

python3 tools/apply_phase.py 20-bgp \
  --profile inter-as --nodes P3,RR500
```

Orden operativo:

1. `00-base`: hostname, loopbacks, interfaces y direccionamiento.
2. IGP: IS-IS u OSPF según el dominio.
3. Transporte: SR-MPLS, labels y reachability de loopbacks.
4. iBGP/RR: familias requeridas y redundancia.
5. eBGP: sesiones externas y políticas explícitas.
6. Servicios: L3VPN, L2VPN/EVPN, multicast o Inter-AS.
7. Seguridad y assurance: AAA, RPKI, telemetría y pruebas.
8. Fallos: convergencia, rollback y recuperación.

Esta prioridad evita diagnosticar BGP cuando el problema real está en una
interfaz, el IGP o la reachability del next-hop.

## 10. Validación

### Estado de nodos

```bash
python3 tools/validate_nodes.py \
  --inventory profiles/inter-as/nodes.csv --workers 4
```

### Enlaces directamente conectados

```bash
python3 tools/validate_links.py \
  --profile inter-as --family both --workers 2
```

### Verificaciones de control plane

En IOS XR:

```text
show interfaces brief
show route ipv4
show route ipv6
show isis adjacency
show ospf neighbor
show ospfv3 neighbor
show bgp summary
show bgp vpnv4 unicast summary
show bgp vpnv6 unicast summary
show mpls forwarding
```

La salida esperada depende del perfil y la fase. Compare siempre contra el
inventario, no contra un número memorizado de otra topología.

La línea base Inter-AS actualmente validada es:

- 23/23 nodos.
- 70/70 pruebas direccionales IPv4/IPv6.
- Conteos IS-IS, OSPFv2 y OSPFv3 acordes con el inventario.
- iBGP RR 6/6, 4/4 y 4/4 por familia VPN.
- eBGP 10/10 extremos IPv4 y 10/10 IPv6.

## 11. Práctica Inter-AS

Conserve un snapshot lógico conocido antes de cada opción:

1. Valide interfaces, loopbacks, IGP e iBGP.
2. Configure eBGP IPv4/IPv6 y políticas de prefijos/comunidades.
3. Practique Option A y documente VRF, RD, RT y rutas PE-CE.
4. Retire Option A o restaure la base.
5. Practique Option B con VPNv4/VPNv6 entre ASBR.
6. Restaure la base.
7. Practique Option C con labeled-unicast y MP-BGP multihop.
8. Introduzca fallos de enlace, RR y ASBR individualmente.
9. Registre estado anterior, hipótesis, comandos y resultado.

No mezcle Options A, B y C durante la primera validación. El objetivo es
entender qué información intercambia cada modelo y dónde vive el control plane.

## 12. AUTO1 y sincronización

AUTO1 ejecuta Ansible, Python, pyATS/Genie, Netmiko, Nornir, Scrapli, NETCONF y
gNMI. El flujo recomendado es:

1. Sincronizar o montar el repositorio en AUTO1.
2. Cambiar inventario, variables o plantillas.
3. Renderizar.
4. Revisar el diff.
5. Ejecutar check-mode o pre-check.
6. Aplicar a canarios.
7. Ejecutar post-check.
8. Aplicar al resto del alcance.
9. Confirmar solamente fuentes reproducibles en Git.

La explicación detallada está en
[AUTO1 Source of Truth](AUTO1-SOURCE-OF-TRUTH.md).

## 13. Troubleshooting y recuperación

Diagnostique de abajo hacia arriba:

```text
contenedor → interfaz → direccionamiento → IGP → labels/next-hop
→ iBGP/RR → eBGP/política → VPN/servicio
```

Errores ya documentados:

- Lab ya desplegado con el mismo nombre.
- Enlace añadido que obliga a recrear un nodo XRd/IOL.
- Interfaces IOL en `administratively down`.
- Diálogo inicial o NVRAM de IOL.
- Limitaciones BFD de XRd Control Plane.
- Colisión de Prefix-SID IPv4/IPv6.
- OSPFv2/OSPFv3 aplicado a una familia incorrecta.
- Política RPL ausente que bloquea BGP.
- Sesión BGP sin la address-family activada.
- Falsos negativos en validadores IPv6.

Consulte:

- [Troubleshooting general](TROUBLESHOOTING.md)
- [Troubleshooting Master](../profiles/master/TROUBLESHOOTING.md)
- [Troubleshooting Inter-AS](../profiles/inter-as/TROUBLESHOOTING.md)

## 14. Flujo Git profesional

Desde AUTO1 o el servidor:

```bash
git status --short --branch
git pull --ff-only
git switch -c agent/nombre-del-cambio
```

Después de modificar y validar:

```bash
git diff --check
git status --short
git add <archivos-del-cambio>
git commit -m "Descripción breve y concreta"
git push -u origin agent/nombre-del-cambio
```

No incluya imágenes Cisco, claves privadas, contraseñas, tokens, backups de
configuración con secretos ni artefactos pesados. Revise
[`SECURITY.md`](../SECURITY.md) y `.gitignore` antes de publicar.

## 15. Criterio de finalización

Una práctica se considera completa cuando:

- El perfil correcto es el único activo.
- El host mantiene memoria, CPU y swap dentro del gate.
- La fuente de verdad reproduce los archivos generados.
- Enlaces, IGP y BGP cumplen el inventario.
- El servicio funciona de extremo a extremo.
- El fallo y el rollback fueron probados.
- La documentación refleja el estado real.
- Git no contiene secretos ni binarios propietarios.

Las referencias técnicas oficiales de cada perfil están en
[Master REFERENCES](../profiles/master/REFERENCES.md) e
[Inter-AS REFERENCES](../profiles/inter-as/REFERENCES.md).
