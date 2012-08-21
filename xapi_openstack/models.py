class Machine(object):
    def __init__(self, data):
        self.data = data
        self.vbds = []

    @property
    def vbdrefs(self):
        return self.data.get('VBDs')

    @property
    def exportable(self):
        if self.disk_vbds:
            for vbd in self.disk_vbds:
                if not vbd.is_vdi:
                    return False
            return True
        return False

    @property
    def disk_vbds(self):
        return [vbd for vbd in self.vbds if vbd.is_disk]

    @property
    def label(self):
        return self.data.get('name_label')

    @property
    def uuid(self):
        return self.data.get('uuid')


class VBD(object):
    def __init__(self, data):
        self.data = data

    @property
    def is_vdi(self):
        return bool(self.data.get('VDI'))

    @property
    def is_disk(self):
        return 'Disk' == self.data.get('type')

    @property
    def vdi_ref(self):
        return self.data.get('VDI')


class VDI(object):
    def __init__(self, data):
        self.data = data

    @property
    def uuid(self):
        return self.data.get('uuid')

    @property
    def sr_ref(self):
        return self.data.get('SR')


class SR(object):
    def __init__(self, data):
        self.data = data

    @property
    def uuid(self):
        return self.data.get('uuid')
