#!/usr/bin/env python3
"""Validate every directly connected link in both directions."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from netmiko import ConnectHandler

from credentials import connection_credentials


ROOT = Path(__file__).resolve().parents[1]


def load_data(
    profile: str,
) -> tuple[dict[str, dict[str, str]], dict[str, list[dict[str, str]]]]:
    inventory = ROOT / "inventory" if profile == "master" else ROOT / "profiles" / profile
    with (inventory / "nodes.csv").open(
        newline="", encoding="utf-8"
    ) as file:
        nodes = {row["name"]: row for row in csv.DictReader(file)}

    links_by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    with (inventory / "links.csv").open(
        newline="", encoding="utf-8"
    ) as file:
        for row in csv.DictReader(file):
            endpoint_a = row["endpoint_a"].split(":", 1)[0]
            endpoint_b = row["endpoint_b"].split(":", 1)[0]

            # Store one directed test definition under each endpoint. Grouping
            # by source keeps one SSH session per node while ensuring that an
            # asymmetric forwarding or interface failure cannot be hidden by a
            # successful ping in the opposite direction.
            a_to_b = dict(row)
            a_to_b["source_node"] = endpoint_a
            a_to_b["destination_node"] = endpoint_b
            a_to_b["direction"] = "a-to-b"
            a_to_b["destination_ipv4"] = row["endpoint_b_ipv4"]
            a_to_b["destination_ipv6"] = row["endpoint_b_ipv6"]
            links_by_source[endpoint_a].append(a_to_b)

            b_to_a = dict(row)
            b_to_a["source_node"] = endpoint_b
            b_to_a["destination_node"] = endpoint_a
            b_to_a["direction"] = "b-to-a"
            b_to_a["destination_ipv4"] = row["endpoint_a_ipv4"]
            b_to_a["destination_ipv6"] = row["endpoint_a_ipv6"]
            links_by_source[endpoint_b].append(b_to_a)
    return nodes, links_by_source


def connect_params(node: dict[str, str]) -> dict[str, object]:
    if node["kind"] == "cisco_xrd":
        return {
            "device_type": "cisco_xr",
            **connection_credentials(node["kind"]),
        }
    return {
        "device_type": "cisco_ios",
        **connection_credentials(node["kind"]),
    }


def validate_source(
    node: dict[str, str],
    links: list[dict[str, str]],
    families: tuple[str, ...],
) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    session = None
    try:
        session = ConnectHandler(
            host=node["mgmt_ipv4"],
            conn_timeout=10,
            auth_timeout=15,
            banner_timeout=25,
            fast_cli=False,
            **connect_params(node),
        )
        for family in families:
            for link in links:
                destination = link[f"destination_{family}"].split("/", 1)[0]
                if family == "ipv6" and node["kind"] == "cisco_xrd":
                    command = f"ping ipv6 {destination} count 3 timeout 1"
                elif family == "ipv6":
                    command = f"ping ipv6 {destination} repeat 3 timeout 1"
                elif node["kind"] == "cisco_xrd":
                    command = f"ping {destination} count 3 timeout 1"
                else:
                    command = f"ping {destination} repeat 3 timeout 1"
                output = session.send_command(command, read_timeout=20)
                if "Success rate is 100 percent" not in output:
                    output = session.send_command(command, read_timeout=20)
                status = (
                    "ok" if "Success rate is 100 percent" in output else "failed"
                )
                summary = next(
                    (
                        line.strip()
                        for line in output.splitlines()
                        if "Success rate is" in line
                    ),
                    "no success-rate line",
                )
                results.append(
                    {
                        "id": link["id"],
                        "family": family,
                        "direction": link["direction"],
                        "source": node["name"],
                        "destination_node": link["destination_node"],
                        "destination": destination,
                        "status": status,
                        "summary": summary,
                    }
                )
    except Exception as exc:
        for family in families:
            for link in links:
                results.append(
                    {
                        "id": link["id"],
                        "family": family,
                        "direction": link["direction"],
                        "source": node["name"],
                        "destination_node": link["destination_node"],
                        "destination": link[f"destination_{family}"].split("/", 1)[0],
                        "status": "failed",
                        "summary": f"{type(exc).__name__}: {exc}".replace(
                            "\n", " "
                        )[:200],
                    }
                )
    finally:
        if session is not None:
            session.disconnect()
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--family",
        choices=("ipv4", "ipv6", "both"),
        default="both",
    )
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument(
        "--profile",
        choices=("master", "inter-as"),
        default="master",
    )
    parser.add_argument(
        "--sources",
        help=(
            "Comma-separated source node names. Default: both endpoints of "
            "every link. Filtering a source runs only its outbound tests."
        ),
    )
    args = parser.parse_args()

    nodes, links_by_source = load_data(args.profile)
    if args.sources:
        selected = {
            name.strip() for name in args.sources.split(",") if name.strip()
        }
        unknown = selected - set(nodes)
        if unknown:
            raise SystemExit(f"Unknown source nodes: {', '.join(sorted(unknown))}")
        links_by_source = {
            name: links
            for name, links in links_by_source.items()
            if name in selected
        }
    results: list[dict[str, str]] = []
    families = ("ipv4", "ipv6") if args.family == "both" else (args.family,)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(validate_source, nodes[name], links, families): name
            for name, links in links_by_source.items()
        }
        for future in as_completed(futures):
            results.extend(future.result())

    results.sort(
        key=lambda item: (
            int("".join(character for character in item["id"] if character.isdigit())),
            item["family"],
            item["direction"],
        )
    )
    for result in results:
        print(
            f"{result['id']}|{result['family']}|"
            f"{result['source']}->{result['destination_node']}"
            f"({result['destination']})|"
            f"{result['status']}|{result['summary']}"
        )

    passed = sum(result["status"] == "ok" for result in results)
    failed = len(results) - passed
    print(
        f"SUMMARY tests={len(results)} families={','.join(families)} "
        f"passed={passed} failed={failed}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
