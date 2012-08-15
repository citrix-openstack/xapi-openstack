import logging
import sys
from optparse import OptionParser
import XenAPI as xenapi


logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger(__name__)


def parse_options(args):
    parser = OptionParser()
    parser.add_option(
        '--xapi-url', dest='xapi_url',
        help='address of xapi, (http://xs1.mydomain.com/)')
    parser.add_option(
        '--user', dest='username',
        help='xapi username')
    parser.add_option(
        '--password', dest='password',
        help='xapi password')
    parser.add_option(
        '--verbose', dest='verbose',
        action='store_true', default=False,
        help='verbose')
    (options, _) = parser.parse_args(args=args)

    return Options(options)


class Options(object):
    def __init__(self, options=None):
        self.xapi_url = options and options.xapi_url
        self.username = options and options.username
        self.password = options and options.password
        self.verbose = options and options.verbose

    @property
    def failed(self):
        return None in [self.xapi_url]


def get_session(options):
    logger.debug('New session to: %s', options.xapi_url)
    session = xenapi.Session(options.xapi_url)
    logger.debug('Authenticating...')
    result = session.xenapi.login_with_password(
        options.username, options.password)
    return session


def get_vbd(session, vbdref):
    return session.xenapi.VBD.get_all_records()[vbdref]


def get_vdi(session, vdiref):
    vdi = session.xenapi.VDI.get_all_records()[vdiref]
    logger.debug('VDI: %s', vdi)
    return vdi


def add_vbds(session, machine):
    if machine.vbdrefs:
        for vbdref in machine.vbdrefs:
            machine.vbds.append(VBD(get_vbd(session, vbdref)))


def add_sr(session, vdi):
    vdi.sr = SR(session.xenapi.SR.get_all_records()[vdi.sr_ref])


def machines(session):
    machine_records = session.xenapi.VM.get_all_records()
    machines = dict()

    for k, v in machine_records.items():
        logging.debug(v)
        machine = Machine(v)
        machines[k] = machine
        vbdrefs = machine.vbdrefs
        add_vbds(session, machine)

    return machines


class Machine(object):
    def __init__(self, data):
        self.data = data
        self.vbds = []

    @property
    def vbdrefs(self):
        return self.data.get('VBDs')

    @property
    def exportable(self):
        if self.disk_vbds:
            for vbd in self.disk_vbds:
                if not vbd.is_vdi:
                    return False
            return True
        return False

    @property
    def disk_vbds(self):
        return [vbd for vbd in self.vbds if vbd.is_disk]

    @property
    def label(self):
        return self.data.get('name_label')

    @property
    def uuid(self):
        return self.data.get('uuid')


class VBD(object):
    def __init__(self, data):
        self.data = data

    @property
    def is_vdi(self):
        return bool(self.data.get('VDI'))

    @property
    def is_disk(self):
        return 'Disk' == self.data.get('type')

    @property
    def vdi_ref(self):
        return self.data.get('VDI')


class VDI(object):
    def __init__(self, data):
        self.data = data

    @property
    def uuid(self):
        return self.data.get('uuid')

    @property
    def sr_ref(self):
        return self.data.get('SR')


class SR(object):
    def __init__(self, data):
        logger.info('SR %s', data)
        self.data = data

    @property
    def uuid(self):
        return self.data.get('uuid')


def main(args, writeline=None):
    def wl(s):
        sys.stdout.write(str(s) + '\n')
    writeline = writeline or wl
    options = parse_options(args)
    if options.failed:
        sys.stderr.write("Missing options, try %s --help\n" % args[0])
        sys.exit(1)
    if options.verbose:
        print 'lll'
        logger.setLevel(logging.DEBUG)

    session = get_session(options)
    for machine in machines(session).values():
        if machine.exportable:
            writeline("vm: %s (%s)" % (machine.label, machine.uuid))
            for vbd in machine.disk_vbds:
                vdi = VDI(get_vdi(session, vbd.vdi_ref))
                writeline("  disk: " + vdi.uuid)
                add_sr(session, vdi)
                writeline(
                    "    location: /var/run/sr-mount/%s/%s.vhd" %
                    (vdi.sr.uuid, vdi.uuid))
