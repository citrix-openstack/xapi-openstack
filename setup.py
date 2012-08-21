from setuptools import setup


setup(
    name='xapi_openstack',
    version='0.0',
    description='Xen API and OpenStack related utilities',
    packages=['xapi_openstack'],
    install_requires=['XenAPI', 'formencode'],
    entry_points = {
        'console_scripts' : [
            'list_vhds = xapi_openstack.scripts:list_vhds',
            'upload_vhd = xapi_openstack.scripts:upload_vhd'
        ]
    }
)
