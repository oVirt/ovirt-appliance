
set -x

export PATH=$PATH:/sbin:/usr/sbin
export TMPDIR=/var/tmp/

# Create the OVA
make
