import unittest
import mock

from xapi_openstack import services


class FakeXenAPISession(object):
    def __init__(self, url, data=None):
        self._url = url
        self._data = data or {}

    def login_with_password(self, username, password):
        self._username = username
        self._password = password

    @property
    def VM(self):
        def get_all_records():
            return self._data.get('VM')
        fake = mock.Mock()
        fake.get_all_records = get_all_records
        return fake

    @property
    def VBD(self):
        def get_all_records():
            return self._data.get('VBD')

        fake = mock.Mock()
        fake.get_all_records = get_all_records
        return fake

    @property
    def VDI(self):
        def get_all_records():
            return self._data.get('VDI')
        fake = mock.Mock()
        fake.get_all_records = get_all_records
        return fake

    @property
    def SR(self):
        def get_all_records():
            return self._data.get('SR')
        fake = mock.Mock()
        fake.get_all_records = get_all_records
        return fake


class FakeXenAPIModule(object):
    def __init__(self, data=None):
        self._sessions = []
        self._data = data or dict()

    def Session(self, url=None):
        result = mock.Mock()
        result.xenapi = FakeXenAPISession(url, self._data)
        self._sessions.append(result.xenapi)
        return result


class MockedXapiTestCase(unittest.TestCase):
    DATA = {}

    def setUp(self):
        self.xapi = FakeXenAPIModule(data=self.DATA)
        self.stored_xenapi = services.xenapi
        services.xenapi = self.xapi

    def tearDown(self):
        services.xenapi = self.stored_xenapi


class GetVDIuuidTestCase(unittest.TestCase):
    def test_get_vdi(self):
        data = {
            'VDI': {
                'vdi1': {}
            }
        }
        vdi = services.get_vdi(FakeXenAPIModule(data).Session(), 'vdi1')
        self.assertTrue(vdi is not None)


class ListMachinesTestCase(unittest.TestCase):
    def test_machines_listed_with_hdd(self):
        data = {
            'VM': {
                'm1': {
                    'name_label': 'machine1',
                    'VBDs': [
                        'vbd1',
                        'vbd2'
                    ],
                    'uuid': 'machine1-uuid'
                },
                'm2': {}
            },
            'VDI': {
                'vdi1': {}
            },
            'VBD': {
                'vbd1': {
                    'VDI': 'vdi1',
                    'uuid': 'vbd1-uuid',
                    'type': 'Disk',
                    'device': 'xvda'
                },
                'vbd2': {
                    'VDI': '',
                    'uuid': 'vbd2-uuid',
                    'type': 'CD',
                    'device': 'xvdd'
                }
            }
        }
        machine_list = services.machines(FakeXenAPIModule(data).Session())
        self.assertIn('m1', machine_list)


class MachineTestCase(unittest.TestCase):
    def test_machine_vbds_mapped(self):
        data = {
            'VM': {
                'm1': {
                    'name_label': 'machine1',
                    'VBDs': [
                        'vbd1',
                        'vbd2'
                    ],
                    'uuid': 'machine1-uuid'
                },
            },
            'VBD': {
                'vbd1': {
                    'VDI': 'vdi1',
                    'uuid': 'vbd1-uuid',
                    'type': 'Disk',
                    'device': 'xvda'
                },
                'vbd2': {
                    'VDI': '',
                    'uuid': 'vbd2-uuid',
                    'type': 'CD',
                    'device': 'xvdd'
                }
            },
        }
        m1 = services.machines(FakeXenAPIModule(data).Session())['m1']
        self.assertEquals(2, len(m1.vbds))
        self.assertEquals('vdi1', m1.vbds[0].vdi_ref)


class ConnectToKeystoneTestCase(unittest.TestCase):

    def test_all_parameters_given_is_valid(self):
        connect = services.ConnectToKeystone(dict(
            user="user",
            password="password",
            tenant_name="demo",
            auth_url="http://127.0.0.1:5000/v2.0"))

        try:
            connect.validate()
        except services.Invalid:
            raise AssertionError()

    def test_missing_parameter(self):
        connect = services.ConnectToKeystone(dict(
            password="password",
            tenant_name="demo",
            auth_url="http://127.0.0.1:5000/v2.0"))

        self.assertRaises(services.Invalid, connect.validate)

    def test_keystone_client_created(self):
        ksclient = mock.Mock()
        c = mock.call

        connect = services.ConnectToKeystone(dict(
            user="user",
            password="password",
            tenant_name="demo",
            auth_url="http://127.0.0.1:5000/v2.0"))

        connect(ksclient=ksclient)

        self.assertEquals(
            [c.Client(
                username="user", password="password",
                tenant_id=None, tenant_name="demo",
                auth_url="http://127.0.0.1:5000/v2.0",
                insecure=False)],
            ksclient.mock_calls
        )


class ConnectToXAPITestCase(unittest.TestCase):
    def test_valid_parameter_set(self):
        connect = services.ConnectToXAPI(dict(
            url='xapiurl', user='xapiuser', password='xapipass'))

        try:
            connect.validate()
        except services.Invalid:
            raise AssertionError()

    def test_missing_a_parameter(self):
        connect = services.ConnectToXAPI(dict(
            user='xapiuser', password='xapipass'))

        with self.assertRaises(services.Invalid):
            connect.validate()

    def test_get_xapi_session(self):
        session = mock.Mock()
        xapi = mock.Mock()
        xapi.Session.return_value = session
        c = mock.call

        connect = services.ConnectToXAPI(dict(
            url="someurl", user='xapiuser',
            password='xapipass'))

        result = connect(xapi=xapi)

        self.assertEquals(
            [
                c.Session("someurl"),
                c.Session().login_with_password('xapiuser', 'xapipass')
            ],
            xapi.mock_calls)

        self.assertEquals(
            session, result.session)
