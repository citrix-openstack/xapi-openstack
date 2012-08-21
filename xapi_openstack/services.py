import logging
import XenAPI as xenapi

from xapi_openstack import models

logger = logging.getLogger(__name__)


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
    return models.VDI(vdi)


def add_vbds(session, machine):
    if machine.vbdrefs:
        for vbdref in machine.vbdrefs:
            machine.vbds.append(models.VBD(get_vbd(session, vbdref)))


def add_sr(session, vdi):
    vdi.sr = models.SR(session.xenapi.SR.get_all_records()[vdi.sr_ref])


def machines(session):
    machine_records = session.xenapi.VM.get_all_records()
    machines = dict()

    for k, v in machine_records.items():
        logging.debug(v)
        machine = models.Machine(v)
        machines[k] = machine
        vbdrefs = machine.vbdrefs
        add_vbds(session, machine)

    return machines


class ValidatingCommand(object):
    schema = None

    def __init__(self, args=None):
        self.args = args or dict()

    def validate(self):
        self.schema().to_python(self.args, None)



