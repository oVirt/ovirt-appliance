
#
# How it works:
# 1. Inherit from Fedora Cloud images with modifications
# 2. Use Fedora 19 boot iso to run lmc
# 3. Create runtime image (qcow2)
# 4. sysprep, sparsify and comvert runtime image to ova
#

# This size must be full GB, in MB
VM_DISK ?= $(shell expr 10 \* 1024)

OVA_RAM ?= 16384
OVA_CPUS ?= 4

ARCH=x86_64
DISTRO=centos
RELEASEVER=7

PYTHON ?= PYTHONPATH="$(PWD)/imagefactory/" python

.SECONDARY:
.PHONY: $(wildcard *.ks.tpl) ovirt-engine-appliance.spec

all: ovirt-engine-appliance.ova
	echo "$@" appliance done

check: ovirt-engine-appliance-manifest-rpm
	egrep -q "^ovirt-engine" ovirt-engine-appliance-manifest-rpm || echo "Engine packages are missing"

%.qcow2: %.ks
	make -f image-tools/build.mk $@ DISTRO=$(DISTRO) RELEASEVER=$(RELEASEVER) DISK_SIZE=$(VM_DISK)
	ls -shal $@

%.ova: %.qcow2
	$(SUDO) $(PYTHON) scripts/create_ova.py -m $(OVA_RAM) -c $(OVA_CPUS) "$*.qcow2" "$@"
	ls -shal $@

ovirt-engine-appliance.spec: VERSION=$(shell date +%Y%m%d)
ovirt-engine-appliance.spec: VERSION_EXTRA=.0
ovirt-engine-appliance.spec: RELEASE=1
ovirt-engine-appliance.spec: OVAFILENAME=ovirt-engine-appliance.ova
ovirt-engine-appliance.spec: ovirt-engine-appliance.spec.in
	sed \
	  -e "s/@VERSION@/$(VERSION)$(VERSION_EXTRA)/" \
	  -e "s/@RELEASE@/$(RELEASE)/" \
	  -e "s/@OVAFILENAME@/$(OVAFILENAME)/" \
	  $< > $@

%.rpm: %.spec
	rpmbuild --define "_sourcedir `pwd`" -ba $<

RPMBUILD = rpmbuild
TMPREPOS = tmp.repos
rpm srpm:   ovirt-engine-appliance.spec ovirt-engine-appliance.ova
	rm -fr "$(TMPREPOS)"
	mkdir -p $(TMPREPOS)/{SPECS,RPMS,SRPMS,SOURCES}
	$(RPMBUILD) --define="_topdir `pwd`/$(TMPREPOS)" --define "_sourcedir `pwd`" -ba $<
	@echo
	@echo "srpm and rpm(s) available at '$(TMPREPOS)'"
	@echo

%-manifest-rpm: %.qcow2
	 make -f image-tools/build.mk $@
