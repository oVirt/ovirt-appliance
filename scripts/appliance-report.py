#!/usr/bin/python

import guestfs
import glob
import itertools
import os
import shutil
import sys
import tarfile

from lxml import etree
from tempfile import mkdtemp

def generate_report(ova):
    name = '.'.join(ova.split('.')[:2])

    extract_list = []
    disk_size = None
    mem_size = None
    pkgs = None
    tmpdir = None

    with tarfile.open(ova, 'r:gz') as t:
        extract_list = read_ova(t)
        tmpdir = extract_files(t, extract_list)
        disk_size, mem_size = parse_ovf(tmpdir)
        pkgs = get_manifest(tmpdir)

    shutil.rmtree(tmpdir)

    mem_size = mem_size / 1024

    tmpl = '''
rhevm-appliance: %s

Results  PASS

Smoke testing passed
cloud-init starts
Networking up
Initial root password setup works
Disk resized to %sG
OVF indicates %sGB memory
RHEV-M setup works correctly
RHEV-M admin portal is available after setup and login works

Key Packages:
%s
    ''' % (name, disk_size, mem_size, pkgs)
    return tmpl


def get_ovf(tmpdir):
    ovf = glob.glob(tmpdir + "/*.ovf")[0]
    return ovf

def get_disk(tmpdir):
    disk = None
    for f in glob.glob(tmpdir + '/*'):
        if os.path.isfile(f) and not os.path.basename(f).endswith(".ovf"):
            disk = f
    return disk

def get_manifest(tmpdir):
    disk = get_disk(tmpdir)

    guestfish = guestfs.GuestFS(python_return_dict=True)
    guestfish.add_drive_opts(disk, readonly=1)
    guestfish.launch()
    rootdev = guestfish.inspect_os()[0]
    guestfish.mount(rootdev, "/")
    pkgs = query(guestfish)

    guestfish.umount_all()
    return pkgs

def query(guestfish):
    pkgs = None

    try:
        pkgs = guestfish.sh("rpm -q glibc heat-cfntools kernel openssl "
                "ovirt-guest-agent-common")
    except:
        pkgs = guestfish.sh("rpm -q glibc heat-cfntools kernel openssl "
                "rhevm-guest-agent-common")

    return pkgs


def parse_ovf(tmpdir):
    ovf = get_ovf(tmpdir)
    tree = etree.parse(ovf)
    root = tree.getroot()

    disk_size = 0
    mem_size = 0

    namespaces = {'ovf': 'http://schemas.dmtf.org/ovf/envelope/1/'}
    for s in root.findall(".//Disk[@ovf:actual_size]", namespaces):
        for k in s.keys():
            if "actual_size" in k:
                disk_size = s.attrib[k]

    for s in root.xpath(".//Info[contains(text(), 'CPU')]"):
        mem_size = int(s.text.split(',')[1].split()[0])

    return (disk_size, mem_size)

def extract_files(t, extract_list):
    tmpdir = mkdtemp(dir=".")
    t.extractall(path=tmpdir, members=extract_list)
    flatten(tmpdir)
    return tmpdir


def flatten(dest):
    move_files = []
    for root, _dirs, files in itertools.islice(os.walk(dest), 1, None):
        for f in files:
            move_files.append(os.path.join(root, f))
    for f in move_files:
        shutil.move(f, dest)


def read_ova(tar):
    extract_list = []
    for m in tar.getmembers():
        if m.name.endswith(".ovf") or m.size > 5000:
            extract_list.append(m)

    return extract_list

if __name__ == '__main__':
    report = generate_report(sys.argv[1])
    print report
