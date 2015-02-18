#!/usr/bin/bash

set -ex

sudo yum -y install libguestfs-tools qemu-system-x86 asciidoc python-sh glusterfs gluster squashfs-tools oz
git submodule update --init --recursive
