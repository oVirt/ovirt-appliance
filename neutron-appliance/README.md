neutron-appliance
=================

The project designed to provide an ease method of creating neutron virtual appliance.
The appliance is being created by [imagefactory](http://imgfac.org/) and sealed by [virt-sysprep](ttp://libguestfs.org/virt-sysprep.1.html).

The neutron appliance contains the following services:
* Neutron server
* Neutron L3 Agent
* Neutron DHCP Agent
* Open vSwitch Agent
* Open vSwitch
* RabbitMQ (message broker)

#### Creating the image
    imagefactory target_image --template neutron/rdo-icehouse-centos-65-ovs_plugin-vlan.tdl openstack-kvm

This will create a qcow2 image based on Centos-65 and includes RDO relesae IceHouse with the listed neutron services configured.
Tested with imagefactory-1.1.4-1.

#### Sealing the created image
    virt-sysprep --add PATH_TO_CREATED_IMAGE --enable net-hwaddr,dhcp-client-state,ssh-hostkeys,ssh-userdir,udev-persistent-net
Once imagefactory is integraded with virt-sysprep (see [open issue](https://github.com/redhat-imaging/imagefactory/issues/329)), the sealing will be executed as part of the image creation process.
Tested with libguestfs-tools-c-1.20.11-2.

#### What is this image good for ?
The IceHouse image, configured with OpenStack neutron services is designed to be imported from oVirt engine and be used for creating VMs within oVirt to serve as keystone and neutron servers.
The image will be available from (oVirt OpenStack Image Repository](glance.ovirt.org), which is configured by default in oVirt engine installation. The image will be imported into ovirt storage domain and will be used for creating VMs based on it.

Further information regarding the neutron appliance can be found in [here](http://www.ovirt.org/Features/NeutronVirtualAppliance).
