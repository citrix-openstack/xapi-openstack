import logging
from formencode import validators, Schema, Invalid, variabledecode

from xapi_openstack.services import (
    ValidatingCommand, ConnectRequest
)

from xapi_openstack.models import KSClient, XAPISession

import argparse


logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


class ConnectToXAPISchema(Schema):
    url = validators.String(not_empty=True)
    user = validators.String(not_empty=True)
    password = validators.String(not_empty=True)


class ConnectToXAPI(ValidatingCommand):
    schema = ConnectToXAPISchema

    def __call__(self, xapi=None):
        session = xapi.Session(self.args['url'])
        session.login_with_password(
            self.args['user'],
            self.args['password'])
        return XAPISession(session)


class UploadVHDSchema(Schema):
    xapi = ConnectToXAPISchema()
    ks = ConnectRequest()
    vhd_uuid = validators.String(not_empty=True)
    image_uuid = validators.String(not_empty=True)


class UploadVHD(ValidatingCommand):
    schema = UploadVHDSchema

    def __call__(self):
        self.validate()
        connect_to_xapi = ConnectToXAPI(self.args['xapi'])

        import XenAPI
        session = connect_to_xapi(xapi=XenAPI)

        sr_uuid = session.get_sr_uuid_by_vdi(self.args['vhd_uuid'])
        sr_path = '/var/run/sr-mount/{0}'.format(sr_uuid)
        logger.info('assuming sr is at: %s', sr_path)


def collect_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('xapi.user')
    parser.add_argument('xapi.password')
    parser.add_argument('xapi.url')
    parser.add_argument('ks.user')
    parser.add_argument('ks.password')
    parser.add_argument('ks.tenant_name')
    parser.add_argument('ks.auth_url')
    parser.add_argument('vhd_uuid')
    parser.add_argument('image_uuid')

    result = dict()

    args = parser.parse_args(argv)
    for name in dir(args):
        if name.startswith('_'):
            continue
        result[name] = getattr(args, name)

    return variabledecode.variable_decode(result)


def main(argv):
    args = collect_args(argv[1:])
    upload = UploadVHD(args)
    logger.setLevel(logging.DEBUG)
    upload()
