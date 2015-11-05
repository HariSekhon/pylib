#
#  Author: Hari Sekhon
#  Date: 2008-03-06 15:20:22 +0000 (Thu, 06 Mar 2008)
#  Reinstantiated Date:
#        2013-07-04 00:08:32 +0100 (Thu, 04 Jul 2013)
#
#  http://github.com/harisekhon
#
#  License: see accompanying LICENSE file
#

""" Personal Library originally started to standardize Nagios Plugin development but superceded by Perl version """

import os
import re
import platform
import string
import sys
#import re
#import signal

__author__      = "Hari Sekhon"
__version__     = 0.6

# Standard Nagios return codes
ERRORS = {
    "OK"        : 0,
    "WARNING"   : 1,
    "CRITICAL"  : 2,
    "UNKNOWN"   : 3,
    "DEPENDENT" : 4
}

libdir = os.path.dirname(__file__) or '.'

valid_nagios_units = ('%', 's', 'ms', 'us', 'B', 'KB', 'MB', 'GB', 'TB', 'c')

def support_msg(repo):
    support_msg = 'Please try latest version from https:/github.com/harisekhon/%s and if problem persists paste the full output in to a ticket for a fix/update at https://github.com/harisekhon/%s/issues' % (repo, repo)
    return support_msg

def printerr(msg, *indent):
    if indent:
        print >> sys.stderr, ">>> ",
    print >> sys.stderr, "%s" % msg

def warn(msg):
     printerr('WARNING: ' + msg)

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
        elif exitcode in ERRORS.keys():
            sys.exit(ERRORS[exitcode])
        else:
            printerr("Code error, non-digit and non-recognized error status passed as second arg to die()")
            sys.exit(ERRORS["CRITICAL"])
    sys.exit(ERRORS["CRITICAL"])

def code_error(msg):
    printerr("CODE ERROR: " + msg)
    sys.exit(ERRORS['UNKNOWN'])

def quit(status, msg):
    """ Quit with status code from ERRORS dictionary after printing given msg """

    printerr(msg)
    sys.exit(ERRORS[status])


# ============================================================================ #
#                           Jython Utils
# ============================================================================ #

def isJython():
    """ Returns True if running in Jython interpreter """

    if "JYTHON_JAR" in dir(sys):
        return True
    else:
        return False


def jython_only():
    """ Die unless we are inside Jython """

    if not isJython():
        die("not running in Jython!")


def print_jython_exception():
    """ Prints last Jython Exception """

    printerr("Error: %s" % sys.exc_info()[1].toString())
    if sys.exc_info()[1].toString() == java_oom:
        printerr(java_oom_fix)
    #import traceback; traceback.print_exc()


if isJython():
    java_oom     = "java.lang.OutOfMemoryError: Java heap space"
    java_oom_fix = "\nAdd/Increase -J-Xmx<value> command line argument\n"

# ============================================================================ #

verbose = False
def vprint(msg):
    """ Print if verbose """

    if verbose:
        print msg,


def read_file_without_comments(filename):
    return [ x.rstrip("\n").split("#")[0].strip() for x in open(filename).readlines() ]


# ============================================================================ #
#                                   REGEX
# ============================================================================ #

# XXX: TODO: remove these after migrating dependent progs to proper regex subs
RE_NAME           = re.compile(r'^[A-Za-z\s\.\'-]+$')
RE_DOMAIN         = re.compile(r'\b(?:[A-Za-z][A-Za-z0-9]{0,62}|[A-Za-z][A-Za-z0-9_\-]{0,61}[a-zA-Z0-9])+\.(?:\b(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])\b\.)*\b(?:[A-Za-z]{2,4}|(?:local|museum|travel))\b', re.I)
RE_EMAIL          = re.compile(r'\b[A-Za-z0-9\._\'\%\+-]{1,64}@[A-Za-z0-9\.-]{1,251}\.[A-Za-z]{2,4}\b')

BLANK_LINE = re.compile('^\s*$')
ALNUM_DASH = re.compile('^[A-Za-z0-9-]+$')

tld_regex = r'(?i)\b(?:'
total_tld_count = 0

def load_tlds(file):
    fh = open(file)
    tld_count = 0
    global total_tld_count
    global tld_regex
    for line in fh.readlines():
        line = line.split('#')[0]
        line = line.strip()
        if BLANK_LINE.match(line):
            continue
        if(ALNUM_DASH.match(line)):
            tld_regex += line + '|'
            tld_count += 1
        else:
            warn("TLD: '%s' from tld file '%s' not validated, skipping that TLD" % (line, file))
    #warn("loaded %s TLDs from file '%s'" % (tld_count, file) )
    total_tld_count += tld_count

tld_file = libdir + '/tlds-alpha-by-domain.txt'
load_tlds(tld_file)
if total_tld_count < 900:
    code_error('%s tlds loaded, expected > 900' % total_tld_count)

custom_tlds = libdir + '/custom_tlds.txt'
if(os.path.isfile(custom_tlds)):
    load_tlds(custom_tlds)

tld_regex = tld_regex.rstrip('|')
tld_regex += r')\b'

domain_component_regex = r'\b[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\b'
# TODO: custom TLDs generated
# AWS regex from http://blogs.aws.amazon.com/security/blog/tag/key+rotation
aws_access_key_regex = r'(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])'
aws_secret_key_regex = r'(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])'
domain_regex       = r'(?:' + domain_component_regex + '\.)*' + tld_regex
domain_regex2      = r'(?:' + domain_component_regex + '\.)+' + tld_regex
domain_regex_strict = domain_regex2
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
process_name_regex = r'[\w\s_\.\/\<\>-]+'
url_path_suffix_regex = r'/(?:[\w.,:\/%&?!=*|\[\]~+-]+)?'
url_regex          = r'(?i)\bhttps?://' + host_regex + '(?::\d{1,5})?(?:' + url_path_suffix_regex + ')?'
user_regex         = r'\b[A-Za-z][A-Za-z0-9_-]*[A-Za-z0-9]\b'
column_regex       = r'\b[\w\:]+\b'
ldap_dn_regex      = r'\b\w+=[\w\s]+(?:,\w+=[\w\s]+)*\b'
krb5_principal_regex = r'(?i)' + user_regex + r'(?:\/' + hostname_regex + r')?(?:\@' + domain_regex + r')?'
threshold_range_regex  = r'^(\@)?(-?\d+(?:\.\d+)?)(:)(-?\d+(?:\.\d+)?)?'
threshold_simple_regex = r'^(-?\d+(?:\.\d+)?)'
version_regex      = r'\d(\.\d+)*'
version_regex_lax  = version_regex + r'-?.*'

def isAlNum(arg):
    if re.match('^[A-Za-z0-9]+$', str(arg)):
        return True
    return False

# isArray

def isAwsAccessKey(arg):
    if re.match('^' + aws_access_key_regex + '$', str(arg)):
        return True
    return False

def isAwsHostname(arg):
    if re.match('^' + aws_hostname_regex + '$', str(arg)):
        return True
    return False

def isAwsFqdn(arg):
    if re.match('^' + aws_fqdn_regex + '$', str(arg)):
        return True
    return False

def isAwsSecretKey(arg):
    if re.match('^' + aws_secret_key_regex + '$', str(arg)):
        return True
    return False

# isChars
# isCode

def isCollection(arg):
    if re.match('^\w(?:[\w\.]*\w)?$', str(arg)):
        return True
    return False

def isDigit(arg):
    return isInt(arg)

def isDatabaseName(arg):
    if re.match('^\w+$', str(arg)):
        return True
    return False

def isDatabaseColumnName(arg):
    if re.match('^' + column_regex + '$', str(arg)):
        return True
    return False

def isDatabaseFieldName(arg):
    arg = str(arg)
    if re.match('^\d+$', arg) or re.match('^[\w()*,._-]+$', arg):
        return True
    return False

def isDatabaseTableName(arg, allow_qualified = False):
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

def isDomain(arg):
    arg = str(arg)
    if len(arg) > 255:
        return False
    if re.match('^' + domain_regex + '$', arg):
        return True
    return False

def isDomainStrict(arg):
    arg = str(arg)
    if len(arg) > 255:
        return False
    if re.match('^' + domain_regex_strict + '$', arg):
        return True
    return False

def isDnsShortname(arg):
    arg = str(arg)
    if len(arg) < 3 or len(arg) > 63:
        return False
    if re.match('^' + hostname_component + '$', arg):
        return True
    return False

def isEmail(arg):
    arg = str(arg)
    if len(arg) > 256:
        return False
    if re.match('^' + email_regex + '$', arg):
        return True
    return False

def isFilename(arg):
    arg = str(arg)
    if re.match('/$', arg) or re.match('^\s*$', arg):
        return False
    if re.match('^' + filename_regex + '$', arg):
        return True
    return False

def isDirname(arg):
    arg = str(arg)
    if re.match('^\s*$', arg):
        return False
    if re.match('^' + dirname_regex + '$', arg):
        return True
    return False

def isFloat(arg, allow_negative = False):
    neg = ''
    if allow_negative == True:
        neg = '-?'
    if re.match('^' + neg + '\d+(?:\.\d+)?', str(arg)):
        return True
    return False

def isFqdn(arg):
    arg = str(arg)
    if len(arg) > 255:
        return False
    if re.match('^' + fqdn_regex + '$', arg):
        return True
    return False

#def isHash

def isHex(arg):
    if re.match('^(?:0x)?[A-Fa-f\d]+$', str(arg)):
        return True
    return False

def isHost(arg):
    arg = str(arg)
    if len(arg) > 255:
        return False
    if re.match('^' + host_regex + '$', str(arg)):
        return True
    return False

def isHostname(arg):
    arg = str(arg)
    if len(arg) > 255:
        return False
    if re.match('^' + hostname_regex + '$', arg):
        return True
    return False

def isInt(arg, *allow_negative):
    neg = ""
    if allow_negative:
        neg = "-?"
    if re.match('^' + neg + '\d+' + '$', str(arg)):
        return True
    return False

def isInterface(arg):
    if re.match('^(?:em|eth|bond|lo|docker)\d+|lo|veth[A-Fa-f0-9]+$', str(arg)):
        return True
    return False

def isIP(arg):
    arg = str(arg)
    if not re.match('^' + ip_regex + '$', str(arg)):
        return False
    octets = arg.split('.')
    if len(octets) > 4:
        return False
    for octet in octets:
        octet = int(octet)
        if octet < 0 or octet > 255:
            return False
    return True

def isJavaException(arg):
    arg = str(arg)
    if re.match('(?:^\s+at|^Caused by:)\s+\w+(?:\.\w+)+', arg):
        return True
    elif re.match('\(.+:[\w-]+\(\d+\)\)', arg):
        return True
    elif re.match('(\b|_).+\.\w+Exception:', arg):
        return True
    elif re.match('^(?:\w+\.)*\w+Exception:', arg):
        return True
    elif re.match('\$\w+\(\w+:\d+\)', arg):
        return True
    return False

# def isJson
# def isXml

def isKrb5Princ(arg):
    if re.match('^' + krb5_principal_regex + '$', str(arg)):
        return True
    return False

def isLabel(arg):
    if re.match('^[\%\(\)\/\*\w\s-]+$', str(arg)):
        return True
    return False

def isLdapDn(arg):
    if re.match('^' + ldap_dn_regex + '$', str(arg)):
        return True
    return False

def isMinVersion(version, min):
    if not isVersionLax(version):
        warn("'%s' is not a recognized version format" % version)
        return False
    if not isFloat(min):
        code_error('invalid second arg passed to min_version')
    min = float(min)
    try:
        parts = version.split('.')
        if parts < 2:
            raise ValueError('no dot detected in version')
        major_version = int(parts[0].strip())
        minor_version = int(parts[1].strip())
    except ValueError, e:
        die("failed to detect version from string '%s': %s" % (version, e))
    version2 = float(str(major_version) + '.' + str(minor_version))
    if version2 >= min:
        return True
    return False

def isNagiosUnit(arg):
    arg = str(arg).lower()
    for unit in valid_nagios_units:
        if arg == unit.lower():
            return True
    return False

def isNoSqlKey(arg):
    if re.match('^([\w\_\,\.\:\+\-]+)$', str(arg)):
        return True
    return False

def isPathQualified(arg):
    if re.match('^(?:\.?\/)', str(arg)):
        return True
    return False

def isPort(arg):
    if not re.match('^(\d+)$', str(arg)):
        return False
    if arg >= 1 and arg <= 65535:
        return True
    return False

def isProcessName(arg):
    if re.match('^' + process_name_regex + '$', str(arg)):
        return True
    return False

def isPythonTraceback(arg):
    arg = str(arg)
    if re.search('^\s+File "' + filename_regex + '", line \d+, in (?:<module>|[A-Za-z]+)', arg):
        return True
    elif re.search('Traceback \(most recent call last\):', arg):
        return True
    return False

# def isRegex

# def isScalar

def isScientific(arg, allow_negative = False):
    neg = ""
    if allow_negative == True:
        neg = "-?"
    if re.match('^' + neg + '\d+(?:\.\d+)?e[+-]?\d+$', str(arg), re.I):
        return True
    return False

# def isThreshold

def isUrl(arg):
    # checking for String yet another breakage between Python 2 and 3
    # see http://stackoverflow.com/questions/4843173/how-to-check-if-type-of-a-variable-is-string-in-python
    arg = str(arg).strip()
    if not re.search('://', arg):
        arg = 'http://' + arg
    if re.match('^' + url_regex + '$', arg):
        return True
    return False

def isUrlPathSuffix(arg):
    if re.match('^' + url_path_suffix_regex + '$', str(arg)):
        return True
    return False

def isUser(arg):
    if re.match('^' + user_regex + '$', str(arg)):
        return True
    return False

def isVersion(arg):
    if re.match('^' + version_regex + '$', str(arg)):
        return True
    return False

def isVersionLax(arg):
    if re.match('^' + version_regex_lax + '$', str(arg)):
        return True
    return False

def isYes(arg):
    if re.match('^\s*y(?:es)?\s*$', str(arg), re.I):
        return True
    return False

def isOS(arg):
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
        raise Exception(supported_os_msg % 'Mac/Darwin')
    return True

def linux_only():
    if not isLinux():
        raise Exception(supported_os_msg % 'Linux')
    return True

def linux_mac_only():
    if not isLinuxOrMac():
        raise Exception(supported_os_msg % 'Linux or Mac/Darwin')
    return True

# XXX: add logging

def min_value(value, min):
    if not isFloat(value):
        code_error('invalid first arg passed to min_value(), must be float')
    if not isFloat(min):
        code_error('invalid second arg passed to min_value(), must be float')
    if (value < min):
        return min
    return value

# msg_perf_thresholds
# msg_thresholds
# month2int
# open_file

def perf_suffix(arg):
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
        return
    return "%d:%.2d" % (int(secs / 60), secs % 60)

def sec2human(secs):
    isFloat(secs) or code_error('invalid non-float argument passed to sec2human')
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

def skip_java_output(mystr):
    if re.search('Class JavaLaunchHelper is implemented in both|^SLF4J', str(mystr)):
        return True
    return False

# tstamp
# tprint
# trim_float
# uniq_array (use set)
# uniq_array2 (preserve order can't use set)

#def user_exists(user):

# validate_*

def which(bin, quit_on_err):
    isFilename(bin) or code_error('invalid filename '%' supplied to which()' % bin)
    if re.matches('^(?:\/|\.\/'):
        if os.path.isfile(bin):
            if os.access(bin, os.X_OK):
                return bin
            elif quit_on_err:
                quit('UNKNOWN', "'%' is not executable")
        elif quit_on_err:
            quit('UNKNOWN', "'%' not found")
    else:
        for basepath in os.getenv('PATH', '').split(os.pathsep):
            path = os.path.join(basepath, bin)
            if os.path.isfile(path):
                if os.access(path, os.X_OK):
                    return path
                elif quit_on_err:
                    quit('UNKNOWN', "'%' is not executable" % path)
        quit('UNKNOWN', "couldn't find '%' in $PATH (%s)" % (bin, os.getenv('PATH', '')))
    return None


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
#    def validate_host(self):
#        """Exits with an error if the hostname
#        does not conform to expected format"""
#
#        # Input Validation - Rock my regex ;-)
#        re_hostname = re.compile("^[a-zA-Z0-9]+[a-zA-Z0-9-]*((([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6})?$")
#        re_ipaddr   = re.compile("^((25[0-5]|2[0-4]\d|[01]\d\d|\d?\d)\.){3}(25[0-5]|2[0-4]\d|[01]\d\d|\d?\d)$")
#
#        if self.server == None:
#            end(UNKNOWN, "You must supply a server hostname or ip address. " \
#                       + "See --help for details")
#
#        if not re_hostname.match(self.server) and \
#           not re_ipaddr.match(self.server):
#            end(UNKNOWN, "Server given does not appear to be a valid " \
#                       + "hostname or ip address")
#
#
##    def validate_port(self):
##        """Exits with an error if the port is not valid"""
##
##        if self.port == None:
##            self.port = ""
##        else:
##            try:
##                self.port = int(self.port)
##                if not 1 <= self.port <= 65535:
##                    raise ValueError
##            except ValueError:
##                end(UNKNOWN, "port number must be a whole number between " \
##                           + "1 and 65535")
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
#
#
#    def vprint(self, threshold, message):
#        """Prints a message if the first arg is numerically greater than the
#        verbosity level"""
#
#        if self.verbosity >= threshold:
#            print "%s" % message
