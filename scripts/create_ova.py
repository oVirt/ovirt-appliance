#!/usr/bin/env python


#from imagefactory_plugins.ovfcommon.ovfcommon import RHEVOVFPackage
#from oz.ozutil import copyfile_sparse
import argparse


class OvaBuilder(object):
    """A simple wrapper around ImgFac'sova building capabilities

    The main difference is that this tool is intended to work standalone.
    """
    def generate_rhevm_ova(self, dst, src,
                           ovf_cpu_count=2, ovf_memory_mb=1024,
                           rhevm_default_display_type="0",
                           rhevm_description="Created by OVABuilder",
                           rhevm_os_descriptor="OtherLinux"):
        """Generate an OVA wrapper for classic VM image files

           Arguments:
               dst: Destination ova file
               src: Source VM image
               ovf_cpu_count: Number of virtual CPUs
               ovf_memory_mb: Amount of memory of the VM in MB
               FIXME more
        """
        return self._generate_ova(dst, src,
                                  "rhevm",
                                  {"ovf_cpu_count": ovf_cpu_count,
                                   "ovf_memory_mb": ovf_memory_mb,
                                   "rhevm_default_display_type":
                                   rhevm_default_display_type,
                                   "rhevm_description": rhevm_description,
                                   "rhevm_os_descriptor": rhevm_os_descriptor
                                   })

    def _generate_ova(self, dst, src, target, params):
        """Generate an OVA file from a disk image for some target
        Arguments:
            dst: Destination of the .ova file
            src: Path to a source VM image
            target: Either rhevm or vsphere
            params: Additional params to FOO FIXME
        """
        if target == 'rhevm':
            klass = RHEVOVFPackage
#        elif target == 'vsphere':
#            klass = VsphereOVFPackage
        else:
            raise RuntimeError("Only supporting rhevm and vsphere images")

        klass_parameters = dict()

        if self.parameters:
            params = ['ovf_cpu_count', 'ovf_memory_mb',
                      'rhevm_default_display_type', 'rhevm_description',
                      'rhevm_os_descriptor',
                      'vsphere_product_name', 'vsphere_product_vendor_name',
                      'vsphere_product_version']

            klass_has = lambda x: klass.__init__.func_code.co_varnames.\
                __contains__(x)

            for param in params:
                if self.parameters.get(param) and klass_has(param):
                    klass_parameters[param] = self.parameters.get(param)

        pkg = klass(disk=src, **klass_parameters)
        ova = pkg.make_ova_package()
        copyfile_sparse(ova, dst)
        pkg.delete()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cpu", type=int,
                        default=4,
                        help="Number of virtual CPUs")
    parser.add_argument("-m", "--mem", type=int,
                        default=2048,
                        help="Amount if virtual RAM in MB")
    parser.add_argument("SRC", type=str,
                        nargs=1,
                        help="Path to raw image (qcow2, raw, ...)")
    parser.add_argument("DST", type=str,
                        nargs=1,
                        help="Path to destination DIR FILE?")

    parser.epilog = """\
This tool can be used to create an OVA wrapper around existing
VM images like plain raw or qcow2 images.

A common usage looks like:

%prog --cpu 4 --mem 4096 -s fedora.qcow2 -d fedora.ova
"""

    options, args = parser.parse_args()

    print (options, args)
