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

Request Handler Class

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import logging
import os
import sys
import traceback
try:
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    print(traceback.format_exc(), end='')
    sys.exit(4)
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pylib'))
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from harisekhon.utils import log, qquit
except ImportError as _:
    print(traceback.format_exc(), end='')
    sys.exit(4)

__author__ = 'Hari Sekhon'
__version__ = '0.1'


class RequestHandler(object):

    def __init__(self):
        # Python 2.x
        #super(RequestHandler, self).__init__()
        # Python 3.x
        # super().__init__()
        pass

    @classmethod
    def curl(cls, url):
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException as _:
            qquit('CRITICAL', _)
        cls.log_output(req)
        cls.check_response_code(req)
        cls.__parse__(req)
        return req

    @staticmethod
    def log_output(req):
        log.debug("response: %s %s", req.status_code, req.reason)
        log.debug("content:\n%s\n%s\n%s", '='*80, req.content.strip(), '='*80)

    @staticmethod
    def check_response_code(req):
        if req.status_code != 200:
            qquit('CRITICAL', "Non-200 response! %s %s" % (req.status_code, req.reason))

    @classmethod
    def __parse__(cls, req):
        soup = BeautifulSoup(req.content, 'html.parser')
        cls.parse_print(soup)
        cls.parse(soup)

    @staticmethod
    def parse_print(soup):
        if log.isEnabledFor(logging.DEBUG):
            log.debug("BeautifulSoup prettified:\n%s\n%s", soup.prettify(), '='*80)

    @staticmethod
    def parse(soup):
        # NOTE: soup.find() can return None - do not chain calls - must test each call 'is not None'
        # link = soup.find('p')[3]
        # link = soup.find('th', text='Uptime:')
        # link = soup.find_next_sibling('th', text='Uptime:')

        # link = soup.find('th', text=re.compile('Uptime:?', re.I))
        # if link is None:
        #     qquit('UNKNOWN', 'failed to find tag')
        # link = link.find_next_sibling()
        # if link is None:
        #     qquit('UNKNOWN', 'failed to find tag (next sibling tag not found)')
        # _ = link.get_text()
        # shorter to just catch NoneType attribute error when tag not found and returns None
        #try:
        #    uptime = soup.find('th', text=re.compile('Uptime:?', re.I)).find_next_sibling().get_text()
        #    version = soup.find('th', text=re.compile('Version:?', re.I)).find_next_sibling().get_text()
        #except (AttributeError, TypeError):
        #    qquit('UNKNOWN', 'failed to find parse Tachyon%(name)s uptime/version info' % self.__dict__)
        #if not _ or not isStr(_) or not re.search(r'...', _):
        #    qquit('UNKNOWN', 'format not recognized: {0}'.format(_))
        pass
