
LMC ?= livemedia-creator
LMC_COMMON_ARGS = --ram=3048 --vcpus=4

BOOTISO ?= boot.iso

SUDO := sudo 


all: ovirt-appliance-fedora.qcow2
	echo Appliance done

%.ks: %.ks.tpl
	ksflatten $< > $@
	sed -i \
		-e "/^-plymouth/ d" \
		-e "/^text/ d" \
		-e "s/^part .*/part \/ --size 4000 --fstype ext4/" \
		-e "s/^network .*/network --activate/" \
		-e "s/^%packages.*/%packages --ignoremissing/" \
		-e "/default\.target/ s/^/#/" \
		-e "/RUN_FIRSTBOOT/ s/^/#/" \
		$@

%.qcow2: TMPDIR=/var/tmp
%.qcow2: %.ks
	$(SUDO) -E $(LMC) --make-disk --iso "$(BOOTISO)" --ks "$<" --image-name "$@" $(LMC_COMMON_ARGS)
	#$(SUDO) -E virt-sparsify --compress --convert qcow2 "$(TMPDIR)/$@" "$(TMPDIR)/$*-sparse.qcow2"
	#$(SUDO) -E virt-sysprep --add "$(TMPDIR)/$*-sparse.qcow2" --selinux-relabel

	#$(SUDO) -E LANG=C LC_ALL=C image-creator -c $< --compression-type=xz -v -d --logfile $(shell pwd)/image.log
