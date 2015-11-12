Integration testing
===================

This directory contains the testcases to test the integration between
Node and Engine.

Dedicated directories to test the sanity of each image independently are
kept in the respective appliance specific test directories.

To test:

    # Install dependencies
    yum install -y \
        libvirt-daemon \
        libvirt-client \
        libvirt-daemon-qemu \
        libvirt-daemon-kvm \
        python-sh \
        virt-install \
        libguestfs \
        libguestfs-tools \
        openssh-clients \
        squashfs-tools \
        python-nose \
        python-pep8 \
        pyflakes
    
    make clean-build-and-check

This will take a long time, because it will build the Engine and Node
appliance, once that is done it will perform the integration tests.
