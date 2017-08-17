#!/usr/bin/python
import os
import charms.reactive as reactive
from charmhelpers.core import hookenv
import base64
import subprocess

config = hookenv.config()
cert = base64.b64decode(config['ssl_ca'])
cert_location = 'maas/public.crt'
cert_filename = os.path.join('/usr/share/ca-certificates', cert_location)

@reactive.when_any('ca-certificate.available', 'ca-certificate.connected')
@reactive.when_not('ca-certificate.installed')
def install_packages(rel=None):
    hookenv.status_set('maintenance', 'Installing ca-certificate')
    hookenv.log("Installing ca-certificate")
    with open('/etc/ca-certificate.conf', 'a') as f:
        f.write(cert_location)
    if not os.path.exists('/usr/share/ca-certificates/maas'):
        os.makedirs('/usr/share/ca-certificates/maas')
    with open(cert_filename, 'w') as ca_file:
        ca_file.write(cert)
    subprocess.Popen("update-ca-certificates")
    reactive.set_state('ca-certificate.installed')
    hookenv.status_set('active', 'Certificate Installed')

@reactive.when('ca-certificate.installed')
@reactive.when(config.changed('ssl_ca'))
def update_certificate(rel=None):
    hookenv.status_set('maintenance', 'Updating ca-certificate')
    hookenv.log('Updating ca-certificate')
    with open(cert_filename, 'w') as ca_file:
        ca_file.write(cert)
    subprocess.Popen("update-ca-certificates")
    hookenv.status_set('active', 'Certificate Installed')
