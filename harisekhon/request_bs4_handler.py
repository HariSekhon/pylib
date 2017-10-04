#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-02-21 12:26:44 +0000 (Sun, 21 Feb 2016)
#
#  https://github.com/harisekhon/pylib
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback
#
#  https://www.linkedin.com/in/harisekhon
#

"""

Request BeautifulSoup Handler Class - Designed to contain various override-able and extendable tests
                                      for handling 'requests' module error handling HTTP scenarios

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import logging
import os
import sys
import traceback
# Python 2.6+ only
from abc import ABCMeta, abstractmethod
try:
    from bs4 import BeautifulSoup
    # import requests
except ImportError:
    print(traceback.format_exc(), end='')
    sys.exit(4)
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pylib'))
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from harisekhon.utils import log
    from harisekhon import RequestHandler
except ImportError as _:
    print(traceback.format_exc(), end='')
    sys.exit(4)

__author__ = 'Hari Sekhon'
__version__ = '0.1'


class RequestBS4Handler(RequestHandler):

    # abstract class
    __metaclass__ = ABCMeta

#     def __init__(self):
#         Python 2.x
#        super(RequestHandler, self).__init__()
#         Python 3.x
#         super().__init__()
#         pass

    def __parse__(self, req):
        soup = BeautifulSoup(req.content, 'html.parser')
        self.soup_print(soup)
        return self.parse(soup)

    def soup_print(self, soup):  # pylint: disable=no-self-use
        if log.isEnabledFor(logging.DEBUG):
            log.debug("BeautifulSoup prettified:\n%s\n%s", soup.prettify(), '=' * 80)

    @abstractmethod
    def parse(self, soup):  # pylint: disable=no-self-use
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
