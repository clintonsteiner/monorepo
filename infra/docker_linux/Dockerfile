FROM redhat/ubi9:latest

RUN dnf -y update \
 && dnf -y install openssh-server openssh-clients sudo procps-ng \
 && dnf -y clean all

# Create user
RUN useradd -m -s /bin/bash dev \
 && echo "dev ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/dev \
 && chmod 0440 /etc/sudoers.d/dev

# SSH hardening (pubkey only)
RUN sed -i \
    -e 's/^#\?PermitRootLogin.*/PermitRootLogin no/' \
    -e 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' \
    -e 's/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' \
    -e 's/^#\?UsePAM.*/UsePAM no/' \
    /etc/ssh/sshd_config

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
