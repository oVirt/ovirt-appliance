#install
#text
keyboard us
lang en_US.UTF-8
#skipx
network --bootproto dhcp
rootpw --plaintext r
firewall --disabled
authconfig --enableshadow --enablemd5
selinux --enforcing
timezone --utc America/New_York
bootloader --location=mbr --append="console=tty0 console=ttyS0,115200"
zerombr
clearpart --all

#part biosboot --fstype=biosboot --size=1
#part /boot --fstype ext4 --size=200 --ondisk=vda
#part pv.2 --size=1 --grow --ondisk=vda
#volgroup VolGroup00 --pesize=32768 pv.2
#logvol swap --fstype swap --name=LogVol01 --vgname=VolGroup00 --size=768 --grow --maxsize=1536
#logvol / --fstype ext4 --name=LogVol00 --vgname=VolGroup00 --size=1024 --grow
part / --fstype ext4 --size 4000
part swap --size 1000
reboot

device xhci-hcd

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
@desktop

# more stuff
bind-utils
-ed
-kexec-tools
-system-config-kdump
-libaio
-libhugetlbfs
-microcode_ctl
-psacct
-quota
-autofs
-smartmontools

@basic-desktop
# package removed from @basic-desktop
-gok

@desktop-platform
# packages removed from @desktop-platform
-redhat-lsb


@fonts

@general-desktop
# package removed from @general-desktop
-gnome-backgrounds
-gnome-user-share
-nautilus-sendto
-orca
-rhythmbox
-vino
-compiz
-compiz-gnome
-evince-dvi
-gnote
-sound-juicer

# @input-methods

@internet-applications
# package added to @internet-applications
# xchat
# packages removed from @internet-applications
-ekiga

@internet-browser

## packages to remove to save diskspace
-scenery-backgrounds
-redhat-lsb-graphics
-qt3
-xinetd
-openswan
-pinentry-gtk
-seahorse
-hunspell-*
-words
-pinfo
-samba-client
-mousetweaks
patch
bridge-utils
net-tools
firefox
m2crypto
seabios
vim
net-tools
bridge-utils
shadow-utils
apr
httpd

## remove some fonts and input methods
# remove Chinese font (Ming face) (8.9 MB)
# we still have wqy-zenhei-fonts 
-cjkuni-fonts-common
-cjkuni-uming-fonts
# remove Korean input method (2.1 MB)
-ibus-hangul
-libhangul

## packages to add
lftp
-thunderbird
#@openafs-client
cups
cups-pk-helper
system-config-printer
system-config-printer-udev
xorg-x11-fonts-100dpi
xorg-x11-fonts-ISO8859-1-100dpi
xorg-x11-fonts-Type1
nautilus-sendto
spice-client
spice-xpi
phonon-backend-gstreamer


%end



%post --nochroot
echo "success nochroot"
%end


%post

sed -i "s/^id:.*/id:5:initdefault:/" /etc/inittab

# https://github.com/garyedwards/spin-kickstarts/blob/master/snippets/autologin-gdm.ks
cat >> /etc/rc.d/init.d/fedora-live << EOF
chown -R ovirt:ovirt /home/ovirt
sed -i -e 's/\[daemon\]/[daemon]\nTimedLoginEnable=true\nTimedLogin=fedora\nTimedLoginDelay=60/' /etc/gdm/custom.conf
if [ -e /usr/share/icons/hicolor/96x96/apps/fedora-logo-icon.png ] ; then
    cp /usr/share/icons/hicolor/96x96/apps/fedora-logo-icon.png /home/fedora/.face
    chown fedora:fedora /home/fedora/.face
    # TODO: would be nice to get e-d-s to pick this one up too... but how?
fi
EOF

echo "success"


%end
