
firstboot --reconfig --enable
user --name=admin --plaintext --password=ovirt --groups=wheel

# Fedora
#repo --name=fedora --mirrorlist=http://mirrors.fedoraproject.org/mirrorlist?repo=fedora-$releasever&arch=$basearch

#repo --name=ovirt --baseurl=http://resources.ovirt.org/pub/ovirt-3.4/rpm/fc19/
#repo --name=ovirt-snap --baseurl=http://resources.ovirt.org/pub/ovirt-3.5-pre/rpm/fc19/
#repo --name=ovirt-snap-static --baseurl=http://resources.ovirt.org/pub/ovirt-3.4-snapshot-static/rpm/fc19/

# CentOS
#url                    --mirrorlist=http://mirrorlist.centos.org/?release=6&arch=x86_64&repo=os
#url --url=http://mirror.netcologne.de/centos/6.5/os/x86_64/
#repo --name=updates    --mirrorlist=http://mirrorlist.centos.org/?release=6&arch=x86_64&repo=updates
#repo --name=epel       --mirrorlist=https://mirrors.fedoraproject.org/metalink?repo=epel-6&arch=x86_64
#repo --name=ovirt      --baseurl=http://resources.ovirt.org/releases/stable/rpm/EL/6/
#repo --name=gluster   --baseurl=http://download.gluster.org/pub/gluster/glusterfs/3.4/3.4.1/EPEL.repo/epel-6/x86_64/
#repo --name=glusternoarch --baseurl=http://download.gluster.org/pub/gluster/glusterfs/3.4/3.4.1/EPEL.repo/epel-6/noarch

# oVirt
#repo --name=ovirt-repos --baseurl=http://resources.ovirt.org/pub/yum-repo/

%post --erroronfail
#
echo "Preparing initial-setup"
#
yum install -y initial-setup
systemctl enable initial-setup-text.service
systemctl disable initial-setup-graphical.service
%end

%post --erroronfail
#
echo "Installing oVirt stuff"
#
yum install -y http://resources.ovirt.org/pub/yum-repo/ovirt-release35.rpm
###yum install -y ovirt-engine
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
%end

%include fedora-spin-kickstarts/fedora-x86_64-cloud.ks
