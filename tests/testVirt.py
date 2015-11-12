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

"""
During test runs you can watch teh VMs by using virt-manager and looking
at your user sessions:

$ virt-manager -c qemu:///session

Main advantage of this testcase templates:
- Use snapshots to provide clean state per testcase
- Inter-VM communication
- root less (run as a normal user)!
"""

from logging import debug
import unittest
import sh
import os
import tempfile
import time
from virt import DiskImage, VM, CloudConfig


NODE_IMG = os.environ.get("TEST_NODE_ROOTFS_IMG",
                          "ovirt-node-appliance.qcow2")

ENGINE_IMG = os.environ.get("TEST_ENGINE_ROOTFS_IMG",
                            "ovirt-engine-appliance.qcow2")


class TimedoutError(Exception):
    pass


def gen_ssh_identity_file():
    f = tempfile.mkdtemp("testing-ssh") + "/id_rsa"
    sh.ssh_keygen(b=2048, t="rsa", f=f, N="", q=True)
    return f


class MachineTestCase(unittest.TestCase):
    """Basic test case to ease VM based testcases

    Just provides a function to create a VM with the relevant
    IP configuration
    """
    @staticmethod
    def _start_vm(name, srcimg, tmpimg, magicnumber, memory_gb=2):
        # FIXME We need permissive mode to work correctly
        assert "Permissive" in sh.getenforce()

        debug("Strating new VM %s" % name)

        ssh_port = 22000 + int(magicnumber)
        ipaddr = "10.11.12.%s" % magicnumber

        img = DiskImage(srcimg).reflink(tmpimg)
        dom = VM.create(name, img, ssh_port=ssh_port, memory_gb=memory_gb)
        dom._ssh_identity_file = gen_ssh_identity_file()

        cc = CloudConfig()
        cc.instanceid = name + "-ci"
        cc.password = str(magicnumber)

        # Brin gup the second NIC for inter-VM networking
        # cc.runcmd = "ip link set dev eth1 up ; ip addr add {ipaddr}/24 dev
        # eth1".format(ipaddr=ipaddr)
        cc.runcmd = ("nmcli con add con-name bus0 ifname eth1 " +
                     "autoconnect yes type ethernet ip4 {ipaddr}/24 ; " +
                     "nmcli con up id bus0").format(ipaddr=ipaddr)
        cc.runcmd += (" ; grep myhostname /etc/nsswitch.conf || sed " +
                      "-i '/hosts:/ s/$/ myhostname/' /etc/nsswitch.conf")
        with open(dom._ssh_identity_file + ".pub", "rt") as src:
            cc.ssh_authorized_keys = [src.read().strip()]
        dom.set_cloud_config(cc)

        return dom


@unittest.skipUnless(os.path.exists(NODE_IMG), "Node image is missing")
class NodeTestCase(MachineTestCase):
    """Class to do just-Node specific testing

    Mainly this set's up a VM based on the Node appliance image
    and ensures that each testcase runs in a fresh snapshot.
    """
    node = None

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(NODE_IMG):
            return

        try:
            n = "%s-node" % cls.__name__
            cls.node = cls._start_vm(n, NODE_IMG, n + ".qcow2", 77)

            debug("Install cloud-init")
            cls.node.fish("sh", "yum install -y sos cloud-init")
        except:
            if cls.node:
                cls.node.undefine()

            raise

    @classmethod
    def tearDownClass(cls):
        debug("Tearing down %s" % cls)
        if cls.node:
            cls.node.undefine()

    def setUp(self):
        debug("Setting up %s" % self)
        self.snapshot = self.node.snapshot()
        self.node.start()

    def tearDown(self):
        debug("Tearing down %s" % self)
        self.snapshot.revert()


class Test_Tier_0_NodeTestcase(NodeTestCase):
    """Class to test that the NodeTestCase class works correctly

    To prevent regressions in the lower layer.
    """
    def test_snapshots_work(self):
        """Check if snapshots are working correct
        """
        has_kernel = lambda: "kernel" in self.node.ssh("rpm -q kernel")

        self.assertTrue(has_kernel())

        with self.node.snapshot().context():
            self.node.ssh("rpm -e --nodeps kernel")
            with self.assertRaises(sh.ErrorReturnCode_1):
                has_kernel()

        self.assertTrue(has_kernel())

    def test_ssh_works(self):
        """Check if basic SSH is working correct
        """
        self.node.ssh("pwd")

    def test_shutdown_works(self):
        """Check if host can be shutdown gracefully
        """
        self.node.ssh("echo We could log in, the host is up")
        self.node.shutdown()

    def test_reboot_works(self):
        """Check that a host can be rebooted and comes back
        """
        self.node.ssh("echo We could log in, the host is up")
        self.node.reboot()
        self.node.ssh("pwd")


@unittest.skipUnless(os.path.exists(NODE_IMG), "Node image is missing")
@unittest.skipUnless(os.path.exists(ENGINE_IMG), "Engine image is missing")
class IntegrationTestCase(MachineTestCase):
    node = None
    engine = None

    # FIXME reduce the number of answers to the minimum
    ENGINE_ANSWERS = """
# For 3.6
[environment:default]
OVESETUP_CONFIG/adminPassword=str:password
OVESETUP_CONFIG/fqdn=str:engine.example.com
OVESETUP_ENGINE_CONFIG/fqdn=str:engine.example.com
OVESETUP_VMCONSOLE_PROXY_CONFIG/vmconsoleProxyHost=str:engine.example.com

OVESETUP_DIALOG/confirmSettings=bool:True
OVESETUP_CONFIG/applicationMode=str:both
OVESETUP_CONFIG/remoteEngineSetupStyle=none:None
OVESETUP_CONFIG/storageIsLocal=bool:False
OVESETUP_CONFIG/firewallManager=str:firewalld
OVESETUP_CONFIG/remoteEngineHostRootPassword=none:None
OVESETUP_CONFIG/firewallChangesReview=bool:False
OVESETUP_CONFIG/updateFirewall=bool:True
OVESETUP_CONFIG/remoteEngineHostSshPort=none:None
OVESETUP_CONFIG/storageType=none:None
OSETUP_RPMDISTRO/requireRollback=none:None
OSETUP_RPMDISTRO/enableUpgrade=none:None
OVESETUP_DB/database=str:engine
OVESETUP_DB/fixDbViolations=none:None
OVESETUP_DB/secured=bool:False
OVESETUP_DB/host=str:localhost
OVESETUP_DB/user=str:engine
OVESETUP_DB/securedHostValidation=bool:False
OVESETUP_DB/port=int:5432
OVESETUP_ENGINE_CORE/enable=bool:True
OVESETUP_CORE/engineStop=none:None
OVESETUP_SYSTEM/memCheckEnabled=bool:False
OVESETUP_SYSTEM/nfsConfigEnabled=bool:False
OVESETUP_CONFIG/sanWipeAfterDelete=bool:True
OVESETUP_PKI/organization=str:Test
OVESETUP_CONFIG/engineHeapMax=str:3987M
OVESETUP_CONFIG/isoDomainName=str:ISO_DOMAIN
OVESETUP_CONFIG/isoDomainMountPoint=str:/var/lib/exports/iso
OVESETUP_CONFIG/isoDomainACL=str:*(rw)
OVESETUP_CONFIG/engineHeapMin=str:100M
OVESETUP_AIO/configure=none:None
OVESETUP_AIO/storageDomainName=none:None
OVESETUP_AIO/storageDomainDir=none:None
OVESETUP_PROVISIONING/postgresProvisioningEnabled=bool:True
OVESETUP_APACHE/configureRootRedirection=bool:True
OVESETUP_APACHE/configureSsl=bool:True
OVESETUP_CONFIG/websocketProxyConfig=bool:True
OVESETUP_RHEVM_SUPPORT/configureRedhatSupportPlugin=bool:False
OVESETUP_VMCONSOLE_PROXY_CONFIG/vmconsoleProxyConfig=bool:True
OVESETUP_VMCONSOLE_PROXY_CONFIG/vmconsoleProxyPort=int:2222
"""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(NODE_IMG):
            return

        if not os.path.exists(ENGINE_IMG):
            return

        try:
            n = "%s-" % cls.__name__
            cls.node = cls._start_vm(n + "node", NODE_IMG,
                                     n + "node.qcow2", 77)
            cls.engine = cls._start_vm(n + "engine", ENGINE_IMG,
                                       n + "engine.qcow2", 88,
                                       memory_gb=4)

            #
            # Do the engine setup
            # This assumes that the engine was tested already and
            # this could probably be pulled in a separate testcase
            #
            cls._node_setup()
            cls._engine_setup()
        except:
            if cls.node:
                cls.node.undefine()

            if cls.engine:
                cls.engine.undefine()

            raise

    @classmethod
    def tearDownClass(cls):
        debug("Tearing down %s" % cls)
        if cls.node:
            cls.node.undefine()

        if cls.engine:
            cls.engine.undefine()

    @classmethod
    def _node_setup(cls):
        debug("Install cloud-init")
        cls.node.fish("sh", "yum install -y sos cloud-init")

        cls.node.start()

        debug("Enable fake qemu support")
        cls.node.ssh("yum install -y vdsm-hook-faqemu")
        cls.node.ssh("sed -i '/vars/ a fake_kvm_support = true' "
                     "/etc/vdsm/vdsm.conf")
        # Bug-Url: https://bugzilla.redhat.com/show_bug.cgi?id=1279555
        cls.node.ssh("sed -i '/fake_kvm_support/ s/false/true/' " +
                     "/usr/lib/python2.7/site-packages/vdsm/config.py")

        cls.node.shutdown()

    @classmethod
    def _engine_setup(cls):
        debug("Installing engine")

        cls.engine.post("/root/ovirt-engine-answers",
                        cls.ENGINE_ANSWERS)

        # To reduce engines mem requirements
        # cls.engine.post("/etc/ovirt-engine/engine.conf.d/90-mem.conf",
        #                 "ENGINE_PERM_MIN=128m\nENGINE_HEAP_MIN=1g\n")

        cls.engine.post("/root/.ovirtshellrc", """
[ovirt-shell]
username = admin@internal
password = password

renew_session = False
timeout = None
extended_prompt = False
url = https://127.0.0.1/ovirt-engine/api
insecure = True
kerberos = False
filter = False
session_timeout = None
ca_file = None
dont_validate_cert_chain = True
key_file = None
cert_file = None
""")

        cls.engine.start()

        debug("Add static hostname for name resolution")
        cls.engine.ssh("sed -i '/^127.0.0.1/ s/$/ engine.example.com/' "
                       "/etc/hosts")

        debug("Run engine setup")
        cls.engine.ssh("engine-setup --offline "
                       "--config-append=/root/ovirt-engine-answers")

        debug("Install sos for log collection")
        cls.engine.ssh("yum install -y sos")

        cls.engine.shutdown()
        debug("Installation completed")

    def setUp(self):
        self.node_snapshot = self.node.snapshot()
        self.engine_snapshot = self.engine.snapshot()
        self.node.start()
        self.engine.start()

    def tearDown(self):
        self.node_snapshot.revert()
        self.engine_snapshot.revert()

    def engine_shell(self, cmd, tries=60):
        """Run a command in the ovirt-shell on the Engine VM

        Before running this command will ensure that the Engine
        is really available (using the ping command)
        """
        oshell = lambda cmd: self.engine.ssh("ovirt-shell --connect -E %r" %
                                             cmd)

        def wait_for_engine(tries=tries):
            while tries >= 0:
                debug("Waiting for engine ...")
                tries -= 1
                if tries == 0:
                    raise TimedoutError()
                if "disconnected" in oshell("ping"):
                    time.sleep(1)
                else:
                    break

        wait_for_engine()

        return oshell(cmd)

    def engine_shell_wait(self, needle, cmd, tries=60):
        """Wait for a needle to turn up in an ovirt-shell command reply
        """
        while tries >= 0:
            debug("Waiting for %r in engine change: %s" % (needle, cmd))
            tries -= 1
            if tries == 0:
                raise TimedoutError()
            reply = self.engine_shell(cmd)
            if needle in reply:
                break
            else:
                time.sleep(1)
        return reply


class Test_Tier_0_IntegrationTestCase(IntegrationTestCase):
    def test_tier_1_intra_network_connectivity(self):
        """Check that the basic IP connectivity between VMs is given
        """
        self.node.ssh("ifconfig")
        self.engine.ssh("ifconfig")

        self.node.ssh("arp -n")
        self.engine.ssh("arp -n")

        self.node.ssh("ping -c10 10.11.12.88")
        self.engine.ssh("ping -c10 10.11.12.77")

    def test_tier_1_node_can_reach_engine(self):
        """Check if the node can reach the engine
        """
        self.node.ssh("ping -c3 -i3 10.11.12.88")
        self.engine.ssh("ping -c3 -i3 10.11.12.77")
        self.node.ssh("curl --fail 10.11.12.88 | grep -i engine")

    def test_tier_2_engine_is_up(self):
        """Check that the engine comes up and provides it's API
        """
        self.engine.ssh("curl --fail 127.0.0.1 | grep -i engine")
        self.engine_shell("ping")


if __name__ == "__main__":
    unittest.main()

# vim: et ts=4 sw=4 sts=4
