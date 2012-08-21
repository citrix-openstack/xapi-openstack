import unittest
import mock
import pickle

from xapi_openstack import models


class MachineUnitTest(unittest.TestCase):
    def test_is_exportable(self):
        m = models.Machine(dict())
        self.assertFalse(m.exportable)

    def test_disk_vdi_is_exportable(self):
        m = models.Machine(dict())

        vbd = mock.Mock()
        vbd.is_vdi = True
        vbd.is_disk = True

        m.vbds.append(vbd)
        self.assertTrue(m.exportable)

    def test_non_disk_vdi_ignored(self):
        m = models.Machine(dict())

        vbd = mock.Mock()
        vbd.is_vdi = True
        vbd.is_disk = False

        m.vbds.append(vbd)
        self.assertFalse(m.exportable)

    def test_machine_with_no_vdi_is_not_exportable(self):
        m = models.Machine(dict())

        non_vdi = mock.Mock()
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


class XAPISessionTestCase(unittest.TestCase):
    def test_get_single_host(self):
        myhost = object()
        session = mock.Mock()
        session.xenapi.host.get_all.return_value = [myhost]

        xapi_session = models.XAPISession(session)
        result = xapi_session.get_single_host()

        self.assertEquals(myhost, result)

    def test_call_glance_plugin(self):
        session = mock.Mock()
        xapi_session = models.XAPISession(session)
        xapi_session.get_single_host = lambda: 'host'  # monkey-patch

        xapi_session.upload_vhd(dict(key='value'))

        self.assertIn(
            mock.call.xenapi.host.call_plugin(
                'host',
                'glance',
                'upload_vhd',
                dict(params=pickle.dumps(dict(key='value')))),
            session.mock_calls)

    def test_get_sr_uuid_by_vdi(self):
        session = mock.Mock()
        session.xenapi.VDI.get_all_records.return_value = {
            'vdi1': {
                'uuid': 'vdiuuid',
                'SR': 'srref'
            }
        }
        session.xenapi.SR.get_all_records.return_value = {
            'srref': {
                'uuid': 'sruuid'
            }
        }

        xapi_session = models.XAPISession(session)

        self.assertEquals(
            'sruuid',
            xapi_session.get_sr_uuid_by_vdi('vdiuuid'))
