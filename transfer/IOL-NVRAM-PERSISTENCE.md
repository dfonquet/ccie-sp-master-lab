# Cisco IOL NVRAM persistence

## Real mechanism

Containerlab `cisco_iol` bind-mounts a complete 1 MiB binary NVRAM read/write:

```text
topology/clab-ccie-sp-master/<node>/nvram_<PID> -> /iol/nvram_<PID>
```

`write memory` and `copy running-config startup-config` update that binary
directly. It contains the complete saved IOS configuration; this solution does
not export, filter, parse, or reconstruct `show running-config`.

The `<PID>` is derived from Containerlab's node index and can change after a
topology edit. To make persistence node-stable, the repository wrapper mirrors
each active binary to this canonical, node-centric location:

```text
topology/persistent/iol/<node>/nvram
```

The binaries contain study configuration and are intentionally ignored by Git.
Backups under `artifacts/backups/` are also ignored.

## Normal workflow

Save normally in IOS:

```text
CE2# copy running-config startup-config
```

Then use the wrapper for lifecycle operations:

```bash
./labctl destroy master
./labctl deploy master
```

Before destroy, `labctl` copies every mounted IOL NVRAM byte-for-byte to its
canonical path and creates a timestamped backup. Before deploy, it calculates
the current expected PID and copies the canonical binary to the exact native
path Containerlab will mount. Do not use `containerlab destroy --cleanup`.

Files under `topology/startup/*.partial.cfg` remain first-boot bootstrap only.
Containerlab applies them when no saved NVRAM exists; a restored NVRAM takes
precedence. They are not the persistence mechanism.

Inspect or take an extra backup:

```bash
python3 tools/iol_nvram.py status
python3 tools/iol_nvram.py backup --label before-study-change
```

## Deliberate reset to bootstrap

After the selected IOL has been stopped:

```bash
python3 tools/iol_nvram.py reset --node CE2 --yes
```

The command refuses to reset a running node, first backs up all canonical
NVRAM, then deletes only that node's canonical and native NVRAM generations.
Its next deploy is a first boot and applies its `.partial.cfg` bootstrap.

Direct raw `containerlab destroy/deploy` bypasses canonical synchronization;
use `labctl` for the persistence guarantee, especially after topology changes.
