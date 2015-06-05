
set -x

export PATH=$PATH:/sbin:/usr/sbin
export TMPDIR=/var/tmp/

make check
