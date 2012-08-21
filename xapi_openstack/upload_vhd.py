from formencode import validators, Schema, Invalid

from xapi_openstack.services import (
    ValidatingCommand, ConnectRequest
)

from xapi_openstack.models import KSClient


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


class XAPISession(object):
    def __init__(self, session):
        self.session = session

    def get_single_host(self, session=None):
        host, = self.session.xenapi.host.get_all()
        return host


class UploadVHDSchema(Schema):
    xapi = ConnectToXAPISchema()
    ks = ConnectRequest()
    vhd_uuid = validators.String(not_empty=True)
    image_uuid = validators.String(not_empty=True)


class UploadVHD(ValidatingCommand):
    schema = UploadVHDSchema
