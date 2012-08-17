import unittest
import mock

from xapi_openstack.upload_vhd import (
    GetXAPIHost, ConnectToKeystone, Invalid, UploadVHD, KSClient
)


class GetXAPIHostTestCase(unittest.TestCase):
    def test_valid_parameter_set(self):
        get_host = GetXAPIHost(dict(
            url='xapiurl', user='xapiuser', password='xapipass'))

        try:
            get_host.validate()
        except Invalid:
            raise AssertionError()

    def test_missing_a_parameter(self):
        get_host = GetXAPIHost(dict(
            user='xapiuser', password='xapipass'))

        with self.assertRaises(Invalid):
            get_host.validate()

    def test_get_xapi_session(self):
        session = mock.Mock()
        xapi = mock.Mock()
        xapi.Session.return_value = session
        c = mock.call

        get_host = GetXAPIHost(dict(
            url="someurl", user='xapiuser',
            password='xapipass'))

        result = get_host.get_xapi_session(xapi=xapi)

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

        get_host = GetXAPIHost()
        result = get_host.get_single_host(session=session)

        self.assertEquals(myhost, result)


class ConnectToKeystoneTestCase(unittest.TestCase):

    def test_all_parameters_given_is_valid(self):
        connect = ConnectToKeystone(dict(
            user="user",
            password="password",
            tenant_name="demo",
            auth_url="http://127.0.0.1:5000/v2.0"))

        try:
            connect.validate()
        except Invalid:
            raise AssertionError()

    def test_missing_parameter(self):
        connect = ConnectToKeystone(dict(
            password="password",
            tenant_name="demo",
            auth_url="http://127.0.0.1:5000/v2.0"))

        self.assertRaises(Invalid, connect.validate)

    def test_keystone_client_created(self):
        ksclient = mock.Mock()
        c = mock.call

        connect = ConnectToKeystone(dict(
            user="user",
            password="password",
            tenant_name="demo",
            auth_url="http://127.0.0.1:5000/v2.0"))

        client = connect(ksclient=ksclient)

        self.assertEquals(
            [c.Client(
                username="user", password="password",
                tenant_id=None, tenant_name="demo",
                auth_url="http://127.0.0.1:5000/v2.0",
                insecure=False)],
            ksclient.mock_calls
        )


class KSClientTestCase(unittest.TestCase):
    def test_auth_token(self):
        atoken = object()
        client = mock.Mock()
        client.auth_token = atoken

        ksclient = KSClient(client)

        self.assertEquals(atoken, ksclient.auth_token)

    def test_glance_host_port(self):
        atoken = object()
        client = mock.Mock()
        client.service_catalog.url_for.return_value = "http://127.0.0.1:9292"

        ksclient = KSClient(client)

        self.assertEquals("127.0.0.1", ksclient.glance_host)
        self.assertEquals(9292, ksclient.glance_port)


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

        with self.assertRaises(Invalid):
            upload.validate()
