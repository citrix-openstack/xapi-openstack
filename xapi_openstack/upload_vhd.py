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
