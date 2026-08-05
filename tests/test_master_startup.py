from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_lab  # noqa: E402


def test_xrd_startup_is_cumulative_and_secret_safe() -> None:
    node = next(node for node in build_lab.NODES if node.name == "P1")
    config = build_lab.render_xrd_startup(node)

    assert "hostname P1" in config
    assert "router isis CORE" in config
    assert "segment-routing mpls sr-prefer" in config
    assert "prefix-sid index 601" in config
    assert "username ${CCIE_XRD_USERNAME}" in config
    assert "secret ${CCIE_XRD_PASSWORD}" in config
    assert node.legacy_loopback6 not in config


def test_topology_uses_kind_specific_startup_files() -> None:
    topology = build_lab.render_topology()

    assert "startup/__clabNodeName__.cfg" in topology
    assert "startup/__clabNodeName__.partial.cfg" in topology


def test_inventory_rendering_uses_platform_independent_newlines(tmp_path) -> None:
    original = build_lab.INVENTORY_DIR
    try:
        build_lab.INVENTORY_DIR = tmp_path
        build_lab.write_inventory()
    finally:
        build_lab.INVENTORY_DIR = original

    assert b"\r\n" not in (tmp_path / "nodes.csv").read_bytes()
    assert b"\r\n" not in (tmp_path / "links.csv").read_bytes()
