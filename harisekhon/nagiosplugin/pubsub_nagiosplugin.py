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
from harisekhon.utils import validate_host, validate_port, validate_float, get_topfile, random_alnum

__author__ = 'Hari Sekhon'
__version__ = '0.3.1'


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
        self._publish_time = None
        self._consume_time = None
        self._total_time = None
        self._precision = 3
        self.status = 'OK'
        self.warning_threshold_default = 1
        self.critical_threshold_default = 2
        self.default_sleep_secs = 1.0
        self.__sleep_secs = 0
        self.sleep_usage = 'Sleep time in seconds before publishing and subscribing ' + \
                           'to give message a chance to appear ' + \
                           '(optional, default: {} secs)'.format(self.default_sleep_secs)

    def add_options(self):
        if not self.name:
            raise CodingError("didn't name check, please set self.name in __init__()")
        self.add_hostoption(self.name, default_host=self.default_host, default_port=self.default_port)
        self.add_thresholds(default_warning=self.warning_threshold_default,
                            default_critical=self.critical_threshold_default)
        self.add_opt('-s', '--sleep', type=float, default=1.0, metavar='secs', help=self.sleep_usage)

    def process_args(self):
        if not self.name:
            raise CodingError("didn't name check, please set self.name in __init__()")
        self.no_args()
        self.host = self.get_opt('host')
        self.port = self.get_opt('port')
        validate_host(self.host)
        validate_port(self.port)
        self.validate_thresholds()
        sleep_secs = self.get_opt('sleep')
        if sleep_secs:
            # validation done through property wrapper
            self.sleep_secs = sleep_secs

    @property
    def sleep_secs(self):
        return self.__sleep_secs

    @sleep_secs.setter
    def sleep_secs(self, secs):
        validate_float(secs, 'sleep_secs')
        log.debug('setting sleep secs to %s secs', secs)
        self.__sleep_secs = float(secs)

    def run(self):
        start = time.time()
        log.info('subscribing')
        self.subscribe()
        log.info('publishing message "%s"', self.publish_message)
        start_publish = time.time()
        self.publish()
        stop_publish = time.time()
        self._publish_time = round(stop_publish - start_publish, self._precision)
        log.info('published in %s secs', self._publish_time)
        if self.sleep_secs:
            log.info('sleeping for %s secs', self.sleep_secs)
            time.sleep(self.sleep_secs)
        start_consume = time.time()
        log.info('consuming message')
        self._consumed_message = self.consume()
        stop_consume = time.time()
        self._consume_time = round(stop_consume - start_consume, self._precision)
        log.info('consumed in %s secs', self._consume_time)
        log.info('consumed message = "%s"', self._consumed_message)
        # resetting to ok is bad - would break inheritance logic
        #self.ok()
        stop = time.time()
        self._total_time = round(stop - start, self._precision)

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
        log.info('checking consumed message "%s" == published message "%s"',
                 self._consumed_message, self.publish_message)
        if self._consumed_message != self.publish_message:
            raise CriticalError("wrote '{0}' but got back '{1}' instead".format(
                self.publish_message, self._consumed_message))
        self.msg = '{0} message published and consumed back successfully'.format(self.name)
        self.msg += ', published in {0:.{1}f} secs'.format(self._publish_time, self._precision)
        self.check_thresholds(self._publish_time)
        self.msg += ', consumed in {0:.{1}f} secs'.format(self._consume_time, self._precision)
        self.check_thresholds(self._consume_time)
        self.msg += ', total time = {0:.{1}f} secs'.format(self._total_time, self._precision)
        self.msg += ' | publish_time={0:.{5}f}s{1} consume_time={2:.{5}f}s{3} total_time={4:.{5}f}s'.format(
            self._publish_time, self.get_perf_thresholds(),
            self._consume_time, self.get_perf_thresholds(),
            self._total_time,
            self._precision)
        qquit(self.status, self.msg)
