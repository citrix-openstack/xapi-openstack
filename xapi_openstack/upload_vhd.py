from formencode import validators, Schema, Invalid
from urlparse import urlparse

from xapi_openstack.services import (
    ValidatingCommand, ConnectRequest
)


class ConnectToKeystone(ValidatingCommand):
    schema = ConnectRequest

    def __call__(self, ksclient=None):
        return KSClient(ksclient.Client(
            username=self.args['user'],
            password=self.args['password'],
            insecure=False,
            tenant_name=self.args['tenant_name'],
            auth_url=self.args['auth_url'],
            tenant_id=None))


class KSClient(object):
    def __init__(self, client):
        self.client = client

    @property
    def auth_token(self):
        return self.client.auth_token

    def _get_endpoint_urlobj(self):
        return urlparse(
            self.client.service_catalog.url_for(
                service_type="image", endpoint_type="publicURL"))

    @property
    def glance_host(self):
        return self._get_endpoint_urlobj().hostname

    @property
    def glance_port(self):
        return self._get_endpoint_urlobj().port


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
