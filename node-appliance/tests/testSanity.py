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

from logging import debug
import unittest
from testVirt import NodeTestCase, IntegrationTestCase


class TestNodeSanity(NodeTestCase):
    """Test some non-runtime Node appliance stuff

    Any testcase only affecting Node should go here.
    """
    def test_required_packages(self):
        pkgs = ["kernel", "vdsm", "cockpit"]
        self.node.ssh("rpm -q " + " ".join(pkgs))


@unittest.skip("FIXME https://bugzilla.redhat.com/1278878")
class TestImgbaseNode(NodeTestCase):
    """Test functionality around imgbase on Node appliance (post-installation)

    Any testcase related to imgbase specific to Node should go here.
    Including plain upgrades.

    FIXME
    These tests need to be run against the installed Node appliance image.
    """
    def test_installed(self):
        """Check if imgbase is installed
        """
        debug("%s" % self.node.ssh("imgbase --version"))

    def test_has_vgs(self):
        """Check if there are any LVM VGs
        """
        vgs = self.node.ssh("vgs --noheadings").strip().splitlines()
        debug("VGs: %s" % vgs)
        self.assertGreater(len(vgs), 0, "No VGs found")

    def test_has_layout(self):
        """Check if there is a valid imgbase layout

        The layout should have been created as part of the install process.
        """
        self.node.ssh("imgbase layout")


class TestIntegrationSanity(IntegrationTestCase):
    """Basic integration testing between Node and Engine

    Add a host, add storage, and spawn a disk-less VM.

    Any testcase involving one Node and one Engine should go
    here.
    """
    def test_add_host(self):
        """Create and add a host and wait for it to come up
        """
        nodename = "node-host"

        self.engine_shell(("add host --name {nodename} --address 10.11.12.77 "
                           "--root_password 77 --cluster-name Default"
                           ).format(nodename=nodename))

        debug("Check that the host is now recognized")
        self.assertTrue(nodename in self.engine_shell("list hosts"))

        debug("Check that the host is getting up")
        self.engine_shell_wait(nodename, "list hosts --query 'status=up'")

    @unittest.skip("Not implemented")
    def test_add_storage(self):
        """Create a storage domain on Engine
        """
        pass

    @unittest.skip("Not implemented")
    def test_spawn_vm(self):
        """Use create a storage domain and host to spawn a disk-less VM
        """
        self.test_add_host()
        self.test_add_storage()
        pass


if __name__ == "__main__":
    unittest.main()

# vim: et ts=4 sw=4 sts=4
