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
# pylint: disable=wrong-import-position
from harisekhon.utils import log, CodingErrorException
from harisekhon import NagiosPlugin
from harisekhon.nagiosplugin import Threshold

class NagiosPluginTester(unittest.TestCase):

    # must prefix with test_ in order for the tests to be called

    # Not using assertRaises >= 2.7 and maintaining compatibility with Python 2.6 servers

    class SubNagiosPlugin(NagiosPlugin):
        def run(self):
            print("running SubNagiosPlugin()")

    def setUp(self):
        self.plugin = self.SubNagiosPlugin()

    def test_threshold(self):
        self.plugin.set_threshold('test', Threshold(5))
        self.assertTrue(isinstance(self.plugin.get_threshold('test'), Threshold))

    def test_set_threshold_invalid(self):
        try:
            self.plugin.set_threshold('test', 5)
            raise Exception('failed to raise CodingErrorException on passing in non-threshold object to Threshold.set_threshold()')
        except CodingErrorException:
            pass

    def test_get_threshold_nonexistent(self):
        try:
            self.plugin.get_threshold('nonexistent')
            raise Exception('failed to raise CodingErrorException for Threshold.get_threshold(nonexistent)')
        except CodingErrorException:
            pass

    def test_validate_threshold(self):
        self.assertEqual(self.plugin.validate_threshold(4, optional=True), None)

    def test_validate_thresholds(self):
        #self.plugin.option.warning = 2
        #self.plugin.option.critical = 3
        #self.assertTrue(isinstance(self.plugin.validate_thresholds(), Threshold))
        self.assertEqual(self.plugin.validate_thresholds(optional=True), None)

    def test_validate_thresholds_nonexistent(self):
        try:
            self.plugin.validate_thresholds()
            raise Exception('failed to raise exception for validate_thresholds() when no thresholds set')
        except SystemExit as _:
            if _.code != 3:
                raise Exception('invalid exit code raised when thresholds are not set')

    def test_check_thresholds(self):
        try:
            self.plugin.check_thresholds(10)
            raise Exception('failed to raise exception for check_thresholds() when thresholds are not set')
        except CodingErrorException:
            pass

    def test_statuses(self):
        self.assertTrue(self.plugin.is_unknown())
        self.plugin.ok()
        self.assertTrue(self.plugin.is_ok())
        self.assertFalse(self.plugin.is_warning())
        self.assertFalse(self.plugin.is_critical())
        self.assertFalse(self.plugin.is_unknown())
        self.plugin.unknown()
        self.assertTrue(self.plugin.is_unknown())
        self.assertFalse(self.plugin.is_ok())
        self.assertFalse(self.plugin.is_warning())
        self.assertFalse(self.plugin.is_critical())
        self.plugin.warning()
        self.assertTrue(self.plugin.is_warning())
        self.assertFalse(self.plugin.is_ok())
        self.assertFalse(self.plugin.is_critical())
        self.assertFalse(self.plugin.is_unknown())
        self.plugin.unknown()
        self.assertTrue(self.plugin.is_warning())
        self.assertFalse(self.plugin.is_ok())
        self.assertFalse(self.plugin.is_critical())
        self.assertFalse(self.plugin.is_unknown())
        self.plugin.critical()
        self.assertTrue(self.plugin.is_critical())
        self.assertFalse(self.plugin.is_ok())
        self.assertFalse(self.plugin.is_warning())
        self.assertFalse(self.plugin.is_unknown())
        self.plugin.warning()
        self.assertTrue(self.plugin.is_critical())
        self.assertFalse(self.plugin.is_ok())
        self.assertFalse(self.plugin.is_warning())
        self.assertFalse(self.plugin.is_unknown())

    def test_invalid_status(self):
        try:
            self.plugin.set_status('invalidstatus')
        except CodingErrorException:
            pass

    def test_critical_exit(self):
        try:
            self.plugin.critical()
            self.plugin.main()
        except SystemExit as _:
            if _.code != 2:
                raise Exception('NagiosPlugin failed to exit CRITICAL')

    def test_nagiosplugin_abstract(self): # pylint: disable=no-self-use
        try:
            NagiosPlugin() # pylint: disable=abstract-class-instantiated
            raise Exception('failed to raise a TypeError when attempting to instantiate abstract class NagiosPlugin')
        except TypeError as _:
            pass


def main():
    # increase the verbosity
    # verbosity Python >= 2.7
    #unittest.main(verbosity=2)
    log.setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(NagiosPluginTester)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()
