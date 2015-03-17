auth --enableshadow --passalgo=sha512
selinux --permissive
network --bootproto=dhcp

rootpw --lock
user --name=node --lock

bootloader --timeout=1

liveimg --url=@ROOTFS_URL@
