
oVirt Virtual Appliance
=======================

KIWI files to build the oVirt Engine Virtual Appliance.


Cloud init support
------------------

Cloud init is a service that allows to pre configure the image on first run using external file

The big all reference for the advanced staff and what cloud init is :

<https://cloudinit.readthedocs.org/en/latest/index.html>

Setting hostname and root password in a nutshell
------------------------------------------------


The following is only a simple example , please make your own and use your own password

Create the user-data and meta-data files
```
cat <<EOF > user-data
#cloud-config
chpasswd:
  list: |
    root: yourpassword
    expire: False
EOF
cat <<EOF > meta-data
instance-id: ovirt-engine
local-hostname: ovirt-engine
EOF
```


You should change the root password in the user-data file (clear text)

Create an iso from those two files:

    $ genisoimage  -output seed.iso -volid cidata -joliet -rock user-data meta-data

Attach the iso to the ovirt-appliance VM on first boot.

Boot

Your root password is now "yourpassword"

Build
-----
You will need

* an internet connection
* at least CentOS 9+
* 5 GB of ram
* 100 GB of disk

Then:
```
cd engine-appliance; kiwi-ng --debug --profile=qcow2 --kiwi-file=centos9.xml system build --description=kiwi/ --target-dir=build
```

Where you can replace centos9.xml with centos10.xml if you want to build a CentOS 10 qcow2.
Or almalinux9.xml/almalinux10.xml for AlmaLinux 9 / AlmaLinux 10 qcow2 image.