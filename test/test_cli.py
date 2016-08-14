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
#                   PyUnit Tests for HariSekhon.CLI
# ============================================================================ #
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals

import logging
import os
import sys
import time
import unittest
from optparse import OptionConflictError
# inspect.getfile(inspect.currentframe()) # filename
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(libdir)
# pylint: disable=wrong-import-position
from harisekhon.utils import CodingError, InvalidOptionException, log
from harisekhon import CLI


class CLITester(unittest.TestCase):

    # must prefix with test_ in order for the tests to be called

    # Not using assertRaises >= 2.7 and maintaining compatibility with Python 2.6 servers

    myDict = {'one': 1, 'two': 2, 'three':3}

    class SubCLI(CLI):
        """ test """
        def run(self):
            print("running SubCLI()")

    def setUp(self):
        self.cli = self.SubCLI()
        self.cli.timeout = 30

    # bails on unit2 discover -v / python -m unittest discover -v
    # because the -v switch trips optparse
        # self.cli.set_default_port(80)
        # try:
        #     self.cli.set_default_port('a')
        #     raise Exception('failed to throw CodingError when sending invalid port to set_default_port()')
        # except CodingError:
        #     pass

    def test_add_hostoption(self):
        self.cli.add_hostoption(name='Ambari', default_host='localhost', default_port=8080)

    def test_add_useroption(self):
        self.cli.add_useroption(name='Ambari', default_user='admin', default_password='mysecret')

    def test_add_hostoption_dup_exception(self):
        try:
            self.cli.add_hostoption()
            self.cli.add_hostoption()
            raise Exception('failed to throw OptionConflictError from optparse OptionParser ' +
                            'when duplicating add_hostoption')
        except OptionConflictError as _:
            pass

    def test_add_hostoption_port_error_exception(self):
        try:
            self.cli.add_hostoption(default_port='error')
            raise Exception('failed to throw CodingError when sending invalid port to add_hostoption')
        except CodingError as _:
            pass

    def test_useroption_dup_exception(self):
        try:
            self.cli.add_useroption()
            self.cli.add_useroption()
            raise Exception('failed to throw OptionConflictError from optparse OptionParser ' +
                            'when duplicating add_useroption')
        except OptionConflictError as _:
            pass

    # set_verbose() won't work because parse args resets it so we change verbose_default instead
    def test_verbose_default_setters_getters(self):
        self.cli.verbose_default = 2
        self.assertEqual(self.cli.verbose_default, 2)
        self.cli.main()
        self.cli.__init__()

    def test_main_and_get_opt_timeout(self):
        self.cli.main()
        self.assertEqual(self.cli.get_opt('timeout'), self.cli.options.timeout)


    def test_reinit_main(self):
        self.cli.__init__()
        self.cli.verbose_default = 3
        self.cli.main()

    def test_reinit_set_verbose(self):
        self.cli.__init__()
        self.cli.verbose = 0
        self.assertEqual(self.cli.verbose, 0)

    def test_set_verbose_none_exception(self):
        try:
            self.cli.verbose = None
            raise Exception('failed to raise CodingError when calling verbose = None')
        except CodingError:
            pass

    def test_set_verbose_default_none_exception(self):
        try:
            self.cli.verbose_default = None
            raise Exception('failed to raise CodingError when calling verbose_default = None')
        except CodingError:
            pass

        # would need to inject self.cli.options.help / self.cli.options.version to trigger those code branches
        # try:
        #     self.cli.main()
        #     raise Exception('failed to raise CodingError when calling main() after setting self.options.help') # pylint: disable=line-too-long
        # except SystemExit as _:
        #     if _.code != 3:
        #         raise Exception('wrong exit code != 3 when triggering usage via self.options.help')

    def test_usage(self):
        self.cli.__init__()
        try:
            self.cli.usage()
            raise Exception('failed to exit on CLI.usage()')
        except SystemExit as _:
            if _.code != 3:
                raise Exception('wrong exit code %s != 3 when exiting usage() from base class CLI' % _.code)

    def test_usage_message(self):
        try:
            self.cli.usage('test message')
            raise Exception('failed to exit on CLI.usage(test message)')
        except SystemExit as _:
            if _.code != 3:
                raise Exception('wrong exit code != 3 when exiting usage(test message) from base class CLI')

    #def test_parser_version(self):
    #    print('parser version = %s' % self.cli.__parser.get_version())
        # I don't populate version in OptionParser now as it creates the switch too high in the option order
        # self.assertTrue(re.search(' version (?:None|%(version_regex)s), CLI version %(version_regex)s, ' +
        #                           'Utils version %(version_regex)s' % globals(), self.cli.__parser.get_version()))

    def test_set_timeout(self):
        try:
            self.cli.timeout = None
            raise Exception('failed to raise CodingError for CLI.timeout = None')
        except CodingError:
            pass
        self.cli.main()

    def test_disable_timeout(self):
        self.cli.timeout = 30
        self.cli.disable_timeout()
        self.assertEquals(self.cli.timeout, 0)

    def test_set_timeout_alpha_exception(self):
        self.cli.__init__()
        try:
            self.cli.timeout = 'a'
            raise Exception('failed to raise CodingError for CLI.timeout = a')
        except CodingError:
            pass

    def test_set_timeout_max_set_timeout_exception(self):
        self.cli.timeout_max = 5
        try:
            self.cli.timeout = 6
            raise Exception('failed to raise InvalidOptionException when setting timeout higher than max')
        except InvalidOptionException:
            pass

    def test_set_timeout_max_alpha_exception(self):
        try:
            self.cli.timeout_max = 'a'
            raise Exception('failed to raise CodingError for timeout_max = a')
        except CodingError:
            pass

    #def test_set_timeout_max(self):
    #    self.cli.timeout_max = None

    def test_set_timeout_default(self):
        cli = self.SubCLI()
        cli.timeout_max = None
        cli.timeout_default = 999999
        cli.timeout_default = 9
        self.assertEqual(cli.timeout_default, 9)
        cli.timeout_default = None

    def test_set_timeout_max_set_timeout_default_exception(self):
        self.cli.timeout_max = 10
        try:
            self.cli.timeout_default = 11
            raise Exception('failed to raise exception on CLI.timeout_default > max')
        except CodingError:
            pass

    def test_timeout_default_max_normal(self):
        cli = self.SubCLI()
        cli.timeout_default = None
        self.assertEqual(cli.timeout_default, None)
        cli.timeout_max = 30
        cli.timeout = 22
        self.assertEqual(cli.timeout, 22)
        cli.main()

    def test_timeout_default_alpha_exception(self):
        self.cli.__init__()
        try:
            self.cli.timeout_default = 'a'
            raise Exception('failed to raise CodingError for CLI.timeout_default = a')
        except CodingError:
            pass

    def test_timeout_default_sleep_exception(self):
        self.cli.timeout_default = 1
        self.cli.run = lambda: time.sleep(3)
        try:
            self.cli.main()
            raise Exception('failed to self-timeout after 1 second')
        except SystemExit as _:
            if _.code != 3:
                raise Exception('wrong exit code != 3 when self timing out CLI')

    def test_invalidoptionexception(self):
        self.cli.__init__()

        def raise_invalidoptionexception():
            raise InvalidOptionException('test')
        self.cli.add_options = raise_invalidoptionexception
        try:
            self.cli.main()
        except SystemExit as _:
            if _.code != 3:
                raise Exception('failed to trap and re-throw InvalidOptionException in CLI main as SystemExit (usage)')

    def test_no_args_exception(self):
        self.cli.__init__()

        try:
            self.cli.args = "blah"
            self.cli.no_args()
            raise Exception('failed to exit via no_args()')
        except SystemExit as _:
            if _.code != 3:
                raise Exception('wrong exit code for no_args()')

    def test_verbose_env(self):
        os.environ['VERBOSE'] = '3'
        cli = self.SubCLI()
        cli.main()

    def test_verbose_env_invalid(self):
        os.environ['VERBOSE'] = 'a'
        cli = self.SubCLI()
        cli.main()

        # self.cli._env_var('', 'test')
        # try:
        #     self.cli._env_var(None, 1)
        #     raise Exception('failed to raise a CodingError in _env_var when sending integer as var')
        # except CodingError as _:
        #     pass
        #
        # try:
        #     self.cli._env_var('test', None)
        #     raise Exception('failed to raise a CodingError in _env_var when sending None as var')
        # except CodingError as _:
        #     pass
        #
        # try:
        #     self.cli._env_var('test', ' ')
        #     raise Exception('failed to raise a CodingError in _env_var when sending blank as var')
        # except CodingError as _:
        #     pass
        #
        # try:
        #     self.cli._env_var(None, 'test')
        #     raise Exception('failed to raise a CodingError in _env_var when sending None name')
        # except CodingError as _:
        #     pass
        #
        # try:
        #     self.cli.env_vars('test', ' ')
        #     raise Exception('failed to raise a CodingError in env_vars() when sending blank var')
        # except CodingError as _:
        #     pass
        #
        # try:
        #     self.cli.env_vars(None, 'test')
        #     raise Exception('failed to raise a CodingError in env_vars() when sending None as name var')
        # except CodingError as _:
        #     pass
        #
        # try:
        #     self.cli.env_vars('test', ['test', None])
        #     raise Exception('failed to raise a CodingError in env_vars() when sending array with blank var')
        # except CodingError as _:
        #     pass
        #
        # try:
        #     self.cli.env_vars('test', self.myDict)
        #     raise Exception('failed to raise a CodingError in env_vars() when sending dict for var')
        # except CodingError as _:
        #     pass

    def test_cli_abstract(self): # pylint: disable=no-self-use
        try:
            CLI() # pylint: disable=abstract-class-instantiated
            raise Exception('failed to raise a TypeError when attempting to instantiate abstract class CLI')
        except TypeError as _:
            # print('caught TypeError when running CLI.main(): %s' % _)
            pass
        # except CodingError as _:
        #     if not re.search('abstract', str(_)):
        #         raise Exception('raised CodingError from CLI.main() but message mismatch')
        # disabled abstract enforcement as it's Python 2.6+ only
        # but base class exits 3 in run() so can catch that too
        # except SystemExit as _:
        #     if _.code != 3:
        #         raise Exception('wrong exit code != 3 when exiting main() from base class CLI')


def main():
    # increase the verbosity
    # verbosity Python >= 2.7
    #unittest.main(verbosity=2)
    log.setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(CLITester)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()
