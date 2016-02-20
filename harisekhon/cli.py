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
from optparse import OptionParser
from optparse import SUPPRESS_HELP
# Python 2.6+ only
from abc import ABCMeta, abstractmethod
# inspect.getfile(inspect.currentframe()) # filename
# libdir = os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), '..')
libdir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(libdir)
import harisekhon # pylint: disable=wrong-import-position
from harisekhon.utils import log, getenvs2, isBlankOrNone, isInt, isPort, isStr, validate_int, plural  # pylint: disable=wrong-import-position
from harisekhon.utils import CodingErrorException, InvalidOptionException, ERRORS, qquit             # pylint: disable=wrong-import-position
from harisekhon.utils import get_topfile, get_file_docstring, get_file_github_repo, get_file_version # pylint: disable=wrong-import-position

__author__ = 'Hari Sekhon'
__version__ = '0.8.0'

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
        self.options = None
        self.args = None
        self.__verbose = None
        self.__verbose_default = 0
        self.__timeout = None
        self.__timeout_default = 10
        self.__timeout_max = 86400
        self.topfile = get_topfile()
        # this gets utrunner.py in PyCharm and runpy.py from unittest
        if os.path.basename(self.topfile) in ('utrunner.py', 'runpy.py'):
            self.topfile = __file__
        #print('topfile = %s' % self.topfile)
        self._docstring = get_file_docstring(self.topfile)
        if self._docstring:
            self._docstring = '\n' + self._docstring.strip() + '\n'
        if self._docstring is None:
            self._docstring = ''
        self._topfile_version = get_file_version(self.topfile)
        # this doesn't work in unit tests
        # if not self._topfile_version:
        #     raise CodingErrorException('failed to get topfile version - did you set a __version__ in top cli program?') # pylint: disable=line-too-long
        self._cli_version = self.__version__
        self._utils_version = harisekhon.utils.__version__
        # returns 'python -m unittest' :-/
        # prog = os.path.basename(sys.argv[0])
        self._prog = os.path.basename(self.topfile)
        self._github_repo = get_file_github_repo(self.topfile)
        # if not self.github_repo:
        #     self.github_repo = 'https://github.com/harisekhon/pytools'
        if self._github_repo:
            self._github_repo = ' - ' + self._github_repo
        # _hidden attributes are shown in __dict__
        self.version = '%(_prog)s version %(_topfile_version)s ' % self.__dict__ + \
                       '=>  CLI version %(_cli_version)s  =>  Utils version %(_utils_version)s' % self.__dict__
        self.usagemsg = 'Hari Sekhon%(_github_repo)s\n\n%(_prog)s version %(_topfile_version)s\n%(_docstring)s\n' \
                        % self.__dict__
        self.usagemsg_short = 'Hari Sekhon%(_github_repo)s\n\n' % self.__dict__
        # set this in simpler client programs when you don't want to exclude
        # self.__parser = OptionParser(usage=self.usagemsg_short, version=self.version)
        # self.__parser = OptionParser(version=self.version)
        # will be added by default_opts later so that it's not annoyingly at the top of the option help
        # also this allows us to print full docstring for a complete description and not just the cli switches
        self.__parser = OptionParser(add_help_option=False) # description=self._docstring # don't want description printed for option errors
        # duplicate key error or duplicate options, sucks
        # self.__parser.add_option('-V', dest='version', help='Show version and exit', action='store_true')
        self.setup()

    def setup(self):
        pass

    def main(self):
        log.debug('running main()')
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
            # move this to NagiosPlugin class
            # if re.match('check_', prog):
            #     sys.stderr = sys.stdin
            # careful causes bad file descriptor for die(), jython_only() and printerr() unit tests
            # sys.stderr = sys.stdin
            log.setLevel(logging.WARN)
            self.verbose = self.get_opt('verbose')
            if self.verbose > 2:
                log.setLevel(logging.DEBUG)
            elif self.verbose > 1:
                log.setLevel(logging.INFO)
            if self.options.debug:
                log.setLevel(logging.DEBUG) # pragma: no cover
            log.info('verbose level: %s', self.verbose)
            if self.timeout is not None:
                validate_int(self.timeout, 'timeout', 0, self.timeout_max)
                log.debug('setting timeout alarm (%s)', self.timeout)
                signal.signal(signal.SIGALRM, self.timeout_handler)
                signal.alarm(int(self.timeout))
            # if self.options.version:
            #     print(self.version)
            #     sys.exit(ERRORS['UNKNOWN'])
            self.run()
            self.__end__()
        except InvalidOptionException as _:
            self.usage(_) # pragma: no cover
        except KeyboardInterrupt:
            # log.debug('Caught control-c...')
            print('Caught control-c...') # pragma: no cover

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
            raise CodingErrorException('passed non-string as arg to CLI.get_opt()')
        if not self.is_option_defined(name):
            raise CodingErrorException('{0} option not defined'.format(name))
        return getattr(self.options, name)

    def is_option_defined(self, name):
        return name in dir(self.options)

    def timeout_handler(self, signum, frame): # pylint: disable=unused-argument
        qquit('UNKNOWN', 'self timed out after %d second%s' % (self.timeout, plural(self.timeout)))

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, secs):
        if not isInt(secs):
            raise CodingErrorException('invalid timeout passed to set_timeout(), must be an integer representing seconds') # pylint: disable=line-too-long
        validate_int(secs, 'timeout', 0, self.timeout_max)
        log.debug('setting timeout to %s secs', secs)
        self.__timeout = secs

    @property
    def timeout_default(self):
        return self.__timeout_default

    # None prevents --timeout switch becoming exposed, whereas 0 will allow
    @timeout_default.setter
    def timeout_default(self, secs):
        if secs is not None:
            if not isInt(secs):
                raise CodingErrorException('invalid timeout passed to timeout_default = , must be an integer representing seconds') # pylint: disable=line-too-long
            # validate_int(secs, 'timeout default', 0, self.__timeout_max )
            if self.timeout_max is not None and secs > self.timeout_max:
                raise CodingErrorException('set default timeout > timeout max')
        log.debug('setting default timeout to %s secs', secs)
        self.__timeout_default = secs

    @property
    def timeout_max(self):
        return self.__timeout_max

    @timeout_max.setter
    def timeout_max(self, secs):
        if secs is not None and not isInt(secs):
            raise CodingErrorException('invalid timeout max passed to set_timeout_max(), must be an integer representing seconds') # pylint: disable=line-too-long
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
            raise CodingErrorException('invalid verbose level passed to verbose(), must be an integer')
        log.debug('setting verbose to %s', arg)
        self.__verbose = int(arg)

    @property
    def verbose_default(self):
        return self.__verbose_default

    @verbose_default.setter
    def verbose_default(self, arg):
        if not isInt(arg):
            raise CodingErrorException('invalid verbose level passed to verbose_default(), must be an integer')
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

        if self.__timeout_default is not None:
            self.add_opt('-t', '--timeout', help='Timeout in secs (default: %d)' % self.__timeout_default,
                         metavar='secs', default=self.__timeout_default)
        self.add_opt('-v', '--verbose', help='Verbose mode (-v, -vv, -vvv)', action='count',
                     default=self.__verbose_default)
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
        except SystemExit: # pragma: no cover
            sys.exit(ERRORS['UNKNOWN'])
        if self.options.help: # pragma: no cover
            self.usage()
        if self.options.version: # pragma: no cover
            print('%(version)s' % self.__dict__)
            sys.exit(ERRORS['UNKNOWN'])
        if 'timeout' in dir(self.options):
            self.timeout = self.get_opt('timeout')
        env_verbose = os.getenv('VERBOSE')
        if isInt(env_verbose):
            if env_verbose > self.verbose:
                log.debug('environment variable $VERBOSE = %s, increasing verbosity', env_verbose)
                self.verbose = env_verbose
        elif env_verbose is None:
            pass
        else:
            log.warn("$VERBOSE environment variable is not an integer ('%s')", env_verbose)
        self.parse_args()
        self.process_args()
        return self.options, self.args

    def parse_args(self):
        pass

    def process_args(self):
        pass

    def add_hostoption(self, name='', default_host=None, default_port=None):
        name2 = ''
        # if isList(name):
        #     name2 = '%s ' % name[0]
        # elif not isBlankOrNone(name):
        if not isBlankOrNone(name):
            name2 = '%s ' % name
        if default_port is not None:
            # assert isPort(default_port)
            if not isPort(default_port):
                raise CodingErrorException('invalid default port supplied to add_hostoption()')
        (host_envs, default_host) = getenvs2('HOST', default_host, name)
        (port_envs, default_port) = getenvs2('PORT', default_port, name)
        self.add_opt('-H', '--host', dest='host', help='%sHost (%s)' % (name2, host_envs), default=default_host)
        self.add_opt('-P', '--port', dest='port', help='%sPort (%s)' % (name2, port_envs), default=default_port)

    def add_useroption(self, name='', default_user=None, default_password=None):
        name2 = ''
        if not isBlankOrNone(name):
            name2 = "%s " % name
        (user_envs, default_user) = getenvs2(['USERNAME', 'USER'], default_user, name)
        (pw_envs, default_password) = getenvs2('PASSWORD', default_password, name)
        self.add_opt('-u', '--user', dest='user', help='%sUsername (%s)' % (name2, user_envs), default=default_user)
        self.add_opt('-p', '--password', dest='password', help='%sPassword (%s)' % (name2, pw_envs),
                     default=default_password)

    @abstractmethod
    def run(self): # pragma: no cover
        raise CodingErrorException('running HariSekhon.CLI().run() - this should be abstract and non-runnable!'
                                   ' You should have overridden this run() method in the client code')

    def end(self):
        pass

    def __end__(self):
        self.end()
