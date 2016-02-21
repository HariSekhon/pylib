#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2014-09-15 20:49:22 +0100 (Mon, 15 Sep 2014)
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
            raise Exception('failed to raise CodingErrorException on passing in non-threshold object to Threshold.set_threshold()') # pylint: disable=line-too-long
        except CodingErrorException:
            pass

    def test_get_threshold_nonexistent(self):
        try:
            self.plugin.get_threshold('nonexistent')
            raise Exception('failed to raise CodingErrorException for Threshold.get_threshold(nonexistent)')
        except CodingErrorException:
            pass

    # def test_get_threshold_none(self):
    #     self.plugin.set_threshold('setToNone', Threshold(None))
    #     try:
    #         self.plugin.get_threshold('setToNone')
    #         raise Exception('failed to raise CodingErrorException for Threshold.get_threshold(setToNone)')
    #     except CodingErrorException:
    #         pass

    def test_add_thresholds(self):
        self.plugin.add_thresholds()
        self.plugin.add_thresholds('test')

    def test_add_thresholds_nonstring_name_exception(self):
        try:
            self.plugin.add_thresholds(None)
            raise Exception('failed to raise exception when passing None to add_thresholds()')
        except CodingErrorException:
            pass

    def test_validate_threshold(self):
        self.assertEqual(self.plugin.validate_threshold('warning', threshold=4, optional=False), None)
        self.assertTrue(isinstance(self.plugin.get_threshold('warning'), Threshold))

    def test_validate_threshold_not_set_exception(self):
        try:
            self.assertEqual(self.plugin.validate_threshold('nonexistent'), None)
            raise Exception('failed to raise CodingErrorException when threshold is not set')
        except CodingErrorException:
            pass

    def test_validate_thresholds(self):
        self.plugin.validate_thresholds('test', 2, 3)
        self.plugin.check_threshold('test_warning', 1)

    # def test_validate_thresholds_nonexistent(self):
    #     try:
    #         self.plugin.validate_thresholds()
    #         raise Exception('failed to raise exception for validate_thresholds() when no thresholds set')
    #     except SystemExit as _:
    #         if _.code != 3:
    #             raise Exception('invalid exit code raised when thresholds are not set')

    def test_check_thresholds(self):
        try:
            self.plugin.check_thresholds(10, 'nonexistent')
            raise Exception('failed to raise exception for check_thresholds() when thresholds are not set')
        except CodingErrorException:
            pass

    def test_check_thresholds_nonstring_name(self):
        try:
            self.plugin.check_thresholds(10, None)
            raise Exception('failed to raise exception for check_thresholds() when name is None')
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
            self.plugin.status = 'invalidstatus'
        except CodingErrorException:
            pass

    def test_main_unhandled_exception(self):
        def raise_exception():
            raise Exception('this is an unhandled exception to be caught')
        self.plugin.run = raise_exception
        try:
            self.plugin.main()
            raise Exception('failed to exit on unhandled exception')
        except SystemExit as _:
            if _.code != 3:
                raise Exception('failed to exit with code 3 upon unhandled exception')
            # if _.message[:7] != 'UNKNOWN':
            #     raise Exception('unhandled exception failed to add UNKNOWN prefix')


    def test_critical_exit(self):
        try:
            self.plugin.critical()
            self.plugin.main()
            raise Exception('plugin failed to terminate')
        except SystemExit as _:
            if _.code != 2:
                raise Exception('NagiosPlugin failed to exit CRITICAL (2), got exit code {0} instead'.format(_.code))

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
