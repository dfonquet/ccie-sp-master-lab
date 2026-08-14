"""Static regression tests for directed-link selection and cardinality."""

from __future__ import annotations

import sys
import types
import unittest


# The CI unit tests exercise inventory construction and scope selection without
# opening network sessions, so lightweight stubs avoid installing Netmiko.
netmiko = types.ModuleType("netmiko")
netmiko.ConnectHandler = object
sys.modules.setdefault("netmiko", netmiko)

credentials = types.ModuleType("credentials")
credentials.connection_credentials = lambda _kind: {}
sys.modules.setdefault("credentials", credentials)

from tools.validate_links import (  # noqa: E402
    load_data,
    ping_command,
    ping_succeeded,
    select_link_sources,
)


class DirectedLinkSelectionTests(unittest.TestCase):
    def test_master_cardinality_is_bidirectional(self) -> None:
        nodes, grouped = load_data("master")
        selected = select_link_sources(nodes, grouped, None)
        directed = [test for tests in selected.values() for test in tests]
        self.assertEqual(114, len(directed))
        self.assertEqual(57, sum(test["direction"] == "a-to-b" for test in directed))
        self.assertEqual(57, sum(test["direction"] == "b-to-a" for test in directed))

    def test_inter_as_cardinality_is_bidirectional(self) -> None:
        nodes, grouped = load_data("inter-as")
        selected = select_link_sources(nodes, grouped, None)
        directed = [test for tests in selected.values() for test in tests]
        self.assertEqual(70, len(directed))

    def test_source_without_data_links_is_rejected(self) -> None:
        nodes, grouped = load_data("master")
        with self.assertRaisesRegex(ValueError, "AUTO1"):
            select_link_sources(nodes, grouped, "AUTO1")

    def test_mixed_selection_with_linkless_node_is_rejected(self) -> None:
        nodes, grouped = load_data("master")
        with self.assertRaisesRegex(ValueError, "AUTO1"):
            select_link_sources(nodes, grouped, "P1,AUTO1")

    def test_unknown_source_is_rejected(self) -> None:
        nodes, grouped = load_data("master")
        with self.assertRaisesRegex(ValueError, "UNKNOWN"):
            select_link_sources(nodes, grouped, "UNKNOWN")

    def test_linux_ipv4_ping_command(self) -> None:
        node = {"kind": "linux"}
        self.assertEqual("ping -c 3 -W 1 10.255.0.112", ping_command(node, "ipv4", "10.255.0.112"))

    def test_linux_ipv6_ping_command(self) -> None:
        node = {"kind": "linux"}
        self.assertEqual(
            "ping -6 -c 3 -W 1 2001:db8:1000:157::",
            ping_command(node, "ipv6", "2001:db8:1000:157::"),
        )

    def test_linux_ping_success_parser(self) -> None:
        self.assertTrue(ping_succeeded({"kind": "linux"}, "3 packets transmitted, 3 received, 0% packet loss"))


if __name__ == "__main__":
    unittest.main()
