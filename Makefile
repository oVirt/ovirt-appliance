
LMC ?= livemedia-creator
LMC_COMMON_ARGS =--ram=1024 --vcpus=4

all: ovirt-appliance-fedora.qcow2
	echo Appliance done

%.qcow2: %.ks
	sudo -E $(LMC) --make-disk --iso boot.iso --ks $< --name $@ $(LMC_COMMON_ARGS)
