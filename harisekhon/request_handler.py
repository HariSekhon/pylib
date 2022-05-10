#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-02-21 12:26:44 +0000 (Sun, 21 Feb 2016)
#
#  https://github.com/HariSekhon/pylib
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback # pylint: disable=line-too-long
#
#  https://www.linkedin.com/in/HariSekhon
#

"""

Request Handler Class - Designed to contain various override-able and extendable tests
                        for handling 'requests' module error handling HTTP scenarios

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import json
# import logging
import os
import sys
import traceback
try:
    import requests
except ImportError:
    print(traceback.format_exc(), end='')
    sys.exit(4)
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pylib'))
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from harisekhon.utils import log, CriticalError, prog, prog_version, code_error
except ImportError as _:
    print(traceback.format_exc(), end='')
    sys.exit(4)

__author__ = 'Hari Sekhon'
__version__ = '0.6.3'


class RequestHandler(object):

    def __init__(self, req=None):
        self.url = None
        if req:
            self.process_req(req)

    def req(self, method, url, *args, **kwargs):
        if '://' not in url:
            url = 'http://' + url
        self.url = url
        log.debug('%s %s', str(method).upper(), url)
        req = None
        user_agent = 'Hari Sekhon {prog} version {version}'.format(prog=prog, version=prog_version)
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['User-Agent'] = user_agent
        try:
            req = getattr(requests, method)(url, *args, **kwargs)
        except requests.exceptions.RequestException as _:
            self.exception_handler(_)
        self.log_output(req)
        self.process_req(req)
        return req

    def get(self, url, *args, **kwargs):
        return self.req('get', url, *args, **kwargs)

    def put(self, url, *args, **kwargs):
        return self.req('put', url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self.req('post', url, *args, **kwargs)

    def head(self, url, *args, **kwargs):
        return self.req('head', url, *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        return self.req('delete', url, *args, **kwargs)

    def process_req(self, req):
        self.check_response(req)
        return req

    def check_response(self, req):
        self.check_response_code(req)
        content = self.__parse__(req)
        self.check_content(content)

    def exception_handler(self, arg):  # pylint: disable=no-self-use
        if not issubclass(type(arg), Exception):
            code_error('RequestHandler.exception_handler arg {} is not a subclass of Exception'.format(arg))
        # TODO: improve this to extract connection refused for more concise errors
        errhint = ''
        # Exception.message deprecated since Python 2.6 and removed in Python 3
        #if 'message' in dir(arg) and 'BadStatusLine' in str(arg.message):
        if 'BadStatusLine' in repr(arg):
            errhint = ' (possibly connecting to an SSL secured port using plain HTTP?)'
        #elif 'https://' in self.url and 'unknown protocol' in str(arg.message):
        elif 'https://' in self.url and 'unknown protocol' in repr(arg):
            errhint = ' (possibly connecting to a plain HTTP port with the -S / --ssl switch enabled?)'
        _type = type(arg).__name__
        msg = str(arg)
        if 'Connection refused' in msg:
            msg = 'Connection refused'
            #msg += to {host}:{port}'.format(arg.host, arg.port)
        raise CriticalError('{type}: {exception}{errhint}'.format(type=_type,
                                                                  exception=msg,
                                                                  errhint=errhint))

    def log_output(self, req):  # pylint: disable=no-self-use
        log.debug("response: %s %s", req.status_code, req.reason)
        log.debug("content:\n%s\n%s\n%s", '=' * 80, req.content.strip(), '=' * 80)

    def check_response_code(self, req):  # pylint: disable=no-self-use
        if req.status_code != 200:
            extra_info = ''
            try:
                json_data = json.loads(req.content)
                for key in ('status', 'message', 'error', 'error_message', 'reason'):
                    if key in json_data:
                        extra_info += ', {key}: {info}'.format(key=key, info=json_data[key])
            except ValueError:
                log.debug('output is not json, not extracting additional error info')
            raise CriticalError('{status} {reason}{extra_info}'
                                .format(status=req.status_code, reason=req.reason, extra_info=extra_info))

    def check_content(self, content):  # pylint: disable=no-self-use
        pass

    def __parse__(self, req):
        return self.parse(req)

    def parse(self, req):  # pylint: disable=no-self-use
        return req.content
