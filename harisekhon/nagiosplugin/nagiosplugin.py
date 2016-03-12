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
#  If you're using my code you're welcome to connect with me on LinkedIn and optionally send me feedback
#  to help improve or steer this or other code I publish
#
#  https://www.linkedin.com/in/harisekhon
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals

import os
import sys
# import traceback
# import logging
# Python 2.6+ only
from abc import ABCMeta, abstractmethod
libdir = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(libdir)
# pylint: disable=wrong-import-position
from harisekhon.utils import ERRORS, qquit, CodingErrorException, log, isStr, log_option
from harisekhon.utils import WarningError, CriticalError, UnknownError
from harisekhon import CLI
from harisekhon.nagiosplugin.threshold import Threshold
from harisekhon.nagiosplugin.threshold import InvalidThresholdException

__author__ = 'Hari Sekhon'
__version__ = '0.8.1'


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
        self.__status = 'UNKNOWN'
        # self.__msg = 'MESSAGE NOT DEFINED'
        self.msg = 'MESSAGE NOT DEFINED'
        self.__thresholds = {'warning': None, 'critical': None}

    # ============================================================================ #
    #                           Nagios Exit Code Functions
    # ============================================================================ #

    # Set status safely - escalate only

    # there is no ok() since that behaviour needs to be determined by scenario

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        if not ERRORS.has_key(status):
            raise CodingErrorException("invalid status '%(status)s' passed to harisekhon.NagiosPlugin.status()")
        self.__status = status

    # @property
    # def msg(self):
    #     return self.__msg

    # @msg.setter
    # def msg(self, msg):
    #     self.__msg = msg

    def ok(self): # pylint: disable=invalid-name
        self.status = 'OK'

    def warning(self):
        if self.status != 'CRITICAL':
            self.status = 'WARNING'

    def critical(self):
        self.status = 'CRITICAL'

    def unknown(self):
        if self.status == 'OK':
            self.status = 'UNKNOWN'

    ############################
    def is_ok(self):
        return self.status == 'OK'

    def is_warning(self):
        return self.status == 'WARNING'

    def is_critical(self):
        return self.status == 'CRITICAL'

    def is_unknown(self):
        return self.status == 'UNKNOWN'

    # ============================================================================ #

    def set_threshold(self, name, threshold):
        if not isinstance(threshold, Threshold):
            raise CodingErrorException('passed a non-threshold to NagiosPlugin.set_threshold()')
        self.__thresholds[name] = threshold

    def get_threshold(self, name, optional=False):
        try:
            _ = self.__thresholds[name]
            if _ is None:
                if optional:
                    return Threshold(None, optional=True)
                else:
                    raise CodingErrorException('threshold {0} is not set (None)'.format(name))
            return _
        except KeyError:
            raise CodingErrorException("threshold '%s' does not exist. " % name +
                                       "Invalid name passed to NagiosPlugin.check_threshold() - typo?")

    def add_thresholds(self, name='', default_warning=None, default_critical=None):
        if not isStr(name):
            raise CodingErrorException('non-string passed as name argument to add_thresholds()')
        default_warning_msg = ''
        default_critical_msg = ''
        if default_warning is not None:
            default_warning_msg = ', default: {0}'.format(default_warning)
        if default_critical is not None:
            default_critical_msg = ', default: {0}'.format(default_critical)
        if name:
            self.add_opt('--{0}-warning'.format(name), metavar='N', default=default_warning,
                         help='{0} warning threshold or ra:nge (inclusive{1})'
                         .format(name.title(), default_warning_msg))
            self.add_opt('--{0}-critical'.format(name), metavar='N', default=default_critical,
                         help='{0} critical threshold or ra:nge (inclusive{1})'
                         .format(name.title(), default_critical_msg))
        else:
            self.add_opt('-w', '--warning', metavar='N', default=default_warning,
                         help='Warning threshold or ra:nge (inclusive{0})'.format(default_warning_msg))
            self.add_opt('-c', '--critical', metavar='N', default=default_critical,
                         help='Critical threshold or ra:nge (inclusive{0})'.format(default_critical_msg))

    def validate_threshold(self, name, threshold=None, optional=False, **kwargs):
        if not isStr(name):
            raise CodingErrorException('non-string name passed to validate_threshold()')
        if threshold is None:
            # log.debug("using threshold option '%s'", name)
            threshold = self.get_opt(name)
            # log.debug("got threshold '%s'", threshold)
        if optional and threshold is None:
            return None
        else:
            try:
                self.__thresholds[name] = Threshold(threshold, name=name, **kwargs)
            except InvalidThresholdException as _:
                self.usage(_)
        log_option(name, threshold)

    def validate_thresholds(self, name='', warning=None, critical=None, **kwargs):
        if not isStr(name):
            raise CodingErrorException('non-string name passed to validate_thresholds()')
        if name:
            name += '_'
        self.validate_threshold('{0}{1}'.format(name, 'warning'), warning, **kwargs)
        self.validate_threshold('{0}{1}'.format(name, 'critical'), critical, **kwargs)

    # inferring threshold type from naming convention, assume critical if can't determine
    def check_threshold(self, name, result):
        _ = self.get_threshold(name, optional=True).check(result)
        if _:
            if 'warning' in name:
                self.warning()
            else:
                self.critical()
            return _
        return ''

    def check_thresholds(self, result, name=''):
        if not isStr(name):
            raise CodingErrorException('non-string passed to check_thresholds()')
        if name:
            name += '_'
        threshold_breach_msg = self.check_threshold('{0}critical'.format(name), result)
        threshold_breach_msg2 = self.check_threshold('{0}warning'.format(name), result)
        if threshold_breach_msg:
            self.msg += ' ' + threshold_breach_msg
        elif threshold_breach_msg2:
            self.msg += ' ' + threshold_breach_msg2

    def get_perf_thresholds(self, boundary='upper'):
        if boundary not in ('lower', 'upper'):
            raise CodingErrorException('invalid boundary passed to msg_perf_thresholds')
        warning = self.get_threshold('warning', optional=True)
        critical = self.get_threshold('critical', optional=True)
        warning_msg = ''
        critical_msg = ''
        if not warning or warning.thresholds[boundary] is not None:
            warning_msg = '{0:g}'.format(warning.thresholds[boundary])
        if not critical or critical.thresholds[boundary] is not None:
            critical_msg = '{0:g}'.format(critical.thresholds[boundary])
        return ';{0};{1}'.format(warning_msg, critical_msg)

    # Generic exception handler for Nagios to rewrite any unhandled exceptions as UNKNOWN rather than allowing
    # the default python exit code of 1 which would equate to WARNING in Nagios compatible systems
    def main(self):
        try:
            # Python 2.x
            super(NagiosPlugin, self).main()
            # Python 3.x
            # super().__init__()
            # redirect_stderr_stdout()
        except CriticalError as _:
            qquit('CRITICAL', _)
        except WarningError as _:
            qquit('WARNING', _)
        except UnknownError as _:
            qquit('UNKNOWN', _)
        except Exception as _:  # pylint: disable=broad-except
            qquit('UNKNOWN', _)
            # Done in utils now so that this also applies to the above specific exit handlers
            # print('UNKNOWN: {0}'.format(_))
            # prints to stderr, Nagios spec wants stdout
            # traceback.print_exc()
            # tb = traceback.format_exc().strip()
            # if tb != 'None':
            #     print('\n{0}'.format(tb), end='')
            # sys.exit(ERRORS['UNKNOWN'])

    @abstractmethod
    def run(self): # pragma: no cover
        pass

    def end(self):
        pass

    def __end__(self):
        self.end()
        log.info('end\n%s\n', '='*80)
        qquit(self.status, self.msg)
