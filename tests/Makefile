
#
## A (probably incomplete) list of packages which need to be installed on the host
#
PKG_DEPS = libvirt-daemon libvirt-client libvirt-daemon-qemu libvirt-daemon-kvm python-sh virt-install libguestfs libguestfs-tools openssh-clients python-pep8 pyflakes

NODE_IMG_FILE = ovirt-node-appliance.qcow2
ENGINE_IMG_FILE = ovirt-engine-appliance.qcow2

export TEST_NODE_ROOTFS_IMG=$(PWD)/../node-appliance/$(NODE_IMG_FILE)
export TEST_ENGINE_ROOTFS_IMG=$(PWD)/../engine-appliance/$(ENGINE_IMG_FILE)

check:
	@pyflakes *.py
	@pep8 *.py
	nosetests --with-xunit -v --no-byte-compile -w .
	-xsltproc nosetests.xslt nosetests.xml

install-deps:
	yum install -y $(PKG_DEPS)

build-recursive:
	cd ../node-appliance/ && make $(NODE_IMG_FILE)
	cd ../engine-appliance/ && make $(ENGINE_IMG_FILE)

check-recursive:
	cd ../node-appliance/ && make check
	cd ../engine-appliance/ && make check

clean-recursive:
	cd ../node-appliance/ && make clean
	cd ../engine-appliance/ && make clean

clean-build-and-check: | clean-recursive build-recursive check-recursive check
	echo PASSED
