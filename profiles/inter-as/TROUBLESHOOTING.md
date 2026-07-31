# Troubleshooting — Lab 2 Inter-AS

This log preserves errors found during the live deployment and the safest
known recovery procedures.

## Links are missing after deployment

**Symptom:** the container is running, but `eth1`/`eth2` or `Gi0-0-0-x`
interfaces are missing.

**Diagnosis:**

```bash
docker exec clab-ccie-sp-inter-as-CE-C ip -br link
sudo containerlab apply -t topology/ccie-sp-inter-as.clab.yml --dry-run
```

Always use `--dry-run`. If the plan recreates additional nodes, calculate the
impact and use `--max-workers 1`.

## XRd is Up/Up but does not forward

A hot-added veth can appear in Linux and IOS XR without becoming operational
in the data plane. Restart the affected node through Containerlab:

```bash
sudo containerlab restart \
  -t topology/ccie-sp-inter-as.clab.yml \
  --node P5
```

Do not use `docker stop/start`; Containerlab must park and restore the veths.

## IOL remains in the System Configuration Dialog

Empty NVRAM can take precedence over `boot_config.txt`. Preserve a copy, clear
only the affected CE NVRAM, and use the Containerlab lifecycle. Never use
`--cleanup` for the entire lab.

Verify afterwards:

```text
show ip interface brief
show ip route vrf clab-mgmt
ping vrf clab-mgmt 10.202.255.1
```

## OSPFv3 IPv4 is rejected

XRd 24.2.11 did not accept `address-family ipv4` under `router ospfv3`.
The validated implementation uses:

- `router ospf <ASN>` for IPv4.
- `router ospfv3 <ASN>` for IPv6.

In addition, `area 0` is a sibling of `address-family ipv6`, not a child of
the address family.

## `exit` breaks an IOS XR hierarchy

In several XR submodes, `exit` returns to global configuration. The phase
applier re-enters the complete path for each XR command. If `% Invalid input`
appears, run a canary and inspect `show configuration failed` before expanding.

## Route policy leaves the session in the RPL editor

`route-policy ... end-policy` must be sent as an atomic block. Do not insert
`root` inside the RPL editor.

## BGP: “The address family has not been initialized”

Initialize the global address family before associating it with the neighbor:

```text
router bgp <ASN>
 address-family ipv4 unicast
 address-family ipv6 unicast
```

IOS XR also requires inbound and outbound route policies for eBGP.

## False negative in the IPv6 BGP summary

IOS XR wraps long IPv6 rows onto two lines. A parser that expects every field
on the address line will report `FAIL`. Validate with:

```text
show bgp ipv6 unicast neighbors <peer>
```

The correct test looks for `BGP state = Established`.
