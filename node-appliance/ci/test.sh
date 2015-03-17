#!/usr/bin/bash

set -ex

export PATH=$PATH:/sbin/:/usr/sbin/

[[ -n "$SQUASHFS_URL" ]]

./autogen.sh
./configure

make rootfs.squashfs.img
make image-install SQUASHFS_URL=$SQUASHFS_URL

IMG="$(make verrel).squashfs.img"
ln -v rootfs.squashfs.img $IMG

# Create an index file for imgbase remote
ls -1 > .index

sed -i "/http_proxy=/ d" *-installation.ks

# FIXME No intergration tests available for now
#make check
