#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-03-13 21:47:07 +0000 (Sun, 13 Mar 2016)
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

Status Check Specialization of NagiosPlugin

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import os
import sys
# Python 2.6+ only
from abc import ABCMeta, abstractmethod
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(libdir)
# pylint: disable=wrong-import-position
from harisekhon.utils import UnknownError, CodingError, qquit
from harisekhon.utils import validate_host, validate_port
from harisekhon.nagiosplugin import NagiosPlugin

__author__ = 'Hari Sekhon'
__version__ = '0.3'


class StatusNagiosPlugin(NagiosPlugin):
    """
    Status Checker Nagios Plugin
    """

    __version__ = __version__
    # abstract class
    __metaclass__ = ABCMeta

    def __init__(self):
        # Python 2.x
        super(StatusNagiosPlugin, self).__init__()
        # Python 3.x
        # super().__init__()
        self.default_host = 'localhost'
        self.default_port = None
        self.host = None
        self.port = None
        self.name = None
        self.state = None
        self.msg2 = ''
        self.perfdata = ''

    def add_options(self):
        if not self.name:
            raise CodingError("didn't name check, please set self.name in __init__()")
        self.add_hostoption(self.name, default_host=self.default_host, default_port=self.default_port)
        self._add_options()

    def _add_options(self):
        pass

    def process_args(self):
        if not self.name:
            raise CodingError("didn't name check, please set self.name in __init__()")
        self.no_args()
        self.host = self.get_opt('host')
        self.port = self.get_opt('port')
        validate_host(self.host)
        validate_port(self.port)
        self._process_args()

    def _process_args(self):
        pass

    def run(self):
        self.ok()
        self.state = self.get_status()

    @abstractmethod
    def get_status(self):
        pass

    def end(self):
        # log.debug('self.state = %s' % self.state)
        if self.state is None:
            raise UnknownError('state is not set!')
        self.msg = "{0} status = '{1}'".format(self.name, self.state)
        if self.msg2:
            self.msg += ', {0}'.format(self.msg2)
        if self.perfdata:
            self.msg += ' | {0}'.format(self.perfdata)
        qquit(self.status, self.msg)
