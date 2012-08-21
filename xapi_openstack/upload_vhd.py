import logging
from formencode import validators, Schema, variabledecode

from xapi_openstack import services
from xapi_openstack.models import KSClient, XAPISession

import argparse


logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


class UploadVHDSchema(Schema):
    xapi = services.ConnectToXAPISchema()
    ks = services.ConnectRequest()
    vhd_uuid = validators.String(not_empty=True)
    image_uuid = validators.String(not_empty=True)


class UploadVHD(services.ValidatingCommand):
    schema = UploadVHDSchema

    def __call__(self):
        self.validate()

        vhd_uuid = self.args['vhd_uuid']
        image_uuid = self.args['image_uuid']

        connect_to_xapi = services.ConnectToXAPI(self.args['xapi'])

        import XenAPI
        session = connect_to_xapi(xapi=XenAPI)

        sr_uuid = session.get_sr_uuid_by_vdi(vhd_uuid)
        sr_path = '/var/run/sr-mount/{0}'.format(sr_uuid)
        logger.info('sr_path: %s', sr_path)

        from keystoneclient.v2_0 import client as ksclient

        connect_to_keystone = services.ConnectToKeystone(self.args['ks'])
        client = connect_to_keystone(ksclient)

        glance_host = client.glance_host
        glance_port = client.glance_port
        auth_token = client.auth_token
        logger.info('glance at host: %s', glance_host)
        logger.info('glance at port: %s', glance_port)
        logger.info('auth_token: %s', auth_token)

        params = {
            'vdi_uuids': [vhd_uuid],
            'image_id': image_uuid,
            'glance_host': glance_host,
            'glance_port': glance_port,
            'sr_path': sr_path,
            'auth_token': auth_token,
            'properties': {}
        }

        session.upload_vhd(params)


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
