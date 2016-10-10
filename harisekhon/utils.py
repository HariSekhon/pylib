#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2008-03-06 15:20:22 +0000 (Thu, 06 Mar 2008)
#  Reinstantiated Date:
#        2013-07-04 00:08:32 +0100 (Thu, 04 Jul 2013)
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

""" Personal Library originally started to standardize Nagios Plugin development """

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals

import ast
import collections
import glob
import inspect
# import itertools
import json
import os
import re
import logging
import logging.config
import platform
import signal
#import six
import string
import sys
import traceback
from types import CodeType
import warnings
import xml.etree.ElementTree as ET
import yaml
# not available Python < 2.7
# try:
#     from xml.etree.ElementTree import ParseError
# except:
#     pass
# Python 2.6 throws ExpatError instead of ParseError
# from xml.parsers.expat import ExpatError

__author__ = 'Hari Sekhon'
__version__ = '0.10.14'

# Standard Nagios return codes
ERRORS = {
    "OK"        : 0,
    "WARNING"   : 1,
    "CRITICAL"  : 2,
    "UNKNOWN"   : 3,
    "DEPENDENT" : 4
}

libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(libdir)
import harisekhon # pylint: disable=wrong-import-position

def get_caller():
    # return inspect.currentframe().f_back.f_back
    # try:
    return inspect.stack()[2][3]
    # except Exception:
    #     return '<failed to get caller function>'

# using get_topfile further down instead now
# prog = os.path.basename(inspect.getfile(inspect.currentframe().f_back))


# ============================================
# add a trace log level for sub tracing
TRACE = 5
logging.addLevelName(TRACE, 'TRACE')

def trace(self, message, *args, **kwargs):
    self.log(TRACE, message, *args, **kwargs)

logging.Logger.trace = trace
# =============================================

logging.config.fileConfig(os.path.join(libdir, 'resources', 'logging.conf'))
log = logging.getLogger('HariSekhonUtils')
# optimization - gives unknown file, unknown function, line 0
# logging._srcfile = None
# optimization - not tested yet
# logging.logThreads = 0
# optimization - causes TypeError: %d format: a number is required, not NoneType
# logging.logProcesses = 0

# avoid expensive info gathering when it will simply be discarded by logger anyway
# if logger.isEnabledFor(logging.DEBUG):
#     log.debug('msg %s %s', expensive_func1, expensive_func2)

# XXX: enable for prod
#raiseExceptions = False

# Settings now controlled separately in logging.conf file
# log.setLevel(logging.WARN)
# log_streamhandler = logging.StreamHandler()
# log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# log_streamhandler.setFormatter(log_formatter)
# log.addHandler(log_streamhandler)

# if re.search(r'\bcheck_', prog):
#     sys.stderr = sys.stdout

valid_nagios_units = ('%', 's', 'ms', 'us', 'B', 'KB', 'MB', 'GB', 'TB', 'c')


def support_msg(repo=None):
    if isBlankOrNone(repo):
        if prog.startswith('check_'):
            repo = 'nagios-plugins'
        else:
            repo = 'pytools'
    _ = 'Please try latest version from https:/github.com/HariSekhon/%(repo)s and if problem persists paste the full output in to a ticket for a fix/update at https://github.com/HariSekhon/%(repo)s/issues' % locals() # pylint: disable=line-too-long
    return _

def support_msg_api(repo=None):
    return 'API may have changed. ' + support_msg(repo)


# doesn't work in Py3K
# Intended for use with CLI tools - will reset stdout which will clash with frameworks
# that already do this to try to capture stdout, for example by using StringIO
def autoflush():
    # this line causes instant exit code 1
    unbuffered = os.fdopen(sys.__stdout__.fileno(), 'w', 0)
    orig_stdout = sys.stdout
    sys.stdout = unbuffered
    return orig_stdout


def printerr(msg=None, indent=False):
    if indent:
        print(">>> ", end='', file=sys.stderr)
    if msg is None:
        print('', file=sys.stderr)
    else:
        print(msg, file=sys.stderr)


def warn(msg):
    log.warn(msg)


def die(msg, *ec):
    """ Print error message and exit program """
    printerr(msg)
    if ec:
        exitcode = ec[0]
        if str(exitcode).isdigit():
            if exitcode > 255:
                sys.exit(exitcode % 256)
            else:
                sys.exit(exitcode)
        # elif exitcode in ERRORS.keys():
        elif exitcode in ERRORS:
            sys.exit(ERRORS[exitcode])
        else:
            log.error("Code error, non-digit and non-recognized error status passed as second arg to die()")
            sys.exit(ERRORS["CRITICAL"])
    sys.exit(ERRORS["CRITICAL"])


def code_error(msg):
    raise CodingError(msg)

# must be named differently to qquit() built-in to avoid overriding the built-in
# overriding the built-in can lead to confusing errors with wrong exit code if forgetting to import this function
def qquit(status, msg=''):
    """ Quit with status code from ERRORS dictionary after printing given msg """
    status = str(status).upper()
    if status not in ERRORS:
        log.warn("invalid status '%s' passed to qquit() by caller '%s', defaulting to critical\n%s",
                 status, get_caller(), traceback.format_exc())
        status = 'CRITICAL'
    # log.error('%s: %s', status, msg)
    if msg:
        print('{0}: {1}'.format(status, msg))
        if log.isEnabledFor(logging.DEBUG):
            # prints to stderr, Nagios spec wants stdout
            # traceback.print_exc()
            _ = traceback.format_exc().strip()
            if _ != 'None':
                print('\n{0}'.format(_))
    sys.exit(ERRORS[status])


# use CLI's self.usage() mostly instead which doesn't require passing in the parser
# and also gets the file docstring at the top of the stack, as well as the version
def usage(parser, msg='', status='UNKNOWN'):
    if msg:
        print('%s\n' % msg)
    # else:
        # topfile = get_topfile()
        # docstring = get_file_docstring(topfile)
        # if isStr(docstring) and docstring:
        #     docstring = '\n'.join([ x.strip() for x in docstring.split('\n') if x ])
        #     print('%s\n' % docstring)
    parser.print_help()
    qquit(status)


def get_topfile():
    # this gets 'python -m unittest' as filename
    # filename = sys.argv[0]
    frame = inspect.stack()[-1][0]
    # filename = inspect.stack()[-1][1]
    filename = inspect.getfile(frame)
    # filename = os.path.splitext(filename)[0] + '.py'
    filename = re.sub('.pyc$', '.py', filename)
    assert isStr(filename)
    # this gets utrunner.py in PyCharm and runpy.py from unittest
    if os.path.basename(filename) in ('utrunner.py', 'runpy.py', 'ipython'):
        return __file__
    # workaround for interactive mode
    if filename == '<stdin>':
        return ''
    # workaround for python -c
    elif filename == '<string>':
        return ''
    else:
        assert isFilename(filename)
    return filename


def get_file_docstring(filename):
    assert isStr(filename)
    assert isFilename(filename)
    # .pyc files cause the following error:
    # TypeError: compile() expected string without null bytes
    filename = re.sub('.pyc$', '.py', filename)
    file_contents = open(filename).read()
    # binary, maybe started with python command
    if '\0' in file_contents:
        #file_contents = ''
        return ''
    try:
        _ = ast.parse(file_contents, filename=filename, mode='exec')
    except TypeError:
        return ''
    return ast.get_docstring(_)
    # inspect.getdoc is another option but looks like it'll only get docstring of object, we want file/module
###### old way #####
#    # returns a code object
#    co = compile(open(filename).read(), filename, 'exec')
#    assert isCode(co)
#    # just let it traceback if something is not as expected so I know if something changes,
#    # otherwise will silently start dropping usage descriptions
#    # if isListOrTuple(code.co_consts) and len(code.co_consts) > 0 and isStr(code.co_consts[0]):
#    # assert hasattr(code, 'co_consts')
#    # code.co_consts is a tuple
#    assert isListOrTuple(co.co_consts)
#    assert len(co.co_consts) > 0
#    if isStr(co.co_consts[0]):
#        return co.co_consts[0]
#    return None


def get_file_version(filename):
    assert isStr(filename)
    assert isFilename(filename)
    # .pyc files cause the following error:
    # TypeError: compile() expected string without null bytes
    filename = re.sub('.pyc$', '.py', filename)
    if re.search(r'\.py$', filename):
        tree = ast.parse(open(filename).read(), filename=filename, mode='exec')
        # print(ast.dump(tree))
        # print(dir(tree._fields))
        for node in (n for n in tree.body if isinstance(n, ast.Assign)):
            if len(node.targets) == 1:
                name = node.targets[0]
                if isinstance(name, ast.Name) and name.id == '__version__':
                    _ = node.value
                    if isinstance(_, ast.Str):
                        return _.s
    return None


def get_file_github_repo(filename):
    assert isStr(filename)
    assert isFilename(filename)
    # .pyc files cause the following error:
    # TypeError: compile() expected string without null bytes
    filename = re.sub('.pyc$', '.py', filename)
    _ = open(filename)
    for line in _:
        if 'https://github.com/harisekhon' in line:
            _.close()
            return line.lstrip('#').strip()
    _.close()
    return ''


def gen_prefixes(prefixes, names, sort_by_names=False):
    if isStr(prefixes):
        prefixes = [prefixes]
    if isStr(names):
        names = [names]
    if not isIterableNotStr(prefixes):
        raise CodingError('non-iterable passed for prefixes to prefix()')
    if not isIterableNotStr(names):
        raise CodingError('non-iterable passed for names to prefix()')
    if '' not in prefixes:
        prefixes.append('')
    # Python 2.6+ only
    # for pair in itertools.product(prefixes, names):
    if sort_by_names:
        pairs = [(x, y) for y in names for x in prefixes]
    else:
        pairs = [(x, y) for x in prefixes for y in names]
    for pair in pairs:
        result = '_'.join(str(z) for z in pair if z)
        # result = result.lstrip('_') # handled by 'if z' now
        if result:
            yield result

def gen_prefixes_env(*args, **kwargs):
    return [normalize_env_var(_) for _ in gen_prefixes(*args, **kwargs)]

def getenv(var, default=None):
    if not isStr(var):
        raise CodingError('supplied non-string for var arg to getenv()')
    if isBlankOrNone(var):
        raise CodingError('supplied blank string for var arg to getenv()')
    log.debug('checking for environment variable: %s', var)
    var = str(var).strip()
    return os.getenv(var, default)

def getenvs(my_vars, default=None, prefix=''):
    if prefix is None:
        raise CodingError('None prefix passed for prefix to getenvs()')
    if not isStr(prefix):
        raise CodingError('non-string passed for prefix to getenvs()')
    result = None
    assert isStr(my_vars) or isList(my_vars)
    if isStr(my_vars):
        for var in gen_prefixes_env(prefix, my_vars, True):
            result = getenv(var)
            if result is not None:
                break
    elif isList(my_vars):
        for var in my_vars:
            if not isStr(var):
                raise CodingError('non-string passed in array to getenvs()')
        for var in gen_prefixes_env(prefix, my_vars, True):
            result = getenv(var)
            if result is not None:
                break
    if result is None:
        result = default
    return result

def normalize_env_var(env_var):
    return re.sub('[^A-Z0-9]', '_', env_var.upper())

# wrapper to getenvs to also return the generated string to use in option help
def getenvs2(my_vars, default, name):
    if not isStr(name):
        raise CodingError('passed non-string for name to getenvs2()')
    name = name.upper()
    assert isStr(my_vars) or isList(my_vars)
    # exclude showing the default for sensitive options
    is_sensitive = False
    sensitive_regex = re.compile('password|passphrase|secret', re.I)
    if isStr(my_vars):
        if sensitive_regex.search(my_vars):
            is_sensitive = True
    elif isList(my_vars):
        for _ in my_vars:
            assert isStr(_)
        for _ in my_vars:
            if sensitive_regex.search(_):
                is_sensitive = True
                break
    my_help = '$' + ', $'.join(gen_prefixes_env(name, my_vars))
    if default is not None:
        if is_sensitive:
            my_help += ', default: ******'
        else:
            my_help += ', default: %(default)s' % locals()
    return my_help, getenvs(my_vars, default, name)


def env_lines():
    return dict_lines(dict(os.environ))


def dict_lines(arg):
    if not isDict(arg):
        raise CodingError("non-dict type '%s' passed to dict_lines" % type(arg))
    # can't use iteritems() any more due to Py3k
    return '\n'.join(('%s = %s' % (key, value) for (key, value) in sorted(arg.items())))


def find_git_root(target):
    target = os.path.abspath(target)
    log.debug("finding git root for target '%s'", target)
    gitroot = target
    while gitroot and gitroot != '/':
        log.debug("trying '%s'", gitroot)
        # os.path.isdir doesn't work on git submodule Dockerfiles in PyTools repo :-/
        if os.path.exists(os.path.join(gitroot, '.git')):
            log.debug("found git root for target '%s': '%s'", target, gitroot)
            return gitroot
        gitroot = os.path.dirname(gitroot)
    return None


# ============================================================================ #
#                              Custom Exceptions
# ============================================================================ #


class NagiosException(Exception):
    pass


# can't do this, there is already a built-in Warning
class WarningError(NagiosException):
    pass


class CriticalError(NagiosException):
    pass


class UnknownError(NagiosException):
    pass


class CodingError(AssertionError):
    pass


# TODO: rename these all to not have the word Exception in them it's excessive
class LinuxOnlyException(AssertionError):
    # def __init__(self, value):
    #     self.value = value
    # def __str__(self):
    #     return repr(self.value)
    pass


class MacOnlyException(AssertionError):
    pass


class InvalidArgumentException(AssertionError):
    pass


class InvalidOptionException(AssertionError):
    pass


class FileNotExecutableException(IOError):
    pass


class InvalidFilenameException(IOError):
    pass


class FileNotFoundException(IOError):
    pass


# ============================================================================ #
#                               Jython Utils
# ============================================================================ #

def isJython():
    """ Returns True if running in Jython interpreter """
    return 'JYTHON_JAR' in dir(sys)


def jython_only():
    """ Die unless we are inside Jython """
    if not isJython():
        die('not running in Jython!')


def get_jython_exception():
    #import traceback; traceback.print_exc()
    if sys.exc_info()[1] is None:
        return ''
    else:
        # return sys.exc_info()[1].toString()
        return sys.exc_info()[1].message


def log_jython_exception():
    """ logs last Jython Exception """
    _ = get_jython_exception()
    log.error('Error: %s', _)
    if isJavaOOM(_):
        log.error(java_oom_fix_msg()) # pragma: nocover


def isJavaOOM(arg):
    # if arg == 'java.lang.OutOfMemoryError: Java heap space':
    if arg is None:
        return False
    if 'java.lang.OutOfMemoryError' in arg:
        return True
    return False


def java_oom_fix_msg():
    return '\nAdd/Increase -J-Xmx<value> command line argument\n'


# ============================================================================ #

def curl(url, *args, **kwargs):
    # request_handler should be a subclass of harisekhon.RequestHandler
    if 'request_handler' in kwargs:
        request_handler = kwargs['request_handler']
        if not isStr(request_handler):
            raise CodingError('request_handler passed to curl() must be a string')
        containing_module = re.sub(r'[^\.]+$', '', request_handler).rstrip('.')
        target_class = request_handler.split('.')[-1]
        # log.debug('containing module is %s' % containing_module)
        module = __import__(containing_module, globals(), locals(), [], -1)
        # module = __import__(request_handler, globals(), locals(), [request_handler.split('.')[-1]], -1)
        _class = getattr(module, target_class)
        del kwargs['request_handler']
        return _class().get(url, *args, **kwargs)
    else:
        return harisekhon.RequestHandler().get(url, *args, **kwargs)

# This doesn't make sense since you always have to override RequestBS4Handler's parse() and then call
# def curl_bs4(*args, **kwargs):
#     # request_handler should be a subclass of harisekhon.RequestBS4Handler
#     if 'request_handler' in kwargs:
#         request_handler = kwargs['request_handler']
#         if not isStr(request_handler):
#             raise CodingError('request_handler passed to curl_bs4() must be a string')
#         containing_module = re.sub(r'[^\.]+$', '', request_handler).rstrip('.')
#         target_class = request_handler.split('.')[-1]
#         # log.debug('containing module is %s' % containing_module)
#         module = __import__(containing_module, globals(), locals(), [], -1)
#         # module = __import__(request_handler, globals(), locals(), [request_handler.split('.')[-1]], -1)
#         _class = getattr(module, target_class)
#         return _class.curl(*args, **kwargs)
#     else:
#         return harisekhon.RequestBS4Handler.curl(*args, **kwargs)


def flatten(arg):
    if not isIterableNotStr(arg):
        yield arg
        return
    #     raise CodingError('passed non-iterable to flatten()')
    # if isInt(arg) or isFloat(arg):
    #     yield arg
    # else:
    for _ in arg:
        if isIterableNotStr(_):
            for sub in flatten(_):
                yield sub
        else:
            yield _


def read_file_without_comments(filename):
    return [x.rstrip("\n").split("#")[0].strip() for x in open(filename).readlines()]


def jsonpp(json_data):
    if isStr(json_data):
        json_data = json.loads(json_data)
    return json.dumps(json_data, sort_keys=True, indent=4, separators=(',', ': '))


def list_sort_dicts_by_value(my_list, key):
    if not isList(my_list):
        raise InvalidArgumentException('non-list passed as first arg to list_sort_dicts_by_key()')
    if not isStr(key):
        raise InvalidArgumentException('non-string passed as second arg to list_sort_dicts_by_key()')
    my_vals = {}
    my_return_list = []
    for _ in my_list:
        if not isDict(_):
            raise AssertionError("list item '%s' is not a dict" % _)
        val = _[key]
        if not isStr(val):
            raise AssertionError("list key '%(key)s' value '%(val)s' is not a string" % locals())
        my_vals[val.lower()] = 1
    # for val in sorted(my_vals.keys()):
    for val in sorted(my_vals):
        for _ in my_list:
            val2 = _[key].lower()
            if val == val2:
                my_return_list.append(_)
    return my_return_list


# ============================================================================ #
#                                   REGEX
# ============================================================================ #

# years and years of Regex expertise and testing has gone in to this, do not edit!
# This also gives flexibility to work around some situations where domain names may not be qquite valid
# (eg .local/.intranet) but still keep things qquite tight
# There are certain scenarios where other generic libraries don't help with these

_tlds = set()

def _load_tlds(filename):
    _ = open(filename)
    tld_count = 0
    re_blank = re.compile(r'^\s*$')
    re_alnum_dash = re.compile('^[A-Za-z0-9-]+$')
    for line in _.readlines():
        line = line.split('#')[0]
        line = line.strip()
        if re_blank.match(line):
            continue
        if re_alnum_dash.match(line):
            _tlds.add(line)
            tld_count += 1
        else:
            warnings.warn("TLD: '%(line)s' from tld file '%(filename)s' not validated, skipping that TLD" % locals())
    log.debug("loaded %(tld_count)s TLDs from file '%(filename)s'")

_tld_file = libdir + '/resources/tlds-alpha-by-domain.txt'
_load_tlds(_tld_file)

def _check_tldcount():
    log.debug('%s total unique TLDs loaded', len(_tlds))
    # must be at least this many if the IANA set loaded properly
    if len(_tlds) < 1000:
        code_error('%s tlds loaded, expected >= 1000' % len(_tlds))
    # make sure we don't double load TLD list
    if len(_tlds) > 2000:
        code_error('%s tlds loaded, expected <= 2000' % len(_tlds))

_check_tldcount()

_custom_tlds = libdir + '/resources/custom_tlds.txt'
if os.path.isfile(_custom_tlds):
    _load_tlds(_custom_tlds)

tld_regex = r'(?i)\b(?:' + '|'.join(_tlds) + r')\b'

# pylint: disable=bad-whitespace
domain_component_regex = r'\b[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\b'
# AWS regex from http://blogs.aws.amazon.com/security/blog/tag/key+rotation
aws_access_key_regex   = r'(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])'
aws_secret_key_regex   = r'(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])'
domain_regex           = r'(?:' + domain_component_regex + r'\.)*' + tld_regex
domain_regex2          = r'(?:' + domain_component_regex + r'\.)+' + tld_regex
domain_regex_strict    = domain_regex2
# must permit numbers as valid host identifiers that are being used in the wild in FQDNs
hostname_component     = r'\b[A-Za-z0-9](?:[A-Za-z0-9_\-]{0,61}[a-zA-Z0-9])?\b'
aws_host_component     = r'ip-(?:10-\d+-\d+-\d+|172-1[6-9]-\d+-\d+|172-2[0-9]-\d+-\d+|172-3[0-1]-\d+-\d+|192-168-\d+-\d+)'  # pylint: disable=line-too-long
hostname_regex         = hostname_component + r'(?:\.' + domain_regex + ')?'
aws_hostname_regex     = aws_host_component + r'(?:\.' + domain_regex + ')?'
dirname_regex          = r'[\/\w\s\\.,:*()=%?+-]+'
filename_regex         = dirname_regex + r'[^\/]'
rwxt_regex             = r'[r-][w-][x-][r-][w-][x-][r-][w-][xt-]'
fqdn_regex             = hostname_component + r'\.' + domain_regex
aws_fqdn_regex         = aws_host_component + r'\.' + domain_regex
# SECURITY NOTE: I'm allowing single quote through as it's found in Irish email addresses.
# This makes the email_regex non-safe without further validation.
# This regex only tests whether it's a valid email address, nothing more.
email_regex            = r"\b[A-Za-z0-9](?:[A-Za-z0-9\._\%\'\+-]{0,62}[A-Za-z0-9\._\%\+-])?@" + domain_regex
# TODO: review this IP regex again
ip_prefix_regex        = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
# now allowing 0 or 255 as the final octet due to CIDR
ip_regex               = ip_prefix_regex + r'(?:25[0-5]|2[0-4][0-9]|[01]?[1-9][0-9]|[01]?0[1-9]|[12]00|[0-9])\b'
subnet_mask_regex      = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[1-9][0-9]|[01]?0[1-9]|[12]00|[0-9])\b'  # pylint: disable=line-too-long
mac_regex              = r'\b[0-9A-F-af]{1,2}[:-](?:[0-9A-Fa-f]{1,2}[:-]){4}[0-9A-Fa-f]{1,2}\b'
host_regex             = r'\b(?:' + hostname_regex + '|' + ip_regex + r')\b'
# I did a scan of registered running process names across several hundred linux servers of a diverse group of
# enterprise applications with 500 unique process names (58k individual processes) to determine that there are cases
# with spaces, slashes, dashes, underscores, chevrons (<defunct>), dots (script.p[ly], in.tftpd etc) to determine
# what this regex should be. Incidentally it appears that Linux truncates registered process names to 15 chars.
# This is not from ps -ef etc it is the actual process registered name, hence init not [init] as it appears in ps output
process_name_regex     = r'\s*[\w_\.\/\<\>-][\w\s_\.\/\<\>-]+'
url_path_suffix_regex  = r'/(?:[\w.,:\/%&?#!=*|\[\]~+-]+)?'
url_regex              = r'(?i)\bhttps?://' + host_regex + r'(?::\d{1,5})?(?:' + url_path_suffix_regex + ')?'
user_regex             = r'\b[A-Za-z][A-Za-z0-9_-]*[A-Za-z0-9]\b'
column_regex           = r'\b[\w\:]+\b'
ldap_dn_regex          = r'\b\w+=[\w\s]+(?:,\w+=[\w\s]+)*\b'
krb5_principal_regex   = r'(?i)' + user_regex + r'(?:\/' + hostname_regex + r')?(?:\@' + domain_regex + r')?'
threshold_range_regex  = r'^(\@)?(-?\d+(?:\.\d+)?)(:)(-?\d+(?:\.\d+)?)?'
threshold_simple_regex = r'^(-?\d+(?:\.\d+)?)'
label_regex            = r'\s*[\%\(\)\/\*\w-][\%\(\)\/\*\w\s-]*'
version_regex          = r'\d+(?:\.\d+)*'
version_regex_short    = r'\d+(?:\.\d+)?'
version_regex_lax      = version_regex + r'-?.+\b'
# pylint: enable=bad-whitespace

##################
#
# see also inspect.isclass(obj)
#                 .ismethod(obj)
#                 .ismodule(obj)
#                 .isfunction(obj)
#                 .istraceback(obj)

# see also .isalpha()
def isAlNum(arg):
    if arg is None:
        return False
    return str(arg).isalnum()
    # if re.match('^[A-Za-z0-9]+$', str(arg)):
    #     return True
    # return False


def isAwsAccessKey(arg):
    if arg is None:
        return False
    if re.match('^' + aws_access_key_regex + '$', str(arg)):
        return True
    return False


def isAwsHostname(arg):
    if arg is None:
        return False
    if re.match('^' + aws_hostname_regex + '$', str(arg)):
        return True
    return False


def isAwsFqdn(arg):
    if arg is None:
        return False
    if re.match('^' + aws_fqdn_regex + '$', str(arg)):
        return True
    return False


def isAwsSecretKey(arg):
    if arg is None:
        return False
    if re.match('^' + aws_secret_key_regex + '$', str(arg)):
        return True
    return False


def isBlankOrNone(arg):
    if arg is None:
        return True
    elif str(arg).strip() == '':
        return True
    return False


def isBool(arg):
    return isinstance(arg, bool)


def isChars(arg, chars):
    if chars is None:
        code_error('no chars passed to isChars()')
    if not isRegex("[" + chars + "]"):
        code_error('invalid char range passed to isChars')
    if re.match('^[' + chars + ']+$', str(arg)):
        return True
    return False

# because 'code' isn't an accessible keyword
# moved import to top
# from types import CodeType
def isCode(arg):
    return isinstance(arg, CodeType)


def isCodeStr(arg):
    if not isStr(arg):
        return False
    try:
        _ = compile(arg, 'test', 'exec')
    except SyntaxError:
        return False
    return isCode(_)


def isCollection(arg):
    if arg is None:
        return False
    if re.match(r'^\w(?:[\w\.]*\w)?$', str(arg)):
        return True
    return False


def isDatabaseName(arg):
    if arg is None:
        return False
    if re.match(r'^\w+$', str(arg)):
        return True
    return False


def isDatabaseColumnName(arg):
    if arg is None:
        return False
    if re.match('^' + column_regex + '$', str(arg)):
        return True
    return False


def isDatabaseFieldName(arg):
    if arg is None:
        return False
    arg = str(arg)
    if re.match(r'^\d+$', arg) or re.match(r'^[A-Za-z][\w()*,._-]+[A-Za-z0-9)]$', arg):
        return True
    return False


def isDatabaseTableName(arg, allow_qualified=False):
    if arg is None:
        return False
    arg = str(arg)
    if allow_qualified is True:
        if re.match(r'^[A-Za-z0-9][\w\.]*[A-Za-z0-9]$', arg):
            return True
    else:
        if re.match(r'^[A-Za-z0-9]\w*[A-Za-z0-9]$', arg):
            return True
    return False


def isDatabaseViewName(arg, allow_qualified=False):
    return isDatabaseTableName(arg, allow_qualified)


def isDict(arg):
    # return type(arg).__name__ == 'dict'
    return isinstance(arg, dict)


def isDirname(arg):
    if arg is None:
        return False
    arg = str(arg)
    if re.match(r'^\s*$', arg):
        return False
    if re.match('^' + dirname_regex + '$', arg):
        return True
    return False


def isDomain(arg):
    if arg is None:
        return False
    arg = str(arg)
    if len(arg) > 255:
        return False
    if re.match('^' + domain_regex + '$', arg):
        return True
    return False


def isDomainStrict(arg):
    if arg is None:
        return False
    arg = str(arg)
    if len(arg) > 255:
        return False
    if re.match('^' + domain_regex_strict + '$', arg):
        return True
    return False


def isDnsShortname(arg):
    if arg is None:
        return False
    arg = str(arg)
    if len(arg) < 3 or len(arg) > 63:
        return False
    if re.match('^' + hostname_component + '$', arg):
        return True
    return False


# SECURITY NOTE: this only validates the email address is valid,
# it's doesn't make it safe to arbitrarily pass to commands or SQL etc!
def isEmail(arg):
    if arg is None:
        return False
    arg = str(arg)
    if len(arg) > 256:
        return False
    if re.match('^' + email_regex + '$', arg):
        return True
    return False


def isFilename(arg):
    if arg is None:
        return False
    arg = str(arg)
    if re.match('/$', arg) or re.match(r'^\s*$', arg):
        return False
    if re.match('^' + filename_regex + '$', arg):
        return True
    return False


def isFloat(arg, allow_negative=False):
    if arg is None:
        return False
    # wouldn't respect default of not allowing negative
    # if type(arg) == 'float':
    # if isinstance(arg, float):
    #     return True
    neg = ''
    if allow_negative is True:
        neg = '-?'
    if re.match('^' + neg + r'\d+(?:\.\d+)?', str(arg)):
        return True
    return False


def isFqdn(arg):
    if arg is None:
        return False
    arg = str(arg)
    if len(arg) > 255:
        return False
    if re.match('^' + fqdn_regex + '$', arg):
        return True
    return False


#def isHash


def isHex(arg):
    if arg is None:
        return False
    if re.match(r'^(?:0x)?[A-Fa-f\d]+$', str(arg)):
        return True
    return False


def isHost(arg):
    if arg is None:
        return False
    arg = str(arg)
    # special case to short-circuit failure when chaining find_active_server.py
    if arg in ('NO_SERVER_AVAILABLE', 'NO_HOST_AVAILABLE'):
        return False
    if len(arg) > 255:
        return False
    if re.match('^' + host_regex + '$', str(arg)):
        return True
    return False


def isHostname(arg):
    if arg is None:
        return False
    arg = str(arg)
    if len(arg) > 255:
        return False
    if re.match('^' + hostname_regex + '$', arg):
        return True
    return False


def isInt(arg, allow_negative=False):
    if arg is None:
        return False
    # wouldn't respect default of not allowing negative
    # if type(arg) == 'int':
    # if isinstance(arg, int):
    #     return True
    neg = ""
    if allow_negative:
        neg = "-?"
    if re.match('^' + neg + r'\d+(?:\.0+)?' + '$', str(arg)):
        return True
    return False


def isInterface(arg):
    if arg is None:
        return False
    if re.match(r'^(?:em|eth|bond|lo|docker)\d+|lo|veth[A-Fa-f0-9]+$', str(arg)):
        return True
    return False


def isIP(arg):
    if arg is None:
        return False
    arg = str(arg)
    octets = arg.split('.')
    if len(octets) > 4:
        return False
    if not re.match('^' + ip_regex + '$', str(arg)):
        return False
    for octet in octets:
        octet = int(octet)
        if int(octet) < 0 or int(octet) > 255:
            return False # pragma: no cover
    return True


def isIterable(arg):
    # collections.Iterable Python 2.6+
    return isinstance(arg, collections.Iterable)


def isIterableNotStr(arg):
    # collections.Iterable Python 2.6+
    return isinstance(arg, collections.Iterable) and not isStr(arg)


def isJavaException(arg):
    if arg is None:
        return False
    arg = str(arg)
    if re.match(r'(?:^\s+at|^Caused by:)\s+\w+(?:\.\w+)+', arg) or \
       re.match('^Exception in thread ', arg) or \
       re.search(r'\w+(?:\.\w+)+\(\w+\.java:\d+\)', arg) or \
       re.search(r'\(.+:[\w]+\(\d+\)\)', arg) or \
       re.search(r'(?:\b|_)(\w+\.)+\w+Exception\b', arg) \
       :
        return True
    return False


def isJson(arg):
    if not isStr(arg):
        return False
    try:
        json.loads(arg)
        return True
    except ValueError:
        pass
    return False


def isYaml(arg):
    if not isStr(arg):
        return False
    try:
        yaml.load(arg)
        return True
    except yaml.YAMLError:
        pass
    return False


def isXml(arg):
    if not isStr(arg):
        return False
    try:
        ET.fromstring(arg)
        return True
    # Python 2.7 throws xml.etree.ElementTree.ParseError, but Python 2.6 throws xml.parsers.expat.ExpatError
    # have to catch generic Exception to be able to handle both
    except Exception: # pylint: disable=broad-except
        pass
    return False


def isKrb5Princ(arg):
    if arg is None:
        return False
    if re.match('^' + krb5_principal_regex + '$', str(arg)):
        return True
    return False


def isLabel(arg):
    if arg is None:
        return False
    if re.match('^' + label_regex + '$', str(arg)):
        return True
    return False


def isLdapDn(arg):
    if arg is None:
        return False
    if re.match('^' + ldap_dn_regex + '$', str(arg)):
        return True
    return False


def isList(arg):
    # return type(arg).__name__ == 'list'
    return isinstance(arg, list)


def isListOrTuple(arg):
    return isList(arg) or isTuple(arg)


def isMinVersion(version, my_min):
    if version is None:
        log.warn("'%s' is not a recognized version format", version)
        return False
    if not isVersionLax(version):
        log.warn("'%s' is not a recognized version format", version)
        return False
    if not isFloat(my_min):
        code_error('invalid second arg passed to min_version')
    my_min = float(my_min)
    # exception should never happen because of the regex
    # try:
    _ = re.search(r'(\d+(?:\.\d+)?)', str(version))
    if _:
        version2 = float(_.group(1))
        if version2 >= my_min:
            return True
    # except ValueError as _:
    #     die("failed to detect version from string '%(version)s': %(_)s" % locals())
    return False


def isNagiosUnit(arg):
    if arg is None:
        return False
    arg = str(arg).lower()
    for unit in valid_nagios_units:
        if arg == unit.lower():
            return True
    return False


def isNoSqlKey(arg):
    if arg is None:
        return False
    if re.match(r'^([\w\_\,\.\:\+\-]+)$', str(arg)):
        return True
    return False


def isPathQualified(arg):
    if arg is None:
        return False
    if re.match(r'^(?:\.?\/)', str(arg)):
        return True
    return False


def isPort(arg):
    if arg is None:
        return False
    if not re.match(r'^\d+$', str(arg)):
        return False
    if int(arg) >= 1 and int(arg) <= 65535:
        return True
    return False


def isProcessName(arg):
    if arg is None:
        return False
    if re.match('^' + process_name_regex + '$', str(arg)):
        return True
    return False


def isPythonTraceback(arg):
    if arg is None:
        return False
    arg = str(arg)
    if re.search(r'^\s+File "' + filename_regex + r'", line \d+, in (?:<module>|[A-Za-z]+)', arg):
        return True
    elif re.search(r'Traceback \(most recent call last\):', arg):
        return True
    return False


def getPythonVersion():
    _ = re.match("^(" + version_regex_short + ")", sys.version.split('\n')[0])
    if _:
        # regex matched so no NumberFormatException on float cast
        return float(_.group(1))
    raise Exception("couldn't determine Python version!") # pragma: no cover
    # this works only from Python 2.7+
    #return '.'.join([str(sys.version_info.major), str(sys.version_info.minor), str(sys.version_info.micro)])
    #return float('.'.join([str(sys.version_info.major), str(sys.version_info.minor)]))


def isPythonVersion(expected):
    if expected is None:
        code_error('no expected version passed to isPythonVersion()')
    version = getPythonVersion()
    return version == expected


def isPythonMinVersion(_):
    if _ is None:
        code_error('no min version passed to isPythonMinVersion()')
    version = getPythonVersion()
    return isMinVersion(version, _)


def isRegex(arg):
    if arg is None:
        return False
    arg = str(arg)
    if arg.strip() == '':
        return False
    try:
        re.match(arg, "")
        return True
    except re.error:
        pass
    return False


# def isScalar


def isSet(arg):
    # return type(arg).__name__ == 'set'
    return isinstance(arg, set)


def isScientific(arg, allow_negative=False):
    if arg is None:
        return False
    neg = ""
    if allow_negative is True:
        neg = "-?"
    if re.match('^' + neg + r'\d+(?:\.\d+)?e[+-]?\d+$', str(arg), re.I):
        return True
    return False


# def isThreshold


def isStr(arg):
    # return type(arg).__name__ in [ 'str', 'unicode' ]
    if isPythonMinVersion(3):
        return isinstance(arg, str)
    else:                                                        # pylint thinks unicode is an undefined variable
        return isinstance(arg, str) or isinstance(arg, unicode)  # pylint: disable=undefined-variable
    # basestring is abstract superclass of both str and unicode
    # update: looks like this is removed in Python 3
    # return isinstance(arg, basestring)


def isStrStrict(arg):
    # return type(arg).__name__ in [ 'str', 'unicode' ]
    return isinstance(arg, str)


def isTuple(arg):
    # return type(arg).__name__ == 'tuple'
    return isinstance(arg, tuple)


def isUnicode(arg):
    # return type(arg).__name__ == 'unicode'
    if isPythonMinVersion(3):
        return isinstance(arg, str)
    else: # pylint thinks unicode is undefined variable just cos it's not in py3k
        return isinstance(arg, unicode) # pylint: disable=undefined-variable


def isUrl(arg):
    if arg is None:
        return False
    # checking for String yet another breakage between Python 2 and 3
    # see http://stackoverflow.com/questions/4843173/how-to-check-if-type-of-a-variable-is-string-in-python
    arg = str(arg).strip()
    if not re.search('://', arg):
        arg = 'http://' + arg
    if re.match('^' + url_regex + '$', arg):
        return True
    return False


def isUrlPathSuffix(arg):
    if arg is None:
        return False
    if re.match('^' + url_path_suffix_regex + '$', str(arg)):
        return True
    return False


def isUser(arg):
    if arg is None:
        return False
    if re.match('^' + user_regex + '$', str(arg)):
        return True
    return False


def isVersion(arg):
    if arg is None:
        return False
    if re.match('^' + version_regex + '$', str(arg)):
        return True
    return False


def isVersionLax(arg):
    if arg is None:
        return False
    if re.match('^' + version_regex_lax + '$', str(arg)):
        return True
    return False


def isYes(arg):
    if arg is None:
        return False
    if re.match(r'^\s*y(?:es)?\s*$', str(arg), re.I):
        return True
    return False


def isOS(arg):
    if arg is None:
        raise code_error('no arg passed to isOS()')
    if platform.system().lower() == str(arg).lower():
        return True
    return False


def isMac():
    return isOS('Darwin')


def isLinux():
    return isOS('Linux')


def isLinuxOrMac():
    return isLinux() or isMac()


supported_os_msg = "this program is only supported on %s at this time"


def mac_only():
    if not isMac():
        raise MacOnlyException(supported_os_msg % 'Mac/Darwin')
    return True


def linux_only():
    if not isLinux():
        raise LinuxOnlyException(supported_os_msg % 'Linux')
    return True


def linux_mac_only():
    if not isLinuxOrMac():
        raise Exception(supported_os_msg % 'Linux or Mac/Darwin')
    return True

# a little extra assertion that the values we're comparing are in fact ints/floats
def min_value(val, min_val):
    if not isFloat(val):
        code_error('invalid first arg passed to min_value(), must be float')
    if not isFloat(min_val):
        code_error('invalid second arg passed to min_value(), must be float')
    return max(val, min_val)


# msg_perf_thresholds
# msg_thresholds
# month2int
# open_file


def perf_suffix(arg):
    if arg is None:
        return ''
    arg = str(arg)
    prefix = r'[\b\s\._-]'
    if re.search(prefix + 'bytes', arg):
        return 'b'
    elif re.search(prefix + 'millis', arg):
        return 'ms'
    return ''


# def pkill(search, kill_flags = ""):
#     search = str(search)
#     if not search:
#         code_error('no search arg specified for pkill sub')
#     if not kill_flags:
#         kill_flags = ''
#     if type(search) != str:
#         code_error('non-string first arg passed to pkill for search')
#     # XXX: FIXME
#     search = search.replace('/', '\\/')
#     search = search.replace("'", '.')
#     # XXX: FIXME
#     return os.popen("ps aux | awk '/" + search + "/ {print \$2}' |
#                      while read pid; do kill " + kill_flags + " $pid >/dev/null 2>&1; done")


def plural(arg):
    # TODO: add support for arrays, dictionaries
    # if type(arg) == int or type(arg) == float:
    if isFloat(arg):
        arg = float(arg)
        if arg == 1:
            return ''
        else:
            return 's'
    return ''

def space_suffix(arg):
    if arg:
        return str(arg) + ' '
    return arg

def space_prefix(arg):
    if arg:
        return ' ' + str(arg)
    return arg


# def prompt


def random_alnum(num):
    if not isInt(num):
        code_error('invalid length passed to random_alnum')
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    import random
    _ = ''.join(random.choice(chars) for _ in range(num))
    return _


# def resolve_ip


def sec2min(secs):
    if not isFloat(secs):
        # raise CodingError('non-float passed to sec2min')
        return ''
    return '%d:%.2d' % (int(secs / 60), secs % 60)


def sec2human(secs):
    if not isFloat(secs):
        code_error('invalid non-float argument passed to sec2human')
    human_time = ''
    if secs >= 86400:
        days = int(secs / 86400)
        human_time += '%d day%s ' % (days, plural(days))
        secs %= 86400
    if secs >= 3600:
        hours = int(secs / 3600)
        human_time += '%d hour%s ' % (hours, plural(hours))
        secs %= 3600
    if secs >= 60:
        mins = int(secs / 60)
        human_time += '%d min%s ' % (mins, plural(mins))
        secs %= 60
    human_time += '%d sec%s' % (secs, plural(secs))
    return human_time


# set_http_timeout
# set_sudo
# set_timeout


def set_timeout(secs, handler=None):
    if not isInt(secs):
        raise CodingError('non-integer passed for secs to set_timeout()')
    if handler:
        signal.signal(signal.SIGALRM, handler)
    signal.alarm(secs)


def skip_java_output(arg):
    if arg is None:
        return False
    if re.search('Class JavaLaunchHelper is implemented in both|^SLF4J', str(arg)):
        return True
    return False


def split_if_str(arg, sep):
    if isStr(arg):
        return arg.split(sep)
    return arg


def uniq_list(my_list):
    if not isList(my_list):
        raise CodingError('non-list passed to uniq_list')
    return list(set(my_list))


# collections.OrderedDict >= Python 2.7+
def uniq_list_ordered(my_list):
    if not isList(my_list):
        raise CodingError('non-list passed to uniq_list_ordered')
    # list2 = []
    # for x in my_list:
    #     if not x in list2:
    #         list2.append(x)
    # return list2
    seen = set()
    seen_add = seen.add
    return [x for x in my_list if not (x in seen or seen_add(x))]


def merge_dicts(*args):
    '''Merge any number of dicts and return result. Precedence goes to key value pairs in latter dicts'''
    tmp_dict = {}
    for arg in args:
        if not isDict(arg):
            code_error('passed non-dictionary argument to merge_dicts()')
        tmp_dict.update(arg)
    return tmp_dict


#def user_exists(user):


# ============================================================================ #
#                           Options Validation
# ============================================================================ #

def validate_alnum(arg, name):
    if not name:
        code_error("second arg 'name' not defined when calling validate_alnum()")
    if not arg:
        raise InvalidOptionException('%(name)s not defined' % locals())
    if isAlNum(arg):
        log_option(name, arg)
        return True
    raise InvalidOptionException("invalid %(name)s '%(arg)s' defined: must be alphanumeric" % locals())


def validate_aws_access_key(arg):
    if not arg:
        raise InvalidOptionException('aws access key not defined')
    arg = str(arg)
    if isAwsAccessKey(arg):
        log_option('aws access key', 'X' * 18 + arg[18:20])
        return True
    raise InvalidOptionException('invalid aws access key defined: must be 20 alphanumeric characters')


def validate_aws_bucket(arg):
    if not arg:
        raise InvalidOptionException('aws bucket not defined')
    arg = str(arg)
    if isDnsShortname(arg):
        log_option('aws bucket', arg)
        return True
    raise InvalidOptionException('invalid aws access key defined: must be 20 alphanumeric characters')


def validate_aws_secret_key(arg):
    if not arg:
        raise InvalidOptionException('aws secret key not defined')
    arg = str(arg)
    if isAwsSecretKey(arg):
        log_option('aws secret key', 'X' * 38 + arg[38:40])
        return True
    raise InvalidOptionException('invalid aws secret key defined: must be 40 alphanumeric characters')


def validate_chars(arg, name, chars):
    if not name:
        code_error("second arg 'name' not defined when calling validate_chars()")
    if not arg:
        raise InvalidOptionException('%(name)s not defined' % locals())
    if isChars(arg, chars):
        log_option(name, arg)
        return True
    raise InvalidOptionException("invalid %(name)s '%(arg)s' defined - must be one of the following chars: %(chars)s" \
                                 % locals())


def validate_collection(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)scollection not defined' % locals())
    if isCollection(arg):
        log_option('%(name)scollection' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)scollection '%(arg)s' defined: " % locals() + \
                                 "must be alphanumeric, with optional periods in the middle")


def validate_database(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)sdatabase not defined' % locals())
    if isDatabaseName(arg):
        log_option('%(name)sdatabase' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)sdatabase '%(arg)s' defined: must be alphanumeric" % locals())


def validate_database_columnname(arg):
    if not arg:
        raise InvalidOptionException('column not defined')
    if isDatabaseColumnName(arg):
        log_option('column', arg)
        return True
    raise InvalidOptionException("invalid column '%(arg)s' defined: must be alphanumeric" % locals())


def validate_database_fieldname(arg):
    if not arg:
        raise InvalidOptionException('field not defined')
    if isDatabaseFieldName(arg):
        log_option('field', arg)
        return True
    raise InvalidOptionException("invalid field '%(arg)s' defined: must be alphanumeric" % locals())


def validate_database_tablename(arg, name='', allow_qualified=False):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)stable not defined' % locals())
    if isDatabaseTableName(arg, allow_qualified):
        log_option('%(name)stable' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)stable '%(arg)s' defined: must be alphanumeric" % locals())


def validate_database_viewname(arg, name='', allow_qualified=False):
    if name:
        name += " "
    if not arg:
        raise InvalidOptionException('%(name)sview not defined' % locals())
    if isDatabaseViewName(arg, allow_qualified):
        log_option('%(name)sview' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)sview '%(arg)s' defined: must be alphanumeric" % locals())


def validate_database_query_select_show(arg, name=''):
    if name:
        name += " "
    if not arg:
        raise InvalidOptionException('%(name)squery not defined' % locals())
    if not re.match(r'^\s*((?:SHOW|SELECT)\s+.+)$', str(arg), re.I):
        raise InvalidOptionException('invalid %(name)squery defined: may only be a SELECT or SHOW statement' % locals())
    if re.search(r'\b(?:insert|update|delete|create|drop|alter|truncate)\b', arg, re.I):
        raise InvalidOptionException('invalid %(name)squery defined: found DML statement keywords!' % locals())
    log_option('%(name)squery' % locals(), arg)
    return True


def validate_dirname(arg, name='', nolog=False):
    if name:
        name += " "
    if not arg:
        raise InvalidOptionException('%(name)sdirectory name not defined' % locals())
    if isDirname(arg):
        if not nolog:
            log_option('%(name)sdirectory' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)sdirectory name defined ('%(arg)s' does not match regex criteria)" \
                                 % locals())


def validate_directory(arg, name='', nolog=False):
    if name:
        name += " "
    if not arg:
        raise InvalidOptionException('%(name)sdirectory not defined' % locals())
    validate_dirname(arg, name, nolog)
    if os.path.isdir(arg):
        if not nolog:
            log_option('%(name)sdirectory' % locals(), arg)
        return True
    raise InvalidOptionException("%(name)sdirectory not found: '%(arg)s'"  % locals())

def validate_dir(arg, name='', nolog=False):
    return validate_directory(arg, name, nolog)

def validate_domain(arg, name=''):
    if name:
        name += " "
    if not arg:
        raise InvalidOptionException('%(name)sdomain not defined' % locals())
    if isDomain(arg):
        log_option('%(name)sdomain' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)sdomain '%(arg)s' defined" % locals())


# SECURITY NOTE: this only validates the email address is valid,
# it's doesn't make it safe to arbitrarily pass to commands or SQL etc!
def validate_email(arg):
    if not arg:
        raise InvalidOptionException('email not defined')
    if isEmail(arg):
        log_option('email', arg)
        return True
    raise InvalidOptionException("invalid email address defined ('%(arg)s' does not match regex criteria)" % locals())


def validate_filename(arg, name='', nolog=False):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)sfilename not defined' % locals())
    if isFilename(arg):
        if not nolog:
            log_option('%(name)sfilename' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)sfilename ('%(arg)s' does not match regex criteria)" % locals())


def validate_file(arg, name='', nolog=False):
    # ends up with double spacing as validate_filename also adds
    # if not arg:
    #     raise InvalidOptionException('%(name)sfilename not defined' % locals())
    validate_filename(arg, name, nolog=nolog)
    if os.path.isfile(arg):
        # if not nolog:
        #     log_option('%(name)sfile' locals(), arg)
        return True
    if name:
        name += ' '
    raise InvalidOptionException("%(name)sfile not found: '%(arg)s'" % locals())


def validate_files(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)sfiles not defined' % locals())
    files = []
    if isStr(arg):
        files = [x.strip() for x in arg.split(',')]
    elif isListOrTuple(arg):
        files = arg
    else:
        raise CodingError('non-list/tuple passed to parse_file_option')
    # not flexible enough
    # list(itertools.chain(*files))
    # list(itertools.chain.from_iterable(files))
    # files = [ str(x).split(',').strip() for x in files ]
    # files = list(itertools.chain(*[str(x).split(',') for x in files]))
    # custom flatten def
    # consider def to split if isStr
    files2 = flatten([split_if_str(x, ',') for x in files])
    files = list(files2)
    for _ in files:
        validate_file(_, name, False)
    log_option('files', files)
    return files


def validate_float(arg, name, my_min, my_max):
    if not name:
        code_error('no name passed for second arg to validate_float()')
    if arg is None:
        raise InvalidOptionException('%(name)s not defined' % locals())
    if isFloat(arg, allow_negative=True):
        arg = float(arg)
        try:
            my_min = float(my_min)
            my_max = float(my_max)
        except ValueError as _:
            code_error('invalid my_min/my_max (%(my_min)s/%(my_max)s) passed to validate_float(): %(_)s' % locals())
        if arg >= my_min and arg <= my_max:
            log_option(name, arg)
            return True
        raise InvalidOptionException('invalid %(name)s defined: must be real number between %(my_min)s and %(my_max)s' \
                                     % locals())
    raise InvalidOptionException("invalid %(name)s '%(arg)s' defined: must be a real number" % locals())


def validate_fqdn(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)sFQDN not defined' % locals())
    if isFqdn(arg):
        log_option('%(name)sfqdn' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)sFQDN '%(arg)s' defined" % locals())


def validate_host(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)shost not defined' % locals())
    if isHost(arg):
        log_option('%(name)shost' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)shost '%(arg)s' defined: not a valid hostname or IP address"
                                 % locals())


def validate_hostname(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)shostname not defined' % locals())
    if isHostname(arg):
        log_option('%(name)shostname' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)shostname '%(arg)s' defined: not a valid hostname" % locals())


def validate_hosts(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)shosts not defined' % locals())
    arg = str(arg)
    host_list = [host.strip() for host in arg.split(',')]
    if not host_list:
        raise InvalidOptionException('%(name)shosts list is empty' % locals())
    return validate_host_list(host_list, name.strip())


def validate_host_list(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)shost list not defined' % locals())
    if not isList(arg):
        raise InvalidOptionException('%(name)s host list is not a list!' % locals())
    for (index, host) in enumerate(arg):
        validate_host(host, name + 'index {0}'.format(index + 1))
    return True


def validate_hostport(arg, name='', port_optional=False):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)shost:port not defined' % locals())
    try:
        parts = arg.split(':')
        len_parts = len(parts)
        if len_parts == 1 and port_optional is True:
            validate_host(parts[0])
            return True
        elif len(parts) == 2 and isHost(parts[0]) and isPort(parts[1]):
            log_option('%(name)shost:port' % locals(), arg)
            return True
        raise ValueError
    except ValueError:
        raise InvalidOptionException("invalid %(name)shost:port '%(arg)s' defined: " % locals() +
                                     "not a valid hostname /IP address + port combination")

def validate_hostport_list(arg, name='', port_optional=False):
    if name:
        name += ' '
    if not isList(arg):
        raise InvalidOptionException('%(name)s host:port list is not a list!' % locals())
    if not arg:
        raise InvalidOptionException('empty %(name)shost:port list' % locals())
    for host in arg:
        if ':' in host:
            validate_hostport(host)
        elif port_optional is not True:
            raise InvalidOptionException('port suffix is mandatory for every host!')
        else:
            validate_host(host)
    return True


def validate_int(arg, name, my_min, my_max):
    if not name:
        code_error('no name passed for second arg to validate_int()')
    if arg is None:
        raise InvalidOptionException('%(name)s not defined' % locals())
    if isInt(arg, allow_negative=True):
        arg = int(arg)
        try:
            if my_min is not None:
                my_min = int(my_min)
            if my_max is not None:
                my_max = int(my_max)
        except ValueError as _:
            code_error('invalid my_min/my_max (%(my_min)s/%(my_max)s) passed to validate_int(): %(_)s' % locals())
        if my_min is not None and arg < my_min:
            raise InvalidOptionException("invalid %(name)s '%(arg)s' defined: cannot be less than %(my_min)s"
                                         % locals())
        if my_max is not None and arg > my_max:
            raise InvalidOptionException("invalid %(name)s '%(arg)s' defined: cannot be greater than %(my_max)s"
                                         % locals())
        log_option(name, arg)
        return True
    raise InvalidOptionException("invalid %(name)s '%(arg)s' defined: must be a real number" % locals())



def validate_interface(arg):
    if not arg:
        raise InvalidOptionException('interface not defined')
    if isInterface(arg):
        log_option('interface', arg)
        return True
    raise InvalidOptionException("invalid interface '%(arg)s' defined: not a valid interface" % locals())


def validate_ip(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)sIP not defined' % locals())
    if isIP(arg):
        log_option('%(name)sIP' % locals(), arg)
        return True
    raise InvalidOptionException("invalid IP '%(arg)s' defined" % locals())


def validate_krb5_princ(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)skrb5 principal not defined' % locals())
    if isKrb5Princ(arg):
        log_option('%(name)skrb5 principal' % locals(), arg)
        return True
    raise InvalidOptionException("invalid krb5 principal '%(arg)s' defined" % locals())


def validate_krb5_realm(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)skrb5 realm not defined' % locals())
    if isDomain(arg):
        log_option('%(name)skrb5 realm' % locals(), arg)
        return True
    raise InvalidOptionException("invalid krb5 realm '%(arg)s' defined" % locals())


def validate_label(arg):
    if not arg:
        raise InvalidOptionException('label not defined')
    if isLabel(arg):
        log_option('label', arg)
        return True
    raise InvalidOptionException("invalid label '%(arg)s' defined: must be an alphanumeric identifier")


def validate_ldap_dn(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('ldap %(name)sdn not defined' % locals())
    if isLdapDn(arg):
        log_option('ldap %(name)sdn' % locals(), arg)
        return True
    raise InvalidOptionException('invalid ldap %(name)sdn defined' % locals())


# validate_metrics

def validate_nosql_key(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)skey not defined' % locals())
    if isNoSqlKey(arg):
        log_option('%(name)skey' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)skey '%(arg)s' defined: may only contain characters: " % locals() + \
                                 "alphanumeric, commas, colons, underscores, pluses, dashes")


def validate_port(arg, name=''):
    if name:
        name += ' '
    if arg is None:
        raise InvalidOptionException('%(name)sport not defined' % locals())
    if isPort(arg):
        log_option('%(name)sport' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)sport number '%(arg)s' defined: " % locals() +
                                 "must be a positive integer between 1 and 65535")


def validate_process_name(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)sprocess name not defined' % locals())
    if isProcessName(arg):
        log_option('%(name)sprocess name' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)sprocess name '%(arg)s' defined" % locals())


# def validate_program_path


def validate_password(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)spassword not defined' % locals())
    if re.search('[`\'"]|\\$\\(', arg):
        raise InvalidOptionException('invalid %(name)spassword defined, may not contain quotes, ' % locals() + \
                                     'subshell escape sequences like $( ) or backticks')
    log_option('%(name)spassword' % locals(), '<omitted>')
    return True


def validate_regex(arg, name=''):
    if name:
        name += ' '
    if isRegex(arg):
        log_option('{0}regex'.format(name), arg)
        return True
    raise InvalidOptionException("invalid %(name)sregex '%(arg)s' defined" % locals())


# def validate_resolvable


def validate_units(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)sunits not defined' % locals())
    if isNagiosUnit(arg):
        log_option('%(name)sunits' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)sunits '%(arg)s' defined: must be one of: " % locals() +
                                 str(valid_nagios_units))


def validate_url(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)surl not defined' % locals())
    if isUrl(arg):
        log_option('%(name)surl' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)surl '%(arg)s' defined" % locals())


def validate_url_path_suffix(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)surl path suffix not defined' % locals())
    if isUrlPathSuffix(arg):
        log_option('%(name)surl path suffix' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)surl path suffix '%(arg)s' defined" % locals())


def validate_user(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%(name)suser not defined' % locals())
    if isUser(arg):
        log_option('%(name)suser' % locals(), arg)
        return True
    raise InvalidOptionException("invalid %(name)suser '%(arg)s' defined: must be alphanumeric" % locals())


# user_exists() not implemented yet
# def validate_user_exists(arg, name=''):
#     if name:
#         name += ' '
#     if not arg:
#         raise InvalidOptionException('%(name)suser not defined' locals())
#     validate_user(arg)
#     if user_exists(arg):
#         return True
#     raise InvalidOptionException('invalid %(name)suser defined, not found on local system' % locals())


# ============================================================================ #


def vlog(msg):
    log.warn(msg)


def vlog2(msg):
    log.info(msg)


def vlog3(msg):
    log.debug(msg)


def log_option(name, option):
    log.info('%s:  %s', name, option)


def which(my_bin):
    if not isFilename(my_bin):
        raise InvalidFilenameException("invalid filename '%(my_bin)s' supplied to which()" % locals())
    my_bin = str(my_bin)
    if re.match(r'^.{0,2}\/', my_bin):
        if os.path.isfile(my_bin):
            if os.access(my_bin, os.X_OK):
                return my_bin
            raise FileNotExecutableException("'%(my_bin)s' is not executable" % locals())
        else:
            # flows nicer in client code to just return None and use as part of "if" tests etc rather than needing
            # exception blocks
            # raise FileNotFoundException("'%s' not found" % my_bin)
            return None
    else:
        for basepath in os.getenv('PATH', '').split(os.pathsep):
            path = os.path.join(basepath, my_bin)
            if os.path.isfile(path):
                if os.access(path, os.X_OK):
                    return path
    # flows nicer in client code to just return None and use as part of "if" tests etc rather than needing
    # exception blocks
    # raise FileNotFoundException("could not find executable file '%s' in $PATH (%s)" % (my_bin, os.getenv('PATH', '')))
    return None


prog = os.path.basename(get_topfile())


# ============================================================================ #
#                               PySpark Utils
# ============================================================================ #

def pyspark_path():
    spark_home = os.getenv('SPARK_HOME', None)
    if spark_home:
        # doesn't contain py4j may as well just use the already unpacked version
        #sys.path.append(os.path.join(spark_home, 'python/lib/pyspark.zip'))
        sys.path.append(os.path.join(spark_home, 'python'))
        # more abstract without version number but not available in spark bin download
        #sys.path.append(os.path.join(spark_home, 'python/build'))
        for _ in glob.glob(os.path.join(spark_home, 'python/lib/py4j-*-src.zip')):
            sys.path.append(_) # pragma: no cover
    else:
        warn("SPARK_HOME not set - probably won't find PySpark libs")
    # needed for Spark 1.4+
    _ = os.environ.get('PYSPARK_SUBMIT_ARGS', '')
    if 'pyspark-shell' not in _:
        _ += ' pyspark-shell'
    os.environ["PYSPARK_SUBMIT_ARGS"] = _

# TODO: XXX: review
# def import_pyspark():
    #pyspark_path()
    # doesn't seem to import properly using 'from module import blah' style
    # seems to only work for complete module imports
    # try:
    #     global SparkContext
    #     global SparkConf
    #     global SQLContext
    #     import pyspark
    #     from pyspark import SparkContext as a
    #     from pyspark import SparkConf as b
    #     from pyspark.sql import SQLContext as c
    #     print(a)
    #     print(b)
    #     print(c)
    #     global SparkContext
    #     global SparkConf
    #     global SQLContext
    #     SparkContext = a
    #     SparkConf = b
    #     SQLContext = c
    # except ImportError, e:
    #     print('module import failed: %s' % e, file=sys.stderr)
    #     sys.exit(ERRORS['UNKNOWN'])

# from math import pow, fabs, sqrt
# def squaredError(label, prediction):
#     """Calculates the the squared error for a single prediction.
#
#     Args:
#         label (float): The correct value for this observation.
#         prediction (float): The predicted value for this observation.
#
#     Returns:
#         float: The difference between the `label` and `prediction` squared.
#     """
#     return pow(fabs(label - prediction), 2)
#
# def calcRMSE(labelsAndPreds):
#     """Calculates the root mean squared error for an `RDD` of (label, prediction) tuples.
#
#     Args:
#         labelsAndPred (RDD of (float, float)): An `RDD` consisting of (label, prediction) tuples.
#
#     Returns:
#         float: The square root of the mean of the squared errors.
#     """
#     return sqrt( labelsAndPreds.map(lambda (label, prediction): squaredError(label, prediction) ).mean() )


# ============================================================================ #

#DEFAULT_TIMEOUT = 10
#CHECK_NAME      = ""
#
#
#def end(status, message):
#    """Prints a message and exits. First arg is the status code
#    Second Arg is the string message"""
#
#    if CHECK_NAME in (None, ""):
#        check_name = ""
#    else:
#        check_name = str(CHECK_NAME).strip() + " "
#
#    if status == OK:
#        print "%sOK: %s" % (check_name, message)
#        sys.exit(OK)
#    elif status == WARNING:
#        print "%sWARNING: %s" % (check_name, message)
#        sys.exit(WARNING)
#    elif status == CRITICAL:
#        print "%sCRITICAL: %s" % (check_name, message)
#        sys.exit(CRITICAL)
#    else:
#        # This one is intentionally different
#        print "UNKNOWN: %s" % message
#        sys.exit(UNKNOWN)
#
## ============================================================================ #
#
#class NagiosTester(object):
#    """Holds state for the Nagios test"""
#
#    def validate_timeout(self):
#        """Exits with an error if the timeout is not valid"""
#
#        if self.timeout is None:
#            self.timeout = DEFAULT_TIMEOUT
#        try:
#            self.timeout = int(self.timeout)
#            if not 1 <= self.timeout <= 65535:
#                end(UNKNOWN, "timeout must be between 1 and 3600 seconds")
#        except ValueError:
#            end(UNKNOWN, "timeout number must be a whole number between " \
#                       + "1 and 3600 seconds")
#
#        if self.verbosity is None:
#            self.verbosity = 0
