import sys

import xapi_openstack.list_vhds
import xapi_openstack.upload_vhd


def list_vhds():
    xapi_openstack.list_vhds.main(sys.argv)


def upload_vhd():
    xapi_openstack.upload_vhd.main(sys.argv)
