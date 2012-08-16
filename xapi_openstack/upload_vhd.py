class UploadVHD(object):
    def __init__(self, username=None, password=None, tenant_name=None,
        auth_url=None
    ):
        self.username = username
        self.password = password
        self.tenant_name = tenant_name
        self.auth_url = auth_url

        self.valid = False

    def validate(self):
        self.valid = True
