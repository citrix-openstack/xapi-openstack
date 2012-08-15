xapi-openstack
==============

XAPI - OpenStack utilities

List VHD files on your XenServer host
-------------------------------------
This command will display the name of the virtual machines, and the disks
attached to it. Templates, machines with non-vhd disks will be filtered out.
You can use the output to export those files to the cloud.

    list_vhds --xapi-url=https://yourserver --user=root --password=pass

