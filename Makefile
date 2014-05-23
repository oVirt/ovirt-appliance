
LMC ?= livemedia-creator
LMC_COMMON_ARGS = --ram=3048 --vcpus=4

BOOTISO ?= boot.iso

all: ovirt-appliance-fedora.qcow2
	echo Appliance done

%.ks: %.ks.tpl
	ksflatten $< > $@
#	sed -i "s/^rootpw.*/rootpw --plaintext ovirt/" $@
	sed -i "s/^part .*/part \/ --size 4000 --fstype ext4/" $@
	sed -i "s/^network .*/network --activate/" $@
	sed -i "s/^%packages.*/%packages --ignoremissing/" $@
	sed -i "/default\.target/ s/^/#/" $@
	echo "firstboot --enable --reconfig" >> $@

%.qcow2: TMPDIR=/var/tmp
%.qcow2: %.ks
	sudo -E $(LMC) --make-disk --iso "$(BOOTISO)" --ks "$<" --image-name "$@" $(LMC_COMMON_ARGS)
	sudo -E virt-sparsify --compress --convert qcow2 "$(TMPDIR)/$@" "$(TMPDIR)/$*-sparse.qcow2"
	sudo -E virt-sysprep --add "$(TMPDIR)/$*-sparse.qcow2" --selinux-relable
	#sudo -E LANG=C LC_ALL=C image-creator -c $< --compression-type=xz -v -d --logfile $(shell pwd)/image.log
