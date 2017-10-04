#!/usr/bin/env python
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
# =========================================================================== #
#                           HariSekhon.CLI
# =========================================================================== #
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals

# import inspect
import logging
import os
import signal
import sys
import time
import traceback
#import traceback
from optparse import IndentedHelpFormatter
from optparse import OptionParser
from optparse import SUPPRESS_HELP
# Python 2.6+ only
from abc import ABCMeta, abstractmethod
import _curses
from blessings import Terminal
# inspect.getfile(inspect.currentframe()) # filename
# libdir = os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), '..')
libdir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(libdir)
# pylint: disable=wrong-import-position
import harisekhon
from harisekhon.utils import log, getenvs2, isBlankOrNone, isInt, isHost, isPort, isStr, isList, validate_int
from harisekhon.utils import CodingError, InvalidOptionException, ERRORS, qquit  # , die
from harisekhon.utils import get_topfile, get_file_docstring, get_file_github_repo, get_file_version, plural
from harisekhon.utils import CriticalError, WarningError, UnknownError

__author__ = 'Hari Sekhon'
__version__ = '0.9.1'


class CLI(object):
    """
    HariSekhon.CLI base class
    """
    __version__ = __version__
    # abstract class
    __metaclass__ = ABCMeta

    # class level attributes go here, can still use self
    # should only be 1 CLI per program

    # make sure to call this super constructor from subclasses if extending __init__():
    # Python 2.x
    # super(SubCLI, self).__init__()
    # Python 3.x
    # super().__init__()
    def __init__(self):
        # instance attributes, feels safer
        self.name = None
        self.default_host = None
        self.default_port = None
        self.default_user = None
        self.default_password = None
        self.options = None
        self.args = None
        self.__verbose_default = 0
        self.__verbose = self.__verbose_default
        self.__timeout_default = 10
        self.__timeout = None
        self.__timeout_max = 86400
        self.__total_run_time = time.time()
        self.topfile = get_topfile()
        self._docstring = get_file_docstring(self.topfile)
        if self._docstring:
            self._docstring = '\n' + self._docstring.strip() + '\n'
        if self._docstring is None:
            self._docstring = ''
        self._topfile_version = get_file_version(self.topfile)
        # this doesn't work in unit tests
        # if self._topfile_version:
        #     raise CodingError('failed to get topfile version - did you set a __version__ in top cli program?')
        self._cli_version = self.__version__
        self._utils_version = harisekhon.utils.__version__
        # returns 'python -m unittest' :-/
        # prog = os.path.basename(sys.argv[0])
        self._prog = os.path.basename(self.topfile)
        self._github_repo = get_file_github_repo(self.topfile)
        # _hidden attributes are shown in __dict__
        self.version = '{prog} version {topfile_version} '.format(prog=self._prog,
                                                                  topfile_version=self._topfile_version) + \
                       '=>  CLI version {cli_version} '.format(cli_version=self._cli_version) + \
                       '=>  Utils version {utils_version}'.format(utils_version=self._utils_version)
        self.usagemsg = 'Hari Sekhon{sep}{github_repo}\n\n{prog}\n{docstring}\n'.format(
            sep=' - ' if self._github_repo else '',
            github_repo=self._github_repo,
            prog=self._prog,
            docstring=self._docstring)
        self.usagemsg_short = 'Hari Sekhon%(_github_repo)s\n\n' % self.__dict__
        # set this in simpler client programs when you don't want to exclude
        # self.__parser = OptionParser(usage=self.usagemsg_short, version=self.version)
        # self.__parser = OptionParser(version=self.version)
        # will be added by default_opts later so that it's not annoyingly at the top of the option help
        # also this allows us to print full docstring for a complete description and not just the cli switches
        # description=self._docstring # don't want description printed for option errors
        width = os.getenv('COLUMNS', None)
        if not isInt(width) or not width:
            try:
                width = Terminal().width
            except _curses.error:
                width = 80
        # limit the width to 200 as we don't want super long strings going all the way across
        # 27" Thunderbolt displays of 364 columns etc.
        width = min(width, 200)
        self.__parser = OptionParser(add_help_option=False, formatter=IndentedHelpFormatter(width=width))
        # duplicate key error or duplicate options, sucks
        # self.__parser.add_option('-V', dest='version', help='Show version and exit', action='store_true')
        self.setup()

    def setup(self):
        pass

    def main(self):
        # DEBUG env var is picked up immediately in pylib utils, do not override it here if so
        if os.getenv('DEBUG'):
            log.setLevel(logging.DEBUG)
        if not log.isEnabledFor(logging.DEBUG) and \
           not log.isEnabledFor(logging.ERROR):  # do not downgrade logging either
            log.setLevel(logging.WARN)
        self.setup()
        try:
            self.add_options()
            self.add_default_opts()
        except InvalidOptionException as _:
            self.usage(_)
        try:
            self.__parse_args__()
            # broken
            # autoflush()
            # too late
            # os.environ['PYTHONUNBUFFERED'] = "anything"
            log.info('Hari Sekhon %s', self.version)
            log.info(self._github_repo)
            log.info('verbose level: %s (%s)', self.verbose, logging.getLevelName(log.getEffectiveLevel()))
            if self.timeout is not None:
                validate_int(self.timeout, 'timeout', 0, self.timeout_max)
                log.debug('setting timeout alarm (%s)', self.timeout)
                signal.signal(signal.SIGALRM, self.timeout_handler)
                signal.alarm(int(self.timeout))
            # if self.options.version:
            #     print(self.version)
            #     sys.exit(ERRORS['UNKNOWN'])
            self.process_options()
            self.process_args()
            try:
                self.run()
            except CriticalError as _:
                qquit('CRITICAL', _)
            except WarningError as _:
                qquit('WARNING', _)
            except UnknownError as _:
                qquit('UNKNOWN', _)
            self.__end__()
        except InvalidOptionException as _:
            if log.isEnabledFor(logging.DEBUG):
                log.debug(traceback.format_exc())
            self.usage(_)  # pragma: no cover
        except KeyboardInterrupt:
            # log.debug('Caught control-c...')
            print('Caught control-c...')  # pragma: no cover
        # except Exception as _:  # pylint: disable=broad-except
        #    exception_type = type(_).__name__
        #    if log.isEnabledFor(logging.DEBUG):
        #        log.debug("exception: '%s'", exception_type)
        #        log.debug(traceback.format_exc())
        #    die('{exception_type}: {msg}'.format(exception_type=exception_type, msg=_))

    def usage(self, msg='', status='UNKNOWN'):
        if msg:
            print('%s\n' % msg)
        else:
            print(self.usagemsg)
        self.__parser.print_help()
        qquit(status)

    def no_args(self):
        if self.args:
            self.usage('invalid non-switch arguments supplied on command line')

    # leave this as optional as some cli tools may not need to add additional options
    # @abstractmethod
    def add_options(self):
        pass

    def add_opt(self, *args, **kwargs):
        self.__parser.add_option(*args, **kwargs)

    def get_opt(self, name):
        if not isStr(name):
            raise CodingError('passed non-string as arg to CLI.get_opt()')
        if not self.is_option_defined(name):
            raise CodingError('{0} option not defined'.format(name))
        return getattr(self.options, name)

    def is_option_defined(self, name):
        return name in dir(self.options)

    def timeout_handler(self, signum, frame):  # pylint: disable=unused-argument
        # problem with this is that it'll print and then the exit exception will be caught and quit() printed again
        # raising a custom TimeoutException will need to be handled in main, but that would also likely print and be
        # re-caught and re-printed by NagiosPlugin
        #print('self timed out after %d second%s' % (self.timeout, plural(self.timeout)))
        #sys.exit(ERRORS['UNKNOWN'])
        # if doing die the same thing same will happen since die is a custom func which prints and then calls exit,
        # only exit would be caught
        qquit('UNKNOWN', 'self timed out after %d second%s' % (self.timeout, plural(self.timeout)))

    def disable_timeout(self):
        log.info('disabling timeout')
        self.timeout = 0
        signal.alarm(0)

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, secs):
        validate_int(secs, 'timeout', 0, self.timeout_max)
        #if not isInt(secs):
        #    raise CodingError('invalid timeout passed to set_timeout(), must be an integer representing seconds')
        log.debug('setting timeout to %s secs', secs)
        self.__timeout = int(secs)

    @property
    def timeout_default(self):
        return self.__timeout_default

    # None prevents --timeout switch becoming exposed, whereas 0 will allow
    @timeout_default.setter
    def timeout_default(self, secs):
        if secs is not None:
            if not isInt(secs):
                raise CodingError('invalid timeout passed assigned to timeout_default, ' +
                                  'must be an integer representing seconds')
            # validate_int(secs, 'timeout default', 0, self.__timeout_max )
            if self.timeout_max is not None and secs > self.timeout_max:
                raise CodingError('set default timeout > timeout max')
            secs = int(secs)
        log.debug('setting default timeout to %s secs', secs)
        self.__timeout_default = secs

    @property
    def timeout_max(self):
        return self.__timeout_max

    @timeout_max.setter
    def timeout_max(self, secs):
        if secs is not None and not isInt(secs):
            raise CodingError('invalid timeout max passed to set_timeout_max(), ' +
                              'must be an integer representing seconds')
        # leave this to be able to set max to any amount
        # validate_int(secs, 'timeout default', 0, self.__timeout_max )
        log.debug('setting max timeout to %s secs', secs)
        self.__timeout_max = secs

    @property
    def verbose(self):
        return self.__verbose

    @verbose.setter
    def verbose(self, arg):
        if not isInt(arg):
            raise CodingError('invalid verbose level passed to verbose(), must be an integer')
        log.debug('setting verbose to %s', arg)
        self.__verbose = int(arg)

    @property
    def verbose_default(self):
        return self.__verbose_default

    @verbose_default.setter
    def verbose_default(self, arg):
        if not isInt(arg):
            raise CodingError('invalid verbose level passed to verbose_default(), must be an integer')
        log.debug('setting default verbose to %s', arg)
        self.__verbose_default = int(arg)

    def add_default_opts(self):
        # This was a hack because main() was called more than once resulting in this being called more than once
        # use separate objects in future
        # for _ in ('--help', '--version', '--timeout', '--verbose', '--debug'):
        #     try:
        #         self.__parser.remove_option(_)
        #     except ValueError:
        #         pass

        if self.timeout_default is not None:
            # do not set default here, detect None and inherit $TIMEOUT if available,
            # set to self.timeout_default afterwards if still none in __parse_args__()
            self.add_opt('-t', '--timeout', help='Timeout in secs ($TIMEOUT, default: %d)' % self.timeout_default,
                         metavar='secs')  # , default=self.timeout_default)
        self.add_opt('-v', '--verbose', help='Verbose level ($VERBOSE=<int>, or use multiple -v, -vv, -vvv)',
                     action='count', default=self.__verbose_default)
        self.add_opt('-V', '--version', action='store_true', help='Show version and exit')
        # this would intercept and return exit code 0
        # self.__parser.add_option('-h', '--help', action='help')
        self.add_opt('-h', '--help', action='store_true', help='Show full help and exit')
        self.add_opt('-D', '--debug', action='store_true', help=SUPPRESS_HELP, default=bool(os.getenv("DEBUG")))

    def __parse_args__(self):
        try:
            (self.options, self.args) = self.__parser.parse_args()
        # I don't agree with zero exit code from OptionParser for help/usage,
        # and want UNKNOWN not CRITICAL(2) for switch mis-usage...
        except SystemExit:  # pragma: no cover
            sys.exit(ERRORS['UNKNOWN'])
        if self.options.help:  # pragma: no cover
            self.usage()
        if self.options.version:  # pragma: no cover
            print('%(version)s' % self.__dict__)
            sys.exit(ERRORS['UNKNOWN'])
        self.__parse_verbose__()
        self.__parse_timeout__()
        self.parse_args()
        return self.options, self.args

    def __parse_verbose__(self):
        self.verbose += int(self.get_opt('verbose'))
        env_verbose = os.getenv('VERBOSE')
        if isInt(env_verbose):
            if env_verbose > self.verbose:
                log.debug('environment variable $VERBOSE = %s, increasing verbosity', env_verbose)
                self.verbose = int(env_verbose)
        elif env_verbose is None:
            pass
        else:
            log.warning("$VERBOSE environment variable is not an integer ('%s')", env_verbose)

        if self.is_option_defined('quiet') and self.get_opt('quiet'):
            self.verbose = 0
        elif self.verbose > 2:
            log.setLevel(logging.DEBUG)
        elif self.verbose > 1:
            log.setLevel(logging.INFO)
        elif self.verbose > 0 and self._prog[0:6] != 'check_':
            log.setLevel(logging.WARN)
        if self.options.debug:
            log.setLevel(logging.DEBUG)  # pragma: no cover
            log.debug('enabling debug logging')
            if self.verbose < 3:
                self.verbose = 3

    def __parse_timeout__(self):
        # reset this to none otherwise unit tests fail to take setting from timeout_default
        # use __timeout to bypass the property setter checks
        self.__timeout = None
        if 'timeout' in dir(self.options):
            timeout = self.get_opt('timeout')
            if timeout is not None:
                log.debug('getting --timeout value %s', self.timeout)
                self.timeout = timeout
        if self.timeout is None:
            env_timeout = os.getenv('TIMEOUT')
            log.debug('getting $TIMEOUT value %s', env_timeout)
            if env_timeout is not None:
                log.debug('env_timeout is not None')
                if isInt(env_timeout):
                    log.debug("environment variable $TIMEOUT = '%s' and timeout not already set, setting timeout = %s",
                              env_timeout, env_timeout)
                    self.timeout = int(env_timeout)
                else:
                    log.warning("$TIMEOUT environment variable is not an integer ('%s')", env_timeout)
        if self.timeout is None:
            log.debug('timeout not set, using default timeout %s', self.timeout_default)
            self.timeout = self.timeout_default

    def parse_args(self):
        pass

    def process_args(self):
        pass

    def process_options(self):
        pass

    def add_hostoption(self, name=None, default_host=None, default_port=None):
        name2 = ''
        # if isList(name):
        #     name2 = '%s ' % name[0]
        # elif not isBlankOrNone(name):
        if name is None:
            name = ''
        # because can't reference name=self.name in def
        if not name:
            # pylint will fail if you use these directly as it tries to resolve them
            if 'name' in self.__dict__ and getattr(self, 'name'):
                name = getattr(self, 'name')
            elif 'software' in self.__dict__ and getattr(self, 'software'):
                name = getattr(self, 'software')
        if not default_host and 'default_host' in self.__dict__ and getattr(self, 'default_host'):
            default_host = getattr(self, 'default_host')
        if not default_port and 'default_port' in self.__dict__ and getattr(self, 'default_port'):
            default_port = getattr(self, 'default_port')
        if not isBlankOrNone(name):
            if isList(name):
                name2 = '{0} '.format(name[0])
            else:
                name2 = '{0} '.format(name)
        if default_host is not None and not isHost(default_host):
            raise CodingError('invalid default host supplied to add_hostoption()')
        if default_port is not None and not isPort(default_port):
            raise CodingError('invalid default port supplied to add_hostoption()')
        (host_envs_help, default_host) = getenvs2(my_vars='HOST', default=default_host, name=name)
        (port_envs_help, default_port) = getenvs2(my_vars='PORT', default=default_port, name=name)
        self.add_opt('-H', '--host', dest='host', help='%sHost (%s)' % (name2, host_envs_help), default=default_host)
        self.add_opt('-P', '--port', dest='port', help='%sPort (%s)' % (name2, port_envs_help), default=default_port)

    def add_useroption(self, name=None, default_user=None, default_password=None):
        name2 = ''
        if name is None:
            name = ''
        # because can't reference name=self.name in def
        if not name:
            if 'name' in self.__dict__ and getattr(self, 'name'):
                name = getattr(self, 'name')
            elif 'software' in self.__dict__ and getattr(self, 'software'):
                name = getattr(self, 'software')
        if not default_user and 'default_user' in self.__dict__ and getattr(self, 'default_user'):
            default_user = getattr(self, 'default_user')
        if not default_password and 'default_password' in self.__dict__ and getattr(self, 'default_password'):
            default_password = getattr(self, 'default_password')
        if not isBlankOrNone(name):
            if isList(name):
                name2 = '{0} '.format(name[0])
            else:
                name2 = '{0} '.format(name)
        (user_envs_help, default_user) = getenvs2(['USERNAME', 'USER'], default_user, name)
        (pw_envs_help, default_password) = getenvs2('PASSWORD', default_password, name)
        self.add_opt('-u', '--user', dest='user',
                     help='%sUsername (%s)' % (name2, user_envs_help), default=default_user)
        self.add_opt('-p', '--password', dest='password',
                     help='%sPassword (%s)' % (name2, pw_envs_help), default=default_password)

    def add_ssl_option(self):
        self.add_opt('-S', '--ssl', action='store_true', default=False, help='Use SSL')

    def add_quietoption(self):
        self.add_opt('-q', '--quiet', action='store_true', help='Quiet mode')

    @abstractmethod
    def run(self):  # pragma: no cover
        raise CodingError('running HariSekhon.CLI().run() - this should be abstract and non-runnable!'
                          ' You should have overridden this run() method in the client code')

    def end(self):
        pass

    def __end__(self):
        self.__total_run_time = time.time() - self.__total_run_time
        self.end()
