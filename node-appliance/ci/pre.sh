#!/usr/bin/bash

set -ex

export PATH=$PATH:/sbin:/usr/sbin
export TMPDIR=/var/tmp/

sudo yum -y install libguestfs-tools qemu-system-x86 asciidoc python-sh glusterfs gluster squashfs-tools
git submodule update --init --recursive
