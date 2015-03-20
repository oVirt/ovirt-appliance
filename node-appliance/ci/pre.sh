#!/usr/bin/bash

set -ex

export PATH=$PATH:/sbin:/usr/sbin
export TMPDIR=/var/tmp/

git submodule update --init --recursive
