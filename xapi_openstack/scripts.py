import sys

import xapi_openstack.list_vhds
import xapi_openstack.upload_vhd


def add_glance_plugin():
    """ssh to a xapi host, copy the required plugins, so that it can
    communicate with glance"""

    raise NotImplementedError("This is not implemented yet")


def list_vhds():
    xapi_openstack.list_vhds.main(sys.argv)


def upload_vhd():
    xapi_openstack.upload_vhd.main(sys.argv)
