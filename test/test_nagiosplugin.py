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
from harisekhon import NagiosPlugin # pylint: disable=wrong-import-position

class NagiosPluginTester(unittest.TestCase):

    # must prefix with test_ in order for the tests to be called

    # Not using assertRaises >= 2.7 and maintaining compatibility with Python 2.6 servers

    class SubNagiosPlugin(NagiosPlugin):
        def run(self):
            print("running SubNagiosPlugin()")


    def test_subnagiosplugin(self):
        obj = self.SubNagiosPlugin()

        self.assertEqual(obj.validate_threshold(4, optional=True), None)

        self.assertTrue(obj.is_unknown())
        obj.ok()
        self.assertTrue(obj.is_ok())
        self.assertFalse(obj.is_warning())
        self.assertFalse(obj.is_critical())
        self.assertFalse(obj.is_unknown())
        obj.unknown()
        self.assertTrue(obj.is_unknown())
        self.assertFalse(obj.is_ok())
        self.assertFalse(obj.is_warning())
        self.assertFalse(obj.is_critical())
        obj.warning()
        self.assertTrue(obj.is_warning())
        self.assertFalse(obj.is_ok())
        self.assertFalse(obj.is_critical())
        self.assertFalse(obj.is_unknown())
        obj.unknown()
        self.assertTrue(obj.is_warning())
        self.assertFalse(obj.is_ok())
        self.assertFalse(obj.is_critical())
        self.assertFalse(obj.is_unknown())
        obj.critical()
        self.assertTrue(obj.is_critical())
        self.assertFalse(obj.is_ok())
        self.assertFalse(obj.is_warning())
        self.assertFalse(obj.is_unknown())
        obj.warning()
        self.assertTrue(obj.is_critical())
        self.assertFalse(obj.is_ok())
        self.assertFalse(obj.is_warning())
        self.assertFalse(obj.is_unknown())

        try:
            obj.set_status('invalidstatus')
        except CodingErrorException:
            pass

        try:
            obj.critical()
            obj.main()
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
