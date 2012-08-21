xapi-openstack
==============

XAPI - OpenStack utilities

List VHD files on your XenServer host
-------------------------------------
This command will display the name of the virtual machines, and the disks
attached to it. Templates, machines with non-vhd disks will be filtered out.
You can use the output to export those files to the cloud.

    list_vhds --xapi-url=https://yourxenserver --user=root --password=pass

Upload VHD files to OpenStack (In Progress)
-------------------------------------------
You will need the appropriate XenAPI Host plugins on your XenServer host.

    upload_vhd root xapipass https://yourxenserver ks.user ks.password \
    tenant_name http://yourkeystone/v2.0 vhd_uuid image_uuid
