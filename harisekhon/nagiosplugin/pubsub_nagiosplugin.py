#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-03-11 20:50:11 +0000 (Fri, 11 Mar 2016)
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

Publish Subscribe Checker Specialization of NagiosPlugin

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import os
import socket
import sys
import time
# Python 2.6+ only
from abc import ABCMeta, abstractmethod
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(libdir)
# pylint: disable=wrong-import-position
from harisekhon.nagiosplugin.nagiosplugin import NagiosPlugin
from harisekhon.utils import qquit, log, CodingError, CriticalError, UnknownError
from harisekhon.utils import validate_host, validate_port, get_topfile, random_alnum

__author__ = 'Hari Sekhon'
__version__ = '0.2.1'


class PubSubNagiosPlugin(NagiosPlugin):
    """
    Publish Subscribe Checker Nagios Plugin
    """

    __version__ = __version__
    # abstract class
    __metaclass__ = ABCMeta

    def __init__(self):
        # Python 2.x
        super(PubSubNagiosPlugin, self).__init__()
        # Python 3.x
        # super().__init__()
        self.name = None
        self.default_host = 'localhost'
        self.default_port = None
        self.host = None
        self.port = None
        self.producer = None
        self.consumer = None
        self.key = os.path.basename(get_topfile()) + '-' + random_alnum(20)
        self.start_offset = None
        timestamp = time.time()
        # socket.getfqdn() hangs on network / DNS outage, use socket.gethostname() instead
        self.publish_message = "Test message from Hari Sekhon {0} on host {1} "\
                               .format(os.path.basename(get_topfile()), socket.gethostname()) + \
                                "at epoch {0} ({1}) with random token '{2}'"\
                               .format(timestamp, time.ctime(timestamp), random_alnum(20))
        self._consumed_message = None
        self._publish_timing = None
        self._consume_timing = None
        self.status = 'OK'
        self.warning = 1
        self.critical = 2

    def add_options(self):
        if not self.name:
            raise CodingError("didn't name check, please set self.name in __init__()")
        self.add_hostoption(self.name, default_host=self.default_host, default_port=self.default_port)
        self.add_thresholds(default_warning=1, default_critical=2)

    def process_args(self):
        if not self.name:
            raise CodingError("didn't name check, please set self.name in __init__()")
        self.no_args()
        self.host = self.get_opt('host')
        self.port = self.get_opt('port')
        validate_host(self.host)
        validate_port(self.port)
        self.validate_thresholds()

    def run(self):
        log.info('subscribing')
        self.subscribe()
        log.info('publishing message \'%s\'', self.publish_message)
        start = time.time()
        self.publish()
        stop = time.time()
        self._publish_timing = stop - start
        start = time.time()
        self._consumed_message = self.consume()
        stop = time.time()
        self._consume_timing = stop - start
        log.info('read in %s secs', self._consume_timing)
        log.info("consumed message = '%s'", self._consumed_message)
        # resetting to ok is bad - would break inheritance logic
        #self.ok()

    @abstractmethod
    def subscribe(self):
        pass

    @abstractmethod
    def publish(self):
        pass

    @abstractmethod
    def consume(self):
        pass

    def end(self):
        if self._consumed_message is None:
            raise UnknownError('read value is not set!')
        log.info("checking consumed message '%s' == published message '%s'",
                 self._consumed_message, self.publish_message)
        if self._consumed_message != self.publish_message:
            raise CriticalError("wrote '{0}' but got back '{1}' instead".format(
                self.publish_message, self._consumed_message))
        self.msg = '{0} message published and consumed back successfully'.format(self.name)
        self.msg += ', published in {0:.7f} secs'.format(self._publish_timing)
        self.check_thresholds(self._publish_timing)
        self.msg += ', consumed in {0:.7f} secs'.format(self._consume_timing)
        self.check_thresholds(self._consume_timing)
        self.msg += ' | publish_time={0:.7f}s{1} consume_time={2:.7f}s{3}'.format(
            self._publish_timing, self.get_perf_thresholds(),
            self._consume_timing, self.get_perf_thresholds())
        qquit(self.status, self.msg)
