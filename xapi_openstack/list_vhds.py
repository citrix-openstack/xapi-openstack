import logging
import sys
from optparse import OptionParser

from xapi_openstack import services


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


def main(args, writeline=None):
    def wl(s):
        sys.stdout.write(str(s) + '\n')
    writeline = writeline or wl
    options = parse_options(args)
    if options.failed:
        sys.stderr.write("Missing options, try %s --help\n" % args[0])
        sys.exit(1)
    if options.verbose:
        logger.setLevel(logging.DEBUG)

    session = services.get_session(options)
    for machine in services.machines(session).values():
        if machine.exportable:
            writeline("vm: %s (%s)" % (machine.label, machine.uuid))
            for vbd in machine.disk_vbds:
                vdi = services.get_vdi(session, vbd.vdi_ref)
                writeline("  disk: " + vdi.uuid)
                services.add_sr(session, vdi)
                writeline(
                    "    location: /var/run/sr-mount/%s/%s.vhd" %
                    (vdi.sr.uuid, vdi.uuid))
