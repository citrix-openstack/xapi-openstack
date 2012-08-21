from formencode import validators, Schema, Invalid

from xapi_openstack.services import (
    ValidatingCommand, ConnectRequest
)

from xapi_openstack.models import KSClient, XAPISession


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
