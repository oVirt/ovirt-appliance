
#
# How it works:
# 1. Inherit from Fedora Cloud images with modifications
# 2. Use Fedora 19 boot iso to run lmc
# 3. Create runtime image (qcow2)
# 4. sysprep, sparsify and comvert runtime image to ova
#

MAIN_NAME ?= ovirt-appliance-fedora

VM_CPUS ?= 4
VM_RAM ?= 4096
VM_DISK ?= 4000

# Units can be used here
VM_GROWSIZE ?= 50GB

OVA_RAM ?= 16384
OVA_CPUS ?= $(VM_CPUS)

LMC ?= livemedia-creator
LMC_COMMON_ARGS = --ram=$(VM_RAM) --vcpus=$(VM_CPUS)

BOOTISO ?= boot.iso

SUDO := sudo 
TMPDIR := /var/tmp

.SECONDARY:


all: $(MAIN_NAME).ova
	echo "$(MAIN_NAME)" appliance done


boot.iso:
	curl -L -O http://download.fedoraproject.org/pub/fedora/linux/releases/19/Fedora/x86_64/os/images/boot.iso


%.ks: %.ks.tpl
	ksflatten $< > $@
	sed -i \
		-e "/^[-]/ d" \
		-e "/^text/ d" \
		-e "s/^part .*/part \/ --size $(VM_DISK) --fstype ext4/" \
		-e "s/^network .*/network --activate/" \
		-e "s/^%packages.*/%packages --ignoremissing/" \
		-e "/default\.target/ s/^/#/" \
		-e "/RUN_FIRSTBOOT/ s/^/#/" \
		-e "/remove authconfig/ s/^/#/" \
		-e "/remove linux-firmware/ s/^/#/" \
		-e "/remove firewalld/ s/^/#/" \
		-e "/^bootloader/ s/bootloader .*/bootloader --location=mbr --timeout=1/" \
		-e "/rawhide/ s/^/#/" \
		-e "/repo --name=\"fedora\"/ s/^repo.*http:/url --mirrorlist=http:/" \
		$@


%.raw: %.ks boot.iso
	$(SUDO) -E $(LMC) --make-disk --iso "$(BOOTISO)" --ks "$<" --image-name "$@" $(LMC_COMMON_ARGS)
	$(SUDO) mv $(TMPDIR)/"$@" .

	# Legacy way:
	#$(SUDO) -E LANG=C LC_ALL=C image-creator -c $< --compression-type=xz -v -d --logfile $(shell pwd)/image.log


%.qcow2: %.raw
	$(SUDO) -E virt-sparsify --compress --convert qcow2 "$<" "$@"
	# FIXME selinux relable must hapen before init-label, before we cna enable
	# relable
	$(SUDO) -E virt-sysprep --no-selinux-relabel --add "$@"
	$(SUDO) qemu-img resize "$@" $(VM_GROWSIZE)

%.ova: %.qcow2
	$(SUDO) python scripts/create_ova.py -m $(OVA_RAM) -c $(OVA_CPUS) "$*.qcow2" "$@"


clean: clean-log
	echo

clean-log:
	rm -f *.log
