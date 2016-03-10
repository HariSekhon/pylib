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

NoSQL Key Write Check Specialization of NagiosPlugin

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import os
import sys
import time
# Python 2.6+ only
from abc import ABCMeta, abstractmethod
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(libdir)
# pylint: disable=wrong-import-position
from harisekhon.utils import CriticalError, UnknownError, CodingErrorException, qquit
from harisekhon.utils import log, get_topfile, random_alnum, validate_host, validate_port
from harisekhon.nagiosplugin import KeyCheckNagiosPlugin

__author__ = 'Hari Sekhon'
__version__ = '0.2'


class KeyWriteNagiosPlugin(KeyCheckNagiosPlugin):
    """
    NoSQL Key Write Checker Nagios Plugin
    """

    __version__ = __version__
    # abstract class
    __metaclass__ = ABCMeta

    def __init__(self):
        # Python 2.x
        super(KeyWriteNagiosPlugin, self).__init__()
        # Python 3.x
        # super().__init__()
        self.key = os.path.basename(get_topfile()) + '-' + random_alnum(20)
        self._write_value = random_alnum(20)
        self._write_timing = None
        self._delete_timing = None

    def add_options(self):
        self.add_hostoption(self.name, default_host=self.default_host, default_port=self.default_port)

    def process_args(self):
        if not self.name:
            raise CodingErrorException("didn't name check, please set self.name in __init__ of " +
                                       "KeyCheckNagiosPlugin")
        self.no_args()
        self.host = self.get_opt('host')
        self.port = self.get_opt('port')
        validate_host(self.host)
        validate_port(self.port)

    def run(self):
        ###############
        # == Write == #
        start = time.time()
        self.write()
        end = time.time()
        self._write_timing = end - start
        log.info('read in %s secs', self._read_timing)
        ##############
        # == Read == #
        # Python 2.x
        super(KeyWriteNagiosPlugin, self).run()
        # Python 3.x
        # super().run()
        if self._read_value != self._write_value:
            raise CriticalError("read back value '%s' does not match written value '%s'!"
                                % (self._read_value, self._write_value))
        ################
        # == Delete == #
        start = time.time()
        self.delete()
        end = time.time()
        self._delete_timing = end - start
        log.info('read in %s secs', self._read_timing)

    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    def end(self):
        # don't inherit read check's end as we want a different output format
        if self._read_value is None:
            raise UnknownError('read value is not set!')
        self.msg = '{0} key written and read back successfully'.format(self.name)
        self.msg += ' | write_time={0:.7f}s read_time={1:.7f}s delete_time={2:.7f}s'.format(
            self._write_timing, self._read_timing, self._delete_timing)
        qquit(self.status, self.msg)
