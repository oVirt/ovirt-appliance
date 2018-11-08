
Virt Virtual Appliance
=======================

Kickstart files to build the oVirt Engine Virtual Appliance.


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
* at least Fedora 19+ or CentOS 7+
* 5 GB of ram
* 10 GB of disk

Then:

    setenforce 0
    yum install -y lorax pykickstart virt-install libguestfs-tools imagefactory imagefactory-plugins-OVA
    make

This will create an ova by:
* create the correct ks from a template
* initiate livemedia-creator to create the runtime image
* sysprep and sparsify the rutime image
* finally use an imagefactory plugin to create the ova 


Some links
----------

* [Fedora Cloud Base](https://git.fedorahosted.org/cgit/spin-kickstarts.git/tree/fedora-x86_64-cloud.ks)
* [Docker "Appliance"](https://fedoraproject.org/wiki/Changes/Docker_Cloud_Image)
* [Move to ImgFac](https://fedoraproject.org/wiki/Changes/Move_to_ImageFactory_For_Cloud_Image_Creation)

