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
Main features of tehse classes:
- root less integration testing
- VM connectivity without bridge
- cloud-init integration to do IP configuration
"""

from logging import debug
import sh
import os
import tempfile
import random
import time
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


def random_mac():
    """Generate a random mac
    """
    mac = [0x00, 0x16, 0x3e,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))


class CloudConfig():
    """Convenience class to create cloud-init configuration
    """
    instanceid = None
    password = None

    runcmd = None

    ssh_authorized_keys = []

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


class DiskImage():
    """Represents a disk image

    Main reason for this wrapper is access to teh reflink feature
    and cleaning the image in the end.
    """
    name = None

    def __init__(self, name):
        self.name = name

    def reflink(self, dst):
        dst = os.path.abspath(dst)
        sh.qemu_img("create", "-fqcow2", "-o",
                    "backing_file=%s" % self.name, dst)
        img = DiskImage(dst)
        img.__del__ = lambda d=dst: sh.rm("-f", d)
        return img

    def __str__(self):
        return self.name


class VM():
    """Represents a VM instance (root-less)
    This is quite high-level. Here the VM (machine) can be configured
    as well as some OS things (using cloud-init).
    Assuming this machine and OS level confgiuration, this class also
    offers a few convenience functions (like ssh) based on the assumed
    configuration of the VM.
    """

    name = None
    _ssh_port = None
    _ssh_identity_file = os.environ["HOME"] + "/.ssh/id_rsa"

    def __del__(self):
        debug("Destroying VM %r" % self.name)
        self.undefine()

    @staticmethod
    def create(name, disk, ssh_port=None, memory_gb=2):
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
                <qemu:arg value='-netdev'/>
                <qemu:arg value='socket,id=busnet0,mcast=230.0.0.1:1234'/>
                <qemu:arg value='-device'/>
                <qemu:arg value='virtio-net-pci,netdev=busnet0,mac={mac}'/>
                </qemu:commandline>
                """.format(ssh_port=ssh_port, mac=random_mac()))
                root.append(snippet)

            return ET.tostring(root)

        define = sh.virsh.bake("define")
        dom = sh.virt_install("--import",
                              "--print-xml",
                              name=name,
                              disk=("path=%s,bus=virtio,"
                                    "discard=unmap,cache=unsafe") % disk,
                              memory=int(1024 * int(memory_gb)),
                              vcpus=4,
                              cpu="host",
                              network="user,model=virtio",
                              watchdog="default,action=poweroff",
                              serial="pty",
                              graphics="none",  # headless
                              noautoconsole=True,
                              filesystem="%s,HOST,mode=squash" % os.getcwd(),
                              memballoon="virtio",  # To save some host-ram
                              rng="/dev/random",  # For entropy
                              check="all=off")

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
        """SSH into the host
        """
        assert self._ssh_port
        args = ("root@127.0.0.1",
                "-oPort=%s" % self._ssh_port,
                "-oConnectTimeout=30",
                "-oConnectionAttempts=3",
                "-oStrictHostKeyChecking=no",
                "-oUserKnownHostsFile=/dev/null",
                "-oBatchMode=yes",
                "-oRequestTTY=force",
                "-oIdentityFile=" + self._ssh_identity_file,
                ) + args
        debug("SSHing: %s %s" % (args, kwargs))
        data = sh.ssh(*args, **kwargs)
        debug("stdout: %s" % data)
        return data

    def snapshot(self):
        """Create a snapshot to revert to

        snap = vm.snapshot()
        …
        snap.revert()
        """
        dom = self

        class VMSnapshot():
            def __init__(self):
                sh.virsh("snapshot-create-as", dom.name)
                self.sname = str(sh.virsh("snapshot-current", "--name",
                                          dom.name)).strip()
                debug("Created snap %r of dom %r" % (self.sname, dom.name))
                # Snapshots just use seconds, sometimes we have more than
                # one snap per second, thus we add an extra sleep to prevent
                # snap-id collisions
                time.sleep(1.2)

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
        """Run guestfish on the disk of the VM
        """
        return sh.guestfish("--network", "-v", "-d", self.name, "-i", *args)

    @logcall
    def start(self):
        """Start the VM
        """
        sh.virsh("start", self.name)

    @logcall
    def destroy(self):
        """Forefully shutdown a VM
        """
        sh.virsh("destroy", self.name)

    @logcall
    def shutdown(self, wait=True, timeout=60):
        """Ask the VM to shutdown (via ACPI)

        Also block until the VM is shutdown
        """
        sh.virsh("shutdown", "--mode=acpi", self.name)
        if wait:
            self.wait_event("lifecycle", timeout=timeout)

    @logcall
    def reboot(self):
        """Ask the VM to reboot (via ACPI)
        """
        sh.virsh("reboot", "--mode=acpi", self.name)

    @logcall
    def undefine(self):
        """Remove a VM definition and it's snapshots
        """
        try:
            self.destroy()
        except Exception:
            pass
        sh.virsh("undefine", "--snapshots-metadata", self.name)

    @logcall
    def wait_event(self, evnt=None, timeout=None):
        """Wait for a event of a VM

        virsh event --help
        """
        args = ["--event", evnt] if evnt else ["--all"]
        if timeout:
            args += ["--timeout", timeout]
        sh.virsh("event", "--domain", self.name, *args)

    def wait_reboot(self, timeout=None):
        """Wait for the VM to reboot
        """
        return self.wait_event("reboot", timeout=timeout)

    def console(self):
        """Attach to the VM serial console
        """
        pty = str(sh.virsh("ttyconsole", self.name)).strip()
        with open(pty, "rb") as src:
            for line in src:
                yield line

    def set_cloud_config(self, cc):
        """Inject a cloud config into the VM by editing the disk
        """
        noclouddir = "/var/lib/cloud/seed/nocloud"
        self.fish("sh", "mkdir -p %s" % noclouddir,
                  ":",
                  "write", "%s/user-data" % noclouddir, cc.user,
                  ":",
                  "write", "%s/meta-data" % noclouddir, cc.meta,
                  )

    def upload(self, local, remote):
        """Copy a file from the host to the guest
        """
        self.fish("upload", local, remote)

    def post(self, remote, data):
        """Write data to a file inside the guest
        """
        self.fish("write", remote, data)

# vim: et ts=4 sw=4 sts=4
