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
import re
import sys
libdir = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(libdir)
# pylint: disable=wrong-import-position
from harisekhon.utils import InvalidOptionException, CodingErrorException, isInt, isBool #, log

__author__ = 'Hari Sekhon'
__version__ = '0.1'

class InvalidThresholdException(InvalidOptionException):
    pass

class Threshold(object):
    """
    HariSekhon.NagiosPlugin.Threshold class for HariSekhon.NagiosPlugin inherited classes to utilize
    """
    __version__ = __version__

    def __init__(self, arg, **kwargs):
        #min=None, max=None, positive=True, integer=True, simple='upper', name='', **kwargs):
        self.name = kwargs.get('name', '')
        if self.name:
            self.name += ' '
        self.thresholds = {'upper': None, 'lower': None}
        self.opts = {'invert': False}

        self.opts['simple'] = kwargs.get('simple', 'upper')
        self.opts['positive'] = kwargs.get('positive', True)
        self.opts['integer'] = kwargs.get('integer', True)
        self.thresholds['min'] = kwargs.get('min', None)
        self.thresholds['max'] = kwargs.get('max', None)

        if self.opts['simple'] not in ('upper', 'lower'):
            raise CodingErrorException('simple threshold type must be one of: upper, lower')
        if not isBool(self.opts['positive']):
            raise CodingErrorException('positive option must be set to either True or False')
        if not isBool(self.opts['integer']):
            raise CodingErrorException('integer option must be set to either True or False')

        self.parse_threshold(arg)

    def parse_threshold(self, arg):
        arg = str(arg)
        threshold_range_regex = re.compile(r'^(\@)?(-?\d+(?:\.\d+)?)(:)(-?\d+(?:\.\d+)?)?$')
        threshold_range_simple = re.compile(r'^(-?\d+(?:\.\d+)?)')
        _ = threshold_range_regex.match(arg)
        if _:
            if _.group(1):
                if not (_.group(2) and _.group(3) and _.group(4)):
                    raise InvalidThresholdException('inverted range @ prefix for {0}threshold '.format(self.name) +
                                                    'makes no sense without both upper and lower boundaries')
                self.opts['invert'] = True
            if _.group(3):
                if _.group(4):
                    self.thresholds['upper'] = float(_.group(4))
                    self.thresholds['lower'] = float(_.group(2))
            else:
                self.thresholds['upper'] = float(_.group(2))
            if self.thresholds['lower'] and self.thresholds['upper']:
                if self.thresholds['lower'] > self.thresholds['upper']:
                    raise InvalidThresholdException('invalid thresholds: lower {0} threshold '.format(arg) +
                                                    'cannot be greater than upper %(arg)s threshold')
        else:
            _ = threshold_range_simple.match(arg)
            if _:
                if self.opts['simple'] == 'upper':
                    self.thresholds['upper'] = float(_.group(1))
                elif self.opts['simple'] == 'lower':
                    self.thresholds['lower'] = float(_.group(1))
            else:
                raise InvalidThresholdException('invalid {0}threshold given, '.format(self.name) +
                                                'must be standard nagios threshold [@][start:]end')

#        self.validate_opts()
#
#    def validate_opts(self):
        for boundary in ('upper', 'lower'):
            if self.opts['positive'] and self.thresholds[boundary] is not None and self.thresholds[boundary] < 0:
                raise InvalidThresholdException('{0}{1} threshold may not be less than zero'.format(self.name, boundary))
            if self.opts['integer'] and self.thresholds[boundary] is not None in self.opts and \
                not isInt(self.thresholds[boundary]):
                raise InvalidThresholdException('{0}{1} threshold must be an integer'.format(self.name, boundary))
            if self.thresholds['min'] is not None and self.thresholds[boundary] is not None and \
               self.thresholds[boundary] < self.thresholds['min']:
                raise InvalidThresholdException('{0} threshold cannot be less than {1}'
                                                .format(boundary, self.thresholds['min']))
            if self.thresholds['max'] is not None and self.thresholds[boundary] is not None and \
               self.thresholds[boundary] > self.thresholds['max']:
                raise InvalidThresholdException('{0} threshold cannot be greater than than {1}'
                                                .format(boundary, self.thresholds['max']))

    def check(self, result):
        result = float(result)
        if self.opts['invert']:
            if self.thresholds['lower'] is not None and self.thresholds['upper'] and \
               result >= self.thresholds['lower'] and result <= self.thresholds['upper']:
                return False
        else:
            if self.thresholds['lower'] is not None and result < self.thresholds['lower']:
                return False
            if self.thresholds['upper'] is not None and result > self.thresholds['upper']:
                return False
        return True
