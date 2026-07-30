# AUTO1: Source of Truth y automatización BGP

Este módulo formaliza el flujo construido en `AUTO1` para RR2 y los seis PE:

```text
Source of Truth → Jinja2 → Render → Validate → Check/Diff
                → Deploy controlado → Post-check BGP
```

La implementación proviene de los archivos utilizados realmente en
`Automation-Notes/LAB-Container`. Se normalizaron sus nombres y carpetas para
evitar duplicados: `group_vars-pe.yml` pasó a
`inventory/group_vars/pe.yml`, `host_varsRR2.yml` a
`inventory/host_vars/RR2.yml`, y los archivos prefijados con
`playbooks-`/`templates-` están ahora en sus directorios nativos.

Los datos viven junto al inventario en `automation/inventory/group_vars/` y
`automation/inventory/host_vars/`, para que Ansible los cargue automáticamente. Las
plantillas están en `automation/templates/`. `rendered/` contiene candidatos
locales y está excluido de Git: se versionan las fuentes, no sus derivados.

## Qué ya tenía AUTO1

La imagen reproducible ya incluía Ansible, las colecciones Cisco IOS/IOS XR,
Python, Jinja2, pyATS/Genie, Netmiko, Nornir, Scrapli, ncclient y pyGNMI.
También existían inventario, prechecks y backups. Este módulo añade el ciclo
de cambio BGP basado en datos, plantillas y controles previos.

## Ejecución desde `/workspace/automation`

```bash
ansible-inventory -i inventory/hosts.yml --host RR2
ansible-inventory -i inventory/hosts.yml --host PE1

ansible-playbook -i inventory/hosts.yml playbooks/validate_bgp_data.yml
ansible-playbook -i inventory/hosts.yml playbooks/validate_pe_loopbacks.yml
ansible-playbook -i inventory/hosts.yml playbooks/discover_loopbacks.yml
ansible-playbook -i inventory/hosts.yml playbooks/render_rr2_bgp.yml
ansible-playbook -i inventory/hosts.yml playbooks/render_pe_bgp.yml

cat rendered/RR2_bgp.cfg
grep -H "bgp router-id" rendered/PE*_bgp.cfg

ansible-playbook -i inventory/hosts.yml playbooks/check_rr2_bgp.yml --check --diff
ansible-playbook -i inventory/hosts.yml playbooks/check_pe_bgp.yml --check --diff
```

Hasta aquí no debe existir ningún cambio real. Tras la revisión humana:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_rr2_bgp.yml \
  --diff -e deploy_confirm=true
ansible-playbook -i inventory/hosts.yml playbooks/deploy_pe_bgp.yml \
  --diff -e deploy_confirm=true
ansible-playbook -i inventory/hosts.yml playbooks/postcheck_bgp.yml
```

El diseño conserva los valores comprobados en el lab: AS 500, RR2
`10.0.0.14`, cluster ID `10.0.0.100`, PE1–PE6 `10.0.0.7–12` y
`Loopback0` como update-source. Los PE se despliegan con `serial: 1`; ambos
playbooks exigen confirmación explícita y crean backup.

## Encendido y apagado

```bash
cd /srv/netlab/labs/ccie-sp-master/topology
sudo containerlab deploy -t ccie-sp-master.clab.yml
sudo containerlab destroy -t ccie-sp-master.clab.yml
sudo docker ps -a --filter "name=clab-ccie-sp-master"
sudo shutdown -h now
```

No use `containerlab destroy` sin `-t` desde un directorio ambiguo. Los
artefactos renderizados, backups, logs, claves e imágenes Cisco no se publican.
