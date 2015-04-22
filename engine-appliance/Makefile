
#
# How it works:
# 1. Inherit from Fedora Cloud images with modifications
# 2. Use Fedora 19 boot iso to run lmc
# 3. Create runtime image (qcow2)
# 4. sysprep, sparsify and comvert runtime image to ova
#

# This size must be full GB, in MB
VM_DISK ?= $(shell expr 10 * 1024)

OVA_RAM ?= 16384
OVA_CPUS ?= 4

ARCH=x86_64
DISTRO=centos
RELEASEVER=7

PYTHON ?= PYTHONPATH="$(PWD)/imagefactory/" python

.SECONDARY:
.PHONY: $(wildcard *.ks.tpl)

all: ovirt-engine-appliance.ova
	echo "$@" appliance done

%.qcow2: %.ks
	make -f image-tools/build.mk $@ DISTRO=$(DISTRO) RELEASEVER=$(RELEASEVER) DISK_SIZE=$(VM_DISK)
	ls -shal $@

%.squashfs.img: %.qcow2
	make -f image-tools/build.mk $@
	ls -shal $@

%.ova: %.qcow2
	$(SUDO) $(PYTHON) scripts/create_ova.py -m $(OVA_RAM) -c $(OVA_CPUS) "$*.qcow2" "$@"
	ls -shal $@

verrel:
	@bash image-tools/image-verrel rootfs oVirtEngineAppliance org.ovirt.engine
