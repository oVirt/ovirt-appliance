#!/usr/bin/bash

set -ex

export PATH=$PATH:/sbin/:/usr/sbin/

make ovirt-node-appliance.squashfs.img
[[ -n "$SQUASHFS_URL" ]] && make image-install SQUASHFS_URL=$SQUASHFS_URL || make image-install

mv anaconda.log anaconda-install.log

IMG="$(make verrel).squashfs.img"
ln -v ovirt-node-appliance.squashfs.img $IMG

# Create an index file for imgbase remote
ls -1 > .index

make check
