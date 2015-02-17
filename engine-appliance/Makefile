
#
# How it works:
# 1. Inherit from Fedora Cloud images with modifications
# 2. Use Fedora 19 boot iso to run lmc
# 3. Create runtime image (qcow2)
# 4. sysprep, sparsify and comvert runtime image to ova
#

VM_CPUS ?= 4
VM_RAM ?= 4096
VM_DISK ?= 3000

OVA_RAM ?= 16384
OVA_CPUS ?= $(VM_CPUS)

ARCH=x86_64
RELEASEVER=19

PYTHON ?= PYTHONPATH="$(PWD)/imagefactory/" python

.SECONDARY:
.PHONY: $(wildcard *.ks.tpl)

all: ovirt-engine-appliance.ova
	echo "$@" appliance done

%.ks: %.ks.tpl
	ksflatten -c $< > $@
	-[ -n "$$http_proxy" ] && sed -i "s/--proxy\S*/--proxy=$$http_proxy/g" $@
	-[ -z "$$http_proxy" ] && sed -i "s/--proxy\S*//g" $@
	sed -i \
	 -e "s/^part .*/part \/ --size $(VM_DISK) --fstype ext4 --fsoptions discard/" \
	 -e "s/^%packages.*/%packages --ignoremissing/" \
	 -e "/^reboot/ s/reboot/poweroff/" \
	 $@


%.qcow2: %.ks
	make -f image-tools/build.mk $@ RELEASEVER=$(RELEASEVER) DISK_SIZE=$$(( $(VM_DISK) / 1000 ))G

%.squashfs.img:
	make -f image-tools/build.mk $@

%.ova: %.qcow2
	$(SUDO) $(PYTHON) scripts/create_ova.py -m $(OVA_RAM) -c $(OVA_CPUS) "$*.qcow2" "$@"

verrel:
	@bash image-tools/image-verrel rootfs oVirtEngineAppliance org.ovirt.engine
