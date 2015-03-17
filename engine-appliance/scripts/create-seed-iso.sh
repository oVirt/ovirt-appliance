
# Ref: http://cloudinit.readthedocs.org/en/latest/topics/datasources.html#no-cloud

{ echo instance-id: iid-local01; echo local-hostname: cloudimg; } > meta-data

printf "#cloud-config\npassword: passw0rd\nchpasswd: { expire: False }\nssh_pwauth: True\n" > user-data

## create a disk to attach with some user-data and meta-data
genisoimage  -output seed.iso -volid cidata -joliet -rock user-data meta-data
