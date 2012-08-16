from formencode import validators, Schema, Invalid


class UploadRequest(Schema):
    username = validators.String(not_empty=True)
    password = validators.String(not_empty=True)
    tenant_name = validators.String(not_empty=True)
    auth_url = validators.String(not_empty=True)


class UploadVHD(object):
    def __init__(self, **args):
        self.args = args
        self.valid = False

    def validate(self):
        self.valid = False
        schema = UploadRequest()
        try:
            schema.to_python(self.args, None)
            self.valid = True
        except Invalid:
            pass

    def get_keystone_client(self, ksclient=None):
        return ksclient.Client(
            username=self.args['username'],
            password=self.args['password'],
            insecure=False,
            tenant_name=self.args['tenant_name'],
            auth_url=self.args['auth_url'],
            tenant_id=None)

    def get_xapi_session(self, xapi=None):
        session = xapi.Session(self.args['xapiurl'])
        session.login_with_password(
            self.args['xapiuser'],
            self.args['xapipass'])
        return session

    def get_single_host(self, session=None):
        host, = session.xenapi.host.get_all()
        return host
