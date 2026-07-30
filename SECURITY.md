# Security and licensing

This repository is a private training lab. The usernames and passwords found
in the examples are deliberately weak lab-only credentials and must never be
used on production systems.

Before sharing the repository publicly:

1. Replace the default credentials or load them from environment variables.
2. Review every generated configuration and automation inventory.
3. Remove operational backups and command outputs.
4. Confirm `.temporary-access/`, `artifacts/` and `xr-storage/` are absent.
5. Never commit Cisco software images, licenses, tokens or entitlement files.

The repository contains only topology definitions, generated configurations
and automation code. Cisco XRd/IOL images must be obtained through authorized
channels and remain outside Git.
