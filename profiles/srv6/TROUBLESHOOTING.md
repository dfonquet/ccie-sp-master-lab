# SRv6 capability troubleshooting

## False link failures caused by platform syntax

IOS XR uses `ping ipv6 <address> count 3`; IOS XE/IOL uses
`ping ipv6 <address> repeat 3`. A platform-neutral validator that sends the XR
form to IOL reports false CE-to-PE failures even when the reverse direction
passes. Use `python tools/validate_srv6_links.py`; it selects the correct form.

## A command parses but commit fails

```text
show configuration failed
show configuration commit changes last 1
show configuration commit list
```

Record the failure as `UNSUPPORTED_COMMIT`. Do not edit the generated command
silently until the platform-specific reason is documented.

## Locator commits but has no operational SID

```text
show segment-routing srv6 locator
show segment-routing srv6 locator MAIN detail
show segment-routing srv6 sid
show running-config segment-routing
```

This may indicate control-plane image limitations. A configured locator is not
proof of FIB programming.

## IS-IS does not advertise the locator

```text
show isis neighbors
show isis database verbose
show isis route ipv6
show route ipv6
show running-config router isis SRV6
```

Verify the locator exists before enabling it under the IS-IS IPv6 address
family. IOS XR does not support SR-MPLS and SRv6 simultaneously in the same
IS-IS address family.

## Management collision

```bash
docker network ls
docker network inspect ccie-sp-srv6-mgmt
docker ps --format '{{.Names}}'
```

Do not reuse the Master (`10.201.255.0/24`) or Inter-AS
(`10.202.255.0/24`) management networks. The SRv6 capability profile owns
`10.203.255.0/24`.

## Safe recovery

Destroy only the topology declared by this profile:

```bash
./labctl destroy srv6
```

Never use a wildcard Docker removal command as a recovery shortcut.
