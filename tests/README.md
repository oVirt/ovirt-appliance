Integration testing
===================

This directory contains the testcases to test the integration between
Node and Engine.

Dedicated directories to test the sanity of each image independently are
kept in the respective appliance specific test directories.

To test:

    # Install dependencies
    sudo yum install -y \
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
        pyflakes \
        libselinux-utils
    
    # Permissive mode is required for now
    sudo setenforce 0
    
    # Checkout the repository
    git clone https://gerrit.ovirt.org/p/ovirt-appliance.git
    cd ovirt-appliance
    git submodule update --init
    cd tests
    
    # The build and testing itself
    make clean-build-and-check

This will take a long time, because it will build the Engine and Node
appliance, once that is done it will perform the integration tests.
