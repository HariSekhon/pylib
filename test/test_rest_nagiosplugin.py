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
#                   PyUnit Tests for HariSekhon.RestNagiosPlugin
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
from harisekhon.utils import log
from harisekhon.nagiosplugin import RestNagiosPlugin

class RestNagiosPluginTester(unittest.TestCase):

    # must prefix with test_ in order for the tests to be called

    # Not using assertRaises >= 2.7 and maintaining compatibility with Python 2.6 servers

    class SubRestNagiosPlugin(RestNagiosPlugin):
        def __init__(self):
            # Python 2.x
            #RestNagiosPlugin.__init__(self)
            super(RestNagiosPluginTester.SubRestNagiosPlugin, self).__init__()
            # Python 3.x
            # super().__init__()
            self.name = 'test'
            self.default_host = 'google.com'
            self.default_port = 80
            self.auth = False
        def parse(self, req):
            self.msg = 'unittest message'

    #def setUp(self):
    #    self.plugin = self.SubRestNagiosPlugin()

    def test_exit_0(self):
        plugin = self.SubRestNagiosPlugin()
        try:
            plugin.main()
            raise Exception('RestSub plugin failed to terminate')
        except SystemExit as _:
            if _.code != 0:
                raise Exception('RestNagiosPlugin failed to exit OK (0), got exit code {0} instead'
                                .format(_.code))

    def test_exit_2(self):
        plugin = self.SubRestNagiosPlugin()
        plugin.default_host = 'localhost'
        plugin.default_port = 65535
        plugin.auth = 'optional'
        try:
            plugin.main()
            raise Exception('RestSub plugin failed to terminate')
        except SystemExit as _:
            if _.code != 2:
                raise Exception('RestNagiosPlugin failed to exit CRITICAL (2), got exit code {0} instead'
                                .format(_.code))

    def test_exit_3(self):
        plugin = self.SubRestNagiosPlugin()
        plugin.auth = True
        try:
            plugin.main()
            raise Exception('RestSub plugin failed to terminate')
        except SystemExit as _:
            if _.code != 3:
                raise Exception('RestNagiosPlugin failed to exit UNKNOWN (3), got exit code {0} instead'
                                .format(_.code))

    def test_plugin_abstract(self):  # pylint: disable=no-self-use
        try:
            RestNagiosPlugin()  # pylint: disable=abstract-class-instantiated
            #raise Exception('failed to raise a TypeError when attempting to instantiate abstract class ' +
            #                'RestNagiosPlugin')
        #except TypeError:
        except SystemExit as _:
            if _.code != 0:
                raise Exception('RestNagiosPlugin failed to exit UNKNOWN (3), got exit code {0} instead'
                                .format(_.code))


def main():
    # increase the verbosity
    # verbosity Python >= 2.7
    #unittest.main(verbosity=2)
    log.setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(RestNagiosPluginTester)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()
