#!/bin/bash -xe
echo "check-patch.sh"
#this scripts build ovirt-node and ovirt-node-is projects

export ARTIFACTSDIR=$PWD/exported-artifacts
#export http_proxy=proxy.phx.ovirt.org:3128
#update modules
git submodule update --init --recursive --force

#patch to avoid kvm staff we are in mock
sed -i '/-enable-kvm/d' engine-appliance/image-tools/anaconda_install
# Enter the Engine Appliance
pushd engine-appliance

# Build imgfac to build Version.py
pushd .
cd imagefactory
python setup.py sdist
popd

mkdir tmp
export TMPDIR="$PWD/tmp/"
export PYTHON="PYTHONPATH='$PWD/imagefactory/' python"
export OVANAME="oVirt-Engine-Appliance-CentOS-x86_64-7-$(date +%Y%m%d)"
export QEMU_APPEND="ip=dhcp proxy="

df -h || :

bash -xe ci/build.sh
bash -xe ci/check.sh

rm -f *.qcow2 || :

mkdir "$ARTIFACTSDIR"

[[ -f ovirt-engine-appliance.ova ]] && mv -v ovirt-engine-appliance.ova "$ARTIFACTSDIR"/"${OVANAME}.ova"
mv -v \
  anaconda.log \
  "$ARTIFACTSDIR/"

ls -shal "$ARTIFACTSDIR/" || :

popd

# Enter the Engine Appliance
pushd engine-appliance

sed "s#@SQUASHFS_URL@#$JOB_URL/lastSuccessfulBuild/artifact/exported-artifacts/ovirt-engine-appliance.squashfs.img#" interactive-installation.ks.in > interactive-installation.ks

mv -v \
  *.ks \
  .treeinfo \
  "$ARTIFACTSDIR/"

# FIXME these files should to go to images/ at some point as well
bash image-tools/bootstrap_anaconda fedora 21
mv -v \
  vmlinuz initrd.img squashfs.img upgrade.img \
  "$ARTIFACTSDIR/"

rm "$ARTIFACTSDIR"/.treeinfo

ln -v "$ARTIFACTSDIR"/*.ova ovirt-engine-appliance.ova
make ovirt-engine-appliance.rpm

mv -v \
  "$HOME"/rpmbuild/RPMS/*/*.rpm \
  "$HOME"/rpmbuild/SRPMS/*.rpm \
  "$ARTIFACTSDIR/"
