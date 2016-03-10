#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-02-21 12:26:44 +0000 (Sun, 21 Feb 2016)
#
#  https://github.com/harisekhon/pytools
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn and optionally send me feedback # pylint: disable=line-too-long
#
#  https://www.linkedin.com/in/harisekhon
#

"""

Request Handler Class - Designed to contain various override-able and extendable tests
                        for handling 'requests' module error handling HTTP scenarios

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

# import logging
import os
import sys
import traceback
try:
    # from bs4 import BeautifulSoup
    import requests
except ImportError:
    print(traceback.format_exc(), end='')
    sys.exit(4)
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pylib'))
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from harisekhon.utils import log, CriticalError
except ImportError as _:
    print(traceback.format_exc(), end='')
    sys.exit(4)

__author__ = 'Hari Sekhon'
__version__ = '0.1'


class RequestHandler(object):

    def __init__(self, req=None):
        # Python 2.x
        #super(RequestHandler, self).__init__()
        # Python 3.x
        # super().__init__()
        if req:
            self.process_req(req)

    @classmethod
    def req(cls, method, url, *args, **kwargs):
        if '://' not in url:
            url = 'http://' + url
        log.debug('GET %s', url)
        req = None
        try:
            req = getattr(requests, method)(url, *args, **kwargs)
        except requests.exceptions.RequestException as _:
            cls.exception_handler(_)
        cls.log_output(req)
        cls.process_req(req)
        return req

    @classmethod
    def get(cls, url, *args, **kwargs):
        return cls.req('get', url, *args, **kwargs)

    @classmethod
    def put(cls, url, *args, **kwargs):
        return cls.req('put', url, *args, **kwargs)

    @classmethod
    def post(cls, url, *args, **kwargs):
        return cls.req('post', url, *args, **kwargs)

    @classmethod
    def head(cls, url, *args, **kwargs):
        return cls.req('head', url, *args, **kwargs)

    @classmethod
    def delete(cls, url, *args, **kwargs):
        return cls.req('delete', url, *args, **kwargs)

    @classmethod
    def process_req(cls, req):
        cls.check_response(req)
        return req

    @classmethod
    def check_response(cls, req):
        cls.check_response_code(req)
        # content = cls.__parse__(req)
        content = cls.parse(req)
        cls.check_content(content)

    @staticmethod
    def exception_handler(_):
        raise CriticalError(_)

    @staticmethod
    def log_output(req):
        log.debug("response: %s %s", req.status_code, req.reason)
        log.debug("content:\n%s\n%s\n%s", '='*80, req.content.strip(), '='*80)

    @staticmethod
    def check_response_code(req):
        if req.status_code != 200:
            raise CriticalError("%s %s" % (req.status_code, req.reason))

    @staticmethod
    def check_content(content):
        pass

    # no need to wrap at this time
    # @classmethod
    # def __parse__(cls, req):
    #     cls.parse(req)

    @staticmethod
    def parse(req):
        return req.content
