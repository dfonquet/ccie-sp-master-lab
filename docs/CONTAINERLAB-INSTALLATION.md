# Containerlab host installation and rationale

## Why Containerlab

Containerlab was selected because the project needs reproducible topology-as-
code, deterministic Linux wiring, Docker-based lifecycle control and direct
integration with Git, Ansible and Python. It complements EVE-NG: EVE-NG is
excellent for interactive GUI labs, while Containerlab makes repeatable builds,
validation and automation easier.

The routing software remains vendor software. Containerlab orchestrates the
containers and links; it does not provide Cisco images or licenses.

## Validated host layout

```text
Windows workstation
└── VMware Workstation
    └── Ubuntu Server VM: netlab-core
        ├── Docker Engine
        ├── Containerlab
        ├── /srv/netlab/docker
        ├── /srv/netlab/labs
        └── /srv/netlab/backups
```

Ubuntu was chosen over the desktop Arch VM for the lab host because it is a
persistent server, already has dedicated `/srv/netlab` storage, and provides a
stable Docker/automation environment. Nested AMD-V/KVM was verified before XRd
deployment.

## Host prerequisites

```bash
uname -a
cat /etc/os-release
nproc
free -h
df -h /srv/netlab
systemd-detect-virt
ls -l /dev/kvm
```

Recommended for this repository: 12 vCPU, 60 GiB RAM, nested virtualization,
at least 100 GB free on `/srv/netlab`, and one heavy profile at a time.

## Docker Engine

Install Docker from Docker's official Ubuntu repository, then verify it. Do not
copy commands from an untrusted convenience script without reviewing it.

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" |
  sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

sudo systemctl enable --now docker
sudo docker version
```

## Containerlab

Use the official installation method and pin/record the version used for lab
validation. The project was validated with 0.77.0.

```bash
bash -c "$(curl -sL https://get.containerlab.dev)"
containerlab version
```

For controlled environments, download a specific release from GitHub, verify
its checksum and install the binary through package management instead of
executing the convenience script.

## Storage placement

Docker data was placed on the dedicated `/srv/netlab` filesystem so large Cisco
layers do not fill the Ubuntu root volume. Before changing Docker's data root,
stop Docker, back up the existing state and follow Docker's documented daemon
configuration procedure. The validated result was:

```text
DockerRootDir=/srv/netlab/docker
StorageDriver=overlay2
```

Verify with:

```bash
docker info --format 'root={{.DockerRootDir}} driver={{.Driver}}'
docker system df
df -h "$(docker info --format '{{.DockerRootDir}}')"
```

## Image preparation

The repository expects locally licensed images:

```text
ios-xr/xrd-control-plane:24.2.11
vrnetlab/cisco_iol:17.12.01
ccie-sp-automation:1.0
```

XRd was loaded from the vendor TAR and recorded by immutable local image ID.
IOL was packaged with vrnetlab. Images, license material and credentials are
excluded from Git.

## Repository deployment model

```bash
git clone https://github.com/dfonquet/ccie-sp-master-lab.git
cd ccie-sp-master-lab
cp .env.example .env
# Edit .env locally; never commit it.

./labctl status
./labctl deploy srv6
./labctl inspect srv6
./labctl destroy srv6
```

Environment variables carry credentials at runtime. They are not embedded in
generated topology or configuration files.

## Why profiles are isolated

Master, Inter-AS and SRv6 have separate management subnets and topology files,
but they share the same CPU, RAM and licensed images. Running more than one
heavy profile would create avoidable boot contention. `labctl` therefore
refuses deployment while another Containerlab profile is active.

## References

- [Containerlab installation](https://containerlab.dev/install/)
- [Containerlab Cisco XRd kind](https://containerlab.dev/manual/kinds/cisco_xrd/)
- [Containerlab vrnetlab kinds](https://containerlab.dev/manual/vrnetlab/)
- [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Docker daemon configuration](https://docs.docker.com/engine/daemon/)
- [vrnetlab](https://github.com/srl-labs/vrnetlab)
