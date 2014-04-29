%include fedora-cloud-base.ks

%packages
kernel
%end

%post
if [ ! -e /etc/sysconfig/kernel ]; then
echo "Creating /etc/sysconfig/kernel."
cat <<EOF > /etc/sysconfig/kernel
# UPDATEDEFAULT specifies if new-kernel-pkg should make
# new kernels the default
UPDATEDEFAULT=yes

# DEFAULTKERNEL specifies the default kernel package type
DEFAULTKERNEL=kernel
EOF
fi
