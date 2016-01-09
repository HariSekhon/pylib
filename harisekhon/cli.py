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
#  http://www.linkedin.com/in/harisekhon/pylib
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
# from abc import ABCMeta, abstractmethod
# inspect.getfile(inspect.currentframe()) # filename
# libdir = os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), '..')
libdir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(libdir)
import harisekhon # pylint: disable=wrong-import-position
from harisekhon.utils import log, getenvs2, isBlankOrNone, isInt, isPort, validate_int, plural       # pylint: disable=wrong-import-position
from harisekhon.utils import CodingErrorException, InvalidOptionException, ERRORS, qquit             # pylint: disable=wrong-import-position
from harisekhon.utils import get_topfile, get_file_docstring, get_file_github_repo, get_file_version # pylint: disable=wrong-import-position

__author__ = 'Hari Sekhon'
__version__ = '0.7.0'

class CLI(object):
    """
    HariSekhon.CLI base class
    """
    __version__ = __version__
    # abstract class
    # __metaclass__ = ABCMeta
    # run() method also be annotated as @abstractmethod

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
        self.verbose = None
        self.verbose_default = 0
        self.timeout = None
        self.timeout_default = 10
        self.topfile = get_topfile()
        # this gets utrunner.py in PyCharm and runpy.py
        # print('topfile = %s' % self.topfile)
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
        # self.parser = OptionParser(usage=self.usagemsg_short, version=self.version)
        # self.parser = OptionParser(version=self.version)
        # will be added by default_opts later so that it's not annoyingly at the top of the option help
        # also this allows us to print full docstring for a complete description and not just the cli switches
        self.parser = OptionParser(add_help_option=False)
        # duplicate key error or duplicate options, sucks
        # self.parser.add_option('-V', dest='version', help='Show version and exit', action='store_true')
        # self.setup()

    # @abstractmethod
    # def setup(self):
    #     pass

    def main(self):
        log.debug('running main()')
        self.add_options()
        self.add_default_opts()
        try:
            self.parse_args()
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
            verbose = self.options.verbose
            if verbose > 2:
                log.setLevel(logging.DEBUG)
            elif verbose > 1:
                log.setLevel(logging.INFO)
            if self.options.debug:
                log.setLevel(logging.DEBUG)
            log.info('verbose level: %s', verbose)
            if self.timeout is not None:
                validate_int(self.timeout, 'timeout', 0, 86400)
                log.debug('setting timeout alarm (%s)', self.timeout)
                signal.signal(signal.SIGALRM, self.timeout_handler)
                signal.alarm(int(self.timeout))
            # if self.options.version:
            #     print(self.version)
            #     sys.exit(ERRORS['UNKNOWN'])
            self.run()
        except InvalidOptionException as _:
            self.usage(_)
        except KeyboardInterrupt:
            # log.debug('Caught control-c...')
            print('Caught control-c...') # pragma: no cover

    def usage(self, msg='', status='UNKNOWN'):
        if msg:
            print('%s\n' % msg)
        else:
            print(self.usagemsg)
        self.parser.print_help()
        qquit(status)

    # @abstractmethod
    def add_options(self):
        pass

    def timeout_handler(self, signum, frame): # pylint: disable=unused-argument
        qquit('UNKNOWN', 'self timed out after %d second%s' % (self.timeout, plural(self.timeout)))

    def get_timeout(self):
        return self.timeout

    def set_timeout(self, secs):
        if not isInt(secs):
            raise CodingErrorException('invalid timeout passed to set_timeout(), must be an integer representing seconds') # pylint: disable=line-too-long
        log.debug('setting timeout to %s secs', secs)
        self.timeout = secs

    def get_timeout_default(self):
        return self.timeout_default

    # None prevents --timeout switch becoming exposed, whereas 0 will allow
    def set_timeout_default(self, secs):
        if secs is not None and not isInt(secs):
            raise CodingErrorException('invalid timeout passed to set_timeout_default(), must be an integer representing seconds') # pylint: disable=line-too-long
        log.debug('setting default timeout to %s secs', secs)
        self.timeout_default = secs

    def get_verbose(self):
        return self.verbose

    def set_verbose(self, arg):
        if not isInt(arg):
            raise CodingErrorException('invalid verbose level passed to set_verbose(), must be an integer')
        log.debug('setting verbose to %s', arg)
        self.verbose = int(arg)

    def get_verbose_default(self):
        return self.verbose_default

    def set_verbose_default(self, arg):
        if not isInt(arg):
            raise CodingErrorException('invalid verbose level passed to set_verbose_default(), must be an integer')
        log.debug('setting default verbose to %s', arg)
        self.verbose_default = int(arg)

    def add_default_opts(self):
        # TODO: why is this called twice to result in a problem without first removing flags?
        for _ in ('--help', '--version', '--timeout', '--verbose', '--debug'):
            try:
                self.parser.remove_option(_)
            except ValueError:
                pass

        if self.timeout_default is not None:
            self.parser.add_option('-t', '--timeout', help='Timeout in secs (default: %d)' % self.timeout_default,
                                   metavar='secs', default=self.timeout_default)
        self.parser.add_option('-v', '--verbose', help='Verbose mode (-v, -vv, -vvv)',
                               action='count', default=self.verbose_default)
        self.parser.add_option('-V', '--version', action='store_true', help='Show version and exit')
        # this would intercept and return exit code 0
        # self.parser.add_option('-h', '--help', action='help')
        self.parser.add_option('-h', '--help', action='store_true', help='Show full help and exit')
        self.parser.add_option('-D', '--debug', action='store_true', help=SUPPRESS_HELP)

    def parse_args(self):
        try:
            (self.options, self.args) = self.parser.parse_args()
        # I don't agree with zero exit code from OptionParser for help/usage,
        # and want UNKNOWN not CRITICAL(2) for switch mis-usage...
        except SystemExit:
            sys.exit(ERRORS['UNKNOWN'])
        if self.options.help:
            self.usage()
        if self.options.version:
            print('%(version)s' % self.__dict__)
            sys.exit(ERRORS['UNKNOWN'])
        self.timeout = self.options.timeout
        return self.options, self.args

    def add_hostoption(self, name='', default_host=None, default_port=None):
        name2 = ''
        if not isBlankOrNone(name):
            name2 = "%s " % name
        if default_port != None:
            # assert isPort(default_port)
            if not isPort(default_port):
                raise CodingErrorException('invalid default port supplied to add_hostoption()')
        (host_envs, default_host) = getenvs2('HOST', default_host, name)
        (port_envs, default_port) = getenvs2('PORT', default_port, name)
        self.parser.add_option('-H', '--host', dest='host', help='%sHost (%s)' % (name2, host_envs),
                               default=default_host)
        self.parser.add_option('-P', '--port', dest='port', help='%sPort (%s)' % (name2, port_envs),
                               default=default_port)

    def add_useroption(self, name='', default_user=None, default_password=None):
        name2 = ''
        if not isBlankOrNone(name):
            name2 = "%s " % name
        (user_envs, default_user) = getenvs2(['USERNAME', 'USER'], default_user, name)
        (pw_envs, default_password) = getenvs2('PASSWORD', default_password, name)
        self.parser.add_option('-u', '--user', dest='user', help='%sUsername (%s)' % (name2, user_envs),
                               default=default_user)
        self.parser.add_option('-p', '--password', dest='password', help='%sPassword (%s)' % (name2, pw_envs),
                               default=default_password)

    # @abstractmethod
    def run(self): # pylint: disable=no-self-use
        raise CodingErrorException('running HariSekhon.CLI().run() - this should be abstract and non-runnable!'
                                   ' You should have overridden this run() method in the client code')
