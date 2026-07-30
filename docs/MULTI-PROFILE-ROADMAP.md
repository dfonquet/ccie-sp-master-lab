# Multi-profile implementation roadmap

The project deliberately separates stable services, Inter-AS and SRv6. A
profile is a complete topology plus Source of Truth, generated configs,
validation and exercises—not merely another configuration folder.

## Acceptance sequence

1. Validate the currently deployed master and save evidence.
2. Destroy master and wait until no `clab-ccie-sp-*` containers remain.
3. Deploy and validate Inter-AS; destroy it.
4. Run the SRv6 capability mini-lab, record supported commands, then deploy the
   full SRv6 profile only when safe.
5. Return to master and verify idempotence.

## Resource gates

Measured host: Ryzen 7 5700G, 16 logical CPUs, 127.85 GiB RAM. At 26 nodes the
VM used roughly 39 GiB resident with 58.5 GiB free on Windows. Four additional
XRd nodes are viable, but startup must be staggered because the initial 26-node
boot produced a transient Linux load above 200.

`labctl` is the guardrail that prevents accidental concurrent heavy profiles.
