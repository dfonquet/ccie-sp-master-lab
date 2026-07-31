"""Load lab credentials from the process environment."""

from __future__ import annotations

import os


def required(name: str) -> str:
    """Return a required environment variable without exposing its value."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Required environment variable {name} is not set. "
            "Copy .env.example to .env, replace its placeholders, and load it."
        )
    return value


def connection_credentials(kind: str) -> dict[str, str]:
    """Return Netmiko username and password for a supported node kind."""
    if kind == "cisco_xrd":
        return {
            "username": os.getenv("CCIE_XRD_USERNAME", "clab"),
            "password": required("CCIE_XRD_PASSWORD"),
        }
    if kind == "cisco_iol":
        return {
            "username": os.getenv("CCIE_IOL_USERNAME", "admin"),
            "password": required("CCIE_IOL_PASSWORD"),
        }
    if kind == "linux":
        return {
            "username": os.getenv("CCIE_AUTO_USERNAME", "student"),
            "password": required("CCIE_AUTO_PASSWORD"),
        }
    raise ValueError(f"Unsupported node kind: {kind}")
