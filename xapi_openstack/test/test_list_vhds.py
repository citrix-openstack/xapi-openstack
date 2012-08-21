import textwrap
import unittest
import xapi_openstack.list_vhds as lvhd

from xapi_openstack.test.test_services import MockedXapiTestCase


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


class FunctionalTestCase(MockedXapiTestCase):
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
