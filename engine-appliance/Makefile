
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
VM_DISK ?= 8000

# Units can be used here
VM_GROWSIZE ?= 50GB

OVA_RAM ?= 16384
OVA_CPUS ?= $(VM_CPUS)

SUDO := sudo
TMPDIR := result-$(shell date +%Y%m%d%H%M%S)

LMC ?= livemedia-creator
LMC_COMMON_ARGS := --ram=$(VM_RAM) --vcpus=$(VM_CPUS)
LMC_COMMON_ARGS += --tmp="$(TMPDIR)"

BOOTISO ?= boot.iso
ARCH := x86_64
RELEASEVER := 19

PYTHON ?= PYTHONPATH="$(PWD)/imagefactory/" python
CURL ?= curl

.SECONDARY:
.PHONY:$(MAIN_NAME).ks.tpl

all: $(MAIN_NAME).ova
	echo "$(MAIN_NAME)" appliance done


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
		-e "/^reboot/ s/reboot/poweroff/" \
		-e "/^services/ s/sshd/sshd,initial-setup-text/" \
		-e "s#\$$basearch#$(ARCH)#g" \
		-e "s#\$$releasever#$(RELEASEVER)#g" \
		$@


%.raw: %.ks
	make -f imgbased/data/images/poor-mans-lmc.makefile \
		KICKSTART="$<" \
		RELEASEVER=$(RELEASEVER) \
		QEMU_APPEND="cmdline $(QEMU_APPEND)" \
		DISK_SIZE=$$( $(VM_DISK) / 1000 ))G \
		run-install
	qemu-img convert -O qcow2 hda.qcow2 "$@"

#	mkdir $(TMPDIR)
#	chmod a+rw $(TMPDIR)
#	$(SUDO) $(LMC) --make-disk --iso "$(BOOTISO)" --ks "$<" --image-name "$@" $(LMC_COMMON_ARGS)
#	mv -v $(TMPDIR)/"$@" .

	# Legacy way:
	#$(SUDO) -E LANG=C LC_ALL=C image-creator -c $< --compression-type=xz -v -d --logfile $(shell pwd)/image.log


%.qcow2: %.raw
	$(SUDO) -E virt-sparsify --compress --convert qcow2 "$<" "$@"
	# FIXME selinux relable must hapen before init-label, before we cna enable
	# relable
	# The options also need to be given explicitly, because some others destroy the firstboot/initial-setup
	$(SUDO) -E virt-sysprep --no-selinux-relabel --add "$@" --enable abrt-data,bash-history,blkid-tab,ca-certificates,crash-data,cron-spool,dhcp-client-state,dovecot-data,hostname,lvm-uuids,machine-id,mail-spool,net-hostname,net-hwaddr,pacct-log,package-manager-cache,random-seed,smolt-uuid,ssh-hostkeys,ssh-userdir,sssd-db-log,udev-persistent-net,utmp,yum-uuid
	$(SUDO) qemu-img resize "$@" $(VM_GROWSIZE)

%.ova: %.qcow2
	$(SUDO) $(PYTHON) scripts/create_ova.py -m $(OVA_RAM) -c $(OVA_CPUS) "$*.qcow2" "$@"


clean: clean-log
	echo

clean-log:
	rm -f *.log
