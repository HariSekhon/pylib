#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2018-03-05 19:10:02 +0000 (Mon, 05 Mar 2018)
#
#  https://github.com/HariSekhon/pylib
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback to help steer this or other code I publish
#
#  https://www.linkedin.com/in/HariSekhon
#

"""

Docker API Check Specialization of NagiosPlugin

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import os
import sys
import time
import traceback
# Python 2.6+ only
from abc import ABCMeta, abstractmethod
try:
    import docker
    # docker-py uses Requests module, catch requests.ConnectionError
    import requests
except ImportError:
    print(traceback.format_exc(), end='')
    sys.exit(4)
srcdir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.join(srcdir, 'pylib')
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from harisekhon.utils import log, log_option, CriticalError, UnknownError
    from harisekhon.utils import validate_chars, validate_file, prog
    from harisekhon.nagiosplugin import NagiosPlugin
except ImportError as _:
    print(traceback.format_exc(), end='')
    sys.exit(4)

__author__ = 'Hari Sekhon'
__version__ = '0.4.1'


class DockerNagiosPlugin(NagiosPlugin):

    __version__ = __version__
    # abstract class
    __metaclass__ = ABCMeta

    def __init__(self):
        # Python 2.x
        super(DockerNagiosPlugin, self).__init__()
        # Python 3.x
        # super().__init__()
        self.default_port = 2376
        self.base_url = None
        self.tls = False
        self.tls_config = False
        self.msg = 'Docker msg not defined yet'
        self.ok()

    def add_options(self):
        self.add_docker_options()

    def add_docker_options(self):
        self.add_opt('-H', '--base-url',
                     help='Dockerd base url (optional). Socket or full tcp address' + \
                          ' eg unix:///var/run/docker.sock or tcp://127.0.0.1:1234' + \
                          '. Uses environment variables by default like docker commands')
        self.add_opt('-T', '--tls', action='store_true',
                     help='Use TLS; implied by --tlsverify (only used with --base-url)')
        self.add_opt('--tlscacert', help='Trust certs signed only by this CA ($DOCKER_CERT_PATH/ca.pem' + \
                                         ", eg '.docker/ca.pem' or '.docker/machine/machines/default/ca.pem'")
        self.add_opt('--tlscert', help='Path to TLS certificate file ($DOCKER_CERT_PATH/cert.pem' + \
                                       ", eg. '.docker/cert.pem' or '.docker/machine/machines/default/cert.pem'")
        self.add_opt('--tlskey', help='Path to TLS certificate key ($DOCKER_CERT_PATH/key.pem' + \
                                      ", eg. '.docker/key.pem' or '.docker/machine/machines/default/key.pem)")
        self.add_opt('--tlsverify', action='store_true', help='Use TLS and verify the remote ($DOCKER_TLS_VERIFY)')

    def process_options(self):
        self.process_docker_options()

    def process_docker_options(self):
        # should look like unix:///var/run/docker.sock or tcp://127.0.0.1:1234
        self.base_url = self.get_opt('base_url')
        if self.base_url:
            validate_chars(self.base_url, 'base url', r'A-Za-z0-9\/\:\.')
        self.tls = self.get_opt('tls')
        if not self.tls and os.getenv('DOCKER_TLS_VERIFY'):
            self.tls = True
        log_option('tls', self.tls)
        if self.tls:
            ca_file = self.get_opt('tlscacert')
            cert_file = self.get_opt('tlscert')
            key_file = self.get_opt('tlskey')
            tls_verify = self.get_opt('tlsverify')
            docker_cert_path = os.getenv('DOCKER_CERT_PATH')
            if docker_cert_path:
                if not ca_file:
                    ca_file = os.path.join(docker_cert_path, 'ca.pem')
                if not cert_file:
                    cert_file = os.path.join(docker_cert_path, 'cert.pem')
                if not key_file:
                    key_file = os.path.join(docker_cert_path, 'key.pem')
                if not tls_verify and os.getenv('DOCKER_TLS_VERIFY'):
                    tls_verify = True
            validate_file(ca_file, 'TLS CA cert file')
            validate_file(cert_file, 'TLS cert file')
            validate_file(key_file, 'TLS key file')
            log_option('TLS verify', tls_verify)
            self.tls_config = docker.tls.TLSConfig(ca_cert=ca_file,  # pylint: disable=redefined-variable-type
                                                   verify=tls_verify,
                                                   client_cert=(cert_file, key_file))

    def run(self):
        start_time = time.time()
        try:
            if self.base_url:
                log.info('connecting to Docker via base url: %s', self.base_url)
                client = docker.DockerClient(base_url=self.base_url,
                                             timeout=max(self.timeout - 1, 1),
                                             tls=self.tls_config,
                                             user_agent='Hari Sekhon {}'.format(prog)
                                            )
            else:
                log.info('connecting to Docker via environment')
                client = docker.from_env()
            # exception happens here
            self.check(client)
        except docker.errors.APIError as _:
            raise CriticalError('Docker API call FAILED: {}'.format(_))
        except requests.ConnectionError as _:
            raise CriticalError('Docker connection failed: {}'.format(_))
        except docker.errors.DockerException as _:
            raise UnknownError(_)
        query_time = time.time() - start_time

        if '|' not in self.msg:
            self.msg += ' |'
        if ' query_time=' not in self.msg:
            self.msg += ' query_time={0:.4f}s'.format(query_time)

    @abstractmethod
    def check(self, client):
        pass
