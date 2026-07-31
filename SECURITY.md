# Security and licensing

This repository is a training lab. No operational password, token, or private
key belongs in the tracked tree. Runtime credentials are loaded from the
environment by using the names documented in `.env.example`; the real `.env`
file is ignored by Git.

Before sharing the repository publicly:

1. Copy `.env.example` to `.env`, replace every placeholder, and load it only
   in the local shell or secret manager.
2. Review every generated configuration and automation inventory.
3. Remove operational backups and command outputs.
4. Confirm `.temporary-access/`, `artifacts/` and `xr-storage/` are absent.
5. Never commit Cisco software images, licenses, tokens or entitlement files.
6. Scan the complete Git history with a current secret scanner.
7. Enable GitHub secret scanning and push protection after publication.

The sample usernames are not secrets. Placeholder passwords in
`.env.example` are intentionally nonfunctional and must be replaced. The
automation fails closed when a required password variable is absent.
Environment variables only supply automation clients; they do not rotate
accounts on running routers. Change live device credentials separately and
never expose the Containerlab management networks to untrusted networks.

The repository contains only topology definitions, generated configurations
and automation code. Cisco XRd/IOL images must be obtained through authorized
channels and remain outside Git.
