#!/usr/bin/env python3
import os
import sys

from netmiko import ConnectHandler


action = sys.argv[1]
session = ConnectHandler(
    device_type="cisco_ios",
    host="10.201.255.132",
    username=os.getenv("CCIE_IOL_USERNAME", "admin"),
    password=os.environ["CCIE_IOL_PASSWORD"],
    fast_cli=False,
)
try:
    if action == "mark":
        session.send_config_set(["ip access-list standard PERSISTENCE-CANARY", "remark NVRAM-PERSISTENCE-CANARY"])
        print(session.save_config())
    elif action == "verify":
        output = session.send_command("show startup-config | include PERSISTENCE-CANARY")
        print(output)
        if "PERSISTENCE-CANARY" not in output:
            raise SystemExit("canary marker not found")
    elif action == "cleanup":
        session.send_config_set(["no ip access-list standard PERSISTENCE-CANARY"])
        print(session.save_config())
    else:
        raise SystemExit(f"unknown action: {action}")
finally:
    session.disconnect()
