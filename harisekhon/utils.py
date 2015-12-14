#
#  Author: Hari Sekhon
#  Date: 2008-03-06 15:20:22 +0000 (Thu, 06 Mar 2008)
#  Reinstantiated Date:
#        2013-07-04 00:08:32 +0100 (Thu, 04 Jul 2013)
#
#  https://github.com/harisekhon/pylib
#
#  License: see accompanying LICENSE file
#

""" Personal Library originally started to standardize Nagios Plugin development """

from __future__ import print_function

import ast
import collections
import inspect
import itertools
import json
import os
import re
import logging
import logging.config
import platform
# import signal
# import string
import signal
import sys
import warnings
import xml.etree.ElementTree as ET
# not available Python < 2.7
# try:
#     from xml.etree.ElementTree import ParseError
# except:
#     pass
# Python 2.6 throws ExpatError instead of ParseError
# from xml.parsers.expat import ExpatError

__author__      = 'Hari Sekhon'
__version__     = '0.9.8'

# Standard Nagios return codes
ERRORS = {
    "OK"        : 0,
    "WARNING"   : 1,
    "CRITICAL"  : 2,
    "UNKNOWN"   : 3,
    "DEPENDENT" : 4
}

libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_caller():
    # return inspect.currentframe().f_back.f_back
    # try:
    return inspect.stack()[2][3]
    # except Exception:
    #     return '<failed to get caller function>'

prog = os.path.basename(inspect.getfile(inspect.currentframe().f_back))

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

def support_msg(repo="pytools"):
    if isBlankOrNone(repo):
        repo = "pylib"
    support_msg = 'Please try latest version from https:/github.com/harisekhon/%s and if problem persists paste the full output in to a ticket for a fix/update at https://github.com/harisekhon/%s/issues' % (repo, repo)
    return support_msg


def printerr(msg, indent=False):
    if indent:
        print(">>> ", end='', file=sys.stderr)
    print("%s" % msg, file=sys.stderr)


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
    raise CodingErrorException(msg)


def quit(status, msg=''):
    """ Quit with status code from ERRORS dictionary after printing given msg """
    status = str(status)
    if status not in ERRORS:
        warnings.warn("invalid status '%s' passed to quit() by caller '%s', defaulting to critical" % (status, get_caller()))
        status = 'CRITICAL'
    if msg:
        # log.error('%s: %s' % (status, msg))
        print('%s: %s' % (status, msg))
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
    quit(status)


def get_topfile():
    # this gets 'python -m unittest' as filename
    # filename = sys.argv[0]
    frame = inspect.stack()[-1][0]
    # filename = inspect.stack()[-1][1]
    filename = inspect.getfile(frame)
    # filename = os.path.splitext(filename)[0] + '.py'
    filename = re.sub('.pyc$', '.py', filename)
    assert isStr(filename)
    assert isFilename(filename)
    return filename


def get_file_docstring(filename):
    assert isStr(filename)
    assert isFilename(filename)
    # .pyc files cause the following error:
    # TypeError: compile() expected string without null bytes
    filename = re.sub('.pyc$', '.py', filename)
    c = ast.parse(open(filename).read(), filename=filename, mode='exec')
    return ast.get_docstring(c)
    # inspect.getdoc is another option but looks like it'll only get docstring of object, we want file/module
###### old way #####
#    # returns a code object
#    co = compile(open(filename).read(), filename, 'exec')
#    assert isCode(co)
#    # just let it traceback if something is not as expected so I know if something changes, otherwise will silently start dropping usage descriptions
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
    if re.search('\.py$', filename):
        tree = ast.parse(open(filename).read(), filename=filename, mode='exec')
        # print(ast.dump(tree))
        # print(dir(tree._fields))
        for node in (n for n in tree.body if isinstance(n, ast.Assign)):
            if len(node.targets) == 1:
                name = node.targets[0]
                if isinstance(name, ast.Name) and name.id == '__version__':
                    v = node.value
                    if isinstance(v, ast.Str):
                        return v.s
    return None


def get_file_github_repo(filename):
    assert isStr(filename)
    assert isFilename(filename)
    # .pyc files cause the following error:
    # TypeError: compile() expected string without null bytes
    filename = re.sub('.pyc$', '.py', filename)
    # TODO: XXX: what bout using ast.get_docstring for this? or inspect.getdoc
    # returns a code object
    f = open(filename)
    for line in f:
        if 'https://github.com/harisekhon' in line:
            f.close()
            return line.lstrip('#').strip()
    f.close()
    return ''


def gen_prefixes(prefixes, names, sort_by_names=False):
    if isStr(prefixes):
        prefixes = [prefixes]
    if isStr(names):
        names = [names]
    if not isIterableNotStr(prefixes):
        raise CodingErrorException('non-iterable passed for prefixes to prefix()')
    if not isIterableNotStr(names):
        raise CodingErrorException('non-iterable passed for names to prefix()')
    # Python 2.6+ only
    # for pair in itertools.product(prefixes, names):
    if sort_by_names:
        pairs = [(x,y) for y in names for x in prefixes]
    else:
        pairs = [(x,y) for x in prefixes for y in names]
    for pair in pairs:
        result = '_'.join(str(z) for z in pair if z)
        # result = result.lstrip('_') # handled by 'if z' now
        if result:
            yield result


def getenv(var, default=None):
    if not isStr(var):
        raise CodingErrorException('supplied non-string for var arg to getenv()')
    if isBlankOrNone(var):
        raise CodingErrorException('supplied blank string for var arg to getenv()')
    log.debug('checking for environment variable: %s' % var)
    var = str(var).strip()
    # env_var = re.sub('[^A-Z0-9]', '_', var.upper())
    return os.getenv(var, default)


def getenvs2(vars, default=None, prefix=''):
    log.setLevel(logging.DEBUG)
    assert isStr(prefix)
    assert prefix is not None
    # if not isStr(prefix):
    #     raise CodingErrorException('non-string passed for prefix to getenvs()')
    # if isBlankOrNone(prefix):
    #     raise CodingErrorException('blank/none prefix passed to getenvs()')
    result = None
    assert isStr(vars) or isList(vars)
    if isStr(vars):
        for var in gen_prefixes(prefix, vars, True):
            result = getenv(var)
            if result is None:
                break
    elif isList(vars):
        for var in vars:
            assert isStr(var)
            # if not isStr(var):
            #     raise CodingErrorException('non-string passed in array to getenvs()')
        for var in gen_prefixes(prefix, vars, True):
            result = getenv(var)
            if result is not None:
                break
    if result is None:
        result = default
    return result


def getenvs(name, vars, default):
    if not isStr(name):
        raise CodingErrorException('passed non-string for name to getenvs2()')
    name = name.upper()
    assert isStr(vars) or isList(vars)
    # exclude showing the default for sensitive options
    is_sensitive = False
    sensitive_regex = re.compile('password|passphrase|secret', re.I)
    if isStr(vars):
        vars = vars.upper()
        if sensitive_regex.search(vars):
            is_sensitive = True
    elif isList(vars):
        for v in vars:
            assert isStr(v)
        for v in vars:
            if sensitive_regex.search(v):
                is_sensitive = True
                break
        vars = [v.upper() for v in vars]
    help = ', '.join(gen_prefixes([name, ''], vars)).upper()
    if default != None and not is_sensitive:
        help += ', default: %(default)s' % locals()
    return help, getenvs2(vars, default, name)


# ============================================================================ #
#                              Custom Exceptions
# ============================================================================ #

class CodingErrorException(AssertionError):
    pass


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
    if 'JYTHON_JAR' in dir(sys):
        return True
    else:
        return False


def jython_only():
    """ Die unless we are inside Jython """
    if not isJython():
        die('not running in Jython!')


def get_jython_exception():
    #import traceback; traceback.print_exc()
    if sys.exc_info()[1] == None:
        return ''
    else:
        # return sys.exc_info()[1].toString()
        return sys.exc_info()[1].message


def log_jython_exception():
    """ logs last Jython Exception """
    e = get_jython_exception()
    log.error('Error: %s' % e)
    if isJavaOOM(e):
        log.error(java_oom_fix_msg())


def isJavaOOM(arg):
    # if arg == 'java.lang.OutOfMemoryError: Java heap space':
    if arg == None:
        return False
    if 'java.lang.OutOfMemoryError' in arg:
        return True
    return False


def java_oom_fix_msg():
    return '\nAdd/Increase -J-Xmx<value> command line argument\n'


# ============================================================================ #

def flatten(arg):
    if not isIterableNotStr(arg):
        yield arg
        return
    #     raise CodingErrorException('passed non-iterable to flatten()')
    # if isInt(arg) or isFloat(arg):
    #     yield arg
    # else:
    for x in arg:
        if isIterableNotStr(x):
            for sub in flatten(x):
                yield sub
        else:
            yield x


def read_file_without_comments(filename):
    return [ x.rstrip("\n").split("#")[0].strip() for x in open(filename).readlines() ]


def jsonpp(jsonData):
    if isStr(jsonData):
        jsonData = json.loads(jsonData)
    return json.dumps(jsonData, sort_keys=True, indent=4, separators=(',', ': '))


def list_sort_dicts_by_value(myList, key):
    if not isList(myList):
        raise InvalidArgumentException('non-list passed as first arg to list_sort_dicts_by_key()')
    if not isStr(key):
        raise InvalidArgumentException('non-string passed as second arg to list_sort_dicts_by_key()')
    myVals = {}
    myReturnList = []
    for d in myList:
        if not isDict(d):
            raise AssertionError("list item '%s' is not a dict" % d)
        val = d[key]
        if not isStr(val):
            raise AssertionError("list key '%s' value '%s' is not a string" % (key, val))
        myVals[val.lower()] = 1
    # for val in sorted(myVals.keys()):
    for val in sorted(myVals):
        for d in myList:
            val2 = d[key].lower()
            if val == val2:
                myReturnList.append(d)
    return myReturnList


# ============================================================================ #
#                                   REGEX
# ============================================================================ #

# years and years of Regex expertise and testing has gone in to this, do not edit!
# This also gives flexibility to work around some situations where domain names may not be quite valid (eg .local/.intranet) but still keep things quite tight
# There are certain scenarios where other generic libraries don't help with these

_tlds = set()

def _load_tlds(file):
    fh = open(file)
    tld_count = 0
    re_blank      = re.compile('^\s*$')
    re_alnum_dash = re.compile('^[A-Za-z0-9-]+$')
    for line in fh.readlines():
        line = line.split('#')[0]
        line = line.strip()
        if re_blank.match(line):
            continue
        if(re_alnum_dash.match(line)):
            _tlds.add(line)
            tld_count += 1
        else:
            warnings.warn("TLD: '%s' from tld file '%s' not validated, skipping that TLD" % (line, file))
    log.debug("loaded %s TLDs from file '%s'" % (tld_count, file) )

_tld_file = libdir + '/resources/tlds-alpha-by-domain.txt'
_load_tlds(_tld_file)

def _check_tldcount():
    log.debug('%s total unique TLDs loaded' % len(_tlds))
    # must be at least this many if the IANA set loaded properly
    if len(_tlds) < 1000:
        code_error('%s tlds loaded, expected >= 1000' % len(_tlds))
    # make sure we don't double load TLD list
    if len(_tlds) > 2000:
        code_error('%s tlds loaded, expected <= 2000' % len(_tlds))

_check_tldcount()

_custom_tlds = libdir + '/resources/custom_tlds.txt'
if(os.path.isfile(_custom_tlds)):
    _load_tlds(_custom_tlds)

tld_regex = r'(?i)\b(?:' + '|'.join(_tlds) + r')\b'

domain_component_regex = r'\b[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\b'
# AWS regex from http://blogs.aws.amazon.com/security/blog/tag/key+rotation
aws_access_key_regex = r'(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])'
aws_secret_key_regex = r'(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])'
domain_regex       = r'(?:' + domain_component_regex + '\.)*' + tld_regex
domain_regex2      = r'(?:' + domain_component_regex + '\.)+' + tld_regex
domain_regex_strict = domain_regex2
# must permit numbers as valid host identifiers that are being used in the wild in FQDNs
hostname_component = r'\b[A-Za-z0-9](?:[A-Za-z0-9_\-]{0,61}[a-zA-Z0-9])?\b'
aws_host_component = r'ip-(?:10-\d+-\d+-\d+|172-1[6-9]-\d+-\d+|172-2[0-9]-\d+-\d+|172-3[0-1]-\d+-\d+|192-168-\d+-\d+)'
hostname_regex     = hostname_component + r'(?:\.' + domain_regex + ')?'
aws_hostname_regex = aws_host_component + r'(?:\.' + domain_regex + ')?'
dirname_regex      = r'[\/\w\s\\.,:*()=%?+-]+'
filename_regex     = dirname_regex + '[^\/]'
rwxt_regex         = r'[r-][w-][x-][r-][w-][x-][r-][w-][xt-]'
fqdn_regex         = hostname_component + '\.' + domain_regex
aws_fqdn_regex     = aws_host_component + '\.' + domain_regex
# SECURITY NOTE: I'm allowing single quote through as it's found in Irish email addresses.
# This makes the email_regex non-safe without further validation. This regex only tests whether it's a valid email address, nothing more.
email_regex        = r"\b[A-Za-z0-9](?:[A-Za-z0-9\._\%\'\+-]{0,62}[A-Za-z0-9\._\%\+-])?@" + domain_regex
# TODO: review this IP regex again
ip_prefix_regex    = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
ip_regex           = ip_prefix_regex + r'(?:25[0-5]|2[0-4][0-9]|[01]?[1-9][0-9]|[01]?0[1-9]|[12]00|[0-9])\b' # now allowing 0 or 255 as the final octet due to CIDR
subnet_mask_regex  = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[1-9][0-9]|[01]?0[1-9]|[12]00|[0-9])\b'
mac_regex          = r'\b[0-9A-F-af]{1,2}[:-](?:[0-9A-Fa-f]{1,2}[:-]){4}[0-9A-Fa-f]{1,2}\b'
host_regex         = r'\b(?:' + hostname_regex + '|' + ip_regex + r')\b'
# I did a scan of registered running process names across several hundred linux servers of a diverse group of enterprise applications with 500 unique process names (58k individual processes) to determine that there are cases with spaces, slashes, dashes, underscores, chevrons (<defunct>), dots (script.p[ly], in.tftpd etc) to determine what this regex should be. Incidentally it appears that Linux truncates registered process names to 15 chars.
# This is not from ps -ef etc it is the actual process registered name, hence init not [init] as it appears in ps output
process_name_regex = r'\s*[\w_\.\/\<\>-][\w\s_\.\/\<\>-]+'
url_path_suffix_regex = r'/(?:[\w.,:\/%&?!=*|\[\]~+-]+)?'
url_regex          = r'(?i)\bhttps?://' + host_regex + '(?::\d{1,5})?(?:' + url_path_suffix_regex + ')?'
user_regex         = r'\b[A-Za-z][A-Za-z0-9_-]*[A-Za-z0-9]\b'
column_regex       = r'\b[\w\:]+\b'
ldap_dn_regex      = r'\b\w+=[\w\s]+(?:,\w+=[\w\s]+)*\b'
krb5_principal_regex = r'(?i)' + user_regex + r'(?:\/' + hostname_regex + r')?(?:\@' + domain_regex + r')?'
threshold_range_regex  = r'^(\@)?(-?\d+(?:\.\d+)?)(:)(-?\d+(?:\.\d+)?)?'
threshold_simple_regex = r'^(-?\d+(?:\.\d+)?)'
label_regex         = r'\s*[\%\(\)\/\*\w-][\%\(\)\/\*\w\s-]*'
version_regex       = r'\d+(\.\d+)*'
version_regex_short = r'\d+(\.\d+)?'
version_regex_lax   = version_regex + r'-?.+\b'

##################
#
# see also inspect.isclass(obj)
#                 .ismethod(obj)
#                 .ismodule(obj)
#                 .isfunction(obj)
#                 .istraceback(obj)

# see also .isalpha()
def isAlNum(arg):
    if arg == None:
        return False
    return str(arg).isalnum()
    # if re.match('^[A-Za-z0-9]+$', str(arg)):
    #     return True
    # return False


def isAwsAccessKey(arg):
    if arg == None:
        return False
    if re.match('^' + aws_access_key_regex + '$', str(arg)):
        return True
    return False


def isAwsHostname(arg):
    if arg == None:
        return False
    if re.match('^' + aws_hostname_regex + '$', str(arg)):
        return True
    return False


def isAwsFqdn(arg):
    if arg == None:
        return False
    if re.match('^' + aws_fqdn_regex + '$', str(arg)):
        return True
    return False


def isAwsSecretKey(arg):
    if arg == None:
        return False
    if re.match('^' + aws_secret_key_regex + '$', str(arg)):
        return True
    return False


def isBlankOrNone(arg):
    if arg == None:
        return True
    elif str(arg).strip() == '':
        return True
    return False


def isChars(arg, chars):
    if chars == None:
        code_error('no chars passed to isChars()')
    if not isRegex("[" + chars + "]"):
        code_error('invalid char range passed to isChars')
    if re.match('^[' + chars + ']+$', str(arg)):
        return True
    return False

# because 'code' isn't an accessible keyword
from types import CodeType
def isCode(arg):
    return isinstance(arg, CodeType)


def isCodeStr(arg):
    if not isStr(arg):
        return False
    try:
        co = compile(arg, 'test', 'exec')
    except SyntaxError:
        return False
    return isCode(co)


def isCollection(arg):
    if arg == None:
        return False
    if re.match('^\w(?:[\w\.]*\w)?$', str(arg)):
        return True
    return False


def isDatabaseName(arg):
    if arg == None:
        return False
    if re.match('^\w+$', str(arg)):
        return True
    return False


def isDatabaseColumnName(arg):
    if arg == None:
        return False
    if re.match('^' + column_regex + '$', str(arg)):
        return True
    return False


def isDatabaseFieldName(arg):
    if arg == None:
        return False
    arg = str(arg)
    if re.match('^\d+$', arg) or re.match('^[A-Za-z][\w()*,._-]+[A-Za-z0-9)]$', arg):
        return True
    return False


def isDatabaseTableName(arg, allow_qualified = False):
    if arg == None:
        return False
    arg = str(arg)
    if allow_qualified == True:
        if re.match('^[A-Za-z0-9][\w\.]*[A-Za-z0-9]$', arg):
            return True
    else:
        if re.match('^[A-Za-z0-9]\w*[A-Za-z0-9]$', arg):
            return True
    return False


def isDatabaseViewName(arg, allow_qualified = False):
    return isDatabaseTableName(arg, allow_qualified)


def isDict(arg):
    # return type(arg).__name__ == 'dict'
    return isinstance(arg, dict)


def isDirname(arg):
    if arg == None:
        return False
    arg = str(arg)
    if re.match('^\s*$', arg):
        return False
    if re.match('^' + dirname_regex + '$', arg):
        return True
    return False


def isDomain(arg):
    if arg == None:
        return False
    arg = str(arg)
    if len(arg) > 255:
        return False
    if re.match('^' + domain_regex + '$', arg):
        return True
    return False


def isDomainStrict(arg):
    if arg == None:
        return False
    arg = str(arg)
    if len(arg) > 255:
        return False
    if re.match('^' + domain_regex_strict + '$', arg):
        return True
    return False


def isDnsShortname(arg):
    if arg == None:
        return False
    arg = str(arg)
    if len(arg) < 3 or len(arg) > 63:
        return False
    if re.match('^' + hostname_component + '$', arg):
        return True
    return False


# SECURITY NOTE: this only validates the email address is valid, it's doesn't make it safe to arbitrarily pass to commands or SQL etc!
def isEmail(arg):
    if arg == None:
        return False
    arg = str(arg)
    if len(arg) > 256:
        return False
    if re.match('^' + email_regex + '$', arg):
        return True
    return False


def isFilename(arg):
    if arg == None:
        return False
    arg = str(arg)
    if re.match('/$', arg) or re.match('^\s*$', arg):
        return False
    if re.match('^' + filename_regex + '$', arg):
        return True
    return False


def isFloat(arg, allow_negative = False):
    if arg == None:
        return False
    # wouldn't respect default of not allowing negative
    # if type(arg) == 'float':
    # if isinstance(arg, float):
    #     return True
    neg = ''
    if allow_negative == True:
        neg = '-?'
    if re.match('^' + neg + '\d+(?:\.\d+)?', str(arg)):
        return True
    return False


def isFqdn(arg):
    if arg == None:
        return False
    arg = str(arg)
    if len(arg) > 255:
        return False
    if re.match('^' + fqdn_regex + '$', arg):
        return True
    return False


#def isHash


def isHex(arg):
    if arg == None:
        return False
    if re.match('^(?:0x)?[A-Fa-f\d]+$', str(arg)):
        return True
    return False


def isHost(arg):
    if arg == None:
        return False
    arg = str(arg)
    if len(arg) > 255:
        return False
    if re.match('^' + host_regex + '$', str(arg)):
        return True
    return False


def isHostname(arg):
    if arg == None:
        return False
    arg = str(arg)
    if len(arg) > 255:
        return False
    if re.match('^' + hostname_regex + '$', arg):
        return True
    return False


def isInt(arg, allow_negative=False):
    if arg == None:
        return False
    # wouldn't respect default of not allowing negative
    # if type(arg) == 'int':
    # if isinstance(arg, int):
    #     return True
    neg = ""
    if allow_negative:
        neg = "-?"
    if re.match('^' + neg + '\d+' + '$', str(arg)):
        return True
    return False


def isInterface(arg):
    if arg == None:
        return False
    if re.match('^(?:em|eth|bond|lo|docker)\d+|lo|veth[A-Fa-f0-9]+$', str(arg)):
        return True
    return False


def isIP(arg):
    if arg == None:
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
            return False
    return True


def isIterable(arg):
    # collections.Iterable Python 2.6+
    return isinstance(arg, collections.Iterable)


def isIterableNotStr(arg):
    # collections.Iterable Python 2.6+
    return isinstance(arg, collections.Iterable) and not isStr(arg)


def isJavaException(arg):
    if arg == None:
        return False
    arg = str(arg)
    if re.match('(?:^\s+at|^Caused by:)\s+\w+(?:\.\w+)+', arg):
        return True
    elif re.match('^Exception in thread ', arg):
        return True
    elif re.search('\w+(?:\.\w+)+\(\w+\.java:\d+\)', arg):
        return True
    elif re.search('\(.+:[\w]+\(\d+\)\)', arg):
        return True
    elif re.search(r'(?:\b|_)(\w+\.)+\w+Exception\b', arg):
        return True
    return False


def isJson(arg):
    if not isStr(arg):
        return False
    try:
        json.loads(arg)
        return True
    except ValueError, e:
        pass
    return False


def isXml(arg):
    if not isStr(arg):
        return False
    try:
        ET.fromstring(arg)
        return True
    # Python 2.7 throws xml.etree.ElementTree.ParseError, but Python 2.6 throws xml.parsers.expat.ExpatError
    except Exception:
        pass
    return False


def isKrb5Princ(arg):
    if arg == None:
        return False
    if re.match('^' + krb5_principal_regex + '$', str(arg)):
        return True
    return False


def isLabel(arg):
    if arg == None:
        return False
    if re.match('^' + label_regex + '$', str(arg)):
        return True
    return False


def isLdapDn(arg):
    if arg == None:
        return False
    if re.match('^' + ldap_dn_regex + '$', str(arg)):
        return True
    return False


def isList(arg):
    # return type(arg).__name__ == 'list'
    return isinstance(arg, list)


def isListOrTuple(arg):
    return isList(arg) or isTuple(arg)


def isMinVersion(version, min):
    if version == None:
        log.warn("'%s' is not a recognized version format" % version)
        return False
    if not isVersionLax(version):
        log.warn("'%s' is not a recognized version format" % version)
        return False
    if not isFloat(min):
        code_error('invalid second arg passed to min_version')
    min = float(min)
    # exception should never happen because of the regex
    # try:
    m = re.search('(\d+(?:\.\d+)?)', str(version))
    if m:
        version2 = float(m.group(1))
        if version2 >= min:
            return True
    # except ValueError, e:
    #     die("failed to detect version from string '%s': %s" % (version, e))
    return False


def isNagiosUnit(arg):
    if arg == None:
        return False
    arg = str(arg).lower()
    for unit in valid_nagios_units:
        if arg == unit.lower():
            return True
    return False


def isNoSqlKey(arg):
    if arg == None:
        return False
    if re.match('^([\w\_\,\.\:\+\-]+)$', str(arg)):
        return True
    return False


def isPathQualified(arg):
    if arg == None:
        return False
    if re.match('^(?:\.?\/)', str(arg)):
        return True
    return False


def isPort(arg):
    if arg == None:
        return False
    if not re.match('^\d+$', str(arg)):
        return False
    if int(arg) >= 1 and int(arg) <= 65535:
        return True
    return False


def isProcessName(arg):
    if arg == None:
        return False
    if re.match('^' + process_name_regex + '$', str(arg)):
        return True
    return False


def isPythonTraceback(arg):
    if arg == None:
        return False
    arg = str(arg)
    if re.search('^\s+File "' + filename_regex + '", line \d+, in (?:<module>|[A-Za-z]+)', arg):
        return True
    elif re.search('Traceback \(most recent call last\):', arg):
        return True
    return False


def getPythonVersion():
    m = re.match("^(" + version_regex_short + ")", sys.version.split('\n')[0])
    if m:
        # regex matched so no NumberFormatException on float cast
        return float(m.group(1))
    raise Exception("couldn't determine Python version!")


def isPythonVersion(expected):
    if expected == None:
        code_error('no expected version passed to isPythonVersion()')
    version = getPythonVersion()
    return version == expected


def isPythonMinVersion(min):
    if min == None:
        code_error('no min version passed to isPythonMinVersion()')
    version = getPythonVersion()
    return isMinVersion(version, min)


def isRegex(arg):
    if arg == None:
        return False
    arg = str(arg)
    if arg.strip() == '':
        return False
    try:
        re.match(arg, "")
        return True
    except re.error, e:
        pass
    return False


# def isScalar


def isScientific(arg, allow_negative = False):
    if arg == None:
        return False
    neg = ""
    if allow_negative == True:
        neg = "-?"
    if re.match('^' + neg + '\d+(?:\.\d+)?e[+-]?\d+$', str(arg), re.I):
        return True
    return False


# def isThreshold


def isStr(arg):
    # return type(arg).__name__ in [ 'str', 'unicode' ]
    return isinstance(arg, str) or isinstance(arg, unicode)
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
    return isinstance(arg, unicode)


def isUrl(arg):
    if arg == None:
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
    if arg == None:
        return False
    if re.match('^' + url_path_suffix_regex + '$', str(arg)):
        return True
    return False


def isUser(arg):
    if arg == None:
        return False
    if re.match('^' + user_regex + '$', str(arg)):
        return True
    return False


def isVersion(arg):
    if arg == None:
        return False
    if re.match('^' + version_regex + '$', str(arg)):
        return True
    return False


def isVersionLax(arg):
    if arg == None:
        return False
    if re.match('^' + version_regex_lax + '$', str(arg)):
        return True
    return False


def isYes(arg):
    if arg == None:
        return False
    if re.match('^\s*y(?:es)?\s*$', str(arg), re.I):
        return True
    return False


def isOS(arg):
    if arg == None:
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
    if arg == None:
        return ''
    arg = str(arg)
    prefix = '[\b\s\._-]'
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
#     return os.popen("ps aux | awk '/" + search + "/ {print \$2}' | while read pid; do kill " + kill_flags + " $pid >/dev/null 2>&1; done")


def plural(arg):
    # TODO: add support for arrays, dictionaries
    if(type(arg) == int or type(arg) == float):
        if arg > 1:
            return 's'
    return ''


# def prompt


# def random_alnum(num):
#     isInt(num) or code_error('invalid length passed to random_alnum')
#     chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
#     string = ""
#     # XXX: TODO
#     return string


# def resolve_ip


def sec2min(secs):
    if not isFloat(secs):
        # raise CodingErrorException('non-float passed to sec2min')
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
        raise CodingErrorException('non-integer passed for secs to set_timeout()')
    if handler:
        signal.signal(signal.SIGALRM, handler)
    signal.alarm(secs)


def skip_java_output(arg):
    if arg == None:
        return False
    if re.search('Class JavaLaunchHelper is implemented in both|^SLF4J', str(arg)):
        return True
    return False


def split_if_str(arg, sep):
    if isStr(arg):
        return arg.split(sep)
    return arg


def uniq_list(myList):
    if not isList(myList):
        raise CodingErrorException('non-list passed to uniq_list')
    return list(set(myList))

# collections.OrderedDict >= Python 2.7+
def uniq_list_ordered(myList):
    if not isList(myList):
        raise CodingErrorException('non-list passed to uniq_list_ordered')
    # list2 = []
    # for x in myList:
    #     if not x in list2:
    #         list2.append(x)
    # return list2
    seen = set()
    seen_add = seen.add
    return [x for x in myList if not (x in seen or seen_add(x))]


#def user_exists(user):


# ============================================================================ #
#                           Options Validation
# ============================================================================ #

def validate_alnum(arg, name):
    if not name:
        code_error("second arg 'name' not defined when calling validate_alnum()")
    if not arg:
        raise InvalidOptionException('%s not defined' % name)
    if isAlNum(arg):
        vlog_option(name, arg)
        return True
    raise InvalidOptionException('invalid %s defined: must be alphanumeric' % name)


def validate_aws_access_key(arg):
    if not arg:
        raise InvalidOptionException('aws access key not defined')
    arg = str(arg)
    if isAwsAccessKey(arg):
        vlog_option('aws access key', 'X' * 18 + arg[18:20])
        return True
    raise InvalidOptionException('invalid aws access key defined: must be 20 alphanumeric characters')


def validate_aws_bucket(arg):
    if not arg:
        raise InvalidOptionException('aws bucket not defined')
    arg = str(arg)
    if isDnsShortname(arg):
        vlog_option('aws bucket', arg)
        return True
    raise InvalidOptionException('invalid aws access key defined: must be 20 alphanumeric characters')


def validate_aws_secret_key(arg):
    if not arg:
        raise InvalidOptionException('aws secret key not defined')
    arg = str(arg)
    if isAwsSecretKey(arg):
        vlog_option('aws secret key', 'X' * 38 + arg[38:40])
        return True
    raise InvalidOptionException('invalid aws secret key defined: must be 40 alphanumeric characters')


def validate_chars(arg, name, chars):
    if not name:
        code_error("second arg 'name' not defined when calling validate_chars()")
    if not arg:
        raise InvalidOptionException('%s not defined' % name)
    if isChars(arg, chars):
        vlog_option(name, arg)
        return True
    raise InvalidOptionException('invalid %s defined: must be one of the following chars: %s' % (name, chars))


def validate_collection(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%scollection not defined' % name)
    if isCollection(arg):
        vlog_option('%scollection' % name, arg)
        return True
    raise InvalidOptionException('invalid %scollection defined: must be alphanumeric, with optional periods in the middle' % name)


def validate_database(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%sdatabase not defined' % name)
    if isDatabaseName(arg):
        vlog_option('%sdatabase' % name, arg)
        return True
    raise InvalidOptionException('invalid %sdatabase defined: must be alphanumeric' % name)


def validate_database_columnname(arg):
    if not arg:
        raise InvalidOptionException('column not defined')
    if isDatabaseColumnName(arg):
        vlog_option('column', arg)
        return True
    raise InvalidOptionException('invalid column defined: must be alphanumeric')


def validate_database_fieldname(arg):
    if not arg:
        raise InvalidOptionException('field not defined')
    if isDatabaseFieldName(arg):
        vlog_option('field', arg)
        return True
    raise InvalidOptionException('invalid field defined: must be alphanumeric')


def validate_database_tablename(arg, name='', allow_qualified=False):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%stable not defined' % name)
    if isDatabaseTableName(arg, allow_qualified):
        vlog_option('%stable' % name, arg)
        return True
    raise InvalidOptionException('invalid %stable defined: must be alphanumeric' % name)


def validate_database_viewname(arg, name='', allow_qualified=False):
    if name:
        name += " "
    if not arg:
        raise InvalidOptionException('%sview not defined' % name)
    if isDatabaseViewName(arg, allow_qualified):
        vlog_option('%sview' % name, arg)
        return True
    raise InvalidOptionException('invalid %sview defined: must be alphanumeric' % name)


def validate_database_query_select_show(arg, name=''):
    if name:
        name += " "
    if not arg:
        raise InvalidOptionException('%squery not defined' % name)
    if not re.match('^\s*((?:SHOW|SELECT)\s+.+)$', str(arg), re.I):
        raise InvalidOptionException('invalid %squery defined: may only be a SELECT or SHOW statement' % name)
    if re.search(r'\b(?:insert|update|delete|create|drop|alter|truncate)\b', arg, re.I):
        raise InvalidOptionException('invalid %squery defined: found DML statement keywords!' % name)
    vlog_option('%squery' % name, arg)
    return True


def validate_dirname(arg, name='', nolog=False):
    if name:
        name += " "
    if not arg:
        raise InvalidOptionException('%sdirectory name not defined' % name)
    if isDirname(arg):
        if not nolog:
            vlog_option('%sdirectory' % name, arg)
        return True
    raise InvalidOptionException('invalid %sdirectory name defined (does not match regex criteria)' % name)


def validate_directory(arg, name='', nolog=False):
    if name:
        name += " "
    if not arg:
        raise InvalidOptionException('%sdirectory not defined' % name)
    validate_dirname(arg, name, nolog)
    if os.path.isdir(arg):
        if not nolog:
            vlog_option('%sdirectory' % name, arg)
        return True
    raise InvalidOptionException("%sdirectory not found '%s'"  % (name, arg))

def validate_dir(arg, name='', nolog=False):
    return validate_directory(arg, name, nolog)

def validate_domain(arg, name=''):
    if name:
        name += " "
    if not arg:
        raise InvalidOptionException('%sdomain not defined' % name)
    if isDomain(arg):
        vlog_option('%sdomain' % name, arg)
        return True
    raise InvalidOptionException("invalid %sdomain '%s' defined" % (name, arg))


# SECURITY NOTE: this only validates the email address is valid, it's doesn't make it safe to arbitrarily pass to commands or SQL etc!
def validate_email(arg):
    if not arg:
        raise InvalidOptionException('email not defined')
    if isEmail(arg):
        vlog_option('email', arg)
        return True
    raise InvalidOptionException('invalid email address defined (does not match regex criteria)')


def validate_filename(arg, name='', nolog=False):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%sfilename not defined' % name)
    if isFilename(arg):
        if not nolog:
            vlog_option('%sfilename' % name, arg)
        return True
    raise InvalidOptionException("invalid %sfilename ('%s' does not match regex criteria)" % (name, arg))


def validate_file(arg, name='', nolog=False):
    if name:
        name += ' '
    # if not arg:
    #     raise InvalidOptionException('%sfilename not defined' % name)
    validate_filename(arg, name, nolog=nolog)
    if os.path.isfile(arg):
        # if not nolog:
        #     vlog_option('%sfile' % name, arg)
        return True
    raise InvalidOptionException("%sfile not found '%s'" % (name, arg))


def validate_files(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%sfiles not defined' % name)
    files = []
    if isStr(arg):
        files = [x.strip() for x in arg.split(',')]
    elif isListOrTuple(arg):
        files = arg
    else:
        raise CodingErrorException('non-list/tuple passed to parse_file_option')
    # not flexible enough
    # list(itertools.chain(*files))
    # list(itertools.chain.from_iterable(files))
    # files = [ str(x).split(',').strip() for x in files ]
    # files = list(itertools.chain(*[str(x).split(',') for x in files]))
    # custom flatten def
    # consider def to split if isStr
    files = flatten([split_if_str(x, ',') for x in files])
    files = list(files)
    for f in files:
        validate_file(f, name, False)
    vlog_option('files', files)
    return files


def validate_float(arg, name, min, max):
    if not name:
        code_error('no name passed for second arg to validate_float()')
    if arg == None:
        raise InvalidOptionException('%s not defined' % name)
    if isFloat(arg, allow_negative=True):
        arg = float(arg)
        try:
            min = float(min)
            max = float(max)
        except ValueError, e:
            code_error('invalid min/max (%s/%s) passed to validate_float(): %s' % (min, max, e))
        if (arg >= min and arg <= max):
            vlog_option(name, arg)
            return True
        raise InvalidOptionException('invalid %s defined: must be real number between %s and %s' % (name, min, max))
    raise InvalidOptionException('invalid %s defined: must be a real number' % name)


def validate_fqdn(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%sFQDN not defined' % name)
    if isFqdn(arg):
        vlog_option('%sfqdn' % name, arg)
        return True
    raise InvalidOptionException("invalid %sFQDN '%s' defined" % (name, arg))


def validate_host(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%shost not defined' % name)
    if isHost(arg):
        vlog_option('%shost' % name, arg)
        return True
    raise InvalidOptionException('invalid %shost defined: not a valid hostname or IP address' % name)

# def validate_hosts
# def validate_hostport


def validate_hostname(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%shostname not defined' % name)
    if isHostname(arg):
        vlog_option('%shostname' % name, arg)
        return True
    raise InvalidOptionException('invalid %shostname defined: not a valid hostname' % name)


def validate_int(arg, name, min, max):
    if not name:
        code_error('no name passed for second arg to validate_int()')
    if arg == None:
        raise InvalidOptionException('%s not defined' % name)
    if isInt(arg, allow_negative=True):
        arg = int(arg)
        try:
            min = int(min)
            max = int(max)
        except ValueError, e:
            code_error('invalid min/max (%s/%s) passed to validate_int(): %s' % (min, max, e))
        if (arg >= min and arg <= max):
            vlog_option(name, arg)
            return True
        raise InvalidOptionException('invalid %s defined: must be real number between %s and %s' % (name, min, max))
    raise InvalidOptionException('invalid %s defined: must be a real number' % name)



def validate_interface(arg):
    if not arg:
        raise InvalidOptionException('interface not defined')
    if isInterface(arg):
        vlog_option('interface', arg)
        return True
    raise InvalidOptionException('invalid interface defined: not a valid interface')


def validate_ip(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%sIP not defined' % name)
    if isIP(arg):
        vlog_option('%sIP' % name, arg)
        return True
    raise InvalidOptionException('invalid IP defined')


def validate_krb5_princ(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%skrb5 principal not defined' % name)
    if isKrb5Princ(arg):
        vlog_option('%skrb5 principal' % name, arg)
        return True
    raise InvalidOptionException('invalid krb5 principal defined')


def validate_krb5_realm(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%skrb5 realm not defined' % name)
    if isDomain(arg):
        vlog_option('%skrb5 realm' % name, arg)
        return True
    raise InvalidOptionException('invalid krb5 realm defined')


def validate_label(arg):
    if not arg:
        raise InvalidOptionException('label not defined')
    if isLabel(arg):
        vlog_option('label', arg)
        return True
    raise InvalidOptionException('invalid label defined: must be an alphanumeric identifier')


def validate_ldap_dn(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('ldap %sdn not defined' % name)
    if isLdapDn(arg):
        vlog_option('ldap %sdn' % name, arg)
        return True
    raise InvalidOptionException('invalid ldap %sdn defined' % name)


# validate_metrics
# validate_node_list
# validate_nodeport_list


def validate_nosql_key(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%skey not defined' % name)
    if isNoSqlKey(arg):
        vlog_option('%skey' % name, arg)
        return True
    raise InvalidOptionException('invalid %skey defined: may only contain characters: alphanumeric, commas, colons, underscores, pluses, dashes' % name)


def validate_port(arg, name=''):
    if name:
        name += ' '
    if arg == None:
        raise InvalidOptionException('%sport not defined' % name)
    if isPort(arg):
        vlog_option('%sport' % name, arg)
        return True
    raise InvalidOptionException('invalid %sport number defined: must be a positive integer between 1 and 65535' % name)


def validate_process_name(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%sprocess name not defined' % name)
    if isProcessName(arg):
        vlog_option('%sprocess name' % name, arg)
        return True
    raise InvalidOptionException('invalid %sprocess name defined' % name)

# def validate_program_path
# def validate_regex


def validate_password(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%spassword not defined' % name)
    if re.search('[`\'"]|\\$\\(', arg):
        raise InvalidOptionException('invalid %spassword defined, may not contain quotes, subshell escape sequences like $( ) or backticks' % name)
    vlog_option('%spassword' % name, '<omitted>')
    return True


# def validate_resolvable


def validate_units(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%sunits not defined' % name)
    if isNagiosUnit(arg):
        vlog_option('%sunits' % name, arg)
        return True
    raise InvalidOptionException('invalid %sunits defined: must be one of: ' % name + str(valid_nagios_units))


def validate_url(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%surl not defined' % name)
    if isUrl(arg):
        vlog_option('%surl' % name, arg)
        return True
    raise InvalidOptionException('invalid %surl defined' % name)


def validate_url_path_suffix(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%surl path suffix not defined' % name)
    if isUrlPathSuffix(arg):
        vlog_option('%surl path suffix' % name, arg)
        return True
    raise InvalidOptionException('invalid %surl path suffix defined' % name)


def validate_user(arg, name=''):
    if name:
        name += ' '
    if not arg:
        raise InvalidOptionException('%suser not defined' % name)
    if isUser(arg):
        vlog_option('%suser' % name, arg)
        return True
    raise InvalidOptionException('invalid %suser defined: must be alphanumeric' % name)


# user_exists() not implemented yet
# def validate_user_exists(arg, name=''):
#     if name:
#         name += ' '
#     if not arg:
#         raise InvalidOptionException('%suser not defined' % name)
#     validate_user(arg)
#     if user_exists(arg):
#         return True
#     raise InvalidOptionException('invalid %suser defined, not found on local system' % name)



# ============================================================================ #

def vlog(msg):
    log.warn(msg)

def vlog2(msg):
    log.info(msg)

def vlog3(msg):
    log.debug(msg)

def vlog_option(name, option):
    vlog2('%-25s %s' % (name, option))


def which(bin):
    if not isFilename(bin):
        raise InvalidFilenameException("invalid filename '%s' supplied to which()" % bin)
    bin = str(bin)
    if re.match('^.{0,2}\/', bin):
        if os.path.isfile(bin):
            if os.access(bin, os.X_OK):
                return bin
            raise FileNotExecutableException("'%s' is not executable" % bin)
        else:
            raise FileNotFoundException("'%s' not found" % bin)
    else:
        for basepath in os.getenv('PATH', '').split(os.pathsep):
            path = os.path.join(basepath, bin)
            if os.path.isfile(path):
                if os.access(path, os.X_OK):
                    return path
    raise FileNotFoundException("could not find executable file '%s' in $PATH (%s)" % (bin, os.getenv('PATH', '') ) )


# ============================================================================ #
#                               PySpark Utils
# ============================================================================ #

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
#    def __init__(self):
#        """Initializes all variables to their default states"""
#
#        try:
#            from subprocess import Popen, PIPE, STDOUT
#        except ImportError:
#            print "UNKNOWN: Failed to import python subprocess module.",
#            print "Perhaps you are using a version of python older than 2.4?"
#            sys.exit(CRITICAL)
#
#        self.server     = ""
#        self.timeout    = DEFAULT_TIMEOUT
#        self.verbosity  = 0
#
#
#    def validate_variables(self):
#        """Runs through the validation of all test variables
#        Should be called before the main test to perform a sanity check
#        on the environment and settings"""
#
#        self.validate_host()
#        self.validate_timeout()
#
#
#
#    def validate_timeout(self):
#        """Exits with an error if the timeout is not valid"""
#
#        if self.timeout == None:
#            self.timeout = DEFAULT_TIMEOUT
#        try:
#            self.timeout = int(self.timeout)
#            if not 1 <= self.timeout <= 65535:
#                end(UNKNOWN, "timeout must be between 1 and 3600 seconds")
#        except ValueError:
#            end(UNKNOWN, "timeout number must be a whole number between " \
#                       + "1 and 3600 seconds")
#
#        if self.verbosity == None:
#            self.verbosity = 0
#
#
#    def run(self, cmd):
#        """runs a system command and returns a tuple containing
#        the return code and the output as a single text block"""
#
#        if cmd == "" or cmd == None:
#            end(UNKNOWN, "Internal python error - " \
#                       + "no cmd supplied for run function")
#
#        self.vprint(3, "running command: %s" % cmd)
#
#        try:
#            process = Popen( cmd.split(),
#                             shell=False,
#                             stdin=PIPE,
#                             stdout=PIPE,
#                             stderr=STDOUT )
#        except OSError, error:
#            error = str(error)
#            if error == "No such file or directory":
#                end(UNKNOWN, "Cannot find utility '%s'" % cmd.split()[0])
#            else:
#                end(UNKNOWN, "Error trying to run utility '%s' - %s" \
#                                                      % (cmd.split()[0], error))
#
#        stdout, stderr = process.communicate()
#
#        if stderr == None:
#            pass
#
#        returncode = process.returncode
#        self.vprint(3, "Returncode: '%s'\nOutput: '%s'" % (returncode, stdout))
#
#        if stdout == None or stdout == "":
#            end(UNKNOWN, "No output from utility '%s'" % cmd.split()[0])
#
#        return (returncode, str(stdout))
#
#
#    def set_timeout(self):
#        """Sets an alarm to time out the test"""
#
#        if self.timeout == 1:
#            self.vprint(2, "setting plugin timeout to 1 second")
#        else:
#            self.vprint(2, "setting plugin timeout to %s seconds"\
#                                                                % self.timeout)
#
#        signal.signal(signal.SIGALRM, self.sighandler)
#        signal.alarm(self.timeout)
#
#
#    def sighandler(self, discarded, discarded2):
#        """Function to be called by signal.alarm to kill the plugin"""
#
#        # Nop for these variables
#        discarded = discarded2
#        discarded2 = discarded
#
#        if self.timeout == 1:
#            timeout = "(1 second)"
#        else:
#            timeout = "(%s seconds)" % self.timeout
#
#        if CHECK_NAME == "" or CHECK_NAME == None:
#            check_name = ""
#        else:
#            check_name = CHECK_NAME.lower().strip() + " "
#
#        end(CRITICAL, "%splugin has self terminated after " % check_name
#                    + "exceeding the timeout %s" % timeout)
