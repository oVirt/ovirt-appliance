
#
# How it works:
# 1. Inherit from Fedora Cloud images with modifications
# 2. Use Fedora 19 boot iso to run lmc
# 3. Create runtime image (qcow2)
# 4. sysprep, sparsify and comvert runtime image to ova
#

#
# OVA specific vars
# #
# This size must be full GB, in MB
VM_DISK ?= $(shell expr 10 \* 1024)

OVA_RAM ?= 16384
OVA_CPUS ?= 4

ARCH=x86_64
DISTRO=centos
RELEASEVER=7

#
# oVirt specific vars
#
OVIRTRELEASERPM=http://plain.resources.ovirt.org/pub/ovirt-4.1-snapshot/rpm/el7/noarch/ovirt-release41-snapshot.rpm
ovirt-engine-appliance.spec: VERSION=4.1
ovirt-engine-appliance.spec: VERSION_EXTRA=
ovirt-engine-appliance.spec: RELEASE=$(shell date +%Y%m%d).1
ovirt-engine-appliance.spec: OVAFILENAME=ovirt-engine-appliance.ova

PYTHON ?= PYTHONPATH="$(PWD)/imagefactory/" python

.SECONDARY:
.PHONY: $(wildcard *.ks.tpl) ovirt-engine-appliance.spec

all: ovirt-engine-appliance.ova
	echo "$@" appliance done

%.ks: data/%.ks.in
	sed \
	 -e "/# Answers/ r data/ovirt-engine-answers" \
	 -e "s|@OVIRTRELEASERPM@|$(OVIRTRELEASERPM)|" \
	 "$<" > "$@"

%.qcow2: %.ks
	make -f image-tools/build.mk $@ DISTRO=$(DISTRO) RELEASEVER=$(RELEASEVER) DISK_SIZE=$(VM_DISK)
	ls -shal $@

%.ova: %.qcow2
	$(SUDO) $(PYTHON) scripts/create_ova.py -m $(OVA_RAM) -c $(OVA_CPUS) "$*.qcow2" "$@"
	ls -shal $@

ovirt-engine-appliance.spec: data/ovirt-engine-appliance.spec.in
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

# Direct for virt-sparsify: http://libguestfs.org/guestfs.3.html#backend
export LIBGUESTFS_BACKEND=direct
# Workaround nest problem: https://bugzilla.redhat.com/show_bug.cgi?id=1195278
export LIBGUESTFS_BACKEND_SETTINGS=force_tcg
export TEST_ENGINE_ROOTFS_IMG=$(PWD)/ovirt-engine-appliance.qcow2
check: ovirt-engine-appliance-manifest-rpm
	grep ovirt-engine ovirt-engine-appliance-manifest-rpm
#	-pyflakes tests/*.py
#	-pep8 tests/*.py
#	cd tests && nosetests --with-xunit -v -w .

clean:
	-rm -vf ovirt-engine-appliance.ova ovirt-engine-appliance.qcow2 ovirt-engine-appliance-manifest-rpm ovirt-engine-appliance.spec
