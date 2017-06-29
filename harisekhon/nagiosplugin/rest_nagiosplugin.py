#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-12-19 17:42:51 +0000 (Mon, 19 Dec 2016)
#
#  https://github.com/harisekhon/pylib
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback to help steer this or other code I publish
#
#  https://www.linkedin.com/in/harisekhon
#

"""

Rest API Check Specialization of NagiosPlugin

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import logging
import json
import os
import sys
import time
import traceback
# Python 2.6+ only
from abc import ABCMeta #, abstractmethod
srcdir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.join(srcdir, 'pylib')
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from harisekhon.utils import log, log_option, UnknownError, support_msg_api, jsonpp
    from harisekhon.utils import validate_host, validate_port, validate_user, validate_password
    from harisekhon.nagiosplugin import NagiosPlugin
    from harisekhon import RequestHandler
except ImportError as _:
    print(traceback.format_exc(), end='')
    sys.exit(4)

__author__ = 'Hari Sekhon'
__version__ = '0.2'


class RestNagiosPlugin(NagiosPlugin):

    __version__ = __version__
    # abstract class
    __metaclass__ = ABCMeta

    def __init__(self):
        # Python 2.x
        super(RestNagiosPlugin, self).__init__()
        # Python 3.x
        # super().__init__()
        self.name = None
        self.default_host = 'localhost'
        self.default_port = 80
        self.default_user = None
        self.default_password = None
        self.host = None
        self.port = None
        self.user = None
        self.password = None
        self.protocol = 'http'
        self.msg = 'rest msg not defined yet'
        self.request = RequestHandler()
        self.req = None
        self.json_data = None
        self.path = None
        self.json = False
        self.auth = True
        self.ok()

    def add_options(self):
        self.add_hostoption(name=self.name,
                            default_host=self.default_host,
                            default_port=self.default_port)
        if self.auth:
            self.add_useroption(name=self.name,
                                default_user=self.default_user,
                                default_password=self.default_password)
        self.add_ssl_option()

    def add_ssl_option(self):
        self.add_opt('-S', '--ssl', action='store_true', default=False, help='Use SSL')

    def process_options(self):
        self.no_args()
        self.host = self.get_opt('host')
        self.port = self.get_opt('port')
        validate_host(self.host)
        validate_port(self.port)
        if self.auth:
            self.user = self.get_opt('user')
            self.password = self.get_opt('password')
            validate_user(self.user)
            validate_password(self.password)
        ssl = self.get_opt('ssl')
        log_option('ssl', ssl)
        if ssl and self.protocol == 'http':
            self.protocol = 'https'

    def run(self):
        start_time = time.time()
        self.req = self.query()
        query_time = time.time() - start_time
        if self.json:
            self.process_json(self.req.content)
        else:
            self.parse(self.req)
        if '|' not in self.msg:
            self.msg += ' |'
        if ' query_time=' not in self.msg:
            self.msg += ' query_time={0:.4f}s'.format(query_time)

    def query(self):
        url = '{proto}://{host}:{port}/'.format(proto=self.protocol,
                                                host=self.host,
                                                port=self.port)
        if self.path:
            url += self.path.lstrip('/')
        auth = None
        if self.user and self.password:
            log.info('authenicating to rest API')
            auth = (self.user, self.password)
        req = self.request.get(url, auth=auth)
        return req

    #@abstractmethod
    def parse(self, req):
        pass

    #@abstractmethod
    def parse_json(self, json_data):
        pass

    def process_json(self, content):
        try:
            self.json_data = json.loads(content)
            if log.isEnabledFor(logging.DEBUG):
                log.debug('JSON prettified:\n\n%s\n%s', jsonpp(self.json_data), '='*80)
            return self.parse_json(self.json_data)
        #except (KeyError, ValueError) as _:
            #raise UnknownError('{0}: {1}. {2}'.format(type(_).__name__, _, support_msg_api()))
        except (KeyError, ValueError):
            raise UnknownError('{0}. {1}'.format(self.exception_msg(), support_msg_api()))
