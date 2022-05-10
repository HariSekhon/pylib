#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-10-12 23:09:32 +0100 (Wed, 12 Oct 2016)
#  Port of my Perl library version from Date: 2014-01-08 15:44:41 +0000 (Wed, 08 Jan 2014)
#
#  https://github.com/HariSekhon/pylib
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback to help steer this or other code I publish
#
#  https://www.linkedin.com/in/HariSekhon
#

"""

HBase Utils

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import re
from harisekhon.utils import InvalidOptionException, log_option

__author__ = 'Hari Sekhon'
__version__ = '0.1'


def isHBaseColumnQualifier(arg):
    if arg is None:
        return False
    if re.match(r'^[A-Za-z][\w\s\(\)\:#]+$', str(arg)):
        return True
    return False


def isHBaseRowKey(arg):
    if arg is None:
        return False
    if re.match(r'^[A-Za-z][\w\:#]+$', str(arg)):
        return True
    return False


def isHBaseTable(arg):
    if arg is None:
        return False
    if re.match(r'^[A-Za-z][\w\:]+$', str(arg)):
        return True
    return False


def validate_hbase_table(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)shbase table not defined' % locals())
    if isHBaseTable(arg):
        log_option('%(name)shbase table' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)shbase table '%(arg)s' defined" % locals())


def validate_hbase_rowkey(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)shbase row key not defined' % locals())
    if isHBaseRowKey(arg):
        log_option('%(name)shbase row key' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)shbase row key '%(arg)s' defined" % locals())


def validate_hbase_column_qualifier(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)shbase column qualifier not defined' % locals())
    if isHBaseColumnQualifier(arg):
        log_option('%(name)shbase column' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)shbase column '%(arg)s' defined" % locals())
