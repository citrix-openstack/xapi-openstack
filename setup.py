from setuptools import setup


setup(
    name='xapi_openstack',
    version='0.0',
    description='Xen API and OpenStack related utilities',
    packages=['xapi_openstack'],
    install_requires=['XenAPI'],
    entry_points = {
        'console_scripts' : [
            'add_glance_plugin = xapi_openstack.scripts:add_glance_plugin',
        ]
    }
)
