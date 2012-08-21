import unittest
import mock
import textwrap

from xapi_openstack.upload_vhd import (
    UploadVHD, KSClient, collect_args
)
from xapi_openstack import services


class UploadVHDTestCase(unittest.TestCase):
    ARGS = {
        'xapi': {
            'url': 'xapiurl',
            'user': 'xapiuser',
            'password': 'xapipass'
        },
        'ks': {
            'auth_url': 'ksurl',
            'password': 'kspass',
            'tenant_name': 'tn',
            'user': 'ksusr'
        },
        'vhd_uuid': 'vhduuid',
        'image_uuid': 'imageuuid'
    }

    def test_with_valid_parameters(self):
        upload = UploadVHD(self.ARGS)
        upload.validate()

    def test_with_invalid_parameters(self):
        upload = UploadVHD()

        with self.assertRaises(services.Invalid):
            upload.validate()


class TestArgParsing(unittest.TestCase):
    def test_option_collecting(self):
        self.assertEquals({
            'xapi': {
                'user': 'xapiusr',
                'password': 'xapipass',
                'url': 'xapiurl',
            },
            'ks': {
                'user': 'ksuser',
                'password': 'kspass',
                'tenant_name': 'tenant',
                'auth_url': 'ksurl',
            },
            'vhd_uuid': 'vhduu',
            'image_uuid': 'imageuu'
        }, collect_args(textwrap.dedent("""
            xapiusr
            xapipass
            xapiurl
            ksuser
            kspass
            tenant
            ksurl
            vhduu
            imageuu
            """).strip().split()))
