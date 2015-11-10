
export TEST_NODE_ROOTFS_IMG=$(PWD)/../node-appliance/ovirt-node-appliance.qcow2
export TEST_ENGINE_ROOTFS_IMG=$(PWD)/../engine-appliance/ovirt-engine-appliance.qcow2

check:
	pyflakes *.py
	pep8 *.py
	nosetests --with-xunit -v -w .

check-recursive:
	cd ../node-appliance/ && make check
	cd ../engine-appliance/ && make check
