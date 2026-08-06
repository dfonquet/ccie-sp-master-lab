#!/usr/bin/env python3

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "xrd-eight"
TOPOLOGY = ROOT / "topology" / "ccie-sp-xrd-eight.clab.yml"
CONFIGS = ROOT / "configs" / "xrd-eight" / "00-foundation"
INVENTORY = PROFILE
AUTO_DIR = ROOT / "automation" / "xrd-eight"
LABCTL = PROFILE / "labctl"

LAB_NAME = "ccie-sp-xrd-eight"
MGMT_NETWORK = "ccie-sp-xrd-eight-mgmt"
MGMT_SUBNET = "10.207.255.0/24"

ISIS_PROCESS = "500-SP"
ISIS_AREA = "49.0001"
SRGB_START = 16000
SRGB_END = 23999
IPV6_PREFIX_SID_OFFSET = 600
XR_STARTUP_INTERVAL = 120


ISP_NODES = [
    {"name": "XR1", "role": "P",         "id": 1, "mgmt": "10.207.255.101"},
    {"name": "XR2", "role": "P",         "id": 2, "mgmt": "10.207.255.102"},
    {"name": "XR3", "role": "PE",        "id": 3, "mgmt": "10.207.255.103"},
    {"name": "XR4", "role": "PE",        "id": 8, "mgmt": "10.207.255.108"},
    {"name": "R1",  "role": "P",         "id": 4, "mgmt": "10.207.255.104"},
    {"name": "R2",  "role": "RR-PCE-RP", "id": 5, "mgmt": "10.207.255.105"},
    {"name": "R3",  "role": "P",         "id": 6, "mgmt": "10.207.255.106"},
    {"name": "R5",  "role": "PE",        "id": 7, "mgmt": "10.207.255.107"},
]


CE_NODES = [
    {"name": "R4",  "role": "CE", "id": 41, "mgmt": "10.207.255.141"},
    {"name": "R7",  "role": "CE", "id": 43, "mgmt": "10.207.255.143"},
    {"name": "R10", "role": "CE", "id": 46, "mgmt": "10.207.255.146"},
]

AUTO_NODE = {
    "name": "AUTO1",
    "role": "AUTOMATION",
    "id": 150,
    "mgmt": "10.207.255.150",
}


# Compact CCIE SP topology:
# four-node full-mesh P core, three dual-homed PE,
# one dual-homed RR/PCE/RP, and three dual-link CE sites.
LINKS = [
    # Four-node P full mesh
    ("L001", "XR1", "XR2", "isp"),
    ("L002", "XR1", "R1",  "isp"),
    ("L003", "XR1", "R3",  "isp"),
    ("L004", "XR2", "R1",  "isp"),
    ("L005", "XR2", "R3",  "isp"),
    ("L006", "R1",  "R3",  "isp"),

    # Provider edge dual-homing
    ("L007", "R5",  "XR1", "isp"),
    ("L008", "R5",  "R1",  "isp"),

    ("L009", "XR4", "XR2", "isp"),
    ("L010", "XR4", "R3",  "isp"),

    ("L011", "XR3", "XR1", "isp"),
    ("L012", "XR3", "R3",  "isp"),

    # RR/PCE/RP dual-homing
    ("L013", "R2", "XR1", "isp"),
    ("L014", "R2", "R3",  "isp"),

    # CE1 dual physical links to PE1
    ("L015", "R4", "R5", "customer"),
    ("L016", "R4", "R5", "customer"),

    # CE2 dual physical links to PE2
    ("L017", "R7", "XR4", "customer"),
    ("L018", "R7", "XR4", "customer"),

    # CE3 dual physical links to PE3
    ("L019", "R10", "XR3", "customer"),
    ("L020", "R10", "XR3", "customer"),
]

ISP_NAMES = {node["name"] for node in ISP_NODES}
ALL_NODES = ISP_NODES + CE_NODES + [AUTO_NODE]
NODE_BY_NAME = {node["name"]: node for node in ALL_NODES}

CONFIGS.mkdir(parents=True, exist_ok=True)
INVENTORY.mkdir(parents=True, exist_ok=True)
TOPOLOGY.parent.mkdir(parents=True, exist_ok=True)

for directory in (
    AUTO_DIR / "workspace",
    AUTO_DIR / "workspace" / "services" / "aaa",
    AUTO_DIR / "workspace" / "services" / "rpki",
    AUTO_DIR / "data",
    AUTO_DIR / "evidence",
    AUTO_DIR / "backups",
):
    directory.mkdir(parents=True, exist_ok=True)

# Configurations in this directory are generated artifacts.
for stale_config in CONFIGS.glob("*.cfg"):
    stale_config.unlink()

port_counter = defaultdict(lambda: 1)
interfaces = defaultdict(list)
rendered_links = []

isp_sequence = 0
customer_sequence = 0

for link_id, endpoint_a, endpoint_b, purpose in LINKS:
    port_a = port_counter[endpoint_a]
    port_b = port_counter[endpoint_b]
    port_counter[endpoint_a] += 1
    port_counter[endpoint_b] += 1

    topo_a = f"{endpoint_a}:eth{port_a}"
    topo_b = f"{endpoint_b}:eth{port_b}"

    if purpose == "isp":
        isp_sequence += 1
        host_a = (isp_sequence - 1) * 2
        host_b = host_a + 1
        ipv4_a = f"10.70.255.{host_a}"
        ipv4_b = f"10.70.255.{host_b}"
        ipv6_a = f"2001:db8:1700:{isp_sequence:x}::"
        ipv6_b = f"2001:db8:1700:{isp_sequence:x}::1"
    else:
        customer_sequence += 1
        host_a = (customer_sequence - 1) * 2
        host_b = host_a + 1
        ipv4_a = f"10.71.255.{host_a}"
        ipv4_b = f"10.71.255.{host_b}"
        ipv6_a = f"2001:db8:2700:{customer_sequence:x}::"
        ipv6_b = f"2001:db8:2700:{customer_sequence:x}::1"

    rendered_links.append({
        "id": link_id,
        "endpoint_a": topo_a,
        "endpoint_b": topo_b,
        "node_a": endpoint_a,
        "node_b": endpoint_b,
        "purpose": purpose,
        "ipv4_a": ipv4_a,
        "ipv4_b": ipv4_b,
        "ipv6_a": ipv6_a,
        "ipv6_b": ipv6_b,
    })

    interfaces[endpoint_a].append({
        "port": port_a,
        "peer": endpoint_b,
        "id": link_id,
        "purpose": purpose,
        "ipv4": ipv4_a,
        "ipv6": ipv6_a,
    })

    interfaces[endpoint_b].append({
        "port": port_b,
        "peer": endpoint_a,
        "id": link_id,
        "purpose": purpose,
        "ipv4": ipv4_b,
        "ipv6": ipv6_b,
    })


def xr_interface(port):
    return f"GigabitEthernet0/0/0/{port - 1}"


def render_xr_config(node):
    name = node["name"]
    node_id = node["id"]
    ipv6_sid_index = IPV6_PREFIX_SID_OFFSET + node_id

    lines = [
        f"hostname {name}",
        "banner motd ^C",
        "------------------------------------------------------------",
        "                    AUTHORIZED ACCESS ONLY",
        "",
        "Este sistema pertenece al laboratorio CCIE Service Provider.",
        "",
        "Toda actividad puede ser supervisada, registrada y auditada.",
        "Si usted no es personal autorizado, desconectese inmediatamente.",
        "",
        "Use of this system indicates acceptance of monitoring",
        "and security policies.",
        "------------------------------------------------------------",
        "^C",
        "banner login ^C",
        "************************************************************",
        "*                                                          *",
        "*          CCCCCC  CCCCCC  III  EEEEEEE     SSSSSS  PPPPPP *",
        "*         CC      CC       III  EE         SS       PP   PP *",
        "*         CC      CC       III  EEEEE       SSSSS   PPPPPP  *",
        "*         CC      CC       III  EE              SS  PP      *",
        "*          CCCCCC  CCCCCC  III  EEEEEEE    SSSSSS   PP      *",
        "*                                                          *",
        "*            CCIE SERVICE PROVIDER LAB ENVIRONMENT         *",
        "*                         (SP)                              *",
        "*                                                          *",
        "************************************************************",
        "^C",
        "interface Loopback0",
        f" description XR8-LAB {node['role']} NODE-ID {node_id}",
        f" ipv4 address 10.70.0.{node_id} 255.255.255.255",
        f" ipv6 address 2001:db8:570:abcd::{node_id}/128",
        " no shutdown",
        "!",
    ]

    isis_interfaces = []

    for interface in interfaces[name]:
        interface_name = xr_interface(interface["port"])

        if interface["purpose"] == "isp":
            lines.extend([
                f"interface {interface_name}",
                f" description {interface['id']} PROVIDER {name} -> {interface['peer']}",
                f" ipv4 address {interface['ipv4']} 255.255.255.254",
                f" ipv6 address {interface['ipv6']}/127",
                " no shutdown",
                "!",
            ])
            isis_interfaces.append(interface_name)
        else:
            lines.extend([
                f"interface {interface_name}",
                f" description {interface['id']} CUSTOMER {name} -> {interface['peer']} - STUDENT SERVICE EDGE",
                " no shutdown",
                "!",
            ])

    lines.extend([
        f"router isis {ISIS_PROCESS}",
        " is-type level-2-only",
        f" net {ISIS_AREA}.0000.0000.{node_id:04d}.00",
        " distribute link-state",
        " address-family ipv4 unicast",
        "  metric-style wide",
        "  advertise passive-only",
        "  mpls traffic-eng level-2-only",
        "  mpls traffic-eng router-id Loopback0",
        "  segment-routing mpls sr-prefer",
        " !",
        " address-family ipv6 unicast",
        "  metric-style wide",
        "  advertise passive-only",
        "  single-topology",
        "  segment-routing mpls",
        " !",
        " interface Loopback0",
        "  passive",
        "  address-family ipv4 unicast",
        f"   prefix-sid index {node_id}",
        "  !",
        "  address-family ipv6 unicast",
        f"   prefix-sid index {ipv6_sid_index}",
        "  !",
        " !",
    ])

    for interface_name in isis_interfaces:
        lines.extend([
            f" interface {interface_name}",
            "  circuit-type level-2-only",
            "  bfd fast-detect ipv4",
            "  bfd fast-detect ipv6",
            "  point-to-point",
            "  hello-padding disable",
            "  address-family ipv4 unicast",
            "   fast-reroute per-prefix",
            "   metric 10",
            "  !",
            "  address-family ipv6 unicast",
            "   fast-reroute per-prefix",
            "   metric 10",
            "  !",
            " !",
        ])

    lines.extend([
        "!",
        "segment-routing",
        f" global-block {SRGB_START} {SRGB_END}",
        "!",
        "end",
        "",
    ])

    return "\n".join(lines)

def render_ce_config(node):
    # Intentionally minimal. No data-plane addressing or protocols.
    return "\n".join([
        f"hostname {node['name']}",
        "end",
        "",
    ])


for node in ISP_NODES:
    (CONFIGS / f"{node['name']}.cfg").write_text(
        render_xr_config(node),
        encoding="utf-8",
        newline="\n",
    )

for node in CE_NODES:
    (CONFIGS / f"{node['name']}.cfg").write_text(
        render_ce_config(node),
        encoding="utf-8",
        newline="\n",
    )


topology_lines = [
    f"name: {LAB_NAME}",
    "",
    "mgmt:",
    f"  network: {MGMT_NETWORK}",
    f"  ipv4-subnet: {MGMT_SUBNET}",
    "",
    "topology:",
    "  kinds:",
    "    cisco_xrd_vrouter:",
    "      image: vrnetlab/cisco_xrd-vrouter:26.2.1",
    "      env:",
    "        XRD_NIC_TYPE: igb",
    "    cisco_iol:",
    "      image: vrnetlab/cisco_iol:17.12.01",
    "",
    "  nodes:",
]

startup_delay = 0

for node in ISP_NODES:
    topology_lines.extend([
        f"    {node['name']}:",
        "      kind: cisco_xrd_vrouter",
        f"      mgmt-ipv4: {node['mgmt']}",
        f"      startup-config: ../configs/xrd-eight/00-foundation/{node['name']}.cfg",
        f"      startup-delay: {startup_delay}",
    ])
    startup_delay += XR_STARTUP_INTERVAL

for node in CE_NODES:
    topology_lines.extend([
        f"    {node['name']}:",
        "      kind: cisco_iol",
        f"      mgmt-ipv4: {node['mgmt']}",
        f"      startup-config: ../configs/xrd-eight/00-foundation/{node['name']}.cfg",
        f"      startup-delay: {startup_delay}",
    ])
    startup_delay += 10

topology_lines.extend([
    "    AUTO1:",
    "      kind: linux",
    f"      mgmt-ipv4: {AUTO_NODE['mgmt']}",
    "      image: ccie-sp-automation:1.0",
    "      cmd: sleep infinity",
    "      env:",
    "        AUTO1_PASSWORD: ${CCIE_AUTO_PASSWORD}",
    "      binds:",
    "        - ../automation/xrd-eight/workspace:/workspace/xrd-eight",
    "        - ../automation/xrd-eight/data:/var/lib/ccie-sp",
    "        - ../automation/xrd-eight/evidence:/evidence",
    "        - ../automation/xrd-eight/backups:/backups",
    "",
    "  links:",
])

for link in rendered_links:
    topology_lines.append(
        f'    - endpoints: ["{link["endpoint_a"]}", "{link["endpoint_b"]}"]'
    )

topology_lines.append("")

TOPOLOGY.write_text(
    "\n".join(topology_lines),
    encoding="utf-8",
    newline="\n",
)


with (INVENTORY / "nodes.csv").open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=[
            "name",
            "role",
            "platform",
            "node_id",
            "mgmt_ipv4",
            "loopback_ipv4",
            "loopback_ipv6",
        ],
    )
    writer.writeheader()

    for node in ISP_NODES:
        writer.writerow({
            "name": node["name"],
            "role": node["role"],
            "platform": "XRd-vRouter-26.2.1",
            "node_id": node["id"],
            "mgmt_ipv4": node["mgmt"],
            "loopback_ipv4": f"10.70.0.{node['id']}/32",
            "loopback_ipv6": f"2001:db8:570:abcd::{node['id']}/128",
        })

    for node in CE_NODES:
        writer.writerow({
            "name": node["name"],
            "role": node["role"],
            "platform": "IOL-XE-17.12.1",
            "node_id": node["id"],
            "mgmt_ipv4": node["mgmt"],
            "loopback_ipv4": "",
            "loopback_ipv6": "",
        })

    writer.writerow({
        "name": AUTO_NODE["name"],
        "role": AUTO_NODE["role"],
        "platform": "Linux",
        "node_id": AUTO_NODE["id"],
        "mgmt_ipv4": AUTO_NODE["mgmt"],
        "loopback_ipv4": "",
        "loopback_ipv6": "",
    })


with (INVENTORY / "links.csv").open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=[
            "id",
            "endpoint_a",
            "endpoint_b",
            "purpose",
            "ipv4_a",
            "ipv4_b",
            "ipv6_a",
            "ipv6_b",
        ],
    )
    writer.writeheader()

    for link in rendered_links:
        writer.writerow({
            "id": link["id"],
            "endpoint_a": link["endpoint_a"],
            "endpoint_b": link["endpoint_b"],
            "purpose": link["purpose"],
            "ipv4_a": f'{link["ipv4_a"]}/31',
            "ipv4_b": f'{link["ipv4_b"]}/31',
            "ipv6_a": f'{link["ipv6_a"]}/127',
            "ipv6_b": f'{link["ipv6_b"]}/127',
        })


LABCTL.write_text(
    """#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOPOLOGY="$ROOT/topology/ccie-sp-xrd-eight.clab.yml"
ISP_FILTER="XR1,XR2,XR3,XR4,R1,R2,R3,R5"

case "${1:-}" in
  deploy-isp)
    sudo containerlab deploy -t "$TOPOLOGY" --node-filter "$ISP_FILTER"
    ;;
  deploy-full)
    : "${CCIE_AUTO_PASSWORD:?Export CCIE_AUTO_PASSWORD before deployment}"
    sudo --preserve-env=CCIE_AUTO_PASSWORD containerlab deploy -t "$TOPOLOGY"
    ;;
  destroy)
    sudo containerlab destroy -t "$TOPOLOGY" --cleanup
    ;;
  status)
    docker ps -a \
      --filter name=clab-ccie-sp-xrd-eight \
      --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
    ;;
  resources)
    free -h
    uptime
    names="$(docker ps \
      --filter name=clab-ccie-sp-xrd-eight \
      --format '{{.Names}}')"
    if [[ -n "$names" ]]; then
      docker stats --no-stream $names
    fi
    ;;
  *)
    echo "Usage: $0 {deploy-isp|deploy-full|destroy|status|resources}"
    exit 1
    ;;
esac
""",
    encoding="utf-8",
    newline="\n",
)
LABCTL.chmod(0o755)

print(f"Generated topology: {TOPOLOGY}")
print(f"Generated ISP configs: {len(ISP_NODES)}")
print(f"Generated CE configs: {len(CE_NODES)}")
print(f"Generated links: {len(rendered_links)}")
print("Repository profile: profiles/xrd-eight")
