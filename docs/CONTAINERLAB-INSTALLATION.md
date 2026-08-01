# Containerlab Host, Image, and AUTO1 Build Guide

This document records how the validated CCIE Service Provider environment was
built. It explains the host decision, Docker and Containerlab installation,
licensed-image transfer, local image construction, AUTO1 creation, verification,
and the operational controls used to protect the workstation.

> This repository does not contain Cisco software, licenses, passwords, private
> keys, or device backups. Obtain every network operating-system artifact from
> an authorized source and comply with the applicable vendor license.

## 1. Why Containerlab

Containerlab was selected for topology-as-code, deterministic Linux wiring,
Docker-based lifecycle control, and direct integration with Git, Ansible, and
Python. It complements EVE-NG rather than replacing it: EVE-NG remains useful
for interactive GUI work, while Containerlab makes generation, validation,
destruction, and reconstruction repeatable.

Containerlab orchestrates nodes and links. It does not supply Cisco images or
licenses.

## 2. Validated architecture

```text
Windows workstation
└── VMware Workstation
    └── Ubuntu Server VM: netlab-core
        ├── nested AMD-V/KVM
        ├── Docker Engine with overlay2
        ├── Containerlab 0.77.0
        ├── /srv/netlab/docker      Docker data root
        ├── /srv/netlab/images      licensed local image staging
        ├── /srv/netlab/labs        Git working copies and topologies
        └── /srv/netlab/backups     repository and device backups
```

Ubuntu Server was selected instead of the desktop Arch VM because the lab host
needed predictable services, dedicated `/srv/netlab` storage, and a stable
automation environment. The CCIE-SP master profile was initially validated
with 12 vCPU and 60 GiB RAM. The VM was later expanded to 16 vCPU and roughly
65 GiB visible RAM. Resource measurements, not allocated values alone, decide
whether a profile is safe to start.

## 3. Host and nested-virtualization checks

Run these checks before installing or starting a lab:

```bash
uname -a
cat /etc/os-release
nproc
free -h
df -h / /srv/netlab
uptime
systemd-detect-virt
ls -l /dev/kvm

test -r /sys/module/kvm_amd/parameters/nested && \
  cat /sys/module/kvm_amd/parameters/nested
test -r /sys/module/kvm_intel/parameters/nested && \
  cat /sys/module/kvm_intel/parameters/nested
```

Expected results are a readable `/dev/kvm`, nested virtualization enabled, no
swap pressure, and sufficient free space under `/srv/netlab`. Run only one
heavy profile (`master`, `inter-as`, or `srv6`) at a time.

## 4. Directory preparation

```bash
sudo mkdir -p \
  /srv/netlab/docker \
  /srv/netlab/images/cisco/xrd/24.2.11 \
  /srv/netlab/images/cisco/iol/17.12.01 \
  /srv/netlab/labs \
  /srv/netlab/backups

sudo chown -R "$USER":"$USER" \
  /srv/netlab/images \
  /srv/netlab/labs \
  /srv/netlab/backups
```

The licensed-image staging directory is deliberately outside the Git working
copy. The root `.gitignore` also rejects common image extensions as a second
control.

## 5. Docker Engine installation

Install Docker Engine from Docker's official Ubuntu repository:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo docker run --rm hello-world
```

Optional non-root access:

```bash
sudo usermod -aG docker "$USER"
```

Log out and back in before testing `docker version`. Membership in the Docker
group grants root-equivalent control of the host; add only trusted operators.

## 6. Dedicated Docker storage

Large NOS layers must not fill the Ubuntu root filesystem. On a new host,
configure the Docker data root before importing images:

```bash
sudo install -d -m 0755 /etc/docker
sudoedit /etc/docker/daemon.json
```

Use valid JSON:

```json
{
  "data-root": "/srv/netlab/docker"
}
```

Then restart and verify:

```bash
sudo systemctl restart docker
docker info --format 'root={{.DockerRootDir}} driver={{.Driver}}'
docker system df
df -h /srv/netlab
```

If Docker already contains images or containers, do not change `data-root`
blindly. Stop Docker, back up the existing state, perform a controlled copy,
and verify the new root before removing the old data. The validated result was
`/srv/netlab/docker` with the `overlay2` storage driver.

## 7. Containerlab installation

The environment was validated with Containerlab `0.77.0`. The reproducible
choice is to request that version explicitly:

```bash
bash -c "$(curl -sL https://get.containerlab.dev)" -- -v 0.77.0
containerlab version
```

Review remote installation scripts before executing them. Containerlab also
publishes deb/rpm packages for controlled package-based installation.

## 8. Transfer licensed images from Windows

The authorized source files were stored on Windows under `E:\Cisco-images`.
They were copied to the isolated staging directory, not into this repository.

First calculate hashes in PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 `
  "E:\Cisco-images\xrd-control-plane-container-x86.24.2.11.tgz"

Get-FileHash -Algorithm SHA256 `
  "E:\Cisco-images\<authorized-iol-binary>"
```

Copy with OpenSSH/SCP:

```powershell
scp "E:\Cisco-images\xrd-control-plane-container-x86.24.2.11.tgz" `
  daniel@netlab-core:/srv/netlab/images/cisco/xrd/24.2.11/

scp "E:\Cisco-images\<authorized-iol-binary>" `
  daniel@netlab-core:/srv/netlab/images/cisco/iol/17.12.01/
```

An IP address may replace `netlab-core` when local DNS is unavailable. On the
Ubuntu VM, calculate the hashes again and compare them with the PowerShell
values:

```bash
sha256sum /srv/netlab/images/cisco/xrd/24.2.11/*
sha256sum /srv/netlab/images/cisco/iol/17.12.01/*
```

A mismatched hash stops the process. Do not import or build from a truncated
or modified artifact.

## 9. Import the Cisco XRd image

XRd was supplied as a vendor container archive, so it did not require
vrnetlab wrapping:

```bash
docker load --input \
  /srv/netlab/images/cisco/xrd/24.2.11/xrd-control-plane-container-x86.24.2.11.tgz

docker image ls --digests | grep -Ei 'xrd|ios-xr'
```

If the archive loads with a different local repository or tag, identify the
loaded reference from the preceding output and add the tag expected by the
topologies:

```bash
docker tag <loaded-xrd-reference> ios-xr/xrd-control-plane:24.2.11
```

Record immutable local evidence:

```bash
docker image inspect ios-xr/xrd-control-plane:24.2.11 \
  --format 'id={{.Id}} created={{.Created}} size={{.Size}}'
```

The validated local XRd image ID was recorded during acceptance, but the image
itself is never pushed to GitHub.

## 10. Build the Cisco IOL-XE vrnetlab image

The supplied folder name suggested `17.15.01`, but CLI verification identified
the software as IOS XE Dublin `17.12.1`. The build input and Docker tag therefore
use the truthful version `17.12.01`.

Install build tools and clone vrnetlab outside the lab repository:

```bash
sudo apt-get update
sudo apt-get install -y git make

cd /srv/netlab/images
git clone https://github.com/srl-labs/vrnetlab.git
cd vrnetlab/cisco/iol
```

Copy the authorized IOL executable into this directory and rename it according
to vrnetlab's required convention:

```bash
cp /srv/netlab/images/cisco/iol/17.12.01/<authorized-iol-binary> \
  ./cisco_iol-17.12.01.bin

make docker-image
docker image inspect vrnetlab/cisco_iol:17.12.01 \
  --format 'id={{.Id}} created={{.Created}} size={{.Size}}'
```

The `.bin` suffix and filename convention are significant to the upstream
Makefile. Confirm the real version from the CLI after the canary boots; never
trust an arbitrary source-folder name over `show version`.

## 11. Required image inventory

Before deployment:

```bash
docker image ls --format '{{.Repository}}:{{.Tag}} | {{.ID}} | {{.Size}}' |
  grep -E 'ios-xr/xrd-control-plane:24.2.11|vrnetlab/cisco_iol:17.12.01|ccie-sp-automation:1.0'
```

Expected local references:

```text
ios-xr/xrd-control-plane:24.2.11
vrnetlab/cisco_iol:17.12.01
ccie-sp-automation:1.0
```

## 12. Build AUTO1

AUTO1 is built from source in `automation/`. It provides Ansible, pyATS/Genie,
Netmiko, Nornir, Scrapli, NETCONF, gNMI, testing utilities, and the Cisco network
collections. NSO itself is not included because it is separately licensed.

Never build this dependency-heavy image while a provider profile is running:

```bash
cd /srv/netlab/labs/ccie-sp-master
./labctl status

docker ps --format '{{.Names}}' | grep '^clab-' && {
  echo 'ABORT: a Containerlab profile is active'
  exit 1
}

docker build --pull \
  --tag ccie-sp-automation:1.0 \
  automation/
```

Verify the toolchain without starting SSH or exposing a password:

```bash
docker run --rm \
  --entrypoint /opt/venv/bin/python \
  ccie-sp-automation:1.0 \
  -c 'import pyats, genie, netmiko, nornir, scrapli, ncclient, pygnmi; print("AUTO1 Python stack OK")'

docker run --rm \
  --entrypoint /opt/venv/bin/ansible \
  ccie-sp-automation:1.0 \
  --version

docker image inspect ccie-sp-automation:1.0 \
  --format 'id={{.Id}} created={{.Created}} size={{.Size}}'
```

## 13. Runtime credentials and AUTO1 lifecycle

Copy the template and edit only the ignored `.env` file:

```bash
cd /srv/netlab/labs/ccie-sp-master
cp .env.example .env
chmod 0600 .env
${EDITOR:-nano} .env

set -a
source .env
set +a
```

`automation/entrypoint.sh` requires `AUTO1_PASSWORD` or
`AUTO1_PASSWORD_FILE`, sets the disposable `student` password at container
startup, removes the variable from the shell, generates SSH host keys, and
starts `sshd`. Credentials are runtime inputs and are not baked into the image
or committed to Git.

AUTO1 is already declared in each generated topology. Deploy through the
profile lifecycle rather than creating an unmanaged duplicate:

```bash
./labctl status
./labctl deploy master
./labctl inspect master
```

Access and validate:

```bash
ssh student@10.201.255.150

docker exec clab-ccie-sp-master-AUTO1 \
  bash -lc 'export PATH=/opt/venv/bin:$PATH; ansible --version; python --version'
```

From AUTO1, the repository is mounted as the automation workspace. Follow
[`AUTO1-SOURCE-OF-TRUTH.md`](AUTO1-SOURCE-OF-TRUTH.md) for render, check-mode,
diff, deployment, post-check, and backup workflows.

## 14. Clone and operate the repository

```bash
cd /srv/netlab/labs
git clone https://github.com/dfonquet/ccie-sp-master-lab.git
cd ccie-sp-master-lab

cp .env.example .env
# Edit .env locally and load it as shown above.

./labctl status
./labctl deploy master
./labctl inspect master
./labctl destroy master
```

Use `inter-as` or `srv6` in place of `master` for the other profiles. `labctl`
refuses to deploy a second heavy profile while another Containerlab lab is
active.

## 15. Acceptance checklist

```bash
docker version
containerlab version
docker info --format 'root={{.DockerRootDir}} driver={{.Driver}}'
docker system df
ls -l /dev/kvm
free -h
uptime
./labctl status
```

Before considering a deployment accepted, record:

- Host OS, CPU count, RAM, swap, `/dev/kvm`, and nested-virtualization state.
- Docker and Containerlab versions.
- Image references, IDs, creation dates, sizes, and source-file SHA-256 hashes.
- Node count, management reachability, CLI version, restart count, and OOM state.
- CPU, RAM, swap, and load after the startup window.
- Any platform limitation such as XRd Control Plane BFD behavior.

## 16. Common mistakes prevented by this design

- Do not place NOS images under the Git repository.
- Do not publish vendor artifacts, license material, `.env`, backups, or keys.
- Do not infer an IOL release from the Windows folder name; verify the CLI.
- Do not build AUTO1 while XRd/vMX profiles are consuming the host.
- Do not run multiple heavy profiles simultaneously.
- Do not use `docker restart` on vrnetlab nodes with live links; use the
  Containerlab lifecycle because an unmanaged restart can lose virtual links.
- Do not remove old Docker data until the new `data-root` is verified.

## References

- [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Docker daemon configuration](https://docs.docker.com/engine/daemon/)
- [Docker post-installation](https://docs.docker.com/engine/install/linux-postinstall/)
- [Containerlab installation](https://containerlab.dev/install/)
- [Containerlab Cisco XRd kind](https://containerlab.dev/manual/kinds/cisco_xrd/)
- [Containerlab vrnetlab kinds](https://containerlab.dev/manual/vrnetlab/)
- [vrnetlab](https://github.com/srl-labs/vrnetlab)
- [vrnetlab Cisco IOL build instructions](https://github.com/srl-labs/vrnetlab/tree/master/cisco/iol)
