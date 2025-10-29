
ARCH=x86_64
VERSION=4.5.1
DISTRO ?= centos
DISTRO_VERSION ?= 9
DISTRO_FULLNAME := $(DISTRO)$(DISTRO_VERSION)
PROFILE ?= copr

#
# oVirt specific vars
#
ovirt-engine-appliance-${DISTRO_FULLNAME}.spec: VERSION_EXTRA=
ovirt-engine-appliance-${DISTRO_FULLNAME}.spec: RELEASE=$(shell date +%Y%m%d%H%M%S).1
ovirt-engine-appliance-${DISTRO_FULLNAME}.spec: QCOW2FILENAME=ovirt-engine-appliance-${DISTRO_FULLNAME}.qcow2

PYTHON ?= python3

export LIBGUESTFS_BACKEND=direct
export TMPDIR=/var/tmp/

.SECONDARY:
.PHONY: ovirt-engine-appliance.spec

all: ovirt-engine-appliance-${DISTRO_FULLNAME}.qcow2
	echo "$@" appliance done

%.qcow2:
	$(SUDO) kiwi-ng --profile=${DISTRO}-${PROFILE} --kiwi-file=${DISTRO_FULLNAME}.xml system build --description=kiwi/ --target-dir=${TMPDIR}/${DISTRO_FULLNAME}
	mv ${TMPDIR}/${DISTRO_FULLNAME}/ovirt-engine-appliance.${ARCH}-$(VERSION).qcow2 $@
	ls -shal $@

ovirt-engine-appliance-${DISTRO_FULLNAME}.spec: data/ovirt-engine-appliance.spec.in
	sed \
	  -e "s/@DISTRO@/$(DISTRO_FULLNAME)/" \
	  -e "s/@VERSION@/$(VERSION)$(VERSION_EXTRA)/" \
	  -e "s/@RELEASE@/$(RELEASE)/" \
	  -e "s/@QCOW2FILENAME@/$(QCOW2FILENAME)/" \
	  $< > $@

%.rpm: %.spec
	rpmbuild --define "_sourcedir `pwd`" -ba $<

RPMBUILD = rpmbuild
TMPREPOS = tmp.repos
rpm srpm: ovirt-engine-appliance-${DISTRO_FULLNAME}.spec ovirt-engine-appliance-${DISTRO_FULLNAME}.qcow2 ovirt-engine-appliance-${DISTRO_FULLNAME}-manifest-rpm
	rm -fr "$(TMPREPOS)"
	mkdir -p $(TMPREPOS)/{SPECS,RPMS,SRPMS,SOURCES}
	$(RPMBUILD) --define="_topdir `pwd`/$(TMPREPOS)" --define "_sourcedir `pwd`" -ba $<
	@echo
	@echo "srpm and rpm(s) available at '$(TMPREPOS)'"
	@echo

%-manifest-rpm: %.qcow2
	mv ${TMPDIR}/${DISTRO_FULLNAME}/ovirt-engine-appliance.${ARCH}-$(VERSION).packages $@

clean:
	rm -vf ovirt-engine-appliance-${DISTRO_FULLNAME}.qcow2 ovirt-engine-appliance-${DISTRO_FULLNAME}.spec ovirt-engine-appliance-${DISTRO_FULLNAME}-manifest-rpm
	rm -rvf ${TMPDIR}/${DISTRO_FULLNAME}
	rm -rvf tmp.repos
