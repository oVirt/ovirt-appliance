.SECONDARY: rootfs.qcow2 rootfs.ks

# FIXME Stick to Fedora until this is solved: http://bugs.centos.org/view.php?id=8239
DISTRO=fedora
RELEASEVER=21

# Builds the rootfs
image-build: rootfs.qcow2

# Simulates an auto-installation
image-install: SQUASHFS_URL="@HOST_HTTP@/rootfs.squashfs.img"
image-install: auto-installation.ks.in
	[[ -f rootfs.squashfs.img ]]
	sed "s#@ROOTFS_URL@#$(SQUASHFS_URL)#" auto-installation.ks.in > auto-installation.ks
	$(MAKE) -f image-tools/build.mk DISTRO=$(DISTRO) RELEASEVER=$(RELEASEVER) DISK_SIZE=$$(( 10 * 1024 )) SPARSE= installed.qcow2

verrel:
	@bash image-tools/image-verrel rootfs NodeAppliance org.ovirt.node

#check: QCOW_CHECK=installation.qcow2
#check:
#	[[ -f "$(QCOW_CHECK)" ]] && make -f tests/runtime/Makefile check-local IMAGE=$(QCOW_CHECK) || :


%.qcow2: %.ks
# Ensure that the url line contains the distro
	egrep -q "^url .*$(DISTRO)" $<
	make -f image-tools/build.mk DISTRO=$(DISTRO) RELEASEVER=$(RELEASEVER) $@

%.squashfs.img: %.qcow2
	 make -f image-tools/build.mk $@
	unsquashfs -ll $@

%-manifest-rpm: %.qcow2
	 make -f image-tools/build.mk $@
