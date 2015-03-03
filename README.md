This repository holds a couple of appliances to be consumed by oVirt

**engine-appliance** An appliance image which has everything oyu need for
oVirt Engine, and thus for a self hosted engine.

Cloud init support
===================
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

Create an iso from those two files

`genisoimage  -output seed.iso -volid cidata -joliet -rock user-data meta-data`

Attach the iso to the ovirt-appliance VM on first boot.

Boot

Your root password is now "yourpassword"
