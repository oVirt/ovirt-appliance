
LMC ?= livemedia-creator
LMC_COMMON_ARGS = --ram=3048 --vcpus=4

BOOTISO ?= boot.iso

SUDO := sudo 


all: ovirt-appliance-fedora.qcow2
	echo Appliance done

boot.iso:
	curl -O http://download.fedoraproject.org/pub/fedora/linux/releases/19/Fedora/x86_64/os/images/boot.iso

%.ks: %.ks.tpl boot.iso
	ksflatten $< > $@
	sed -i \
		-e "/^[-]/ d" \
		-e "/^text/ d" \
		-e "s/^part .*/part \/ --size 4000 --fstype ext4/" \
		-e "s/^network .*/network --activate/" \
		-e "s/^%packages.*/%packages --ignoremissing/" \
		-e "/default\.target/ s/^/#/" \
		-e "/RUN_FIRSTBOOT/ s/^/#/" \
		-e "/remove authconfig/ s/^/#/" \
		-e "/remove linux-firmware/ s/^/#/" \
		-e "/remove firewalld/ s/^/#/" \
		-e "/^bootloader/ s/bootloader .*/bootloader --location=mbr --timeout=1/" \
		-e "/dummy/ s/^/#/" \
		$@

%.qcow2: TMPDIR=/var/tmp
%.qcow2: %.ks
	$(SUDO) -E $(LMC) --make-disk --iso "$(BOOTISO)" --ks "$<" --image-name "$@" $(LMC_COMMON_ARGS)
	#$(SUDO) -E LANG=C LC_ALL=C image-creator -c $< --compression-type=xz -v -d --logfile $(shell pwd)/image.log

post-process: IMAGE=
post-process:
	[[ -n $$IMAGE ]]
	$(SUDO) -E virt-sysprep --add "$(IMAGE)" --selinux-relabel
	$(SUDO) -E virt-sparsify --compress --convert qcow2 "$(IMAGE)" "$(IMAGE).sparse.qcow2"

publish:
	[[ -n $$OS_USERNAME ]]
	[[ -n $$OS_PASSWORD ]]
	[[ -n $$IMAGE ]]
	OS_IMAGE_URL=glance.ovirt.org:9292/ glance image-create --name "oVirt Virtual Appliance (Fedora 19)" \
		--is-public true \
		--disk-format qcow2 \
		--container-format raw \
		--file $(IMAGE)
