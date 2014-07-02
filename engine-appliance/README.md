
Virt Virtual Appliance
=======================

Kickstart files to build the oVirt Engine Virtual Appliance.


Design
------

Initially the image will be based on the Fedora Cloud base.

Later on a CentOS based image can also be considered.


Build
-----
You will need

* an internet connection
* at least Fedora 19.
* 5 GB of ram
* 10 GB of disk

Then:

    setenforce 0
    yum install -y lorax pykickstart virt-install
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

