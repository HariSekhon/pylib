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
from harisekhon.utils import InvalidOptionException, CodingError, isBool, isInt, isFloat, log

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
        log.debug('%sthreshold simple = %s', self.name, self.opts['simple'])
        log.debug('%sthreshold positive = %s', self.name, self.opts['positive'])
        log.debug('%sthreshold integer = %s', self.name, self.opts['integer'])
        log.debug('%sthreshold min = %s', self.name, self.thresholds['min'])
        log.debug('%sthreshold max = %s', self.name, self.thresholds['max'])

        if self.opts['simple'] not in ('upper', 'lower'):
            raise CodingError('simple threshold type must be one of: upper, lower')
        if not isBool(self.opts['positive']):
            raise CodingError('positive option must be set to either True or False')
        if not isBool(self.opts['integer']):
            raise CodingError('integer option must be set to either True or False')

        self.__parse_threshold__(arg, kwargs.get('optional'))

    def __parse_threshold__(self, arg, optional=False):
        if arg is None:
            if optional:
                return
            else:
                raise InvalidThresholdException('no {0}threshold defined'.format(self.name))
        arg = str(arg)
        log.debug("%sthreshold given = '%s'", self.name, arg)
        threshold_range_regex = re.compile(r'^(\@)?(-?\d+(?:\.\d+)?)(:)(-?\d+(?:\.\d+)?)?$')
        threshold_range_simple = re.compile(r'^(-?\d+(?:\.\d+)?)$')
        _ = threshold_range_regex.match(arg)
        if _:
            if _.group(1):
                if not (_.group(2) and _.group(3) and _.group(4)):
                    raise InvalidThresholdException('inverted range @ prefix for {0}threshold '.format(self.name) +
                                                    'makes no sense without both upper and lower boundaries')
                self.opts['invert'] = True
                log.debug('%sthreshold invert = True', self.name)
            if _.group(3):
                if _.group(4):
                    self.thresholds['upper'] = float(_.group(4))
                    self.thresholds['lower'] = float(_.group(2))
            else:
                self.thresholds['upper'] = float(_.group(2))
            log.debug('%sthreshold upper boundary = %s', self.name, self.thresholds['upper'])
            log.debug('%sthreshold lower boundary = %s', self.name, self.thresholds['lower'])
            if self.thresholds['lower'] and self.thresholds['upper']:
                if self.thresholds['lower'] > self.thresholds['upper']:
                    raise InvalidThresholdException('invalid thresholds: {0}lower threshold '.format(self.name) +
                                                    '({0}) cannot be greater than upper threshold ({1})'
                                                    .format(self.thresholds['lower'], self.thresholds['upper']))
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
            log.debug('%sthreshold upper boundary = %s', self.name, self.thresholds['upper'])
            log.debug('%sthreshold lower boundary = %s', self.name, self.thresholds['lower'])

#        self.validate_opts()
#
#    def validate_opts(self):
        for boundary in ('upper', 'lower'):
            if self.opts['positive'] and self.thresholds[boundary] is not None and \
               self.thresholds[boundary] < 0:
                raise InvalidThresholdException('{0}{1} threshold may not be less than zero'
                                                .format(self.name, boundary))
            if self.opts['integer'] and self.thresholds[boundary] is not None and \
               not isInt(self.thresholds[boundary], allow_negative=True):
                raise InvalidThresholdException('{0}{1} threshold must be an integer'.format(self.name, boundary))
            if self.thresholds['min'] is not None and self.thresholds[boundary] is not None and \
               self.thresholds[boundary] < self.thresholds['min']:
                raise InvalidThresholdException('{0}{1} threshold cannot be less than minimum {2}'
                                                .format(self.name, boundary, self.thresholds['min']))
            if self.thresholds['max'] is not None and self.thresholds[boundary] is not None and \
               self.thresholds[boundary] > self.thresholds['max']:
                raise InvalidThresholdException('{0}{1} threshold cannot be greater than than maximum {2}'
                                                .format(self.name, boundary, self.thresholds['max']))

    def check(self, result):
        if not isFloat(result):
            return '(not a float!)'
        result = float(result)
        if self.opts['invert']:
            if self.thresholds['lower'] is not None and self.thresholds['upper'] is not None and \
               result >= self.thresholds['lower'] and result <= self.thresholds['upper']:
                return '({0:g} <= {1:g} <= {2:g})'.format(self.thresholds['lower'], result, self.thresholds['upper'])
        else:
            if self.thresholds['lower'] is not None and result < self.thresholds['lower']:
                return '({0:g} < {1:g})'.format(result, self.thresholds['lower'])
            if self.thresholds['upper'] is not None and result > self.thresholds['upper']:
                return '({0:g} > {1:g})'.format(result, self.thresholds['upper'])
        return ''
