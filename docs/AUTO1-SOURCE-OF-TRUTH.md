# AUTO1: Source of Truth y automatización BGP

Este módulo formaliza el flujo construido en `AUTO1` para RR2 y los seis PE:

```text
Source of Truth → Jinja2 → Render → Validate → Check/Diff
                → Deploy controlado → Post-check BGP
```

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
ansible-playbook -i inventory/hosts.yml playbooks/render_bgp.yml

cat rendered/RR2_bgp.cfg
grep -H "bgp router-id" rendered/PE*_bgp.cfg

ansible-playbook -i inventory/hosts.yml playbooks/check_bgp.yml --check --diff
```

Hasta aquí no debe existir ningún cambio real. Tras la revisión humana:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/deploy_bgp.yml \
  --diff -e deploy_confirm=true
ansible-playbook -i inventory/hosts.yml playbooks/postcheck_bgp.yml
```

El despliegue usa `serial: 1`, exige confirmación explícita y crea backup.
Para practicar solo con RR2 se puede añadir `--limit RR2`; para los PE,
`--limit pe`.

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
