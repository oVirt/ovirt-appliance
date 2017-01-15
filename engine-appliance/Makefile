
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
BOOTISOURL=http://mirror.centos.org/centos/$(RELEASEVER)/os/$(ARCH)/images/boot.iso

LMC ?= livemedia-creator
LMC_RAM ?= 2048
LMC_CPUS ?= 4

#
# oVirt specific vars
#
OVIRTRELEASERPM=http://resources.ovirt.org/pub/yum-repo/ovirt-release41-pre.rpm
ovirt-engine-appliance.spec: VERSION=4.1
ovirt-engine-appliance.spec: VERSION_EXTRA=
ovirt-engine-appliance.spec: RELEASE=$(shell date +%Y%m%d).1
ovirt-engine-appliance.spec: OVAFILENAME=ovirt-engine-appliance.ova

PYTHON ?= PYTHONPATH="$(PWD)/imagefactory/" python

# Direct for virt-sparsify: http://libguestfs.org/guestfs.3.html#backend
export LIBGUESTFS_BACKEND=direct
# Workaround nest problem: https://bugzilla.redhat.com/show_bug.cgi?id=1195278
export LIBGUESTFS_BACKEND_SETTINGS=force_tcg
export TMPDIR=/var/tmp/
export TEST_ENGINE_ROOTFS_IMG=$(PWD)/ovirt-engine-appliance.qcow2

.SECONDARY:
.PHONY: $(wildcard *.ks.tpl) ovirt-engine-appliance.spec

all: ovirt-engine-appliance.ova
	echo "$@" appliance done

boot.iso:
	curl $(CURLOPTS) -O $(BOOTISOURL)

%.ks: data/%.ks.in
	sed \
	 -e "/# Answers/ r data/ovirt-engine-answers" \
	 -e "s|@OVIRTRELEASERPM@|$(OVIRTRELEASERPM)|" \
	 "$<" > "$@"

%.qcow2: SPARSE=1
%.qcow2: %.ks boot.iso
	$(LMC) --make-disk --kernel-args="ip=ens2:dhcp" --ram=$(LMC_RAM) --vcpus=$(LMC_CPUS) --iso=boot.iso --ks=$< --qcow2 --image-name=$@
	mv /var/tmp/$@ .
	-[[ -n "$(SPARSE)" ]] && [[ "$$(virt-sparsify --help)" =~ --in-place ]] && ( virt-sparsify --in-place $@ ; ln $@ $@.sparse ; )
	-[[ -n "$(SPARSE)" ]] && [[ ! -f $@.sparse ]] && [[ "$$(virt-sparsify --help)" =~ --check-tempdir ]] && virt-sparsify --check-tmpdir=continue $@ $@.sparse
	-[[ -n "$(SPARSE)" ]] && [[ ! -f $@.sparse ]] && virt-sparsify $@ $@.sparse
	-[[ -f $@.sparse ]] &&  ( mv -v $@.sparse $@ ; rm -f $@.sparse ; )
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
	rpmbuild --define "_sourcedir `pwd`" --define "dist .fc24" -bb $<

RPMBUILD = rpmbuild
TMPREPOS = tmp.repos
rpm srpm:   ovirt-engine-appliance.spec ovirt-engine-appliance.ova
	rm -fr "$(TMPREPOS)"
	mkdir -p $(TMPREPOS)/{SPECS,RPMS,SRPMS,SOURCES}
	$(RPMBUILD) --define="_topdir `pwd`/$(TMPREPOS)" --define "_sourcedir `pwd`" -ba $<
	$(RPMBUILD) --define="_topdir `pwd`/$(TMPREPOS)" --define "dist .fc24" --rebuild $(TMPREPOS)/SRPMS/*.src.rpm
	@echo
	@echo "srpm and rpm(s) available at '$(TMPREPOS)'"
	@echo

%-manifest-rpm: %.qcow2
	guestfish --ro -i -a $< sh 'rpm -qa | sort -u' > $@

check: ovirt-engine-appliance-manifest-rpm
	grep ovirt-engine ovirt-engine-appliance-manifest-rpm
#	-pyflakes tests/*.py
#	-pep8 tests/*.py
#	cd tests && nosetests --with-xunit -v -w .

clean:
	-rm -vf ovirt-engine-appliance.ova ovirt-engine-appliance.qcow2 ovirt-engine-appliance-manifest-rpm ovirt-engine-appliance.spec
