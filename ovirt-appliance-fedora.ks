%include fedora-spin-kickstarts/fedora-x86_64-cloud.ks

#repo --name=ovirt     --baseurl=http://resources.ovirt.org/releases/stable/rpm/EL/6/
#repo --name=gluster   --baseurl=http://download.gluster.org/pub/gluster/glusterfs/3.4/3.4.1/EPEL.repo/epel-6.5/x86_64/
#repo --name=glusternoarch --baseurl=http://download.gluster.org/pub/gluster/glusterfs/3.4/3.4.1/EPEL.repo/epel-6.5/noarch/

#url                    --mirrorlist=http://mirrorlist.centos.org/?release=6&arch=x86_64&repo=os
url --url=http://mirror.netcologne.de/centos/6.5/os/x86_64/
repo --name=updates    --mirrorlist=http://mirrorlist.centos.org/?release=6&arch=x86_64&repo=updates
repo --name=epel       --mirrorlist=https://mirrors.fedoraproject.org/metalink?repo=epel-6&arch=x86_64
repo --name=ovirt      --baseurl=http://resources.ovirt.org/releases/stable/rpm/EL/6/
#repo --name=gluster   --baseurl=http://download.gluster.org/pub/gluster/glusterfs/3.4/3.4.1/EPEL.repo/epel-6/x86_64/
#repo --name=glusternoarch --baseurl=http://download.gluster.org/pub/gluster/glusterfs/3.4/3.4.1/EPEL.repo/epel-6/noarch

%packages
@basic-desktop-environment
@gnome-desktop-environment
%end

%post
