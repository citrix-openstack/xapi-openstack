import unittest
import mock

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


class UploadVhdKeystoneCallsTestCase(unittest.TestCase):
    def test_keystone_client_created(self):
        ksclient = mock.Mock()
        c = mock.call

        upload = UploadVHD(
            username="user",
            password="password",
            tenant_name="demo",
            auth_url="http://127.0.0.1:5000/v2.0")

        client = upload.get_keystone_client(ksclient=ksclient)

        self.assertEquals(
            [c.Client(
                username="user", password="password",
                tenant_id=None, tenant_name="demo",
                auth_url="http://127.0.0.1:5000/v2.0",
                insecure=False)],
            ksclient.mock_calls
        )


class InstructXapiToUploadTestCase(unittest.TestCase):
    def test_get_xapi_session(self):
        xapi = mock.Mock()
        c = mock.call

        upload = UploadVHD(xapiurl="someurl", xapiuser='xapiuser', xapipass='xapipass')

        upload.get_xapi_session(xapi=xapi)

        self.assertEquals([
            c.Session("someurl"),
            c.Session().login_with_password('xapiuser', 'xapipass')
            ],
            xapi.mock_calls)
