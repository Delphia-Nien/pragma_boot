The pragma_boot script
----------------------

**pragma_boot** is the main program to instantiate Virtual Machine in PRAGMA.
It accepts the following agruments:

Usage: pragma_boot [-v][-d][--basepath path] --list [options] | --vcname vcname [options]

Options:
 General options
 
 * --version, show program's version number and exit 
  
 * -h, --help show this help message and exit 

 * --basepath=BASEPATH, The base path used to find all the cluster images (default is /state/partition1/vm-images)
                        
 * -v, --verbose, Print all debugging information to stdout

 * -d, --debug, Print only the command that will be executed do not execute them
                        
 * --list, list available virtual machines

 * --vcname=VCNAME,  The name of the cluster which should be started

List Options:
 Options for --list command


Create Options:
 Options for --vcname command

 * --key=KEY, The ssh key that will be authorized on the frontend of the cluster (default is /root/.ssh/id_rsa.pub)
  
 * --num_cpus=NUM_CPUS, The nuber of cpus requested to start up (default is 0 only frontend will be started)
 
 * --enable-ipop-client=IPOP_CLIENTINFO_FILE, Start up virtual cluster as an ipop client to another virtual cluster

 * --enable-ipop-server=IPOP_SERVERINFO_FILE, Fetch the ipopserver.info file from the IPOP-enabled frontend when started and write to provided file


pragma_boot invokes the follwing subscripts which will be invoked in the order described below.
In the commands below the ve_dirver will be replaced with the local Virtual Engine (VE)
driver (the base path used to find all the VE drivers can be configured in the file
site_conf.conf)
site_conf.conf should be used also to set the path for the temporary_directory used for
staging all VM images


* **ve_driver/fix_images** prepare the given VC images to be run on the current system
  (fix kernel, drivers, boot options, for current platform, etc.).
  It's input arguments are (in the following order):

  1. **vc_in_file**     the path to the vc-in.xml file of the virtual machine we have to convert
  2. **temp_directory** the temporary directory used to place all the temporary virtual
  3. **node_type**      a command separated list of node type to be prepared
     (e.g. "frontend,compute")

* **ve_driver/allocate** this script takes care of verifying that there are enough
  resources to satisfy the user request, if so it will also allocate public IP,
  private IPs, MAC addresses, and computing resources. If the system can create
  SMP nodes it can allocate less compute node with multiple cpus in each node.
  If successful it will write a /root/vc-out.xml file inside the various virtual machines
  images (see below for more info)

  1. **num_cpus**       it specifies the number of CPU requested by the user.
  2. **vc_in_path**     it points to the vc-in.xml of the selected cluster
  3. **vc_out_path**    this should point to the path where the frontend vc-out.xml will be saved
  4. **temp_directory** the temporary directory used to place all the temporary virtual
  5. **key**            The path to the ssh public key that will be authorized to the
     frontend root account


* **ve_driver/boot** it takes care of starting the VM on the local virtualization
  engine. Its input parameters are:
  
  1. **file_path**      the path where the vm image is
  2. **host_name**      the name of the host we want to boot
  3. **temp_directory** the temporary directory used to place all the temporary virtual
  4. **vc_out_path**    this should point to the path where the frontend vc-out.xml is saved
  5. **ipop_serverinfo_file**  path to store/fetch ipopserver.info file
  6. **ipop_client**    0 if ipopserver.info file needs to be fetched or 1 if file needs to be installed



The sequence of calls for the driver is the following:

1. fix_images: called once for each pragma_boot invocation
2. allocate: called once for each pragma_boot invocation
3. boot: called once for each node in the cluster


input and output XML file example
=================================


vc-in.xml file example. This xml file is a concatenation of the libvirt xml
of a frontend and of a compute node (enclosed between the ``frontend`` and
``compute`` tag) with few extra tags added at the beginning and at the end.

::

 <vc version='0.1'>
   <virtualization engine='kvm' type='hvm' arch='x86_64'/>
   <driver>rocks6_client</driver>
   <frontend>
     <!-- this is the libvirt xml syntax unmodified 
          see: http://libvirt.org -->
     <domain type='kvm'>
       <name>calit2-119-222</name>
       <os>
         <type>hvm</type>
         <boot dev='network'/>
         <boot dev='hd'/>
         <bootmenu enable='yes'/>
       </os>
       <memory>1048576</memory>
       <vcpu>1</vcpu>
       <features>
               <acpi/>
               <apic/>
               <pae/>
       </features>
       <devices>
         <emulator>/usr/libexec/qemu-kvm</emulator>
         <interface type='bridge'>
           <source bridge='eth0.2'/>
           <mac address='7a:77:6e:40:00:07'/>
           <model type='virtio' />
         </interface>
         <interface type='bridge'>
           <source bridge='eth1'/>
           <mac address='7a:77:6e:40:00:08'/>
           <model type='virtio' />
         </interface>
         <disk type='file' device='disk'>
           <driver name='qemu' type='raw'/>
           <source file='calit2-119-222.img.gz'/>
           <target dev='hda' bus='ide'/>
         </disk>
         <graphics type='vnc' port='-1'/>
         <console tty='/dev/pts/0'/>
       </devices>
     </domain>
     <!-- end libvirt xml format -->
   </frontend>
   <compute>
     <boot_dependency parent='frontend'>
       <wait type='clock' value='300'/>
     </boot_dependency>
     <!-- this is the libvirt xml syntax unmodified 
          see: http://libvirt.org -->
     <domain type='kvm'>
       <name>compute-0-0-0</name>
       <os>
         <type>hvm</type>
         <boot dev='network'/>
         <boot dev='hd'/>
         <bootmenu enable='yes'/>
       </os>
       <memory>1048576</memory>
       <vcpu>1</vcpu>
       <features>
         <acpi/>
         <apic/>
         <pae/>
       </features>
       <devices>
         <emulator>/usr/libexec/qemu-kvm</emulator>
         <interface type='bridge'>
           <source bridge='eth0.2'/>
           <mac address='7a:77:6e:40:00:0a'/>
           <model type='virtio' />
         </interface>
         <disk type='file' device='disk'>
           <driver name='qemu' type='raw'/>
           <source file='hosted-vm-0-0-1.img.gz'/>
           <target dev='hda' bus='ide'/>
         </disk>
         <graphics type='vnc' port='-1'/>
         <console tty='/dev/pts/0'/>
       </devices>
     </domain>
     <!-- end libvirt xml format -->
   </compute>
   <networks>
     <network name='private'>
       <ipaddress>10.1.1.1</ipaddress>
       <netmask>255.255.0.0</netmask>
     </network>
     <frontend>
         <public>eth1</public>
     </frontend>
   </networks>
 </vc>


vc-out.xml file example for a frontend

::

 <vc>
   <frontend>
     <public fqdn="somehost.ucsd.edu" ip="123.123.123.123" netmask="255.255.255.0" gw="123.123.123.1" mac="7a:77:6e:40:00:10"/>
     <private ip="10.1.1.1" netmask="255.255.0.0" mac="7a:77:6e:40:00:09"/>
   </frontend>
   <compute count="2">
     <node name="hosted-vm-0-1-0" mac="7a:77:6e:40:00:15" ip="10.1.0.254" cpus="2"/>
     <node name="hosted-vm-0-0-0" mac="7a:77:6e:40:00:14" ip="10.1.0.253" cpus="2"/>
   </compute>
   <network>
     <dns ip="8.8.8.8" search="local" domain=""/>
   </network>
   <key>ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA6vUe5tX+DztYyvUf6n+diFGbOOU9hcGLuXIY/NeLpIHePzpCyoS3Axx3HjjTiIekReUFIwgdWVaFqWtfYp4GpgqAdUThzoCNJqsENY884NTsoUV86Eou/E6fXIr3A2Z0Mr4vI8K5AouRMHLeoFZXgDyNZ7xJnRP0h2aTQNmx3lh8yUt2J/t7J5MphftPWEoYlfS9CdzXpxjxq2srWnDDwPMp7k9vOI8RaVKwfDBEGT6TITtzwNc5gRzTOv6OxxUr3z5n7MI6i5kiKDjmXSpd28gq/IgpTBZ6Ur0/Eq0EufrEHoSWHXdTF5/cAYrqhJJaqr6Movku0eeElvOCBxjTDw== root@somehost.ucsd.edu</key>
 </vc>

vc-out.xml file example for a compute node

::

 <vc>
   <frontend>
     <public fqdn="somehost.ucsd.edu"/>
   </frontend>
   <compute>
     <private fqdn="hosted-vm-0-1-0" ip="10.1.1.30" netmask="255.255.0.0" gw="10.1.1.1" mac="7a:77:6e:40:00:15"/>
   </compute>
   <network>
     <dns ip="8.8.8.8" search="local" domain=""/>
   </network>
   <key>ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA6vUe5tX+DztYyvUf6n+diFGbOOU9hcGLuXIY/NeLpIHePzpCyoS3Axx3HjjTiIekReUFIwgdWVaFqWtfYp4GpgqAdUThzoCNJqsENY884NTsoUV86Eou/E6fXIr3A2Z0Mr4vI8K5AouRMHLeoFZXgDyNZ7xJnRP0h2aTQNmx3lh8yUt2J/t7J5MphftPWEoYlfS9CdzXpxjxq2srWnDDwPMp7k9vOI8RaVKwfDBEGT6TITtzwNc5gRzTOv6OxxUr3z5n7MI6i5kiKDjmXSpd28gq/IgpTBZ6Ur0/Eq0EufrEHoSWHXdTF5/cAYrqhJJaqr6Movku0eeElvOCBxjTDw== root@somehost.ucsd.edu</key>
 </vc>

PRAGMA Virtual Cluster Requirements
==================================

To create a virtual cluster which is compatible with PRAGMA infrastructure the 
nodes must respect the following criteria (with the current versio of software):

- Physical frontend must have fuse and libguestfs-tools-c
- All host run inside kvm-based virtualization engine.
- Each VM have a single disk image
- VM disk images can be compressed using Lempel-Ziv coding (with extension .gz)
- VM disk images must be in raw format (no cow, or other format supported)
- The first partition is the / partition
- No LVM/RAID or other fancy FS type is supported
- Frontend VM contains 2 network interfaces. The first one connects to private
  network. The other connect to public network
- Compute VM contains 1 network interface connected to private network
- when the frontend boot, it expects a file in /root/vc-out.xml as described
  above to configure its network interfaces and the list of compute hosts
- when the compute node boot, it expects a file in /root/vc-out.xml as descibed 
  above to configure its network

Cloud Repository
================

PRAGMA Bootstrap currently support 3 repository types which can be configured in site_conf.conf file. Some repository type may requires extra settings.

* **Local** Disable cloud repository completely.

* **Http** Repository hosted on any http/https server including Amazon S3. No authentication is supported.

  * **repository_url** : Base url of the repository. For Amazon S3, the url is `https://s3.amazonaws.com/<bucket_name>`. Note that for Amazon S3, the file must be publicly accessible. **Do not omit http:// or https://**

* **CloudFront** Repository hosted on Amazon CloudFront with automatic signed url creation.

  * **repository_url** : CloudFront `domain name` of the distribution to use. Can be found on AWS CloudFront Console. **Do not omit http:// or https://**
  * **keypair_id** : CloudFront Key Pair. Generated from AWS Security Console. See extras section for instruction.
  * **private_key_file** : Full path to private key file corresponded to keypair_id. Generated from AWS Security Console. See extras section for instruction.

Python Dependencies

* boto
* rsa

Example of <files> section in vc-in.xml . This extension only available for Http and CloudFront repository.

::

 <files>
  <file type="splited_gzip" filename="frontend.vda">
    <part>frontend.vda.gz.a</part>
    <part>frontend.vda.gz.b</part>
    <part>frontend.vda.gz.c</part>
  </file>
  <file type="gzip" filename="compute.vda">
    <part>compute.vda.gz</part>
  </file>
  <file type="raw">
    <part>dummy.py</part>
  </file>
  <file type="splited" filename="compute-copy.vda">
    <part>compute-copy.vda.a</part>
    <part>compute-copy.vda.b</part>
    <part>compute-copy.vda.c</part>
    <part>compute-copy.vda.d</part>
  </file>
 </files>

Extras
======

**Generating CloudFront Key Pair**

1. Log into AWS Console
2. Click on account name and select `Security Credentials`
3. Expand `CloudFront Key Pairs` section and click `Create New Key Pair`
4. Download public key, private key and take note of access key id (keypair id)

TODO
======

#. Make fuse and libguestfs-tools-c part of the roll
#. update documentation (Readme)
#. move driver.conf and a template for it to /etc from pragma/drivers/kvm_rocks (and same for other drivers)
#. implement ipop (possibly need to build a  new roll first)
#. intergrate pragma-boot an pragma_boot_roll into one
#. revise the open nebula driver
#. revise core/cpu allocation 
#. fix reconfig of sge on compute nodes in dynip roll
#. fid MustBeRoot = 1 logic in pragma script.




