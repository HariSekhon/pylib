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
#  http://www.linkedin.com/in/harisekhon
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
from harisekhon.utils import *

class CLI:
    """
    HariSekhon.CLI base class
    """
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
        self.opts    = {}
        self.parser  = OptionParser()

    def main(self):
        try:
            self.parse_args()
            self.run()
        except KeyboardInterrupt, e:
            pass

    def usage(self, msg='', status='UNKNOWN'):
        frame = inspect.stack()[-1][0]
        topfile = inspect.getfile(frame)
        # topfile = inspect.stack()[-1][1]
        docstring = get_file_docstring(topfile)
        if isStr(docstring) and docstring:
            docstring = '\n'.join([ x.strip() for x in docstring.split('\n') if x ])
            print('%s\n' % docstring)
        if msg:
            print('%s\n' % msg)
        self.parser.print_help()
        quit(status)

    # @override this
    def add_options(self):
        pass

    def parse_args(self):
        self.add_options()
        (self.options, self.args) = self.parser.parse_args()
        # return self.parser.parse_args()

    def set_default_port(self, port, name=''):
        if not isPort(port):
            raise CodingErrorException('invalid port supplied to set_default_port()')
        self.opts[name] = self.opts.get(name, {})
        self.opts[name]['port'] = self.opts[name].get('port', {})
        self.opts[name]['port']['default'] = port
        # this often happens before env_creds(), so don't set port opt since env_vars() will politely not set it then
        # if not 'port' in self.opts:
        #     self.opts['port'] = port

    def envs2string(self, name, store_var, default_val=None):
        myStr = '$' + ', $'.join(self.opts[name][store_var]['envs'])
        if not isBlankOrNone(default_val):
           myStr += ", default: %s" % default_val
        return myStr

    def add_hostoption(self, name='', default_host=None, default_port=None):
        name2 = ''
        if not isBlankOrNone(name):
            name2 = "%s " % name
        if default_port != None and not isPort(default_port):
            raise CodingErrorException('invalid default port supplied to add_hostoption()')
        self.env_vars(name, 'HOST', prefix=True)
        self.env_vars(name, 'PORT', prefix=True)
        host_env_help = self.envs2string(name, 'host', default_val=default_host)
        port_env_help = self.envs2string(name, 'port', default_val=default_port)
        if 'default' in self.opts[name]['port'] and default_port == None:
            default_port = self.opts[name]['port']['default']
        if default_host:
            self.opts[name]['host']['val'] = self.opts[name]['host'].get('val', default_host)
        if default_port:
            self.opts[name]['port']['val'] = self.opts[name]['port'].get('val', default_port)
        self.parser.add_option('-H', '--host', dest='host', help='%sHost (%s)' % (name2, host_env_help), metavar='<host>')
        self.parser.add_option('-P', '--port', dest='port', help='%sPort (%s)' % (name2, port_env_help), metavar='<port>')

    def add_useroption(self, name='', default_user=None, default_password=None):
        name2 = ''
        if not isBlankOrNone(name):
            name2 = "%s " % name
        self.env_vars(name, ['USERNAME', 'USER'], prefix=True)
        self.env_vars(name, 'PASSWORD', prefix=True)
        user_env_help     = self.envs2string(name, 'username', default_val=default_user)
        password_env_help = self.envs2string(name, 'password', default_val=default_password)
        if default_user:
            self.opts[name]['username']['val'] = self.opts[name]['username'].get('val', default_user)
        if default_password:
            self.opts[name]['password']['val'] = self.opts[name]['password'].get('val', default_password)
        self.parser.add_option('-u', '--user',     dest='host', help='%sUsername (%s)' % (name2, user_env_help),     metavar='<user>')
        self.parser.add_option('-p', '--password', dest='port', help='%sPassword (%s)' % (name2, password_env_help), metavar='<password>')

    def _env_var(self, name, var, store_var=None):
        if not isStr(name):
            raise CodingErrorException('supplied non-string for name var arg to CLI.env_var()')
        if not isStr(var):
            raise CodingErrorException('supplied non-string for var arg to CLI.env_var()')
        if isBlankOrNone(var):
            raise CodingErrorException('supplied blank string for var arg to CLI.env_var()')
        name = name.strip()
        var = str(var).strip()
        if isBlankOrNone(store_var):
            store_var = var
        store_var = store_var.lower().strip()
        env_var = re.sub('[^A-Z0-9]', '_', var.upper())
        val = os.getenv(env_var, None)
        self.opts[name] = self.opts.get(name, {})
        self.opts[name][store_var] = self.opts[name].get(store_var, {})
        self.opts[name][store_var]['envs'] = self.opts[name][store_var].get('envs', list())
        self.opts[name][store_var]['envs'].append(env_var)
        if val != None:
            # skip if already set
            if not 'val' in self.opts[name][store_var]:
                self.opts[name][store_var]['val'] = val

    def env_vars(self, name, var, prefix=False):
        if not isStr(name):
            raise CodingErrorException('non-string passed for name to env_vars()')
        # if isBlankOrNone(name):
        #     raise CodingErrorException('blank/none name passed to env_vars()')
        if isStr(var):
            if prefix and not isBlankOrNone(name):
                self._env_var(name, name + ' ' + var, var)
            self._env_var(name, var, var)
        elif isList(var):
            for v in var:
                if not isStr(v):
                    raise CodingErrorException('non-string passed in array to env_vars()')
            if prefix and not isBlankOrNone(name):
                for v in var:
                    self._env_var(name, name + '_' + v, var[0])
            for v in var:
                self._env_var(name, v, var[0])
        else:
            raise CodingErrorException('non-string / non-array passed as vars to env_vars()')

    # @abstractmethod
    def run(self):
        raise CodingErrorException('running HariSekhon.CLI() - this should be abstract and non-runnable!')
        # sys.exit(2)
