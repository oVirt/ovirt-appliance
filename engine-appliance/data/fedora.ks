services --enabled=sshd
url --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=fedora-$releasever&arch=$arch
repo --name=updates --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=updates-released-f$releasever&arch=$arch
# Fixes bz#1594856
updates https://bugzilla.redhat.com/attachment.cgi?id=1454675
