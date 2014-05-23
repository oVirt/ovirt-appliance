
firstboot --reconfig
user --name=admin --plaintext --password=none --groups=wheel

%packages
initial-setup
%end

%post --erroronfail
#
echo "Preparing initial-setup"
#
yum install -y initial-setup plymouth
touch /etc/reconfigSys
systemctl enable initial-setup-text.service
systemctl disable initial-setup-graphical.service

# Default tty is ttyS0, to display initial-setup on tty0 we need to set this explicitly
sed -i \
  -e "/^StandardOutput/ a TTYPath=/dev/tty0" \
  -e "/^Description/ a Before=cloud-init-local.service cloud-init.service" \
  /usr/lib/systemd/system/initial-setup-text.service
%end

%post --erroronfail
#
echo "Pre-Installing oVirt stuff"
#
yum install -y http://resources.ovirt.org/pub/yum-repo/ovirt-release35.rpm
yum install -y ovirt-engine

#
echo "Creating a partial answer file"
#
cat > /root/ovirt-engine-answers <<__EOF__
[environment:default]
OVESETUP_CORE/engineStop=none:None
OVESETUP_DIALOG/confirmSettings=bool:True
OVESETUP_DB/database=str:engine
OVESETUP_DB/fixDbViolations=none:None
OVESETUP_DB/secured=bool:False
OVESETUP_DB/securedHostValidation=bool:False
OVESETUP_DB/host=str:localhost
OVESETUP_DB/user=str:engine
OVESETUP_DB/port=int:5432
OVESETUP_SYSTEM/nfsConfigEnabled=bool:False
OVESETUP_CONFIG/applicationMode=str:virt
OVESETUP_CONFIG/firewallManager=str:firewalld
OVESETUP_CONFIG/websocketProxyConfig=none:True
OVESETUP_CONFIG/storageType=str:nfs
OVESETUP_PROVISIONING/postgresProvisioningEnabled=bool:True
OVESETUP_APACHE/configureRootRedirection=bool:True
OVESETUP_APACHE/configureSsl=bool:True
OSETUP_RPMDISTRO/requireRollback=none:None
OSETUP_RPMDISTRO/enableUpgrade=none:None
__EOF__
%end

#%post --nochroot
# echo "Copy local stuff into the rootfs"
#cp -r oVirtLiveFiles $INSTALL_ROOT/root
#%end

%post --erroronfail
#
echo "Enabling sudo for wheels"
#
sed -i "/%wheel.*NOPASSWD/ s/^#//" /etc/sudoers
passwd --delete root
passwd --expire root
%end


%include fedora-spin-kickstarts/fedora-cloud-base.ks
