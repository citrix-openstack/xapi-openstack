from formencode import validators, Schema, Invalid, variabledecode
from urlparse import urlparse


class ConnectRequest(Schema):
    username = validators.String(not_empty=True)
    password = validators.String(not_empty=True)
    tenant_name = validators.String(not_empty=True)
    auth_url = validators.String(not_empty=True)


class ValidatingCommand(object):
    schema = None

    def __init__(self, args=None):
        self.args = args or dict()

    def validate(self):
        self.schema().to_python(self.args, None)


class ConnectToKeystone(ValidatingCommand):
    schema = ConnectRequest

    def get_keystone_client(self, ksclient=None):
        return ksclient.Client(
            username=self.args['username'],
            password=self.args['password'],
            insecure=False,
            tenant_name=self.args['tenant_name'],
            auth_url=self.args['auth_url'],
            tenant_id=None)

    @property
    def auth_token(self):
        return self.get_keystone_client().auth_token

    def _get_endpoint_urlobj(self):
        return urlparse(
            self.get_keystone_client().service_catalog.url_for(
                service_type="image", endpoint_type="publicURL"))

    @property
    def glance_host(self):
        return self._get_endpoint_urlobj().hostname

    @property
    def glance_port(self):
        return self._get_endpoint_urlobj().port


class GetXAPIHostSchema(Schema):
    xapiurl = validators.String(not_empty=True)
    user = validators.String(not_empty=True)
    password = validators.String(not_empty=True)


class GetXAPIHost(ValidatingCommand):
    schema = GetXAPIHostSchema

    def get_xapi_session(self, xapi=None):
        session = xapi.Session(self.args['xapiurl'])
        session.login_with_password(
            self.args['user'],
            self.args['password'])
        return session

    def get_single_host(self, session=None):
        host, = session.xenapi.host.get_all()
        return host


class UploadVHDSchema(Schema):
    xapi = GetXAPIHostSchema()


class UploadVHD(ValidatingCommand):
    schema = UploadVHDSchema
