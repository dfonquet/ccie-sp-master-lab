# Validation runbook

Run from the Ubuntu host:

```bash
cd /srv/netlab/labs/ccie-sp-master
```

## Management and software

```bash
/srv/netlab/venvs/ccie-sp/bin/python tools/validate_nodes.py --workers 2
```

Expected:

```text
SUMMARY total=26 tcp22_open=26 cli_ok=26
```

## Provider standard

```bash
/srv/netlab/venvs/ccie-sp/bin/python \
  tools/validate_provider_standard.py --workers 2
```

Expected:

```text
SUMMARY nodes=14 passed=14 failed=0
```

## Directly connected links

```bash
/srv/netlab/venvs/ccie-sp/bin/python \
  tools/validate_links.py --family both --workers 2
```

Expected:

```text
SUMMARY tests=78 families=ipv4,ipv6 passed=78 failed=0
```

## IOS XR checks

```text
show ipv4 interface brief
show ipv6 interface brief
show isis neighbors
show isis database summary
show route isis
show isis segment-routing label table
show mpls forwarding labels 16014
show mpls forwarding labels 16614
```

Example IPv6 end-to-end test from P1:

```text
ping ipv6 2001:db8:500:abcd::14 \
  source 2001:db8:500:abcd::1 count 5 timeout 1
```

## AUTO1 checks

```bash
ssh student@10.201.255.150
cd /workspace
ansible-inventory --graph
python3 scripts/hello_netmiko.py
ansible-playbook playbooks/precheck.yml --limit P1
```
