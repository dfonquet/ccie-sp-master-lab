FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PATH=/opt/venv/bin:$PATH \
    ANSIBLE_COLLECTIONS_PATH=/usr/share/ansible/collections \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash-completion \
        ca-certificates \
        curl \
        dnsutils \
        git \
        iproute2 \
        iputils-ping \
        jq \
        less \
        nano \
        net-tools \
        openssh-client \
        openssh-server \
        openssl \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        snmp \
        sudo \
        tcpdump \
        traceroute \
        vim \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.yml /tmp/

RUN python3 -m venv /opt/venv \
    && pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && mkdir -p /usr/share/ansible/collections \
    && ansible-galaxy collection install \
        -p /usr/share/ansible/collections \
        -r /tmp/requirements.yml \
    && useradd --create-home --shell /bin/bash student \
    && echo 'student:ccie@123' | chpasswd \
    && usermod -aG sudo student \
    && printf 'student ALL=(ALL) NOPASSWD:ALL\n' >/etc/sudoers.d/student \
    && chmod 0440 /etc/sudoers.d/student \
    && mkdir -p /run/sshd /workspace \
    && chown student:student /workspace \
    && rm -f /etc/ssh/ssh_host_* \
    && sed -ri 's/^#?PasswordAuthentication .*/PasswordAuthentication yes/' \
        /etc/ssh/sshd_config \
    && sed -ri 's/^#?PermitRootLogin .*/PermitRootLogin no/' \
        /etc/ssh/sshd_config

RUN printf '%s\n' 'export PATH=/opt/venv/bin:$PATH' \
        >>/home/student/.bashrc \
    && printf '%s\n' 'export PATH=/opt/venv/bin:$PATH' \
        >>/home/student/.profile \
    && chown student:student /home/student/.bashrc /home/student/.profile

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod 0755 /usr/local/bin/entrypoint.sh

WORKDIR /workspace
EXPOSE 22
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
