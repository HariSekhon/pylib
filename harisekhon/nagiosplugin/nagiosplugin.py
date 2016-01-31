#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2014-09-15 20:49:37 +0100 (Mon, 15 Sep 2014)
#
#  https://github.com/harisekhon/pylib
#
#  License: see accompanying Hari Sekhon LICENSE file
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals

import os
import sys
# import logging
# Python 2.6+ only
from abc import ABCMeta, abstractmethod
libdir = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(libdir)
# pylint: disable=wrong-import-position
from harisekhon.utils import ERRORS, qquit, CodingErrorException
from harisekhon import CLI
from harisekhon.nagiosplugin.threshold import Threshold
from harisekhon.nagiosplugin.threshold import InvalidThresholdException

__author__ = 'Hari Sekhon'
__version__ = '0.4'

class NagiosPlugin(CLI):
    """
    HariSekhon.NagiosPlugin class for rapid development of Nagios Plugins in Python
    """
    __version__ = __version__
    # abstract class
    __metaclass__ = ABCMeta

    def __init__(self):
        # Python 2.x
        super(NagiosPlugin, self).__init__()
        # Python 3.x
        # super().__init__()
        # redirect_stderr_stdout()
        self.__status__ = 'UNKNOWN'
        self.msg = 'MESSAGE NOT DEFINED'
        self.__thresholds = {'warning': None, 'critical': None}

    # ============================================================================ #
    #                           Nagios Exit Code Functions
    # ============================================================================ #

    # Set status safely - escalate only

    # there is no ok() since that behaviour needs to be determined by scenario

    def get_status(self):
        return self.__status__

    def set_status(self, status):
        if not ERRORS.has_key(status):
            raise CodingErrorException("invalid status '%(status)s' passed to harisekhon.NagiosPlugin.set_status()")
        self.__status__ = status

    def ok(self): # pylint: disable=invalid-name
        self.set_status('OK')

    def warning(self):
        if self.get_status() != 'CRITICAL':
            self.set_status('WARNING')

    def critical(self):
        self.set_status('CRITICAL')

    def unknown(self):
        if self.get_status() == 'OK':
            self.set_status('UNKNOWN')

    ############################
    def is_ok(self):
        return self.get_status() == 'OK'

    def is_warning(self):
        return self.get_status() == 'WARNING'

    def is_critical(self):
        return self.get_status() == 'CRITICAL'

    def is_unknown(self):
        return self.get_status() == 'UNKNOWN'

    # ============================================================================ #

    def set_threshold(self, name, threshold):
        if not isinstance(threshold, Threshold):
            raise CodingErrorException('passed a non-threshold to NagiosPlugin.set_threshold()')
        self.__thresholds[name] = threshold

    def get_threshold(self, name):
        try:
            return self.__thresholds[name]
        except KeyError:
            raise CodingErrorException("threshold '%s' does not exist" % name +
                                       "invalid name passed to NagiosPlugin.check_threshold() - typo?")

    def validate_threshold(self, arg, optional=False, **kwargs): # pylint: disable=no-self-use
        if optional:
            return None
        else:
            try:
                return Threshold(arg, **kwargs)
            except InvalidThresholdException as _:
                self.usage('UNKNOWN', _)

    def validate_thresholds(self, optional=False, **kwargs):
        # pylint is reading this wrong
        # pylint: disable=too-many-function-args
        if 'warning' in dir(self.options):
            self.set_threshold('warning',
                               self.validate_threshold(
                                   self.options.warning,
                                   optional=optional,
                                   name='warning',
                                   **kwargs)
                              )
        elif optional:
            pass
        else:
            qquit('UNKNOWN', 'warning threshold not defined')
        if 'critical' in dir(self.options):
            self.set_threshold('critical',
                               self.validate_threshold(
                                   self.options.critical,
                                   optional=optional,
                                   name='critical',
                                   **kwargs)
                              )
        elif optional:
            pass
        else:
            qquit('UNKNOWN', 'critical threshold not defined')

    def check_threshold(self, name, result):
        if self.get_threshold(name).check(result):
            self.critical()
        elif self.get_threshold(name).check(result):
            self.warning()

    def check_thresholds(self, result):
        self.check_threshold('warning', result)
        self.check_threshold('critical', result)

    @abstractmethod
    def run(self):
        pass

    def end(self):
        qquit(self.get_status(), self.msg)
