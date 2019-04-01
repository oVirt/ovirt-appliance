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

from logging import error
import unittest
import sh
from sh import guestfish
import os


# Increase the capture length of python-sh to show complete errors
sh.ErrorReturnCode.truncate_cap = 999999


qcowimg = os.environ.get("TEST_ENGINE_ROOTFS_IMG",
                         "ovirt-engine-appliance.qcow2")


@unittest.skipUnless(os.path.exists(qcowimg), "qcow2 is missing")
class TestRootfsQcow2Image(unittest.TestCase):
    _fish = guestfish.bake("-ia", qcowimg, _ok_code=[0, 1])
    sh = _fish.bake("sh")

    def test_package(self):
        """Ensure the main packages are installed
        """
        req_pkgs = ["ovirt-engine", "qemu-guest-agent"]

        def has_pkg(pkg):
            try:
                self.sh("rpm -q " + pkg)
            except Exception as e:
                error("Package is missing: %s (%s)" % (pkg, e))
                return False
            return True

        for rpkg in req_pkgs:
            self.assertTrue(has_pkg(rpkg))

    def test_selinux_denials(self):
        """Ensure that there are no denials righ after appliance creation
        """
        denials = self.sh("grep denied /var/log/audit/audit.log").splitlines()
        assert len(denials) == 0, \
            "To many denials: %s\n%s" % (len(denials), denials)

# vim: et ts=4 sw=4 sts=4
