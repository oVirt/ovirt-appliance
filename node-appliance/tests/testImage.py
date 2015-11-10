#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2015 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#

import unittest
import sh
from sh import guestfish
import tempfile
import os
import shutil
import re


# Increase the capture length of python-sh to show complete errors
sh.ErrorReturnCode.truncate_cap = 999999


def log(x):
    print(x)


squashfsimg = os.environ.get("TEST_NODE_SQUASHFS_IMG",
                             "ovirt-node-appliance.squashfs.img")
qcowimg = os.environ.get("TEST_NODE_ROOTFS_IMG",
                         "ovirt-node-appliance.qcow2")


@unittest.skipUnless(os.path.exists(qcowimg), "qcow2 is missing")
class TestRootfsQcow2Image(unittest.TestCase):
    _fish = guestfish.bake("-ia", qcowimg, _ok_code=[0, 1])
    sh = _fish.bake("sh")

    def test_package(self):
        """Ensure the main packages are installed
        """
        req_pkgs = ["vdsm", "cockpit"]

        missing_pkgs = []
        all_builds = self.sh("rpm -qa").splitlines()

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
        """Ensure that there is only one partition in the appliance image
        """
        pt = self._fish("list-partitions").splitlines()
        pt_len = len(pt)
        assert pt_len == 1, "More than one partition: %s" % pt_len

    def test_selinux_denials(self):
        """Ensure that there are no denials righ after appliance creation
        """
        denials = self.sh("grep denied /var/log/audit/audit.log").splitlines()
        assert len(denials) == 0, \
            "To many denials: %s\n%s" % (len(denials), denials)


@unittest.skipUnless(os.path.exists(squashfsimg), "squashfs is missing")
class TestRootfsSquashfsImage(unittest.TestCase):
    dest = None
    img = None

    _fish = guestfish.bake("-ia", squashfsimg, _ok_code=[0, 1])
    sh = _fish.bake("sh")

    @classmethod
    def setUpClass(cls):
        cls.dest = tempfile.mktemp(dir=os.getcwd())
        log("Using dest: %s" % cls.dest)
        if os.path.exists(squashfsimg):
            sh.unsquashfs("-li", "-d", cls.dest, squashfsimg)
            cls.img = "%s/LiveOS/rootfs.img" % cls.dest

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.dest):
            log("Removing tree: %s" % cls.dest)
            assert os.getcwd() in cls.dest
            shutil.rmtree(cls.dest)

    def test_one_partition(self):
        """Ensure that the image is really just a filesystem image

        … and not a disk image (image with a partition table).
        """
        from sh import file as _file
        filetype = _file(self.img)
        log("Found filetype: %s" % filetype)
        assert "filesystem" in filetype

    def test_fsck(self):
        """Ensure that the filesystem is clean
        """
        sh.fsck("-nvf", self.img)
