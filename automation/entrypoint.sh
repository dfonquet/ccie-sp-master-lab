#!/usr/bin/env bash
set -euo pipefail

if [[ -n "${AUTO1_PASSWORD_FILE:-}" ]]; then
  AUTO1_PASSWORD="$(<"${AUTO1_PASSWORD_FILE}")"
fi

: "${AUTO1_PASSWORD:?Set AUTO1_PASSWORD or AUTO1_PASSWORD_FILE at runtime}"
printf 'student:%s\n' "${AUTO1_PASSWORD}" | chpasswd
unset AUTO1_PASSWORD

ssh-keygen -A
exec /usr/sbin/sshd -D -e
