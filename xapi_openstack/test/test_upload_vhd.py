import unittest

from xapi_openstack.upload_vhd import UploadVHD


class UploadVhdTestCase(unittest.TestCase):
    def test_parameter_validation(self):
        upload = UploadVHD(
            username="user",
            password="password",
            tenant_name="demo",
            auth_url="http://127.0.0.1:5000/v2.0")

        upload.validate()

        self.assertEquals(True, upload.valid)

        
