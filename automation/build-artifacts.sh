#!/bin/bash -xe

set -e

df -h || :

export ARTIFACTSDIR=$PWD/exported-artifacts
#export http_proxy=proxy.phx.ovirt.org:3128

git submodule update --init --recursive --force
#patch to avoid kvm staff we are in mock
sed -i '/-enable-kvm/d' engine-appliance/image-tools/anaconda_install

# Enter the Engine Appliance
pushd engine-appliance

 # Build imgfac to build Version.py
 pushd imagefactory
  python setup.py sdist
 popd

 mkdir tmp
 export TMPDIR="$PWD/tmp/"
 export PYTHON="PYTHONPATH='$PWD/imagefactory/' python"
 export OVANAME="oVirt-Engine-Appliance-CentOS-x86_64-7-$(date +%Y%m%d)"
 export QEMU_APPEND="ip=dhcp proxy="

 export PATH=$PATH:/sbin:/usr/sbin
 export TMPDIR=/var/tmp/

 mkdir "$ARTIFACTSDIR"

 # Create the OVA
 make

 # Do some sanity checks
 make check || :

 [[ -f ovirt-engine-appliance.ova ]] && ln -v ovirt-engine-appliance.ova "$ARTIFACTSDIR"/"${OVANAME}.ova"
 [[ -f ovirt-engine-appliance.qcow2 ]] && ln -v ovirt-engine-appliance.qcow2 "$ARTIFACTSDIR"/
 mv -v \
   anaconda.log \
   "$ARTIFACTSDIR/"

 # Finally, create the rpm
 make ovirt-engine-appliance.rpm

 mv -v \
   "$HOME"/rpmbuild/RPMS/*/*.rpm \
   "$HOME"/rpmbuild/SRPMS/*.rpm \
   "$ARTIFACTSDIR/"
 ls -shal "$ARTIFACTSDIR/" || :
