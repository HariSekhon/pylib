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
from harisekhon.utils import ERRORS, log
from harisekhon import NagiosPlugin

class test_NagiosPlugin(unittest.TestCase):

    # XXX: must prefix with test_ in order for the tests to be called

    # Not using assertRaises >= 2.7 and maintaining compatibility with Python 2.6 servers

    class SubNagiosPlugin(NagiosPlugin):
        def run(self):
            print("running SubNagiosPlugin()")

    # bails on unit2 discover -v / python -m unittest discover -v
    # because the -v switch trips optparse
    def test_SubNagiosPlugin(self):
        c = self.SubNagiosPlugin()

        self.assertTrue(c.is_unknown())
        c.status = 'OK'
        self.assertTrue(c.is_ok())
        self.assertFalse(c.is_warning())
        self.assertFalse(c.is_critical())
        self.assertFalse(c.is_unknown())
        c.unknown()
        self.assertTrue(c.is_unknown())
        self.assertFalse(c.is_ok())
        self.assertFalse(c.is_warning())
        self.assertFalse(c.is_critical())
        c.warning()
        self.assertTrue(c.is_warning())
        self.assertFalse(c.is_ok())
        self.assertFalse(c.is_critical())
        self.assertFalse(c.is_unknown())
        c.unknown()
        self.assertTrue(c.is_warning())
        self.assertFalse(c.is_ok())
        self.assertFalse(c.is_critical())
        self.assertFalse(c.is_unknown())
        c.critical()
        self.assertTrue(c.is_critical())
        self.assertFalse(c.is_ok())
        self.assertFalse(c.is_warning())
        self.assertFalse(c.is_unknown())
        c.warning()
        self.assertTrue(c.is_critical())
        self.assertFalse(c.is_ok())
        self.assertFalse(c.is_warning())
        self.assertFalse(c.is_unknown())

        try:
            c.critical()
            c.main()
        except SystemExit as _:
            if _.code != 2:
                raise Exception('NagiosPlugin failed to exit CRITICAL')

    def test_NagiosPlugin_abstract(self):
        try:
            c = NagiosPlugin() # pylint: disable=abstract-class-instantiated
            raise Exception('failed to raise a TypeError when attempting to instantiate abstract class NagiosPlugin')
        except TypeError as _:
            pass


def main():
    # increase the verbosity
    # verbosity Python >= 2.7
    #unittest.main(verbosity=2)
    log.setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(test_NagiosPlugin)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()
