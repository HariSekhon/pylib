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

__author__  = 'Hari Sekhon'
__version__ = '0.1'

import inspect
import os
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

    # do this to make sure the super constructor runs
    # super(B, self).__init__()
    def __init__(self):
        # instance attributes, feels safer
        self.options = None
        self.args    = None
        topfile   = get_topfile()
        docstring = get_file_docstring(topfile)
        self.usagemsg = ''
        if docstring:
            '\n' + docstring.strip() + '\n'
        self.topfile_version = get_file_version(topfile)
        self.cli_version = self.__version__
        self.utils_version = harisekhon.utils.__version__
        # returns 'python -m unittest' :-/
        # prog = os.path.basename(sys.argv[0])
        self.prog = os.path.basename(topfile)
        self.github_repo = get_file_github_repo(topfile)
        if self.github_repo:
            self.github_repo = ' - ' + self.github_repo
        self.version = '%(prog)s version %(topfile_version)s, CLI version %(cli_version)s, Utils version %(utils_version)s' % self.__dict__
        self.usagemsg = 'Hari Sekhon%(github_repo)s\n\n%(prog)s\n%(usagemsg)s' % self.__dict__
        # self.parser = OptionParser(usage=self.usagemsg, version=self.version)
        self.parser = OptionParser(version=self.version)
        # duplicate key error or duplicate options, sucks
        # self.parser.add_option('-V', dest='version', help='Show version and exit', action='store_true')

    def main(self):
        try:
            self.parse_args()
            # if self.options.version:
            #     print(self.version)
            #     sys.exit(ERRORS['UNKNOWN'])
            self.run()
        except KeyboardInterrupt, e:
            pass

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

    def parse_args(self):
        self.add_options()
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
        (host_envs, default_host) = getenvs(name, 'HOST', default_host)
        (port_envs, default_port) = getenvs(name, 'PORT', default_port)
        self.parser.add_option('-H', '--host', dest='host', help='%sHost (%s)' % (name2, host_envs),
                               default=default_host)
        self.parser.add_option('-P', '--port', dest='port', help='%sPort (%s)' % (name2, port_envs),
                               default=default_port)

    def add_useroption(self, name='', default_user=None, default_password=None):
        name2 = ''
        if not isBlankOrNone(name):
            name2 = "%s " % name
        (user_envs, default_user)   = getenvs(name, ['USERNAME','USER'], default_user)
        (pw_envs, default_password) = getenvs(name, 'PASSWORD', default_password)
        self.parser.add_option('-u', '--user',     dest='user', help='%sUsername (%s)' % (name2, user_envs),
                               default=default_user)
        self.parser.add_option('-p', '--password', dest='password', help='%sPassword (%s)' % (name2, pw_envs),
                               default=default_password)


    # @abstractmethod
    def run(self):
        raise CodingErrorException('running HariSekhon.CLI() - this should be abstract and non-runnable!')
        # sys.exit(2)
