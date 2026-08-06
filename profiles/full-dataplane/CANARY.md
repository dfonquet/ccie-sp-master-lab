# Full Dataplane Canary

This isolated gate validates one XRd vRouter micro-VM before any provider-core rollout. It does not use the full-profile configuration and therefore cannot produce false failures from interfaces whose peers were filtered out.

## Scope

- one XRd vRouter 26.2.1 with `4` vCPU and `10240` MiB RAM;
- `igb` dataplane NIC mapped to `GigabitEthernet0/0/0/0`;
- one lightweight Alpine probe;
- management, SSH, IOS XR platform and configuration acceptance;
- bidirectional IPv4 and IPv6 forwarding over one emulated PCI link.

## Deploy

```bash
sudo containerlab deploy \
  -t topology/ccie-sp-full-dataplane-canary.clab.yml \
  --max-workers 1 \
  --timeout 20m
```

## Mandatory acceptance

1. Both containers are healthy/running with zero restarts and no OOM state.
2. SSH to `clab@10.205.254.101` succeeds using the locally supplied lab credential.
3. `show platform` reports IOS XR RUN.
4. `show configuration failed` is empty.
5. `GigabitEthernet0/0/0/0` is Up/Up.
6. P1 reaches `192.0.2.0` and `2001:db8:ffff:1::`.
7. PROBE1 reaches `192.0.2.1` and `2001:db8:ffff:1::1`.
8. Swap remains unused and host available memory stays above 20 GiB.

## Destroy

```bash
sudo containerlab destroy \
  -t topology/ccie-sp-full-dataplane-canary.clab.yml
```

Never deploy the canary beside another Containerlab profile.
