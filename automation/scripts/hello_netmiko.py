#!/usr/bin/env python3
"""Small exam-style Netmiko example against P1."""

from netmiko import ConnectHandler


device = {
    "device_type": "cisco_xr",
    "host": "10.201.255.101",
    "username": "clab",
    "password": "clab@123",
}

with ConnectHandler(**device) as session:
    print(session.send_command("show isis neighbors"))
