#!/bin/bash -xe
echo "build-appliance.sh as $0"

df -h || :
#this scripts build ovirt-node and ovirt-node-is projects
[[ ! -c /dev/kvm ]] && mknod /dev/kvm c 10 232
export PATH=$PATH:/usr/libexec
export ARTIFACTSDIR=$PWD/exported-artifacts
#export http_proxy=proxy.phx.ovirt.org:3128

move_logs() {
        mv -v *.{log,ks} "$ARTIFACTSDIR/" || :
}

trap move_logs EXIT

seq 0 9 | xargs -I {} mknod /dev/loop{} b 7 {} || :

git submodule update --init --recursive --force --remote

export PYTHON="python3"
export QEMU_APPEND="ip=dhcp proxy="
export PATH=$PATH:/sbin:/usr/sbin
export TMPDIR=/var/tmp/

build_and_export_appliance() {
    local target="$1"
    local distro="$2"
    local releasever="$3"
    local appliance_rpm_name="$4"

    # Enter the Engine Appliance
    pushd engine-appliance

    export OVANAME="oVirt-Engine-Appliance-CentOS-x86_64-8-$(date +%Y%m%d%H%M%S)"

    mkdir -p "$target"

    dist="$(rpm --eval %{dist})"
    make RELEASEVER="${releasever}" DISTRO="${distro}" APPLIANCE_RPM_NAME="${appliance_rpm_name}"

    # Move artifacts to target
    [[ -f ovirt-engine-appliance.ova ]] && mv -v ovirt-engine-appliance.ova "$target"/"${OVANAME}.ova"
    [[ -f ovirt-engine-appliance.qcow2 ]] && mv -v ovirt-engine-appliance.qcow2 "$target"
    [[ -f ovirt-engine-appliance-manifest-rpm ]] && mv -v ovirt-engine-appliance-manifest-rpm "$target"
    [[ -f ovirt-engine-appliance-unsigned-rpms ]] && mv -v ovirt-engine-appliance-unsigned-rpms "$target"
    mv -v \
      "$HOME"/rpmbuild/RPMS/*/*.rpm \
      "$HOME"/rpmbuild/SRPMS/*.rpm \
      "$target"
    ls -shal "$target" || :
    mv -v *.{log,ks} "$target"
    make clean
    popd
}

build_and_export_appliance "${ARTIFACTSDIR}" "${DISTRO}" "${RELEASEVER}" "${APPLIANCE_RPM_NAME}"
