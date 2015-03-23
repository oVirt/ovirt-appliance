#!/usr/bin/env python
# vim: et ts=4 sw=4 sts=4

import unittest
import sh
from sh import guestfish
import tempfile
import os
import shutil
import re
from unittest import SkipTest


# Increase the capture length of python-sh to show complete errors
sh.ErrorReturnCode.truncate_cap = 999999


def log(x):
    print(x)


def lines(data):
    """This method is not suited for big data
    """
    return [l for l in data.split("\n") if l]


squashfsimg = "ovirt-node-appliance.squashfs.img"
qcowimg = "ovirt-node-appliance.qcow2"


class TestRootfsQcow2Image(unittest.TestCase):
    _fish = guestfish.bake("-ia", qcowimg, _ok_code=[0, 1])
    sh = _fish.bake("sh")

    def test_package(self):
        req_pkgs = ["vdsm", "cockpit", "glusterfs-server", "vdsm-cli", "ovirt-engine-cli"]

        missing_pkgs = []
        all_builds = lines(self.sh("rpm -qa"))

        def name_from_build(build):
            return re.sub(r"-[^-]+-[^-]+$", "", build)

        all_pkgs = dict((name_from_build(b), b) for b in all_builds)
        for rpkg in req_pkgs:
            if rpkg in all_pkgs:
                log("'%s' is in the image" % all_pkgs[rpkg])
            else:
                missing_pkgs.append(rpkg)

        assert len(missing_pkgs) == 0, \
            "Some packages are missing: %s" % missing_pkgs

    def test_partitioning(self):
        pt = lines(self._fish("list-partitions"))
        pt_len = len(pt)
        assert pt_len == 1, "More than one partition: %s" % pt_len

    def test_selinux_denials(self):
        denials = lines(self.sh("grep denied /var/log/audit/audit.log"))
        assert len(denials) == 0, \
            "To many denials: %s\n%s" % (len(denials), denials)


class TestRootfsSquashfsImage(unittest.TestCase):
    dest = None
    img = None

    _fish = guestfish.bake("-ia", squashfsimg, _ok_code=[0, 1])
    sh = _fish.bake("sh")

    @classmethod
    def setUpClass(cls):
        cls.dest = tempfile.mktemp(dir=os.getcwd())
        log("Using dest: %s" % cls.dest)
        sh.unsquashfs("-li", "-d", cls.dest, squashfsimg)
        cls.img = "%s/LiveOS/rootfs.img" % cls.dest

    @classmethod
    def tearDownClass(cls):
        log("Removing tree: %s" % cls.dest)
        assert os.getcwd() in cls.dest
        shutil.rmtree(cls.dest)

    def test_one_partition(self):
        from sh import file as _file
        filetype = _file(self.img)
        log("Found filetype: %s" % filetype)
        assert "filesystem" in filetype

    def test_fsck(self):
        sh.fsck("-nvf", self.img)

    def test_valid_fstree(self):
        raise SkipTest("Not implemented")
        # FIXME check if /boot /sbin etc exists
