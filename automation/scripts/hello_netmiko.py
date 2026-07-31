#!/usr/bin/env python3
"""Small exam-style Netmiko example against P1."""

import os

from netmiko import ConnectHandler


device = {
    "device_type": "cisco_xr",
    "host": "10.201.255.101",
    "username": os.getenv("CCIE_XRD_USERNAME", "clab"),
    "password": os.environ["CCIE_XRD_PASSWORD"],
}

with ConnectHandler(**device) as session:
    print(session.send_command("show isis neighbors"))
