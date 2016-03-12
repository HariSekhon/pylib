#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-02-14 16:25:48 +0000 (Sun, 14 Feb 2016)
#
#  https://github.com/harisekhon/pytools
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback
#
#  https://www.linkedin.com/in/harisekhon
#

"""

NoSQL Key Checker Specialization of NagiosPlugin

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import os
import re
import sys
import time
# Python 2.6+ only
from abc import ABCMeta, abstractmethod
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(libdir)
# pylint: disable=wrong-import-position
from harisekhon.nagiosplugin.nagiosplugin import NagiosPlugin
from harisekhon.utils import qquit, log, CodingErrorException, UnknownError
from harisekhon.utils import validate_host, validate_port, validate_regex, validate_chars, isFloat

__author__ = 'Hari Sekhon'
__version__ = '0.2'


class KeyCheckNagiosPlugin(NagiosPlugin):
    """
    NoSQL Key Checker Nagios Plugin
    """

    __version__ = __version__
    # abstract class
    __metaclass__ = ABCMeta

    def __init__(self):
        # Python 2.x
        super(KeyCheckNagiosPlugin, self).__init__()
        # Python 3.x
        # super().__init__()
        self.name = None
        self.default_host = 'localhost'
        self.default_port = None
        self.host = None
        self.port = None
        self.key = None
        self.regex = None
        self._read_value = None
        self._read_timing = None
        self.status = 'OK'

    def add_options(self):
        self.add_hostoption(self.name, default_host=self.default_host, default_port=self.default_port)
        self.add_opt('-k', '--key', help='Key to query from %s' % self.name)
        self.add_opt('-r', '--regex', help="Regex to compare the key's value against (optional)")
        self.add_thresholds()

    def process_args(self):
        if not self.name:
            raise CodingErrorException("didn't name check, please set self.name in __init__ of " +
                                       "KeyCheckNagiosPlugin")
        self.no_args()
        self.host = self.get_opt('host')
        self.port = self.get_opt('port')
        validate_host(self.host)
        validate_port(self.port)
        self.key = self.get_opt('key')
        self.regex = self.get_opt('regex')
        if not self.key:
            self.usage('--key not defined')
        self.key = self.key.lstrip('/')
        validate_chars(self.key, 'key', r'\w\/-')
        if self.regex:
            validate_regex(self.regex, 'key')
        self.validate_thresholds(optional=True)

    def run(self):
        start = time.time()
        self._read_value = self.read()
        stop = time.time()
        self._read_timing = stop - start
        log.info('read in %s secs', self._read_timing)
        log.info("value = '%s'", self._read_value)
        # resetting to ok is bad - would break inheritance logic
        #self.ok()

    @abstractmethod
    def read(self):
        pass

    def end(self):
        if self._read_value is None:
            raise UnknownError('read value is not set!')
        self.msg = "%s key '%s' value = '%s'" % (self.name, self.key, self._read_value)
        if self.regex:
            if not re.search(self.regex, self._read_value):
                self.critical()
                self.msg += " (did not match expected regex '%(regex)s')" % self.__dict__
            #elif self.get_verbose():
            #    self.msg += " (matched regex '%s')" % regex
        self.check_thresholds(self._read_value)
        if isFloat(self._read_value):
            self.msg += " | '{0}'={1}{2} query_time={3:.7f}s".format(self.key, self._read_value, self.get_perf_thresholds(), self._read_timing)
        qquit(self.status, self.msg)
