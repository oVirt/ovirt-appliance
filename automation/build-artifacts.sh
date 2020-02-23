#!/bin/bash -xe
echo "build-artifacts.sh"

df -h || :
#this scripts build ovirt-node and ovirt-node-is projects
[[ ! -c /dev/kvm ]] && mknod /dev/kvm c 10 232
export PATH=$PATH:/usr/libexec
export ARTIFACTSDIR=$PWD/exported-artifacts
#export http_proxy=proxy.phx.ovirt.org:3128

move_logs() {
        mv -v *.{log,ks} "$ARTIFACTSDIR/"
}

trap move_logs EXIT

seq 0 9 | xargs -I {} mknod /dev/loop{} b 7 {} || :

git submodule update --init --recursive --force --remote

# Enter the Engine Appliance
pushd engine-appliance

 mkdir tmp
 export TMPDIR="$PWD/tmp/"
 export PYTHON="python3"
 export OVANAME="oVirt-Engine-Appliance-CentOS-x86_64-8-$(date +%Y%m%d%H%M%S)"
 export QEMU_APPEND="ip=dhcp proxy="

 export PATH=$PATH:/sbin:/usr/sbin
 export TMPDIR=/var/tmp/

 mkdir "$ARTIFACTSDIR"

 dist="$(rpm --eval %{dist})"
 # Create the OVA
 if [[ ${dist} = .fc* ]]; then
    fcrel="$(rpm --eval %{fedora})"
    export OVANAME="oVirt-Engine-Appliance-Fedora-x86_64-${fcrel}-$(date +%Y%m%d%H%M%S)"
    make FC_RELEASE=${fcrel} &
 else
    make &
 fi
 tail -f virt-install.log --pid=$! --retry ||:

 tar tvf ovirt-engine-appliance.ova

 # Do some sanity checks
 make check

 [[ -f ovirt-engine-appliance.ova ]] && ln -v ovirt-engine-appliance.ova "$ARTIFACTSDIR"/"${OVANAME}.ova"
 [[ -f ovirt-engine-appliance.qcow2 ]] && ln -v ovirt-engine-appliance.qcow2 "$ARTIFACTSDIR"/
 [[ -f ovirt-engine-appliance-manifest-rpm ]] && ln -v ovirt-engine-appliance-manifest-rpm "$ARTIFACTSDIR"/
 [[ -f ovirt-engine-appliance-unsigned-rpms ]] && ln -v ovirt-engine-appliance-unsigned-rpms "$ARTIFACTSDIR"/

 # Finally, create the rpm
 make ovirt-engine-appliance.rpm

 mv -v \
   "$HOME"/rpmbuild/RPMS/*/*.rpm \
   "$HOME"/rpmbuild/SRPMS/*.rpm \
   "$ARTIFACTSDIR/"
 ls -shal "$ARTIFACTSDIR/" || :
