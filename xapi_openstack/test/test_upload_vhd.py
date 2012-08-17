import unittest
import mock

from xapi_openstack.upload_vhd import (
    UploadVHD, ConnectToKeystone, Invalid
)


class UploadVHDTestCase(unittest.TestCase):
    def test_get_xapi_session(self):
        session = mock.Mock()
        xapi = mock.Mock()
        xapi.Session.return_value = session
        c = mock.call

        upload = UploadVHD(
            xapiurl="someurl", xapiuser='xapiuser',
            xapipass='xapipass')

        result = upload.get_xapi_session(xapi=xapi)

        self.assertEquals(
            [
                c.Session("someurl"),
                c.Session().login_with_password('xapiuser', 'xapipass')
            ],
            xapi.mock_calls)

        self.assertEquals(
            session, result)

    def test_get_single_host(self):
        myhost = object()
        session = mock.Mock()
        session.xenapi.host.get_all.return_value = [myhost]

        upload = UploadVHD()
        result = upload.get_single_host(session=session)

        self.assertEquals(myhost, result)


class ConnectToKeystoneTestCase(unittest.TestCase):

    def test_all_parameters_given_is_valid(self):
        connect = ConnectToKeystone(
            username="user",
            password="password",
            tenant_name="demo",
            auth_url="http://127.0.0.1:5000/v2.0")

        try:
            connect.validate()
        except Invalid:
            raise AssertionError()

    def test_missing_parameter(self):
        connect = ConnectToKeystone(
            password="password",
            tenant_name="demo",
            auth_url="http://127.0.0.1:5000/v2.0")

        self.assertRaises(Invalid, connect.validate)

    def test_keystone_client_created(self):
        ksclient = mock.Mock()
        c = mock.call

        connector = ConnectToKeystone(
            username="user",
            password="password",
            tenant_name="demo",
            auth_url="http://127.0.0.1:5000/v2.0")

        client = connector.get_keystone_client(ksclient=ksclient)

        self.assertEquals(
            [c.Client(
                username="user", password="password",
                tenant_id=None, tenant_name="demo",
                auth_url="http://127.0.0.1:5000/v2.0",
                insecure=False)],
            ksclient.mock_calls
        )

    def test_auth_token(self):
        atoken = object()
        client = mock.Mock()
        client.auth_token = atoken

        class MockConnector(ConnectToKeystone):
            def get_keystone_client(self, ksclient=None):
                return client

        connector = MockConnector()

        self.assertEquals(atoken, connector.auth_token)

    def test_glance_host_port(self):
        atoken = object()
        client = mock.Mock()
        client.service_catalog.url_for.return_value = "http://127.0.0.1:9292"

        class MockConnector(ConnectToKeystone):
            def get_keystone_client(self, ksclient=None):
                return client

        connector = MockConnector()

        self.assertEquals("127.0.0.1", connector.glance_host)
        self.assertEquals(9292, connector.glance_port)
