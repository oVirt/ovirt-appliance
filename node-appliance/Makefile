# FIXME Stick to Fedora until this is solved: http://bugs.centos.org/view.php?id=8239
DISTRO=centos
RELEASEVER=7

# Builds the rootfs
image-build: ovirt-node-appliance.qcow2
	cp -v anaconda.log anaconda-$@.log

# Simulates an auto-installation
image-install: SQUASHFS_URL="@HOST_HTTP@/ovirt-node-appliance.squashfs.img"
image-install: ovirt-node-appliance-auto-installation.ks.in ovirt-node-appliance.squashfs.img
	sed -e "s#@SQUASHFS_URL@#$(SQUASHFS_URL)#" ovirt-node-appliance-auto-installation.ks.in > ovirt-node-appliance-auto-installation.ks
	$(MAKE) -f image-tools/build.mk DISTRO=$(DISTRO) RELEASEVER=$(RELEASEVER) DISK_SIZE=$$(( 10 * 1024 )) SPARSE= ovirt-node-appliance-auto-installation.qcow2
	cp -v anaconda.log anaconda-$@.log

verrel:
	@bash image-tools/image-verrel rootfs org.ovirt.Node x86_64

# Direct for virt-sparsify: http://libguestfs.org/guestfs.3.html#backend
export LIBGUESTFS_BACKEND=direct
# Workaround nest problem: https://bugzilla.redhat.com/show_bug.cgi?id=1195278
export LIBGUESTFS_BACKEND_SETTINGS=force_tcg
export TEST_NODE_ROOTFS_IMG=$(PWD)/ovirt-node-appliance.qcow2
export TEST_NODE_SQUASHFS_IMG=$(PWD)/ovirt-node-appliance.squashfs.img
check: ovirt-node-appliance.squashfs.img ovirt-node-appliance.qcow2
	cd tests && nosetests --with-xunit -v -w .


%.qcow2: %.ks
# Ensure that the url line contains the distro
	egrep -q "^url .*$(DISTRO)" $<
	make -f image-tools/build.mk DISTRO=$(DISTRO) RELEASEVER=$(RELEASEVER) $@

%.squashfs.img: %.qcow2
	make -f image-tools/build.mk $@
	unsquashfs -ll $@

%-manifest-rpm: %.qcow2
	 make -f image-tools/build.mk $@
