#!/usr/bin/env python3
"""Manage stable, node-centric persistence for Containerlab Cisco IOL NVRAM."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "inventory" / "nodes.csv"
LAB_DIR = ROOT / "topology" / "clab-ccie-sp-master"
STORE = ROOT / "topology" / "persistent" / "iol"
BACKUP_ROOT = ROOT / "artifacts" / "backups"


def inventory_rows() -> list[dict[str, str]]:
    with INVENTORY.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def iol_nodes() -> list[str]:
    return [row["name"] for row in inventory_rows() if row["kind"] == "cisco_iol"]


def expected_pid(node: str) -> int:
    # Containerlab assigns node indexes in lexical node-name order; IOL uses index+1.
    names = sorted(row["name"] for row in inventory_rows())
    return names.index(node) + 1


def canonical(node: str) -> Path:
    return STORE / node / "nvram"


def nvram_files(node: str) -> list[Path]:
    return sorted((LAB_DIR / node).glob("nvram_[0-9][0-9][0-9][0-9][0-9]"))


def expected_native(node: str) -> Path:
    return LAB_DIR / node / f"nvram_{expected_pid(node):05d}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def container_mounts(node: str) -> list[dict[str, object]] | None:
    result = subprocess.run(
        ["docker", "inspect", f"clab-ccie-sp-master-{node}", "--format", "{{json .Mounts}}"],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return None
    return json.loads(result.stdout)


def active_nvram(node: str) -> Path | None:
    mounts = container_mounts(node)
    if mounts is None:
        return None
    candidates = [
        Path(str(m["Source"]))
        for m in mounts
        if str(m.get("Destination", "")).startswith("/iol/nvram_") and m.get("RW") is True
    ]
    if len(candidates) != 1:
        raise SystemExit(f"{node}: expected one RW /iol/nvram_* mount, found {len(candidates)}")
    return candidates[0]


def atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    shutil.copy2(source, temporary)
    os.replace(temporary, destination)


def capture() -> int:
    count = 0
    for node in iol_nodes():
        source = active_nvram(node)
        if source is None:
            files = nvram_files(node)
            expected = expected_native(node)
            source = expected if expected in files else (files[-1] if files else None)
        if source is None or not source.is_file():
            print(f"{node}|SKIP|no native NVRAM found")
            continue
        atomic_copy(source, canonical(node))
        print(f"{node}|CAPTURED|{source}|sha256={sha256(source)}")
        count += 1
    print(f"CAPTURE nodes={count}")
    return 0


def prepare() -> int:
    if any(container_mounts(node) is not None for node in iol_nodes()):
        raise SystemExit("refusing prepare while a Master IOL container is running")
    count = 0
    for node in iol_nodes():
        source = canonical(node)
        if not source.is_file():
            print(f"{node}|FIRST-BOOT|no canonical NVRAM; bootstrap remains eligible")
            continue
        destination = expected_native(node)
        atomic_copy(source, destination)
        print(f"{node}|PREPARED|{destination}|sha256={sha256(destination)}")
        count += 1
    print(f"PREPARE nodes={count}")
    return 0


def status() -> int:
    failures = 0
    for node in iol_nodes():
        active = active_nvram(node)
        saved = canonical(node)
        expected = expected_native(node)
        historical = len(nvram_files(node))
        problems = []
        if active is not None and active.name != expected.name:
            problems.append(f"active={active.name},expected={expected.name}")
        if not saved.is_file():
            problems.append("canonical-missing")
        elif active is not None and sha256(saved) != sha256(active):
            problems.append("canonical-stale")
        state = "FAIL" if problems else "OK"
        failures += bool(problems)
        print(
            f"{node}|{state}|pid={expected_pid(node)}|active={active or '-'}|canonical={saved if saved.exists() else '-'}"
            f"|native_files={historical}|detail={','.join(problems) or 'synchronized'}"
        )
    print(f"SUMMARY nodes={len(iol_nodes())} failures={failures}")
    return 1 if failures else 0


def backup(label: str) -> int:
    capture()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = BACKUP_ROOT / f"{stamp}-{label}"
    target.mkdir(parents=True, exist_ok=False)
    manifest = []
    for node in iol_nodes():
        source = canonical(node)
        if not source.is_file():
            continue
        destination = target / node / "nvram"
        atomic_copy(source, destination)
        manifest.append({"node": node, "source": str(source), "backup": str(destination), "size": source.stat().st_size, "sha256": sha256(source)})
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"BACKUP directory={target} nodes={len(manifest)}")
    return 0


def reset(node: str, confirmed: bool) -> int:
    if node not in iol_nodes():
        raise SystemExit(f"unknown IOL node: {node}")
    if not confirmed:
        raise SystemExit("refusing reset without --yes")
    if container_mounts(node) is not None:
        raise SystemExit(f"refusing reset: {node} container is running")
    backup(f"before-{node.lower()}-nvram-reset")
    removed = []
    for path in [canonical(node), *nvram_files(node)]:
        if path.exists():
            path.unlink()
            removed.append(str(path))
    print(f"RESET node={node} removed={len(removed)}")
    print("The next deployment will treat this node as first boot and apply its .partial.cfg bootstrap.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    actions = parser.add_subparsers(dest="action", required=True)
    for action in ("status", "capture", "prepare"):
        actions.add_parser(action)
    backup_parser = actions.add_parser("backup")
    backup_parser.add_argument("--label", default="iol-nvram")
    reset_parser = actions.add_parser("reset")
    reset_parser.add_argument("--node", required=True)
    reset_parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()
    if args.action == "status":
        return status()
    if args.action == "capture":
        return capture()
    if args.action == "prepare":
        return prepare()
    if args.action == "backup":
        return backup(args.label)
    return reset(args.node, args.yes)


if __name__ == "__main__":
    raise SystemExit(main())
