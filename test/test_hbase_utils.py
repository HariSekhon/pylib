#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-10-12 23:16:44 +0100 (Wed, 12 Oct 2016)
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

"""
# ============================================================================ #
#                   PyUnit Tests for HariSekhon HBase Utils
# ============================================================================ #
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import logging
import os
import sys
import unittest
# unittest2 from pypi works for Python 2.4-2.6
# import unittest2
# inspect.getfile(inspect.currentframe()) # filename
# libdir = os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), '..')
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(libdir)
# pylint: disable=wrong-import-position
from harisekhon.utils import *  # pylint: disable=wildcard-import,unused-wildcard-import
from harisekhon.hbase.utils import *  # pylint: disable=wildcard-import

# pylint: disable=invalid-name,no-self-use

# class test_HariSekhonHBaseUtils(unittest2.TestCase):
class HBaseUtilsTester(unittest.TestCase):
    # must prefix with test_ in order for the tests to be called

    # Not using assertRaises >= 2.7 and maintaining compatibility with Python 2.6 servers

    # Class attributes - can still access via self.<attrib> as it's less typing than test_HariSekhonUtils.<attrib>
    # libdir = libdir
    libfile = os.path.join(libdir, 'harisekhon', 'utils.py')
    myList = [1, 2, 3]
    mySet = set(myList)
    myTuple = (1, 2, 3)
    myDict = {'one': 1, 'two': 2, 'three': 3}
    jsondata = '{ "name": { "first": "Hari", "last": "Sekhon" } }'
    jsondata_broken = '{ "name": { "first": "Hari", "last": "Sekhon" } '  # missing closing brace intentionally
    yamldata = open(os.path.join(libdir, 'test', 'test.yaml')).read()
    yamldata_simple = 'name:    Hari Sekhon'
    yamldata_broken_tab = 'name:\tHari Sekhon'

    def setUp(self):
        # TODO: XXX: review if needed
        log.setLevel(logging.DEBUG)
        # pass

    def test_isHBaseColumnQualifier(self):
        self.assertTrue(isHBaseColumnQualifier('cf1:q1'))
        self.assertFalse(isHBaseColumnQualifier('?'))

    def test_isHBaseRowKey(self):
        self.assertTrue(isHBaseRowKey('one#two'))
        self.assertFalse(isHBaseRowKey('?'))
        
    def test_isHBaseTable(self):
        self.assertTrue(isHBaseTable('hbase:meta'))
        self.assertFalse(isHBaseTable('?'))
        
    def test_validate_hbase_column_qualifier(self):
        self.assertTrue(validate_hbase_column_qualifier('cf1:q1'))
        
    def test_validate_hbase_rowkey(self):
        self.assertTrue(validate_hbase_rowkey('one#two'))
        
    def test_validate_hbase_table(self):
        self.assertTrue(validate_hbase_table('hbase:meta'))
        
# ============================================================================ #
    def test_validate_hbase_column_qualifier_exception(self):
        try:
            validate_hbase_column_qualifier('?')
            raise Exception('validate_hbase_column_qualifier() failed to raise exception for ?')
        except InvalidOptionException:
            pass

    def test_validate_hbase_column_qualifier_blank(self):
        try:
            validate_hbase_column_qualifier('')
            raise Exception('validate_hbase_column_qualifier() failed to raise exception for blank')
        except InvalidOptionException:
            pass

    def test_validate_hbase_column_qualifier_none(self):
        try:
            validate_hbase_column_qualifier(None)
            raise Exception('validate_hbase_column_qualifier() failed to raise exception for none')
        except InvalidOptionException:
            pass

# ============================================================================ #
    def test_validate_hbase_rowkey_exception(self):
        try:
            validate_hbase_rowkey('?')
            raise Exception('validate_hbase_rowkey() failed to raise exception for ?')
        except InvalidOptionException:
            pass

    def test_validate_hbase_rowkey_blank(self):
        try:
            validate_hbase_rowkey('')
            raise Exception('validate_hbase_rowkey() failed to raise exception for blank')
        except InvalidOptionException:
            pass

    def test_validate_hbase_rowkey_none(self):
        try:
            validate_hbase_rowkey(None)
            raise Exception('validate_hbase_rowkey() failed to raise exception for none')
        except InvalidOptionException:
            pass

# ============================================================================ #
    def test_validate_hbase_table_exception(self):
        try:
            validate_hbase_table('?')
            raise Exception('validate_hbase_table() failed to raise exception for ?')
        except InvalidOptionException:
            pass

    def test_validate_hbase_table_blank(self):
        try:
            validate_hbase_table('')
            raise Exception('validate_hbase_table() failed to raise exception for blank')
        except InvalidOptionException:
            pass

    def test_validate_hbase_table_none(self):
        try:
            validate_hbase_table(None)
            raise Exception('validate_hbase_table() failed to raise exception for none')
        except InvalidOptionException:
            pass

# ============================================================================ #

def main():
    # increase the verbosity
    # verbosity Python >= 2.7
    # unittest.main(verbosity=2)
    log.setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(HBaseUtilsTester)
    unittest.TextTestRunner(verbosity=2).run(suite)
    # unittest2.main(verbosity=2)


if __name__ == '__main__':
    main()
