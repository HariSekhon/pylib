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
#                   PyUnit Tests for HariSekhon.CLI
# ============================================================================ #
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os
import sys
import time
import unittest
from optparse import OptionConflictError
# inspect.getfile(inspect.currentframe()) # filename
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(libdir)
from harisekhon.utils import CodingErrorException, InvalidOptionException, log # pylint: disable=wrong-import-position
from harisekhon import CLI # pylint: disable=wrong-import-position

class CLITester(unittest.TestCase):

    # must prefix with test_ in order for the tests to be called

    # Not using assertRaises >= 2.7 and maintaining compatibility with Python 2.6 servers

    myDict = {'one': 1, 'two': 2, 'three':3}

    class SubCLI(CLI):
        def run(self):
            print("running SubCLI()")

    # bails on unit2 discover -v / python -m unittest discover -v
    # because the -v switch trips optparse
    def test_subcli(self):
        obj = self.SubCLI()
        # obj.set_default_port(80)
        # try:
        #     obj.set_default_port('a')
        #     raise Exception('failed to throw CodingErrorException when sending invalid port to set_default_port()')
        # except CodingErrorException:
        #     pass
        obj.add_hostoption(name='Ambari', default_host='localhost', default_port=8080)
        obj.add_useroption(name='Ambari', default_user='admin', default_password='mysecret')
        try:
            obj.add_hostoption()
            raise Exception('failed to throw OptionConflictError from optparse OptionParser ' +
                            'when duplicating add_hostoption')
        except OptionConflictError as _:
            pass
        try:
            obj.add_hostoption(default_port='error')
            raise Exception('failed to throw CodingErrorException when sending invalid port to add_hostoption')
        except CodingErrorException as _:
            pass
        try:
            obj.add_useroption()
            raise Exception('failed to throw OptionConflictError from optparse OptionParser ' +
                            'when duplicating add_useroption')
        except OptionConflictError as _:
            pass

        # set_verbose() won't work because parse args resets it so we change verbose_default instead
        obj.main()
        obj.set_verbose_default(2)
        self.assertEqual(obj.get_verbose_default(), 2)
        obj.main()
        obj.set_verbose_default(3)
        obj.main()
        obj.set_verbose(0)
        self.assertEqual(obj.get_verbose(), 0)
        try:
            obj.set_verbose(None)
            raise Exception('failed to raise CodingErrorException when calling set_verbose(None)')
        except CodingErrorException:
            pass
        try:
            obj.set_verbose_default(None)
            raise Exception('failed to raise CodingErrorException when calling set_verbose_default(None)')
        except CodingErrorException:
            pass

        # would need to inject obj.options.help / obj.options.version to trigger those code branches
        # try:
        #     obj.main()
        #     raise Exception('failed to raise CodingErrorException when calling main() after setting self.options.help') # pylint: disable=line-too-long
        # except SystemExit as _:
        #     if _.code != 3:
        #         raise Exception('wrong exit code != 3 when triggering usage via self.options.help')

        try:
            obj.usage()
            raise Exception('failed to exit on CLI.usage()')
        except SystemExit as _:
            if _.code != 3:
                raise Exception('wrong exit code %s != 3 when exiting usage() from base class CLI' % _.code)

        try:
            obj.usage('test message')
            raise Exception('failed to exit on CLI.usage(test message)')
        except SystemExit as _:
            if _.code != 3:
                raise Exception('wrong exit code != 3 when exiting usage(test message) from base class CLI')

        print('parser version = %s' % obj.parser.get_version())
        # I don't populate version in OptionParser now as it creates the switch too high in the option order
        # self.assertTrue(re.search(' version (?:None|%(version_regex)s), CLI version %(version_regex)s, ' +
        #                           'Utils version %(version_regex)s' % globals(), obj.parser.get_version()))

        try:
            obj.set_timeout(None)
            raise Exception('failed to raise CodingErrorException for CLU.set_timeout(None)')
        except CodingErrorException:
            pass
        obj.main()

        obj.set_timeout(22)
        self.assertEqual(obj.get_timeout(), 22)
        try:
            obj.set_timeout('a')
            raise Exception('failed to raise CodingErrorException for CLU.set_timeout(a)')
        except CodingErrorException:
            pass

        obj.set_timeout_max(5)
        try:
            obj.set_timeout(6)
            raise Exception('failed to raise InvalidOptionException when setting timeout higher than max')
        except InvalidOptionException:
            pass
        try:
            obj.set_timeout_max('a')
            raise Exception('failed to raise CodingErrorException for set_timeout_max(a)')
        except CodingErrorException:
            pass
        obj.set_timeout_max(None)
        obj.set_timeout_default(999999)
        obj.set_timeout_default(9)
        self.assertEqual(obj.get_timeout_default(), 9)
        obj.set_timeout_default(None)
        obj.set_timeout_max(10)
        try:
            obj.set_timeout_default(11)
            raise Exception('failed to raise exception on CLI.set_timeout_default() > max')
        except CodingErrorException:
            pass
        self.assertEqual(obj.get_timeout_default(), None)
        obj.main()
        try:
            obj.set_timeout_default('a')
            raise Exception('failed to raise CodingErrorException for CLI.set_timeout_default(a)')
        except CodingErrorException:
            pass
        obj.set_timeout_default(1)
        obj.run = lambda: time.sleep(3)
        try:
            obj.main()
            raise Exception('failed to self-timeout after 1 second')
        except SystemExit as _:
            if _.code != 3:
                raise Exception('wrong exit code != 3 when self timing out CLI')

        def raise_invalidoptionexception():
            raise InvalidOptionException('test')
        obj.add_options = raise_invalidoptionexception
        try:
            obj.main()
        except SystemExit as _:
            if _.code != 3:
                raise Exception('failed to trap and re-throw InvalidOptionException in CLI main as SystemExit (usage)')

        # obj._env_var('', 'test')
        # try:
        #     obj._env_var(None, 1)
        #     raise Exception('failed to raise a CodingErrorException in _env_var when sending integer as var')
        # except CodingErrorException as _:
        #     pass
        #
        # try:
        #     obj._env_var('test', None)
        #     raise Exception('failed to raise a CodingErrorException in _env_var when sending None as var')
        # except CodingErrorException as _:
        #     pass
        #
        # try:
        #     obj._env_var('test', ' ')
        #     raise Exception('failed to raise a CodingErrorException in _env_var when sending blank as var')
        # except CodingErrorException as _:
        #     pass
        #
        # try:
        #     obj._env_var(None, 'test')
        #     raise Exception('failed to raise a CodingErrorException in _env_var when sending None name')
        # except CodingErrorException as _:
        #     pass
        #
        # try:
        #     obj.env_vars('test', ' ')
        #     raise Exception('failed to raise a CodingErrorException in env_vars() when sending blank var')
        # except CodingErrorException as _:
        #     pass
        #
        # try:
        #     obj.env_vars(None, 'test')
        #     raise Exception('failed to raise a CodingErrorException in env_vars() when sending None as name var')
        # except CodingErrorException as _:
        #     pass
        #
        # try:
        #     obj.env_vars('test', ['test', None])
        #     raise Exception('failed to raise a CodingErrorException in env_vars() when sending array with blank var')
        # except CodingErrorException as _:
        #     pass
        #
        # try:
        #     obj.env_vars('test', self.myDict)
        #     raise Exception('failed to raise a CodingErrorException in env_vars() when sending dict for var')
        # except CodingErrorException as _:
        #     pass

    def test_cli_abstract(self): # pylint: disable=no-self-use
        try:
            CLI() # pylint: disable=abstract-class-instantiated
            raise Exception('failed to raise a TypeError when attempting to instantiate abstract class CLI')
        except TypeError as _:
            # print('caught TypeError when running CLI.main(): %s' % _)
            pass
        # except CodingErrorException as _:
        #     if not re.search('abstract', str(_)):
        #         raise Exception('raised CodingErrorException from CLI.main() but message mismatch')
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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCLI)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()
