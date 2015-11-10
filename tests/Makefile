
NODE_IMG_FILE = ovirt-node-appliance.qcow2
ENGINE_IMG_FILE = ovirt-engine-appliance.qcow2

export TEST_NODE_ROOTFS_IMG=$(PWD)/../node-appliance/$(NODE_IMG_FILE)
export TEST_ENGINE_ROOTFS_IMG=$(PWD)/../engine-appliance/$(ENGINE_IMG_FILE)

check:
	pyflakes *.py
	pep8 *.py
	nosetests --with-xunit -v --no-byte-compile -w .

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
