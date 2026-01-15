if [[ $(rpm --eval '%{centos_ver}') == '9' ]]; then
    authselect select minimal
else
    authselect select local
fi

systemctl enable firewalld
systemctl enable sshd
systemctl enable fstrim.timer
systemctl enable cockpit.socket
systemctl enable qemu-guest-agent
firewall-offline-cmd --add-service=cockpit

if [[ "$kiwi_profiles" == *"cbs-testing"* ]]; then
    # Enable oVirt Testing Repository
    dnf config-manager --set-enabled centos-ovirt45-testing
    dnf config-manager --set-enabled ovirt-45-upstream-testing
fi

# Install oVirt Packages
dnf -y install ovirt-engine \
            ovirt-engine-dwh \
            ovirt-provider-ovn \
            ovirt-engine-extension-aaa-ldap \
            ovirt-engine-extension-aaa-ldap-setup \
            ovirt-engine-extension-aaa-misc