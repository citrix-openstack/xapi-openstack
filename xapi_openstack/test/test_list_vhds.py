import textwrap
import unittest
import xapi_openstack.list_vhds as lvhd

from xapi_openstack import models
from xapi_openstack.test.test_services import FakedTestCase


class ParseOptionsTestCase(unittest.TestCase):
    def test_options_fail(self):
        options = lvhd.parse_options(['stg.py'])
        self.assertTrue(options.failed)

    def test_options_ok(self):
        options = lvhd.parse_options(
            ['stg.py', '--xapi-url=http://localhost/'])
        self.assertFalse(options.failed)


class Fake(object):
    pass


class FunctionalTestCase(FakedTestCase):
    DATA = {
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
            'vdi1': {
                'uuid': 'vdi1-uuid',
                'SR': 'srref'
            }
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
        'SR': {
            'srref': {
                'uuid': 'sr-uuid'
            }
        }
    }

    def test_list_machines_logs_in(self):
        lines = []
        writeline = lambda s: lines.append(str(s))

        lvhd.main(
            ['--xapi-url=someurl', '--user=user', '--password=password'],
            writeline=writeline)

        session = self.xapi._sessions[0]
        self.assertEquals('user', session._username)
        self.assertEquals('password', session._password)
        self.assertEquals('someurl', session._url)

        self.assertEquals(
            textwrap.dedent("""
            vm: machine1 (machine1-uuid)
              disk: vdi1-uuid
                location: /var/run/sr-mount/sr-uuid/vdi1-uuid.vhd""").strip(),
            '\n'.join(lines))


class MachineUnitTest(unittest.TestCase):
    def test_is_exportable(self):
        m = models.Machine(dict())
        self.assertFalse(m.exportable)

    def test_disk_vdi_is_exportable(self):
        m = models.Machine(dict())

        vbd = Fake()
        vbd.is_vdi = True
        vbd.is_disk = True

        m.vbds.append(vbd)
        self.assertTrue(m.exportable)

    def test_non_disk_vdi_ignored(self):
        m = models.Machine(dict())

        vbd = Fake()
        vbd.is_vdi = True
        vbd.is_disk = False

        m.vbds.append(vbd)
        self.assertFalse(m.exportable)

    def test_machine_with_no_vdi_is_not_exportable(self):
        m = models.Machine(dict())

        non_vdi = Fake()
        non_vdi.is_vdi = False
        non_vdi.is_disk = True
        m.vbds.append(non_vdi)
        self.assertFalse(m.exportable)

    def test_machine_name(self):
        m = models.Machine({
            'name_label': 'somemachine'
        })

        self.assertEquals('somemachine', m.label)


class VBDTestCase(unittest.TestCase):
    def test_is_vdi(self):
        vbd = models.VBD(dict())

        self.assertFalse(vbd.is_vdi)
        self.assertIsNone(vbd.vdi_ref)

    def test_is_vdi_true(self):
        vbd = models.VBD({
            'VDI': 'somevdiref'
        })

        self.assertTrue(vbd.is_vdi)

    def test_empty_is_not_a_disk(self):
        vbd = models.VBD(dict())

        self.assertFalse(vbd.is_disk)

    def test_Disk_type_is_a_disk(self):
        vbd = models.VBD({
            'type': 'Disk'
        })

        self.assertTrue(vbd.is_disk)

    def test_vdi(self):
        vbd = models.VBD({
            'VDI': 'vdiref'
        })

        self.assertEquals('vdiref', vbd.vdi_ref)


class VDITestCase(unittest.TestCase):
    def test_uuid(self):
        vdi = models.VDI(dict())
        self.assertIsNone(vdi.uuid)

    def test_uuid_value(self):
        vdi = models.VDI({
            'uuid': 'someuuid'
        })
        self.assertEquals('someuuid', vdi.uuid)
