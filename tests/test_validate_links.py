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

from tools.validate_links import load_data, select_link_sources  # noqa: E402


class DirectedLinkSelectionTests(unittest.TestCase):
    def test_master_cardinality_is_bidirectional(self) -> None:
        nodes, grouped = load_data("master")
        selected = select_link_sources(nodes, grouped, None)
        directed = [test for tests in selected.values() for test in tests]
        self.assertEqual(94, len(directed))
        self.assertEqual(47, sum(test["direction"] == "a-to-b" for test in directed))
        self.assertEqual(47, sum(test["direction"] == "b-to-a" for test in directed))

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


if __name__ == "__main__":
    unittest.main()
