
#
# How it works:
# 1. Inherit from Fedora Cloud images with modifications
# 2. Use Fedora 19 boot iso to run lmc
# 3. Create runtime image (qcow2)
# 4. sysprep, sparsify and comvert runtime image to ova
#

VM_DISK ?= 10000

OVA_RAM ?= 16384
OVA_CPUS ?= 4

ARCH=x86_64
DISTRO=fedora
RELEASEVER=21

PYTHON ?= PYTHONPATH="$(PWD)/imagefactory/" python

.SECONDARY:
.PHONY: $(wildcard *.ks.tpl)

all: ovirt-engine-appliance.ova
	echo "$@" appliance done

#%.ks: %.ks.tpl
#	ksflatten -c $< > $@
#	-[ -n "$$http_proxy" ] && sed -i "s/--proxy\S*/--proxy=$$http_proxy/g" $@
#	-[ -z "$$http_proxy" ] && sed -i "s/--proxy\S*//g" $@
#	sed -i \
#	 -e "s/^part .*/part \/ --size $(VM_DISK) --fstype ext4 --fsoptions discard/" \
#	 -e "s/^%packages.*/%packages --ignoremissing/" \
#	 -e "/^reboot/ s/reboot/poweroff/" \
#	 $@


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
