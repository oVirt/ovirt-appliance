# vim: et sts=2 sw=2

set -x

export ARTIFACTSDIR=$PWD/exported-artifacts

build() {
  bash -xe ci/pre.sh
  bash -xe ci/build.sh
  bash -xe ci/test.sh

  mkdir "$ARTIFACTSDIR"

  mv -v \
    *.qcow2 \
    *.squashfs.img \
    *.log \
    *-manifest-rpm \
    "$ARTIFACTSDIR/"

  ls -shal "$ARTIFACTSDIR/" || :
}

prepare_boot() {
  # The squashfs url is now pointing to the image in the jenkins instance
  local SQUASHFS_URL="$JOB_URL/lastSuccessfulBuild/artifact/exported-artifacts/ovirt-node-appliance.squashfs.img"

  # Also update the kickstarts to point to that url
  sed "s#@SQUASHFS_URL@#$SQUASHFS_URL#" interactive-installation.ks.in > interactive-installation.ks
  sed "s#@SQUASHFS_URL@#$SQUASHFS_URL#" auto-installation.ks.in > auto-installation.ks
  sed -i -e "/http_proxy=/ d" -e "s/^poweroff/reboot/" *-installation.ks

  # Fetch the installer image of Fedora 21, can get removed once CentOS 7.1 is released
  bash image-tools/bootstrap_anaconda fedora 21

  mv -v \
    *.ks .treeinfo \
    "$ARTIFACTSDIR/"

  # FIXME these files should to go to images/ at some point as well
  mv -v \
    vmlinuz initrd.img squashfs.img upgrade.img \
    "$ARTIFACTSDIR/"

  mkdir -p "$ARTIFACTSDIR/images/"

  ls -shal "$ARTIFACTSDIR/" "$ARTIFACTSDIR/images" || :
}

build
prepare_boot
