import unittest

from xapi_openstack.upload_vhd import UploadVHD


class UploadVhdValidationTestCase(unittest.TestCase):
    def test_all_parameters_given_is_valid(self):
        upload = UploadVHD(
            username="user",
            password="password",
            tenant_name="demo",
            auth_url="http://127.0.0.1:5000/v2.0")

        upload.validate()

        self.assertTrue(upload.valid)

    def test_missing_parameter(self):
        upload = UploadVHD(
            password="password",
            tenant_name="demo",
            auth_url="http://127.0.0.1:5000/v2.0")

        upload.validate()

        self.assertFalse(upload.valid)
        
