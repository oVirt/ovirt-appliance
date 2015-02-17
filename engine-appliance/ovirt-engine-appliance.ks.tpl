
%include http://jenkins.ovirt.org/job/fabiand_ovirt-node-tng_image_build_daily_testing/lastSuccessfulBuild/artifact/exported-artifacts/rootfs.ks

user --name=admin --plaintext --password=none --groups=wheel

%packages
initial-setup
dracut-modules-growroot
cloud-init
%end

%post --erroronfail
set -x
systemctl enable initial-setup-text.service || :
systemctl disable initial-setup-graphical.service || :

sed -i "/%wheel.*NOPASSWD/ s/^#//" /etc/sudoers
%end


%post --erroronfail
set -x
yum install -y http://resources.ovirt.org/pub/yum-repo/ovirt-release35.rpm
yum install -y ovirt-engine ovirt-guest-agent

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
