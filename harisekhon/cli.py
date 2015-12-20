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
#  If you're using my code you're welcome to connect with me on LinkedIn and optionally send me feedback to help improve or steer this or other code I publish
#
#  http://www.linkedin.com/in/harisekhon/pylib
#

"""
# =========================================================================== #
#                           HariSekhon.CLI
# =========================================================================== #
"""

__author__  = 'Hari Sekhon'
__version__ = '0.1'

import inspect
import os
import signal
import sys
from optparse import OptionParser
# Python 2.6+ only
# from abc import ABCMeta, abstractmethod
# inspect.getfile(inspect.currentframe()) # filename
# libdir = os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), '..')
libdir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(libdir)
import harisekhon
from harisekhon.utils import *

class CLI (object):
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
        self.__default_opts = None
        self.verbose_default = 0
        self.timeout = None
        self.timeout_default = 1
        self.topfile = get_topfile()
        # this gets utrunner.py in PyCharm and runpy.py
        # print('topfile = %s' % self.topfile)
        self.docstring = get_file_docstring(self.topfile)
        if self.docstring:
            self.docstring = '\n' + self.docstring.strip() + '\n'
        self.topfile_version = get_file_version(self.topfile)
        self.cli_version = self.__version__
        self.utils_version = harisekhon.utils.__version__
        # returns 'python -m unittest' :-/
        # prog = os.path.basename(sys.argv[0])
        self.prog = os.path.basename(self.topfile)
        self.github_repo = get_file_github_repo(self.topfile)
        # if not self.github_repo:
        #     self.github_repo = 'https://github.com/harisekhon/pytools'
        if self.github_repo:
            self.github_repo = ' - ' + self.github_repo
        self.version = '%(prog)s version %(topfile_version)s, CLI version %(cli_version)s, Utils version %(utils_version)s' % self.__dict__
        self.usagemsg = '\n\nHari Sekhon%(github_repo)s\n\n%(prog)s\n%(docstring)s\n%(prog)s [options]' % self.__dict__
        self.usagemsg_short = '\n\nHari Sekhon%(github_repo)s\n\n%(prog)s [options]' % self.__dict__
        # set this in simpler client programs when you don't want to exclude
        # self.parser = OptionParser(usage=self.usagemsg_short, version=self.version)
        self.parser = OptionParser(version=self.version)
        # duplicate key error or duplicate options, sucks
        # self.parser.add_option('-V', dest='version', help='Show version and exit', action='store_true')

    def timeout_handler(self, signum, frame):
        quit('UNKNOWN', 'self timed out after %d seconds' % self.timeout)

    def main(self):
        log.debug('running main()')
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
            log.info('verbose level: %s' % verbose)
            if self.timeout is not None:
                log.debug('setting timeout alarm (%s)' % self.timeout)
                signal.signal(signal.SIGALRM, self.timeout_handler)
                signal.alarm(self.timeout)
            # if self.options.version:
            #     print(self.version)
            #     sys.exit(ERRORS['UNKNOWN'])
            self.run()
        except KeyboardInterrupt, e:
            # log.debug('Caught control-c...')
            print('Caught control-c...')

    def usage(self, msg='', status='UNKNOWN'):
        if msg:
            print('%s\n' % msg)
        else:
            print(self.usagemsg)
        self.parser.print_help()
        quit(status)

    # @override this
    def add_options(self):
        pass

    def set_timeout(self, secs):
        if not isInt(secs):
            raise CodingErrorException('invalid timeout passed to set_timeout(), must be an integer representing seconds')
        log.debug('setting timeout to %s secs' % secs)
        self.timeout = secs

    # None prevents --timeout switch becoming exposed, whereas 0 will allow
    def set_timeout_default(self, secs):
        if secs is not None and not isInt(secs):
            raise CodingErrorException('invalid timeout passed to set_timeout_default(), must be an integer representing seconds')
        log.debug('setting default timeout to %s secs' % secs)
        self.timeout_default = secs

    def set_verbose(self, arg):
        if not isInt(arg):
            raise CodingErrorException('invalid verbose level passed to set_verbose(), must be an integer')
        log.debug('setting verbose to %s' % arg)
        self.verbose = arg

    def set_verbose_default(self, arg):
        if not isInt(arg):
            raise CodingErrorException('invalid verbose level passed to set_verbose_default(), must be an integer')
        log.debug('setting default verbose to %s' % arg)
        self.verbose_default = arg

    def add_default_opts(self):
        if self.__default_opts:
            return
        if self.timeout_default is not None:
            self.parser.add_option('-t', '--timeout', help='Timeout in secs (default: %d)' % self.timeout_default,
                                   metavar='secs', default=self.timeout_default)
        self.parser.add_option('-v', '--verbose', help='Verbose mode (-v, -vv, -vvv ...)',
                               action='count', default=self.verbose_default)
        self.__default_opts = 1

    def parse_args(self):
        self.add_options()
        self.add_default_opts()
        (self.options, self.args) = self.parser.parse_args()
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
        self.parser.add_option('-u', '--user',     dest='user', help='%sUsername (%s)' % (name2, user_envs),
                               default=default_user)
        self.parser.add_option('-p', '--password', dest='password', help='%sPassword (%s)' % (name2, pw_envs),
                               default=default_password)

    # @abstractmethod
    def run(self):
        raise CodingErrorException('running HariSekhon.CLI().run() - this should be abstract and non-runnable!'
                                   ' You should have overridden this run() method in the client code')
        # sys.exit(2)