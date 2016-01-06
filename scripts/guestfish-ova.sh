#!/usr/bin/bash

err() { echo "ERROR $@" >&2 ; }
info() { echo "INFO  $@" ; }

usage() {
  echo "Usage: $0 OVAFILENAME [<guestfish arguments>]" ;
  echo " Extracts the given OVA, runs guestfish on the image, and creates an OVA again after quitting guestfish." ;
  echo " See 'man guestfish' for all available options." ; }

[[ ! -f "$1" ]] && { usage ; exit 1 ; }


OVA=$(realpath $1)
shift

TMPDIR=$(mktemp -d -p $PWD --suffix "-ova.d")
NEWOVA=${OVA%.ova}-$(date +%Y%m%d%H%M%S).ova

( # Try
  set -e
  cd "$TMPDIR"
  info "Extracting OVA '$OVA' to '$TMPDIR' (this can take a while)"
  tar xf "$OVA"
  IMAGEFILE=$(ls -1 images/*/*.meta | sed "s/\.meta//")
  info "Found image file '$IMAGEFILE', running guestfish"
  info "Once you are done, exit guestfish and the new OVA will be generated"
  guestfish --network -i -a "$IMAGEFILE" $@
  info "Wrapping up new OVA '$NEWOVA' (this can take a while)."
  tar cvzSf "$NEWOVA" *
)
test $? -gt 0 && { # Except
  err "Something failed"
  err "Temporary files: $TMPDIR"
  err "New OVA: $NEWOVA"
  exit 1
}

# Finally
rm -rf "$TMPDIR"
info "Old OVA: $OVA"
info "New OVA: $NEWOVA"
