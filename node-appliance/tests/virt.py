#!/usr/bin/env python
# vim: et ts=4 sw=4 sts=4

import logging
from logging import debug

logging.basicConfig(level=logging.DEBUG)

import sh
import os
import tempfile
from contextlib import contextmanager
import xml.etree.ElementTree as ET


# Increase the capture length of python-sh to show complete errors
sh.ErrorReturnCode.truncate_cap = 999999


def lines(data):
    """This method is not suited for big data
    """
    return [l for l in data.split("\n") if l]


squashfsimg = "ovirt-node-appliance.squashfs.img"
qcowimg = "ovirt-node-appliance.qcow2"


def logcall(func):
    def logged(*args, **kwargs):
        debug("%s(%s, %s)" % (func, args, kwargs))
        r = func(*args, **kwargs)
        return r
    return logged


def get_ssh_pubkey():
    pubkey = os.environ["HOME"] + "/.ssh/id_rsa.pub"
    with open(pubkey, "rt") as src:
        return src.read().strip()


class CloudConfig():
    instanceid = None
    password = None

    runcmd = None

    ssh_authorized_keys = [get_ssh_pubkey()]

    @property
    def user(self):
        data = []
        data.append("#cloud-config")
        data.append("disable_root: False")

        data.append("chpasswd:")
        data.append("  expire: False")
        if self.password:
            data.append("  list: |")
            data.append("     root:%s" % self.password)

        if self.password:
            data.append("password: %s" % self.password)
            data.append("passwd: { expire: False }")
            data.append("ssh_pwauth: True")

        if self.runcmd:
            data.append("runcmd:")
            # data.append(" - %s" % json.dumps(self.runcmd))
            data.append(" - %s" % self.runcmd)

        if self.ssh_authorized_keys:
            data.append("ssh_authorized_keys:")
            for key in self.ssh_authorized_keys:
                data.append("  - %s" % key.strip())

        data = "\n".join(data)
        debug("userdata: %s" % data)
        return data

    @property
    def meta(self):
        data = []
        data.append("instance-id: %s" % self.instanceid)
        data.append("local-hostname: %s" % self.instanceid)

        data = "\n".join(data)
        debug("metadata: %s" % data)
        return data


class Image():
    name = None

    def __init__(self, name):
        self.name = name

    def reflink(self, dst):
        dst = os.path.abspath(dst)
        sh.qemu_img("create", "-fqcow2", "-o",
                    "backing_file=%s" % self.name, dst)
        img = Image(dst)
        img.__del__ = lambda d=dst: sh.rm("-f", dst)
        return img

    def __str__(self):
        return self.name


class VM():
    name = None
    _ssh_port = None

    def __del__(self):
        debug("Destroying VM %r" % self.name)
        self.undefine()

    @staticmethod
    def create(name, disk, ssh_port=None):
        def __hack_dom_pre_creation(domxml):
            root = ET.fromstring(domxml)

            if ssh_port:
                # Needed to make guest ssh port accessible from the outside
                # http://blog.vmsplice.net/2011/04/
                # how-to-pass-qemu-command-line-options.html
                ET.register_namespace("qemu", "http://libvirt.org/"
                                      "schemas/domain/qemu/1.0")
                snippet = ET.fromstring("""
                <qemu:commandline
                 xmlns:qemu="http://libvirt.org/schemas/domain/qemu/1.0">
                <qemu:arg value='-redir'/>
                <qemu:arg value='tcp:{ssh_port}::22'/>
                <qemu:arg value='-net'/>
                <qemu:arg value='socket,mcast=230.0.0.1:1234'/>
                </qemu:commandline>
                """.format(ssh_port=ssh_port))
                root.append(snippet)

            return ET.tostring(root)

        define = sh.virsh.bake("define")
        dom = sh.virt_install("--import",
                              "--print-xml",
                              name=name,
                              disk=("path=%s,bus=virtio,"
                                    "discard=unmap,cache=unsafe") % disk,
                              memory=2048, vcpus=4, cpu="host",
                              network="user,model=virtio",
                              watchdog="default,action=poweroff",
                              serial="pty",
                              graphics="none",
                              noautoconsole=True,
                              filesystem="%s,HOST,mode=squash" % os.getcwd(),
                              check="path_in_use=off")

        dom = __hack_dom_pre_creation(str(dom))

        with tempfile.NamedTemporaryFile() as tmpfile:
            tmpfile.write(str(dom))
            tmpfile.flush()
            define(tmpfile.name)

        vm = VM()
        vm.name = name
        vm.disk = disk
        vm._ssh_port = ssh_port

        return vm

    def ssh(self, *args, **kwargs):
        assert self._ssh_port
        args = ("root@127.0.0.1", "-tt",
                "-oConnectTimeout=30",
                "-oConnectionAttempts=3",
                "-oStrictHostKeyChecking=no",
                "-oUserKnownHostsFile=/dev/null",
                "-oBatchMode=yes",
                "-p%s" % self._ssh_port) + args
        debug("SSHing: %s %s" % (args, kwargs))
        return sh.ssh(*args, **kwargs)

    @logcall
    def attach_cdrom(self, iso):
        sh.virsh("attach-disk", self.name, iso, "sd", live=True)

    def snapshot(self):
        dom = self

        class VMSnapshot():
            def __init__(self):
                sh.virsh("snapshot-create-as", dom.name)
                self.sname = str(sh.virsh("snapshot-current", "--name",
                                          dom.name)).strip()
                debug("Created snap %r of dom %r" % (self.sname, dom.name))

            def revert(self):
                sh.virsh("snapshot-revert", dom.name, self.sname)
                sh.virsh("snapshot-delete", dom.name, self.sname)
                debug("Deleted snap %r of dom %r" % (self.sname, dom.name))

            @contextmanager
            def context(self):
                yield self
                self.revert()

        snap = VMSnapshot()
        snap.dom = dom

        return snap

    @logcall
    def fish(self, *args):
        return sh.guestfish("-v", "-d", self.name, "-i", *args)

    @logcall
    def start(self):
        sh.virsh("start", self.name)

    @logcall
    def destroy(self):
        sh.virsh("destroy", self.name)

    @logcall
    def undefine(self):
        try:
            self.destroy()
        except Exception:
            pass
        sh.virsh("undefine", "--snapshots-metadata", self.name)

    @logcall
    def wait_event(self, evnt=None, timeout=None):
        """virsh event --help
        """
        args = ["--event", evnt] if evnt else ["--all"]
        if timeout:
            args += ["--timeout", timeout]
        sh.virsh("event", "--domain", self.name, *args)

    def wait_reboot(self, timeout=None):
        return self.wait_event("reboot", timeout=timeout)

    def console(self):
        pty = str(sh.virsh("ttyconsole", self.name)).strip()
        with open(pty, "rb") as src:
            for line in src:
                yield line

    def set_cloud_config(self, cc):
        noclouddir = "/var/lib/cloud/seed/nocloud"
        self.fish("sh", "mkdir -p %s" % noclouddir,
                  ":",
                  "write", "%s/user-data" % noclouddir, cc.user,
                  ":",
                  "write", "%s/meta-data" % noclouddir, cc.meta,
                  )


def legacy():
    node_img = Image("ovirt-node-appliance.qcow2").reflink("node-test.qcow2")

    cc = CloudConfig()
    cc.ssh_authorized_keys = [get_ssh_pubkey()]

    node = VM.create("node", node_img, ssh_port=7777)
    with node.snapshot():
        node.set_cloud_config(cc)
        node.start()
        print(node.ssh("ping -c1 10.0.2.2"))
