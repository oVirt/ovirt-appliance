#!/bin/bash -xe

ova=$1
rpmdir=$2
remote_dir=$(basename ${rpmdir})

tmpdir=$(mktemp -dp /var/tmp)
tar -C ${tmpdir} -xf ${ova}
qcow=$(find ${tmpdir}/images -type f ! -name "*.meta")

export LIBGUESTFS_BACKEND=direct

guestfish <<_EOF_
 add ${qcow}
 run
 mount /dev/ovirt/root /
 mount /dev/ovirt/var /var
 mount /dev/ovirt/log /var/log
 mount /dev/ovirt/tmp /tmp
 mount /dev/ovirt/audit /var/log/audit
 copy-in ${rpmdir} /tmp/
 sh "rpm -Uhv /tmp/${remote_dir}/*.rpm --force --nodeps"
 umount-all
_EOF_

pushd ${tmpdir}
tar -cvzf ${OLDPWD}/NEW-${ova} *
popd

rm -rf ${tmpdir}
