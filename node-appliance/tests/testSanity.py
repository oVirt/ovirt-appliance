#!/usr/bin/env python
# vim: et ts=4 sw=4 sts=4

import logging
from logging import debug

logging.basicConfig(level=logging.DEBUG)

import unittest
import sh
import os
import tempfile
from virt import Image, VM, CloudConfig

NODE_IMG = os.environ.get("TEST_NODE_ROOTFS_IMG",
                          "ovirt-node-appliance.qcow2")


def gen_ssh_identity_file():
    f = tempfile.mkdtemp("testing-ssh") + "/id_rsa"
    sh.ssh_keygen(b=2048, t="rsa", f=f, N="", q=True)
    return f


class MachineTestCase(unittest.TestCase):
    @staticmethod
    def _start_vm(name, srcimg, tmpimg, magicnumber):
        debug("Strating new VM %s" % name)

        ssh_port = 42000 + int(magicnumber)
        ipsuffix = magicnumber

        img = Image(srcimg).reflink(tmpimg)
        dom = VM.create(name, img, ssh_port=ssh_port)
        dom._ssh_identity_file = gen_ssh_identity_file()

        cc = CloudConfig()
        cc.instanceid = name + "-ci"
        cc.password = name
        cc.runcmd = "ip addr add 10.11.12.%s/24 dev eth1" % ipsuffix
        with open(dom._ssh_identity_file + ".pub", "rt") as src:
            cc.ssh_authorized_keys = [src.read().strip()]
        dom.set_cloud_config(cc)

        return dom


class NodeTestCase(MachineTestCase):
    @classmethod
    def setUpClass(cls):
        debug("SetUpClass %s" % cls)
        n = "node-%s" % cls.__name__
        cls.node = cls._start_vm(n, NODE_IMG, n + ".qcow2", 77)

    @classmethod
    def tearDownClass(cls):
        debug("Tearing down %s" % cls)
        cls.node.undefine()

    def setUp(self):
        debug("Setting up %s" % self)
        self.snapshot = self.node.snapshot()
        self.node.start()

    def tearDown(self):
        debug("Tearing down %s" % self)
        self.snapshot.revert()


class TestNodeTestcase(NodeTestCase):
    """Let's ensure that the basic functionality is working
    """
    def test_snapshots_work(self):
        has_kernel = lambda: "kernel" in self.node.ssh("rpm -q kernel")

        self.assertTrue(has_kernel())

        with self.node.snapshot().context():
            self.node.ssh("rpm -e --nodeps kernel")
            with self.assertRaises(sh.ErrorReturnCode_1):
                has_kernel()

        self.assertTrue(has_kernel())

    def test_ssh_works(self):
        self.node.ssh("pwd")

    def test_reboot_works(self):
        with self.assertRaises(sh.ErrorReturnCode_255):
            self.node.ssh("reboot")
        self.node.wait_reboot(timeout=60)
        self.node.ssh("pwd")


class TestBasicNode(NodeTestCase):
    def test_required_packages(self):
        pkgs = ["kernel", "vdsm"]
        self.node.ssh("rpm -q " + " ".join(pkgs))


@unittest.skip("We need to test the installed image to fix this")
class TestImgbaseNode(NodeTestCase):
    def test_installed(self):
        debug("%s" % self.node.ssh("imgbase --version"))

    def test_has_vgs(self):
        vgs = self.node.ssh("vgs --noheadings").strip().splitlines()
        debug("VGs: %s" % vgs)
        self.assertGreater(len(vgs), 0, "No VGs found")

    def test_has_layout(self):
        self.node.ssh("imgbase layout")


@unittest.skip("Needs the Engine Appliance to work")
class IntegrationTestCase(MachineTestCase):
    ENGINE_ANSWERS = """
# For 3.6
[environment:default]
OVESETUP_CONFIG/adminPassword=str:ovirt
OVESETUP_CONFIG/fqdn=str:engine.example.com
OVESETUP_ENGINE_CONFIG/fqdn=str:engine.example.com
OVESETUP_VMCONSOLE_PROXY_CONFIG/vmconsoleProxyHost=str:engine.example.com

OVESETUP_DIALOG/confirmSettings=bool:True
OVESETUP_CONFIG/applicationMode=str:both
OVESETUP_CONFIG/remoteEngineSetupStyle=none:None
OVESETUP_CONFIG/storageIsLocal=bool:False
OVESETUP_CONFIG/firewallManager=str:iptables
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
OVESETUP_SYSTEM/memCheckEnabled=bool:True
OVESETUP_SYSTEM/nfsConfigEnabled=bool:False
OVESETUP_CONFIG/sanWipeAfterDelete=bool:True
OVESETUP_PKI/organization=str:Test
OVESETUP_CONFIG/engineHeapMax=str:3987M
OVESETUP_CONFIG/isoDomainName=str:ISO_DOMAIN
OVESETUP_CONFIG/isoDomainMountPoint=str:/var/lib/exports/iso
OVESETUP_CONFIG/isoDomainACL=str:*(rw)
OVESETUP_CONFIG/engineHeapMin=str:3987M
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
        print("SetUpClass %s" % cls)
        n = "-%s" % cls.__name__
        cls.node = cls._start_vm("node" + n, NODE_IMG,
                                 "node-" + n + ".qcow2", 77)
        ENGINE_IMG = NODE_IMG
        cls.engine = cls._start_vm("engine" + n, ENGINE_IMG,
                                   "engine" + n + ".qcow2", 88)

        # FIXME
        # Here we need to do the engine setup
        debug("Installing engine")
        cls.engine.post("/root/engine-answers", cls.ENGINE_ANSWERS)
        cls.engine.start()
        debug(cls.engine.ssh("engine-setup --offline --config=/root/engine-answers"))
        cls.engine.shutdown()
        debug("Installation completed")

    @classmethod
    def tearDownClass(cls):
        debug("Tearing down %s" % cls)
        cls.node = None
        cls.engine = None

    def setUp(self):
        self.node_snapshot = self.node.snapshot()
        self.engine_snapshot = self.engine.snapshot()
        self.node.start()
        self.engine.start()

    def tearDown(self):
        self.node_snapshot.revert()
        self.engine_snapshot.revert()


class TestIntegrationTestCase(IntegrationTestCase):
    def test_intra_network_connectivity(self):
        debug("Node: %s" % self.node.ssh("ifconfig"))
        debug("Engine: %s" % self.engine.ssh("ifconfig"))

        debug(self.node.ssh("ping -c1 10.11.12.88"))
        debug(self.engine.ssh("ping -c1 10.11.12.77"))

    @unittest.skip("Not implemented")
    def test_add_host(self):
        pass

    @unittest.skip("Not implemented")
    def test_spawn_vm(self):
        pass


if __name__ == "__main__":
    unittest.main()
