#!/usr/bin/env bash
set -euo pipefail

# host keys
ssh-keygen -A

# install authorized_keys if mounted
if [ -f /tmp/authorized_keys ]; then
  install -d -m 700 -o dev -g dev /home/dev/.ssh
  install -m 600 -o dev -g dev /tmp/authorized_keys /home/dev/.ssh/authorized_keys
fi

exec /usr/sbin/sshd -D -e
