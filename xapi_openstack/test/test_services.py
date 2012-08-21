import unittest
from xapi_openstack import services


class Fake(object):
    pass


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
            print self._data
            return self._data.get('VM')
        fake = Fake()
        fake.get_all_records = get_all_records
        return fake

    @property
    def VBD(self):
        def get_all_records():
            return self._data.get('VBD')

        fake = Fake()
        fake.get_all_records = get_all_records
        return fake

    @property
    def VDI(self):
        def get_all_records():
            return self._data.get('VDI')
        fake = Fake()
        fake.get_all_records = get_all_records
        return fake

    @property
    def SR(self):
        def get_all_records():
            return self._data.get('SR')
        fake = Fake()
        fake.get_all_records = get_all_records
        return fake


class FakeXenAPIModule(object):
    def __init__(self, data=None):
        self._sessions = []
        self._data = data or dict()

    def Session(self, url=None):
        result = Fake()
        result.xenapi = FakeXenAPISession(url, self._data)
        self._sessions.append(result.xenapi)
        return result


class FakedTestCase(unittest.TestCase):
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
