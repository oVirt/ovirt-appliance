authselect select minimal
firewall --enabled --service=cockpit
systemctl enable sshd
systemctl enable fstrim.timer
systemctl enable cockpit.socket
systemctl enable qemu-guest-agent

# Install oVirt Packages
dnf -y install ovirt-engine \
            ovirt-engine-dwh \
            ovirt-provider-ovn \
            ovirt-engine-extension-aaa-ldap \
            ovirt-engine-extension-aaa-ldap-setup \
            ovirt-engine-extension-aaa-misc