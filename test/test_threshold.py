#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2014-09-15 20:49:22 +0100 (Mon, 15 Sep 2014)
#
#  http://github.com/harisekhon/pylib
#
#  License: see accompanying LICENSE file
#

"""
# ============================================================================ #
#                   PyUnit Tests for HariSekhon.NagiosPlugin
# ============================================================================ #
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os
import sys
import unittest
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(libdir)
from harisekhon.utils import log, CodingErrorException # pylint: disable=wrong-import-position
from harisekhon.nagiosplugin import Threshold, InvalidThresholdException # pylint: disable=wrong-import-position

class NagiosThresholdTester(unittest.TestCase):

    # must prefix with test_ in order for the tests to be called

    # Not using assertRaises >= 2.7 and maintaining compatibility with Python 2.6 servers

    def setUp(self):
        self.threshold = Threshold(5)
        self.threshold_lower = Threshold(5, simple='lower')
        self.threshold_range = Threshold('5:10')
        self.threshold_range_inverted = Threshold('@5:10')

    def test_threshold_check_upper(self):
        self.assertTrue(self.threshold.check(4))
        self.assertTrue(self.threshold.check(5))
        self.assertFalse(self.threshold.check(6))

    def test_threshold_check_lower(self):
        self.assertFalse(self.threshold_lower.check(4))
        self.assertTrue(self.threshold_lower.check(5))
        self.assertTrue(self.threshold_lower.check(6))

    def test_threshold_check_range(self):
        self.assertTrue(self.threshold_range.check(5))
        self.assertTrue(self.threshold_range.check(7))
        self.assertTrue(self.threshold_range.check(10))
        self.assertFalse(self.threshold_range.check(4))
        self.assertFalse(self.threshold_range.check(11))

    def test_threshold_check_range_inverted(self):
        self.assertFalse(self.threshold_range_inverted.check(5))
        self.assertFalse(self.threshold_range_inverted.check(6))
        self.assertFalse(self.threshold_range_inverted.check(10))
        self.assertTrue(self.threshold_range_inverted.check(4))
        self.assertTrue(self.threshold_range_inverted.check(11))

    def test_invalid_inverted_range_no_upper(self):
        try:
            Threshold('@5:')
            raise Exception('failed to raise InvalidThresholdException for invalid inverted range no upper')
        except InvalidThresholdException:
            pass

    def test_invalid_inverted_range_no_lower(self):
        try:
            Threshold('@:10')
            raise Exception('failed to raise InvalidThresholdException for invalid inverted range no lower')
        except InvalidThresholdException:
            pass


    def test_invalid_simple(self):
        try:
            Threshold(5, simple='blah')
            raise Exception('failed to raise InvalidThresholdException for invalid simple threshold type')
        except CodingErrorException:
            pass

    def test_invalid_positive(self):
        try:
            Threshold(5, simple='upper', positive=1)
            raise Exception('failed to raise InvalidThresholdException for invalid positive type')
        except CodingErrorException:
            pass

    def test_invalid_integer(self):
        try:
            Threshold(5, simple='upper', integer=1)
            raise Exception('failed to raise InvalidThresholdException for invalid integer type')
        except CodingErrorException:
            pass


def main():
    # increase the verbosity
    # verbosity Python >= 2.7
    #unittest.main(verbosity=2)
    log.setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(NagiosThresholdTester)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()
