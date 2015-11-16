#
#  Author: Hari Sekhon
#  Date: 2013-01-06 01:25:55 +0000 (Sun, 06 Jan 2013)
#
#  http://github.com/harisekhon/pylib
#
#  License: see accompanying LICENSE file
#

# ============================================================================ #
#                   PyUnit Tests for HariSekhonUtils
# ============================================================================ #

from __future__ import print_function

import inspect
import os
import sys
import unittest
# inspect.getfile(inspect.currentframe()) # filename
libdir = os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), '..')
sys.path.append(libdir)
import HariSekhonUtils
from HariSekhonUtils import *

class test_HariSekhonUtils(unittest.TestCase):

    # XXX: must prefix with test_ in order for the tests to be called

    def setUp(self):
        self.libdir = libdir
        self.libfile = os.path.join(libdir, 'HariSekhonUtils.py')

    #def runTest(self):

    # Python 2.7+
    # @unittest.skip('skipping test codes')
    def test_status_codes(self):
        self.assertEqual(ERRORS['OK'],       0)
        self.assertEqual(ERRORS['WARNING'],  1)
        self.assertEqual(ERRORS['CRITICAL'], 2)
        self.assertEqual(ERRORS['UNKNOWN'],  3)

    def test_printerr(self):
        printerr('testing')
        printerr('testing', True)

    def test_warn(self):
        warn('testing')

    def test_die(self):
        try:
            die('test')
            raise Exception('failed to raise SystemExit exception from die(test)')
        except SystemExit, e:
            if e.code != 2:
                raise Exception("incorrect exit code '%s' raised by die(test)" % e.code)
            # also gives 2 not 'test'
            # if e.message != 'test':
            #     raise Exception("incorrect exit message '%s' raised by die()" % e.message)
        try:
            die('test', 4)
            raise Exception('failed to raise SystemExit exception from die(test, 4)')
        except SystemExit, e:
            if e.code != 4:
                raise Exception("incorrect exit code '%s' raised by die(test, 4)" % e.code)
            # also gives 2 not 'test'
            # if e.message != 'test':
            #     raise Exception("incorrect exit message '%s' raised by die()" % e.message)
        try:
            die('test', 5 + 256)
            raise Exception('failed to raise SystemExit exception from die(test, 5 + 256)')
        except SystemExit, e:
            if e.code != 5:
                raise Exception("incorrect exit code '%s' raised by die(test, 5 + 256)" % e.code)
            # also gives 2 not 'test'
            # if e.message != 'test':
            #     raise Exception("incorrect exit message '%s' raised by die()" % e.message)
        try:
            die('test', 'UNKNOWN')
            raise Exception('failed to raise SystemExit exception from die(test, UNKNOWN)')
        except SystemExit, e:
            if e.code != 3:
                raise Exception("incorrect exit code '%s' raised by die(test, UNKNOWN)" % e.code)
        try:
            die('test', 'unrecognized_status')
            raise Exception('failed to raise SystemExit exception from die(test, unrecognized_status)')
        except SystemExit, e:
            if e.code != 2:
                raise Exception("incorrect exit code '%s' raised by die(test, UNKNOWN)" % e.code)

    def test_quit(self):
        try:
            quit('UNKNOWN', 'test')
            raise Exception('failed to raise SystemExit exception from quit(UNKNOWN, test)')
        except SystemExit, e:
            if e.code != 3:
                raise Exception("incorrect exit code '%s' raised by quit(UNKNOWN, test)" % e.code)

    def test_quit_wrong_status(self):
        try:
            quit('wrongstatus', 'test')
            raise Exception('failed to raise SystemExit exception from quit(wrongstatus, test)')
        except SystemExit, e:
            if e.code != 2:
                raise Exception("incorrect exit code '%s' raised by quit(wrongstatus, test)" % e.code)

    def test_usage(self):
        from optparse import OptionParser
        parser = OptionParser()
        try:
            usage(parser, status='UNKNOWN')
            raise Exception('failed to raise SystemExit exception from usage(parser)')
        except SystemExit, e:
            if e.code != ERRORS['UNKNOWN']:
                raise Exception("incorrect exit code '%s' raised by usage(parser)" % e.code)
        try:
            usage(parser, '', 'WARNING')
            raise Exception('failed to raise SystemExit exception from usage(parser)')
        except SystemExit, e:
            if e.code != ERRORS['WARNING']:
                raise Exception("incorrect exit code '%s' raised by usage(parser)" % e.code)
        try:
            usage(parser, 'msg', 'UNKNOWN')
            raise Exception('failed to raise SystemExit exception from usage(parser, msg)')
        except SystemExit, e:
            if e.code != ERRORS['UNKNOWN']:
                raise Exception("incorrect exit code '%s' raised by usage(parser)" % e.code)

    def test_code_error(self):
        try:
            code_error('test')
            raise Exception('code_error() failed to raise exception')
        except CodingErrorException:
            pass


    def test_check_tldcount(self):
        HariSekhonUtils._check_tldcount()
        log.debug('resetting _tlds to empty')
        HariSekhonUtils._tlds = set()
        try:
            HariSekhonUtils._check_tldcount()
            raise Exception('HariSekhonUtils.check_tldcount() failed to raise exception before IANA list loaded')
        except CodingErrorException:
            pass

    def test_load_tlfs(self):
        # check we can't accidentally double load the IANA list
        HariSekhonUtils._load_tlds(HariSekhonUtils._tld_file)
        HariSekhonUtils._load_tlds(HariSekhonUtils._tld_file)
        HariSekhonUtils._check_tldcount()
        os.system('echo "=" > fake_tld.txt')
        HariSekhonUtils._load_tlds('fake_tld.txt')
        # artifically double load tlds and check
        tlds = HariSekhonUtils._tlds
        HariSekhonUtils._tlds.clear()
        for x in range(2000):
            HariSekhonUtils._tlds.add(x)
        HariSekhonUtils._check_tldcount()
        HariSekhonUtils._tlds.add('2001')
        try:
            HariSekhonUtils._check_tldcount()
            raise Exception('failed to raise CodingErrorException on double loaded TLDs')
        except CodingErrorException, e:
            pass
        # reset the TLDs
        HariSekhonUtils._tlds = tlds


# ============================================================================ #
#                               Jython
# ============================================================================ #

    def test_isJython(self):
        self.assertFalse(isJython())
        sys.JYTHON_JAR = 'blah'
        self.assertTrue(isJython())
        del sys.JYTHON_JAR

    def test_jython_only(self):
        sys.JYTHON_JAR = 'blah'
        jython_only()
        del sys.JYTHON_JAR
        try:
            jython_only()
            raise Exception('failed to exit/raise exception when calling jython_only()')
        except SystemExit:
            pass

    def test_get_jython_exception(self):
        self.assertEquals(get_jython_exception(), '')

    def test_log_jython_exception(self):
        log_jython_exception()

    def test_isJavaOOM(self):
        self.assertTrue(isJavaOOM('java.lang.OutOfMemoryError: Java heap space'))
        self.assertTrue(isJavaOOM('java.lang.OutOfMemoryError'))
        self.assertFalse(isJavaOOM('blah'))
        self.assertFalse(isJavaOOM(''))
        self.assertFalse(isJavaOOM(None))

    def test_java_oom_fix_msg(self):
        # assertIn >= Python 2.7
        self.assertTrue('-J' in java_oom_fix_msg())


# ============================================================================ #
#                          OS Validation Functions
# ============================================================================ #

    def test_isOS(self):
        self.assertEqual(isOS(platform.system()), isOS(platform.system()))
        try:
            isOS(None)
            raise Exception('failed to raise exception for none arg')
        except CodingErrorException:
            pass


    if isLinux():
        def test_isLinux_string(self):
            self.assertEqual(platform.system(), 'Linux')

        def test_isLinux_ON_LINUX(self):
            self.assertTrue(isLinux())

        def test_isMac(self):
            self.assertFalse(isMac())

        def test_linux_only(self):
            self.assertTrue(linux_only())

        def test_mac_only_ON_LINUX(self):
            # assertRaises >= 2.7
            try:
                mac_only()
                raise Exception('failed to raise mac only exception when running on Linux')
            except MacOnlyException:
                pass

    if isMac():
        def test_isMac_string(self):
            self.assertEqual(platform.system(), 'Darwin')

        def test_isLinux_ON_MAC(self):
            self.assertFalse(isLinux())

        def test_isLinux(self):
            self.assertTrue(isMac())

        def test_mac_only(self):
            self.assertTrue(mac_only())

        def test_linux_only_ON_MAC(self):
            # assertRaises >= 2.7
            try:
                linux_only()
                raise Exception('failed to raise linux_only exception when running on Mac')
            except LinuxOnlyException:
                pass

    if isLinux() or isMac():
        def test_isLinuxOrMac(self):
            self.assertTrue(isLinuxOrMac())
        def test_linux_mac_only(self):
            self.assertTrue(linux_mac_only())

# ============================================================================ #
#                          Validation Functions
# ============================================================================ #

    def test_isAlNum(self):
        self.assertTrue(isAlNum('ABC123efg'))
        self.assertTrue(isAlNum('0'))
        self.assertFalse(isAlNum('1.2'))
        self.assertFalse(isAlNum(' '))
        self.assertFalse(isAlNum('hari\@domain.com'))
        self.assertFalse(isAlNum(None))

    def test_isAwsAccessKey(self):
        self.assertTrue(isAwsAccessKey('A' * 20))
        self.assertTrue(isAwsAccessKey('1' * 20))
        self.assertTrue(isAwsAccessKey('A1' * 10))
        self.assertFalse(isAwsAccessKey('@' * 20))
        self.assertFalse(isAwsAccessKey('A' * 40))
        self.assertFalse(isAwsAccessKey('1' * 40))
        self.assertFalse(isAwsAccessKey(' '))
        self.assertFalse(isAwsAccessKey(None))

    def test_isAwsHostname(self):
        self.assertTrue(isAwsHostname('ip-172-31-1-1'))
        self.assertTrue(isAwsHostname('ip-172-31-1-1.eu-west-1.compute.internal'))
        self.assertFalse(isAwsHostname('harisekhon'))
        self.assertFalse(isAwsHostname('10.10.10.1'))
        self.assertFalse(isAwsHostname(' '))
        self.assertFalse(isAwsHostname(None))

    def test_isAwsFqdn(self):
        self.assertTrue(isAwsFqdn('ip-172-31-1-1.eu-west-1.compute.internal'))
        self.assertFalse(isAwsFqdn('ip-172-31-1-1'))
        self.assertFalse(isAwsFqdn(' '))
        self.assertFalse(isAwsFqdn(None))

    def test_isAwsSecretKey(self):
        self.assertTrue(isAwsSecretKey('A' * 40))
        self.assertTrue(isAwsSecretKey('1' * 40))
        self.assertFalse(isAwsSecretKey('@' * 40))
        self.assertFalse(isAwsSecretKey('A' * 20))
        self.assertFalse(isAwsSecretKey('A' * 20))
        self.assertFalse(isAwsSecretKey(' '))
        self.assertFalse(isAwsSecretKey(None))

    def test_isBlankOrNone(self):
        self.assertTrue(isBlankOrNone(' '))
        self.assertTrue(isBlankOrNone(''))
        self.assertTrue(isBlankOrNone('   '))
        self.assertTrue(isBlankOrNone(None))
        self.assertFalse(isBlankOrNone(' a'))
        self.assertFalse(isBlankOrNone(' a '))

    def test_isChars(self):
        self.assertTrue(isChars('Alpha-01_', 'A-Za-z0-9_-'))
        self.assertFalse(isChars('Alpha-01_*', 'A-Za-z0-9_-'))

    def test_isChars_exception_blank_chars(self):
        try:
            isChars('alpha', '')
            raise Exception('failed to coding raise exception for blank chars')
        except CodingErrorException:
            pass

    def test_isChars_exception_none_chars(self):
        try:
            isChars('alpha', None)
            raise Exception('failed to coding raise exception for none chars')
        except CodingErrorException:
            pass

    def test_isChars_exception_invalid_char_range(self):
        try:
            isChars('alpha', 'c-a')
            raise Exception('failed to coding raise exception for invalid char range')
        except CodingErrorException:
            pass

    def test_isCollection(self):
        self.assertTrue(isCollection('students.grades'))
        self.assertFalse(isCollection('wrong\@.grades'))
        self.assertFalse(isCollection(' '))
        self.assertFalse(isCollection(None))

    def test_isDatabaseName(self):
        self.assertTrue(isDatabaseName('mysql1'))
        self.assertFalse(isDatabaseName('my@sql'))
        self.assertFalse(isDatabaseName(' '))
        self.assertFalse(isDatabaseName(None))

    def test_isDatabaseColumnName(self):
        self.assertTrue(isDatabaseColumnName('myColumn_1'))
        self.assertFalse(isDatabaseColumnName("'column'"))
        self.assertFalse(isDatabaseColumnName(' '))
        self.assertFalse(isDatabaseColumnName(None))

    # rely on this for MySQL field by position
    def test_isDatabaseFieldName(self):
        self.assertTrue(isDatabaseFieldName('age'))
        self.assertTrue(isDatabaseFieldName(2))
        self.assertTrue(isDatabaseFieldName('count(*)'))
        self.assertFalse(isDatabaseFieldName('\@something'))
        self.assertFalse(isDatabaseFieldName(' '))
        self.assertFalse(isDatabaseFieldName(None))

    def test_isDatabaseTableName(self):
        self.assertTrue(isDatabaseTableName('myTable_1'))
        self.assertFalse(isDatabaseTableName("'table'"))
        self.assertTrue(isDatabaseTableName('default.myTable_1', True))
        self.assertFalse(isDatabaseTableName('default.myTable_1', False))
        self.assertFalse(isDatabaseTableName('default.myTable_1'))
        self.assertFalse(isDatabaseTableName(' '))
        self.assertFalse(isDatabaseTableName(None))

    def test_isDatabaseViewName(self):
        self.assertTrue(isDatabaseViewName('myView_1'))
        self.assertFalse(isDatabaseViewName("'View'"))
        self.assertTrue(isDatabaseViewName('default.myView_1', True))
        self.assertFalse(isDatabaseViewName('default.myView_1', False))
        self.assertFalse(isDatabaseViewName('default.myView_1'))
        self.assertFalse(isDatabaseViewName(' '))
        self.assertFalse(isDatabaseViewName(None))

    def test_isDict(self):
        self.assertTrue(isDict({'one':1,'two':2,'three':3}))
        self.assertTrue(isDict({}))
        self.assertFalse(isDict([]))
        self.assertFalse(isDict('blah'))
        self.assertFalse(isDict(None))
        self.assertFalse(isDict(file))

    def test_isDirname(self):
        self.assertTrue(isDirname('test_Dir'))
        self.assertTrue(isDirname('/tmp/test'))
        self.assertTrue(isDirname('./test'))
        self.assertFalse(isDirname('\@me'))
        self.assertFalse(isDirname(' '))
        self.assertFalse(isDirname(None))

    def test_isDomain(self):
        self.assertTrue(isDomain('localDomain'))
        self.assertTrue(isDomain('domain.local'))
        self.assertTrue(isDomain('harisekhon.com'))
        self.assertTrue(isDomain('1harisekhon.com'))
        self.assertTrue(isDomain('com'))
        self.assertTrue(isDomain('a' * 63 + '.com'))
        self.assertTrue(isDomain('compute.internal'))
        self.assertTrue(isDomain('eu-west-1.compute.internal'))
        self.assertFalse(isDomain('a' * 64))
        self.assertFalse(isDomain('a' * 252 + '.com'))
        self.assertFalse(isDomain('harisekhon'))
        self.assertFalse(isDomain(' '))
        self.assertFalse(isDomain(None))

    def test_isDomainStrict(self):
        self.assertTrue(isDomainStrict('123domain.com'))
        self.assertTrue(isDomainStrict('domain.local'))
        self.assertFalse(isDomainStrict('com'))
        self.assertTrue(isDomainStrict('domain.com'))
        self.assertTrue(isDomainStrict('domain.local'))
        self.assertTrue(isDomainStrict('domain.localDomain'))
        self.assertTrue(isDomainStrict('domain.local'))
        self.assertTrue(isDomainStrict('harisekhon.com'))
        self.assertTrue(isDomainStrict('1harisekhon.com'))
        self.assertTrue(isDomainStrict('a' * 63 + '.com'))
        self.assertTrue(isDomainStrict('compute.internal'))
        self.assertTrue(isDomainStrict('eu-west-1.compute.internal'))
        self.assertFalse(isDomainStrict('localDomain'))
        self.assertFalse(isDomainStrict('com'))
        self.assertFalse(isDomainStrict('a' * 64))
        self.assertFalse(isDomainStrict('a' * 252 + '.com'))
        self.assertFalse(isDomainStrict('harisekhon'))
        self.assertFalse(isDomainStrict(' '))
        self.assertFalse(isDomainStrict(None))

    def test_isDnsShortname(self):
        self.assertTrue(isDnsShortname('myHost'))
        self.assertFalse(isDnsShortname('myHost.domain.com'))
        self.assertFalse(isDnsShortname(' '))
        self.assertFalse(isDnsShortname(None))

    def test_isEmail(self):
        self.assertTrue(isEmail("hari'sekhon@gmail.com"))
        self.assertTrue(isEmail('hari@LOCALDOMAIN'))
        self.assertFalse(isEmail('harisekhon'))
        self.assertFalse(isEmail('a' * 257))
        self.assertFalse(isEmail(' '))
        self.assertFalse(isEmail(None))

    def test_isFilename(self):
        self.assertTrue(isFilename('some_File.txt'))
        self.assertTrue(isFilename('/tmp/test'))
        self.assertFalse(isFilename('@me'))
        self.assertFalse(isFilename(' '))
        self.assertFalse(isFilename(None))

    def test_isFloat(self):
        self.assertTrue(isFloat(1))
        self.assertTrue(isFloat('1'))
        self.assertFalse(isFloat(-1))
        self.assertFalse(isFloat('-1'))
        self.assertTrue(isFloat(1, True))
        self.assertTrue(isFloat('1', True))

        self.assertTrue(isFloat(1.1))
        self.assertTrue(isFloat('1.1'))

        self.assertFalse(isFloat(-1.1))
        self.assertFalse(isFloat('-1.1'))

        self.assertTrue(isFloat(-1.1, True))
        self.assertTrue(isFloat('-1.1', True))

        self.assertFalse(isFloat('nan'))
        self.assertFalse(isFloat('nan', True))

        self.assertFalse(isFloat(' ', True))
        self.assertFalse(isFloat(None, True))

    def test_isFqdn(self):
        self.assertTrue(isFqdn('hari.sekhon.com'))
        # denying this results in failing host.local as well
        self.assertFalse(isFqdn('hari@harisekhon.com'))
        self.assertFalse(isFqdn('a' * 256))
        self.assertFalse(isFqdn(' '))
        self.assertFalse(isFqdn(None))

    def test_isHex(self):
        self.assertTrue(isHex('0xAf09b'))
        self.assertFalse(isHex('0xhari'))
        self.assertTrue(isHex(0))
        self.assertFalse(isHex('g'))
        self.assertFalse(isHex(' '))
        self.assertFalse(isHex(None))

    def test_isHost(self):
        self.assertTrue(isHost('harisekhon.com'))
        self.assertTrue(isHost('harisekhon'))
        self.assertTrue(isHost('ip-172-31-1-1'))
        self.assertTrue(isHost('10.10.10.1'))
        self.assertTrue(isHost('10.10.10.10'))
        self.assertTrue(isHost('10.10.10.100'))
        self.assertTrue(isHost('10.10.10.0'))
        self.assertTrue(isHost('10.10.10.255'))
        self.assertFalse(isHost('10.10.10.256'))
        self.assertFalse(isHost('a' * 256))
        self.assertFalse(isHost(' '))
        self.assertFalse(isHost(None))

    def test_isHostname(self):
        self.assertTrue(isHostname('harisekhon.com'))
        self.assertTrue(isHostname('harisekhon'))
        self.assertTrue(isHostname('a'))
        self.assertTrue(isHostname('1'))
        self.assertTrue(isHostname('harisekhon1.com'))
        self.assertTrue(isHostname('1harisekhon.com'))
        self.assertFalse(isHostname('-help'))
        self.assertTrue(isHostname('a' * 63))
        self.assertFalse(isHostname('a' * 256))
        self.assertFalse(isHostname('hari~sekhon'))
        self.assertFalse(isHostname(' '))
        self.assertFalse(isHostname(None))

    def test_isInt(self):
        self.assertTrue(isInt(0))
        self.assertTrue(isInt(1))
        self.assertFalse(isInt(-1))
        self.assertFalse(isInt(1.1))
        self.assertFalse(isInt('a'))
        self.assertFalse(isInt(' '))
        self.assertFalse(isInt(''))
        self.assertFalse(isInt(None))

    def test_isInterface(self):
        self.assertTrue(isInterface('eth0'))
        self.assertTrue(isInterface('bond3'))
        self.assertTrue(isInterface('lo'))
        self.assertTrue(isInterface('docker0'))
        self.assertTrue(isInterface('vethfa1b2c3'))
        self.assertFalse(isInterface('vethfa1b2z3'))
        self.assertFalse(isInterface('b@ip'))
        self.assertFalse(isInterface(' '))
        self.assertFalse(isInterface(None))

    def test_isIP(self):
        self.assertTrue(isIP('10.10.10.1'))
        self.assertTrue(isIP('10.10.10.10'))
        self.assertTrue(isIP('10.10.10.100'))
        self.assertTrue(isIP('254.0.0.254'))
        self.assertTrue(isIP('255.255.255.254'))
        # may be entirely valid depending on the CIDR subnet mask
        self.assertTrue(isIP('10.10.10.0'))
        self.assertFalse(isIP('10.10.10.10.10'))
        self.assertTrue(isIP('10.10.10.255'))
        self.assertFalse(isIP('10.10.10.256'))
        self.assertFalse(isIP('10.10.-1.10'))
        self.assertFalse(isIP('x.x.x.x'))
        self.assertFalse(isIP(' '))
        self.assertFalse(isIP(None))

    def test_isJavaException(self):
        self.assertTrue(isJavaException('        at org.apache.ambari.server.api.services.stackadvisor.StackAdvisorRunner.runScript(StackAdvisorRunner.java:96)'))
        self.assertTrue(isJavaException('java.util.HashMap.writeObject(HashMap.java:1016)'))
        self.assertTrue(isJavaException('Exception in thread "main" java.lang.NullPointerException'))
        self.assertTrue(isJavaException('java.util.concurrent.RejectedExecutionException: Task java.util.concurrent.FutureTask@617d1af1 rejected from java.util.concurrent.ThreadPoolExecutor@5c73f637'))
        self.assertTrue(isJavaException('java.lang.NullPointerException:'))
        self.assertTrue(isJavaException(' java.lang.NullPointerException'))
        self.assertFalse(isJavaException('blah'))
        self.assertFalse(isJavaException(' '))
        self.assertFalse(isJavaException(None))

    def test_isJson(self):
        data = '{ "name": { "first": "Hari", "last": "Sekhon" } }'
        data_broken = '{ "name": { "first": "Hari", "last": "Sekhon" } ' # missing closing brace intentionally
        self.assertTrue(isJson(data))
        self.assertFalse(isJson(data_broken))
        self.assertFalse(isJson(''))
        self.assertFalse(isJson(None))

    def test_isKrb5Princ(self):
        self.assertTrue(isKrb5Princ('tgt/HARI.COM@HARI.COM'))
        self.assertTrue(isKrb5Princ('hari'))
        self.assertTrue(isKrb5Princ('hari@HARI.COM'))
        self.assertTrue(isKrb5Princ('hari/my.host.local@HARI.COM'))
        self.assertTrue(isKrb5Princ('cloudera-scm/admin@REALM.COM'))
        self.assertTrue(isKrb5Princ('cloudera-scm/admin@SUB.REALM.COM'))
        self.assertTrue(isKrb5Princ('hari@hari.com'))
        self.assertFalse(isKrb5Princ('hari$HARI.COM'))
        self.assertFalse(isKrb5Princ(' '))
        self.assertFalse(isKrb5Princ(None))

    def test_isLabel(self):
        self.assertTrue(isLabel('st4ts_used (%)'))
        self.assertFalse(isLabel('b@dlabel'))
        self.assertFalse(isLabel(' '))
        self.assertFalse(isLabel(None))

    def test_isLdapDn(self):
        self.assertTrue(isLdapDn('uid=hari,cn=users,cn=accounts,dc=local'))
        self.assertFalse(isLdapDn('hari@LOCAL'))
        self.assertFalse(isLdapDn(' '))
        self.assertFalse(isLdapDn(None))

    def test_isList(self):
        self.assertTrue(isList([1,2,3]))
        self.assertTrue(isList([]))
        self.assertFalse(isList(None))
        self.assertFalse(isList(file))

    def test_isMinVersion(self):
        self.assertTrue(isMinVersion('1.3.0', '1.3'))
        self.assertTrue(isMinVersion('1.3.0-alpha', '1.3'))
        self.assertTrue(isMinVersion('1.3', '1.3'))
        self.assertTrue(isMinVersion('1.4', '1.3'))
        self.assertTrue(isMinVersion('1.3.1', '1.2'))
        self.assertTrue(isMinVersion('1.3.1', 1.2))
        self.assertFalse(isMinVersion('1.3.1', '1.4'))
        self.assertFalse(isMinVersion('1.2.99', '1.3'))
        self.assertFalse(isMinVersion(' ', '1.3'))
        self.assertFalse(isMinVersion(None, '1.3'))

    def test_isNagiosUnit(self):
        self.assertTrue(isNagiosUnit('s'))
        self.assertTrue(isNagiosUnit('ms'))
        self.assertTrue(isNagiosUnit('us'))
        self.assertTrue(isNagiosUnit('B'))
        self.assertTrue(isNagiosUnit('KB'))
        self.assertTrue(isNagiosUnit('MB'))
        self.assertTrue(isNagiosUnit('GB'))
        self.assertTrue(isNagiosUnit('TB'))
        self.assertTrue(isNagiosUnit('c'))
        self.assertTrue(isNagiosUnit('%'))
        self.assertFalse(isNagiosUnit('Kbps'))
        self.assertFalse(isNagiosUnit(' '))
        self.assertFalse(isNagiosUnit(None))

    def test_isNoSqlKey(self):
        self.assertTrue(isNoSqlKey('HariSekhon:check_riak_write.pl:riak1:1385226607.02182:20abc'))
        self.assertFalse(isNoSqlKey('HariSekhon@check_riak_write.pl'))
        self.assertFalse(isNoSqlKey(' '))
        self.assertFalse(isNoSqlKey(None))

    def test_isPathQualified(self):
        self.assertTrue(isPathQualified('./blah'))
        self.assertTrue(isPathQualified('/blah'))
        self.assertTrue(isPathQualified('./path/to/blah.txt'))
        self.assertTrue(isPathQualified('/path/to/blah.txt'))
        self.assertTrue(isPathQualified('/tmp/.blah'))
        self.assertFalse(isPathQualified('blah'))
        self.assertFalse(isPathQualified('.blah'))
        self.assertFalse(isPathQualified('#tmpfile#'))
        self.assertFalse(isPathQualified('Europe/London'))
        # not supporting tilda home dirs
        self.assertFalse(isPathQualified('~blah'))
        self.assertFalse(isPathQualified(' '))
        self.assertFalse(isPathQualified(None))

    def test_isPort(self):
        self.assertTrue(isPort(1))
        self.assertTrue(isPort(80))
        self.assertTrue(isPort('8080'))
        self.assertTrue(isPort(65535))
        self.assertFalse(isPort(65536))
        self.assertFalse(isPort('a'))
        self.assertFalse(isPort(-1))
        self.assertFalse(isPort(0))
        self.assertFalse(isPort(' '))
        self.assertFalse(isPort(None))

    def test_isProcessName(self):
        self.assertTrue(isProcessName('../my_program'))
        self.assertTrue(isProcessName('ec2-run-instances'))
        self.assertTrue(isProcessName('sh <defunct>'))
        self.assertFalse(isProcessName('./b\@dfile'))
        self.assertFalse(isProcessName('[init] 3'))
        self.assertFalse(isProcessName(' '))
        self.assertFalse(isProcessName(None))

    def test_isPythonTraceback(self):
        self.assertTrue(isPythonTraceback('  File "/var/lib/ambari-server/resources/scripts/stack_advisor.py", line 154, in <module>'))
        self.assertTrue(isPythonTraceback('... Traceback (most recent call last):'))
        self.assertFalse(isPythonTraceback('blah'))
        self.assertFalse(isPythonTraceback(' '))
        self.assertFalse(isPythonTraceback(None))

    def test_isPythonVersion(self):
        self.assertTrue(isPythonVersion(getPythonVersion()))
        try:
            isPythonVersion(None)
            raise Exception('failed to raise exception for none arg')
        except CodingErrorException:
            pass

    def test_isPythonMinVersion(self):
        self.assertTrue(isPythonMinVersion('2.3'))
        self.assertFalse(isPythonMinVersion('10.0'))
        try:
            isPythonMinVersion(' ')
            raise Exception('failed to raise exception for blank version')
        except CodingErrorException:
            pass
        try:
            isPythonMinVersion(None)
            raise Exception('failed to raise exception for none version')
        except CodingErrorException:
            pass

    def test_isRegex(self):
        self.assertTrue(isRegex('.*'))
        self.assertTrue(isRegex('(.*)'))
        self.assertFalse(isRegex('(.*'))
        self.assertFalse(isRegex(''))
        self.assertFalse(isRegex(None))

    def test_isScientific(self):
        self.assertTrue(isScientific('1.2345E10'))
        self.assertTrue(isScientific('1e-10'))
        self.assertFalse(isScientific('-1e-10'))
        self.assertTrue(isScientific('-1e-10', True))
        self.assertFalse(isScientific(' ', True))
        self.assertFalse(isScientific(None, True))

    def test_isStr(self):
        self.assertTrue(isStr('test'))
        self.assertTrue(isStr(unicode('abcdef')))
        self.assertTrue(isStr(''))
        self.assertFalse(isStr(None))
        self.assertFalse(isStr(file))

    def test_isUrl(self):
        self.assertTrue(isUrl('www.google.com'))
        self.assertTrue(isUrl('http://www.google.com'))
        self.assertTrue(isUrl('https://gmail.com'))
        self.assertTrue(isUrl(1))
        self.assertFalse(isUrl('-help'))
        self.assertTrue(isUrl('http://cdh43:50070/dfsnodelist.jsp?whatNodes=LIVE'))
        self.assertFalse(isUrl(' '))
        self.assertFalse(isUrl(None))

    def test_isUrlPathSuffix(self):
        self.assertTrue(isUrlPathSuffix('/'))
        self.assertTrue(isUrlPathSuffix('/?var=something'))
        self.assertTrue(isUrlPathSuffix('/dir1/file.php?var=something+else&var2=more%20stuff'))
        self.assertTrue(isUrlPathSuffix('/*'))
        self.assertTrue(isUrlPathSuffix('/~hari'))
        self.assertFalse(isUrlPathSuffix('hari'))
        self.assertFalse(isUrlPathSuffix(' '))
        self.assertFalse(isUrlPathSuffix(None))

    def test_isUser(self):
        self.assertTrue(isUser('hadoop'))
        self.assertTrue(isUser('hari1'))
        self.assertTrue(isUser('mysql_test'))
        self.assertTrue(isUser('cloudera-scm'))
        self.assertFalse(isUser('-hari'))
        self.assertFalse(isUser('9hari'))
        self.assertFalse(isUser(' '))
        self.assertFalse(isUser(None))

    def test_isVersion(self):
        self.assertTrue(isVersion(1))
        self.assertTrue(isVersion('2.1.2'))
        self.assertTrue(isVersion('2.2.0.4'))
        self.assertTrue(isVersion('3.0'))
        self.assertFalse(isVersion('a'))
        self.assertFalse(isVersion('3a'))
        self.assertFalse(isVersion('1.0-2'))
        self.assertFalse(isVersion('1.0-a'))
        self.assertFalse(isVersion(' '))
        self.assertFalse(isVersion(None))

    def test_isVersionLax(self):
        self.assertTrue(isVersion(1))
        self.assertTrue(isVersionLax('2.1.2'))
        self.assertTrue(isVersionLax('2.2.0.4'))
        self.assertTrue(isVersionLax('3.0'))
        self.assertFalse(isVersionLax('a'))
        self.assertTrue(isVersionLax('3a'))
        self.assertTrue(isVersionLax('1.0-2'))
        self.assertTrue(isVersionLax('1.0-a'))
        self.assertFalse(isVersionLax('hari'))
        self.assertFalse(isVersionLax(' '))
        self.assertFalse(isVersionLax(None))

    def test_isXml(self):
        self.assertTrue(isXml('<blah></blah>'))
        self.assertFalse(isXml('<blah>'))
        self.assertFalse(isXml(' '))
        self.assertFalse(isXml(''))
        self.assertFalse(isXml(None))

    def test_isYes(self):
        self.assertTrue(isYes('yEs'))
        self.assertTrue(isYes('y'))
        self.assertTrue(isYes('Y'))
        self.assertFalse(isYes('yE'))
        self.assertFalse(isYes('no'))
        self.assertFalse(isYes('n'))
        self.assertFalse(isYes('N'))
        self.assertFalse(isYes(''))
        self.assertFalse(isYes(' '))
        self.assertFalse(isYes(None))

# ============================================================================ #

    def test_min_value(self):
        self.assertEquals(min_value(1, 4), 4)
        self.assertEquals(min_value(3, 1), 3)
        self.assertEquals(min_value(3, 4), 4)
        try:
            min_value(None, 4)
            raise Exception('failed to raise exception for none first arg')
        except CodingErrorException:
            pass
        try:
            min_value(3, None)
            raise Exception('failed to raise exception for none second arg')
        except CodingErrorException:
            pass

    #def test_human_units(self):
        # self.assertTrue(human_units(1023),               '1023 bytes',   'human_units(1023) eq '1023 bytes'');
        # self.assertTrue(human_units(1023*(1024**1)),     '1023KB',       'human_units KB');
        # self.assertTrue(human_units(1023.1*(1024**2)),   '1023.1MB',    'human_units MB');
        # self.assertTrue(human_units(1023.2*(1024**3)),   '1023.2GB',    'human_units GB');
        # self.assertTrue(human_units(1023.31*(1024**4)),  '1023.31TB',    'human_units TB');
        # self.assertTrue(human_units(1023.012*(1024**5)), '1023.01PB',    'human_units PB');
        # self.assertTrue(human_units(1023*(1024**6)), '1023EB', 'human_units EB'');

    def test_perf_suffix(self):
        self.assertEqual(perf_suffix('blah_in_bytes'), 'b')
        self.assertEqual(perf_suffix('blah_in_millis'), 'ms')
        self.assertEqual(perf_suffix('blah.bytes'), 'b')
        self.assertEqual(perf_suffix('blah.millis'), 'ms')
        self.assertEqual(perf_suffix('blah.blah2'), '')
        self.assertEqual(perf_suffix(' '), '')
        self.assertEqual(perf_suffix(None), '')

    # def test_pkill(self):
    #     self.assertFalse(pkill('nonexistentprogram'))

    def test_plural(self):
        self.assertEqual(plural(1), '')
        self.assertEqual(plural(''), '')
        self.assertEqual(plural(' '), '')
        self.assertEqual(plural(None), '')
        self.assertEqual(plural(2), 's')

    #def test_random_alnum(self):
        # like(random_alnum(20),  qr/^[A-Za-z0-9]{20}$/,                      'random_alnum(20)');
        # like(random_alnum(3),  qr/^[A-Za-z0-9][A-Za-z0-9][A-za-z0-9]$/,     'random_alnum(3)');

    def test_read_file_without_comments(self):
        read_file_without_comments(self.libfile)

    def test_jsonpp(self):
        data = '{ "name": { "first": "Hari", "last": "Sekhon" } }'
        data2 = '{\n    "name": {\n        "first": "Hari",\n        "last": "Sekhon"\n    }\n}'
        # print("jsonpp(data) = " + jsonpp(data))
        self.assertEqual(jsonpp(json.loads(data)), data2)
        self.assertEqual(jsonpp(data), data2)

    def test_list_sort_dicts_by_value(self):
        myList = [ { "name": "DATANODE" }, { "name": "STORM_UI_SERVER" }, { "name": "SUPERVISOR" }, { "name": "FLUME_HANDLER" }, { "name": "HISTORYSERVER" }, { "name": "RESOURCEMANAGER" }, { "name": "HCAT" }, { "name": "OOZIE_CLIENT" }, { "name": "PIG" }, { "name": "HIVE_CLIENT" }, { "name": "HDFS_CLIENT" }, { "name": "NIMBUS" }, { "name": "APP_TIMELINE_SERVER" }, { "name": "SPARK_CLIENT"}, {"name": "FALCON_CLIENT"}, {"name": "METRICS_MONITOR"}, {"name": "ACCUMULO_TSERVER"}, {"name": "SLIDER"}, {"name": "ACCUMULO_CLIENT"}, {"name": "HBASE_CLIENT"}, {"name": "ZOOKEEPER_SERVER"}, {"name": "MAPREDUCE2_CLIENT"}, {"name": "ZOOKEEPER_CLIENT"}, {"name": "SECONDARY_NAMENODE"}, {"name": "YARN_CLIENT"}, {"name": "SQOOP"}, {"name": "DRPC_SERVER" }, { "name": "MAHOUT" }, { "name": "HBASE_REGIONSERVER" }, { "name": "NODEMANAGER" }, { "name": "TEZ_CLIENT" } ]
        sortedList = [ {'name': 'ACCUMULO_CLIENT'}, {'name': 'ACCUMULO_TSERVER'}, {'name': 'APP_TIMELINE_SERVER'}, {'name': 'DATANODE'}, {'name': 'DRPC_SERVER'}, {'name': 'FALCON_CLIENT'}, {'name': 'FLUME_HANDLER'}, {'name': 'HBASE_CLIENT'}, {'name': 'HBASE_REGIONSERVER'}, {'name': 'HCAT'}, {'name': 'HDFS_CLIENT'}, {'name': 'HISTORYSERVER'}, {'name': 'HIVE_CLIENT'}, {'name': 'MAHOUT'}, {'name': 'MAPREDUCE2_CLIENT'}, {'name': 'METRICS_MONITOR'}, {'name': 'NIMBUS'}, {'name': 'NODEMANAGER'}, {'name': 'OOZIE_CLIENT'}, {'name': 'PIG'}, {'name': 'RESOURCEMANAGER'}, {'name': 'SECONDARY_NAMENODE'}, {'name': 'SLIDER'}, {'name': 'SPARK_CLIENT'}, {'name': 'SQOOP'}, {'name': 'STORM_UI_SERVER'}, {'name': 'SUPERVISOR'}, {'name': 'TEZ_CLIENT'}, {'name': 'YARN_CLIENT'}, {'name': 'ZOOKEEPER_CLIENT'}, {'name': 'ZOOKEEPER_SERVER'} ]
        # print('sortedList = %s' % list_sort_dicts_by_value(myList, 'name'))
        self.assertEquals(list_sort_dicts_by_value(myList, 'name'), sortedList)
        self.assertEquals(list_sort_dicts_by_value([], 'name'), [])
        try:
            list_sort_dicts_by_value(myList, 'brokenkey')
            raise Exception('failed to raise KeyError exception for invalid/missing key')
        except KeyError, e:
            pass
        try:
            list_sort_dicts_by_value(myList, None)
            raise Exception('failed to raise InvalidArgumentException when passed a non-string None for key')
        except InvalidArgumentException, e:
            pass
        try:
            list_sort_dicts_by_value('notAList', 'name')
            raise Exception('failed to raise InvalidArgumentException when passed a non-list')
        except InvalidArgumentException, e:
            pass
        try:
            list_sort_dicts_by_value([['test']], 'name')
            raise Exception('failed to raise AssertionError when list contains non-dict')
        except AssertionError, e:
            pass
        try:
            list_sort_dicts_by_value([{'name':['embedded_array_should_have_been_string']}], 'name')
            raise Exception('failed to raise AssertionError when list dict key value is not a string')
        except AssertionError, e:
            pass

    def test_support_msg(self):
        # avoid assertRegexpMatches as it's only available >= 2.7
        self.assertTrue(re.search('https://github.com/harisekhon/testrepo/issues', support_msg('testrepo')))
        self.assertTrue(re.search('https://github.com/harisekhon/pylib/issues', support_msg('')))

    def test_skip_java_output(self):
        self.assertTrue(skip_java_output('Class JavaLaunchHelper is implemented in both'))
        self.assertTrue(skip_java_output('SLF4J'))
        self.assertFalse(skip_java_output('aSLF4J'))
        self.assertFalse(skip_java_output(' SLF4J '))
        self.assertFalse(skip_java_output(' '))
        self.assertFalse(skip_java_output(''))
        self.assertFalse(skip_java_output(None))


        # def test_resolve_ip(self):
    #     # if not on a decent OS assume I'm somewhere lame like a bank where internal resolvers don't resolve internet addresses
    #     # this way my continous integration tests still run this one
    #     # still applies to Hortonworks Sandbox running on a banking VM :-/
    #     if(isLinuxOrMac()):
    #         if(os.getenv('TRAVIS', None) or os.popen('PATH=$PATH:/usr/sbin dmidecode | grep -i virtual').read().strip() == '' ):
    #             self.assertEqual(resolve_ip('a.resolvers.level3.net'),    '4.2.2.1')
    #             # self.assertEqual(validate_resolvable('a.resolvers.level3.net'),    '4.2.2.1',      'validate_resolvable('a.resolvers.level3.net')');
        # self.assertTrue(resolve_ip('4.2.2.2'),                   '4.2.2.2',      'resolve_ip('4.2.2.2') returns 4.2.2.2');
        # self.assertTrue(validate_resolvable('4.2.2.2'),                   '4.2.2.2',      'validate_resolvable('4.2.2.2') returns 4.2.2.2');

    def test_sec2human(self):
        self.assertEqual(sec2human(1),     '1 sec')
        self.assertEqual(sec2human(10),    '10 secs')
        self.assertEqual(sec2human(61),    '1 min 1 sec')
        self.assertEqual(sec2human(3676),  '1 hour 1 min 16 secs')
        self.assertEqual(sec2human(100000), '1 day 3 hours 46 mins 40 secs')
        try:
            sec2human(None)
            raise Exception('failed to raise exception for none')
        except CodingErrorException:
            pass
        try:
            sec2human('')
            raise Exception('failed to raise exception for blank')
        except CodingErrorException:
            pass
        try:
            sec2human(' ')
            raise Exception('failed to raise exception for spaces')
        except CodingErrorException:
            pass

    def test_sec2min(self):
        self.assertEqual(sec2min(65),     '1:05')
        self.assertEqual(sec2min(30),     '0:30')
        self.assertEqual(sec2min(3601),   '60:01')
        self.assertEqual(sec2min(0),      '0:00')
        self.assertEqual(sec2min(-1),     '')
        self.assertEqual(sec2min('aa'),   '')
        self.assertEqual(sec2min(''),     '')
        self.assertEqual(sec2min(' '),    '')
        self.assertEqual(sec2min(None),   '')

# ============================================================================ #
#                          Validation Functions
# ============================================================================ #

    # Not using assertRaises >= 2.7 and maintaining compatibility with Python 2.6 servers
    def test_validate_alnum(self):
        self.assertTrue(validate_alnum('Alnum2Test99', 'alnum test'))
        self.assertTrue(validate_alnum('0', 'alnum zero'))

    def test_validate_alnum_exception(self):
        try:
            validate_alnum('Alnum2Test99*', 'alnum invalid')
            raise Exception('validate_alnum() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_alnum_exception_noname(self):
        try:
            validate_alnum('Alnum2Test99*', '')
            raise Exception('validate_alnum() failed to raise exception for no name')
        except CodingErrorException:
            pass

    def test_validate_alnum_exception_none(self):
        try:
            validate_alnum(None, 'alnum invalid')
            raise Exception('validate_alnum() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_alnum_exception_blank(self):
        try:
            validate_alnum('', 'alnum invalid')
            raise Exception('validate_alnum() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_aws_access_key(self):
        self.assertTrue(validate_aws_access_key('A' * 20))

    def test_validate_aws_access_key_exception(self):
        try:
            validate_aws_access_key('A' * 19 + '*')
            raise Exception('validate_aws_access_key() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_aws_access_key_exception_none(self):
        try:
            validate_aws_access_key(None)
            raise Exception('validate_aws_access_key() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_aws_access_key_exception_blank(self):
        try:
            validate_aws_access_key('')
            raise Exception('validate_aws_access_key() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_aws_bucket(self):
        self.assertTrue(validate_aws_bucket('BucKeT63'))

    def test_validate_aws_bucket_exception(self):
        try:
            validate_aws_bucket('A' * 64)
            raise Exception('validate_aws_bucket() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_aws_bucket_exception_none(self):
        try:
            validate_aws_bucket(None)
            raise Exception('validate_aws_bucket() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_aws_bucket_exception_blank(self):
        try:
            validate_aws_bucket('')
            raise Exception('validate_aws_bucket() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_aws_secret_key(self):
        self.assertTrue(validate_aws_secret_key('A' * 40))
        self.assertTrue(validate_aws_secret_key('1' *40))
        self.assertTrue(validate_aws_secret_key('A1' * 20))

    def test_validate_aws_secret_key_exception(self):
        try:
            validate_aws_secret_key('A' * 41)
            raise Exception('validate_aws_secret_key() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_aws_secret_key_exception_none(self):
        try:
            validate_aws_secret_key(None)
            raise Exception('validate_aws_secret_key() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_aws_secret_key_exception_space(self):
        try:
            validate_aws_secret_key(' ')
            raise Exception('validate_aws_secret_key() failed to raise exception for space')
        except InvalidOptionException:
            pass

    def test_validate_aws_secret_key_exception_blank(self):
        try:
            validate_aws_secret_key('')
            raise Exception('validate_aws_secret_key() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_chars(self):
        self.assertTrue(validate_chars('log_date=2015-05-23_10', 'validate chars', 'A-Za-z0-9_=-'))

    def test_validate_chars_exception(self):
        try:
            validate_chars('log_date=2015-05-23_10*', 'validate chars broken', 'A-Za-z0-9_=-')
            raise Exception('validate_chars() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_chars_exception_noname(self):
        try:
            validate_chars('log_date=2015-05-23_10*', '', 'A-Za-z0-9_=-')
            raise Exception('validate_chars() failed to raise exception for no name')
        except CodingErrorException:
            pass

    def test_validate_chars_exception_none(self):
        try:
            validate_chars(None, 'validate chars broken', 'A-Za-z0-9_=-')
            raise Exception('validate_chars() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_chars_exception_blank(self):
        try:
            validate_chars('', 'validate chars broken', 'A-Za-z0-9_=-')
            raise Exception('validate_chars() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_collection(self):
        self.assertTrue(validate_collection('students.grades'))
        self.assertTrue(validate_collection('students.grades', 'name'))

    def test_validate_collection_exception(self):
        try:
            validate_collection('students.grades*')
            raise Exception('validate_collection() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_collection_exception_none(self):
        try:
            validate_collection(None)
            raise Exception('validate_collection() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_collection_exception_blank(self):
        try:
            validate_collection('')
            raise Exception('validate_collection() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_database(self):
        self.assertTrue(validate_database('mysql', 'MySQL'))

    def test_validate_database_exception(self):
        try:
            validate_database('mysql*', 'MySQL')
            raise Exception('validate_database() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_database_exception_none(self):
        try:
            validate_database(None, 'MySQL')
            raise Exception('validate_database() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_database_exception_blank(self):
        try:
            validate_database('', 'MySQL')
            raise Exception('validate_database() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_database_columnname(self):
        self.assertTrue(validate_database_columnname('myColumn_1'))

    def test_validate_database_columnname_exception(self):
        try:
            validate_database_columnname('myColumn_1*')
            raise Exception('validate_database_columnname() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_database_columnname_exception_none(self):
        try:
            validate_database_columnname(None)
            raise Exception('validate_database_columnname() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_database_columnname_exception_blank(self):
        try:
            validate_database_columnname('')
            raise Exception('validate_database_columnname() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_database_fieldname(self):
        self.assertTrue(validate_database_fieldname('age'))
        self.assertTrue(validate_database_fieldname(10))
        self.assertTrue(validate_database_fieldname('count(*)'))

    def test_validate_database_fieldname_exception(self):
        try:
            validate_database_fieldname('age*')
            raise Exception('validate_database_fieldname() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_database_fieldname_exception_none(self):
        try:
            validate_database_fieldname(None)
            raise Exception('validate_database_fieldname() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_database_fieldname_exception_blank(self):
        try:
            validate_database_fieldname('')
            raise Exception('validate_database_fieldname() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_database_tablename(self):
        self.assertTrue(validate_database_tablename('myTable', 'Hive'))
        self.assertTrue(validate_database_tablename('default.myTable', 'Hive', allow_qualified=True))

    def test_validate_database_tablename_exception(self):
        try:
            validate_database_tablename('myTable*', 'Hive')
            raise Exception('validate_database_tablename() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_database_tablename_exception_none(self):
        try:
            validate_database_tablename(None, 'Hive')
            raise Exception('validate_database_tablename() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_database_tablename_exception_blank(self):
        try:
            validate_database_tablename('', 'Hive')
            raise Exception('validate_database_tablename() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_database_viewname(self):
        self.assertTrue(validate_database_viewname('myview', 'Hive'))
        self.assertTrue(validate_database_viewname('default.myview', 'Hive', allow_qualified=True))

    def test_validate_database_viewname_exception(self):
        try:
            validate_database_viewname('myview*', 'Hive')
            raise Exception('validate_database_viewname() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_database_viewname_exception_none(self):
        try:
            validate_database_viewname(None, 'Hive')
            raise Exception('validate_database_viewname() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_database_viewname_exception_blank(self):
        try:
            validate_database_viewname('', 'Hive')
            raise Exception('validate_database_viewname() failed to raise exception for blank')
        except InvalidOptionException:
            pass


# ============================================================================ #

    def test_validate_database_query_select_show(self):
        self.assertTrue(validate_database_query_select_show('select * from myTable', 'name'))
        self.assertTrue(validate_database_query_select_show('select count(*) from db.myTable'))

    def test_validate_database_query_select_show_exception(self):
        try:
            validate_database_query_select_show('drop myTable', 'name')
            raise Exception('validate_database_query_select_show() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_database_query_select_show_exception_embedded_delete(self):
        try:
            validate_database_query_select_show('select * from (delete * from myTable)', 'name')
            raise Exception('validate_database_query_select_show() failed to raise exception for embedded delete')
        except InvalidOptionException:
            pass

    def test_validate_database_query_select_show_exception_none(self):
        try:
            validate_database_query_select_show(None, 'name')
            raise Exception('validate_database_query_select_show() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_database_query_select_show_exception_blank(self):
        try:
            validate_database_query_select_show('')
            raise Exception('validate_database_query_select_show() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_dirname(self):
        self.assertTrue(validate_dirname('test_Dir', 'name'))
        self.assertTrue(validate_dirname('/tmp/test'))
        self.assertTrue(validate_dirname('/nonexistentdir', None, True))

    def test_validate_dirname_exception(self):
        try:
            validate_dirname('b@ddir')
            raise Exception('validate_dirname() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_dirname_exception_none(self):
        try:
            validate_dirname(None)
            raise Exception('validate_dirname() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_dirname_exception_blank(self):
        try:
            validate_dirname('')
            raise Exception('validate_dirname() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_directory(self):
        if isLinuxOrMac():
            self.assertTrue(validate_directory('/etc', 'name'))
            self.assertTrue(validate_dir('/etc/'))

    def test_validate_directory_exception(self):
        try:
            validate_directory('/nonexistentdir')
            raise Exception('validate_directory() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_directory_exception_none(self):
        try:
            validate_directory(None)
            raise Exception('validate_directory() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_directory_exception_blank(self):
        try:
            validate_directory('')
            raise Exception('validate_directory() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_domain(self):
        self.assertTrue(validate_domain('localDomain', 'name'))
        self.assertTrue(validate_domain('domain.local'))
        self.assertTrue(validate_domain('harisekhon.com'))
        self.assertTrue(validate_domain('1harisekhon.com'))
        self.assertTrue(validate_domain('com'))
        self.assertTrue(validate_domain('a' * 63 + '.com'))
        self.assertTrue(validate_domain('compute.internal'))
        self.assertTrue(validate_domain('eu-west-1.compute.internal'))

    def test_validate_domain_exception(self):
        try:
            validate_domain('harisekhon')
            raise Exception('validate_domain() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_domain_exception64(self):
        try:
            validate_domain('a' * 64)
            raise Exception('validate_domain() failed to raise exception for 64 char')
        except InvalidOptionException:
            pass

    def test_validate_domain_exception_none(self):
        try:
            validate_domain(None)
            raise Exception('validate_domain() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_domain_exception_blank(self):
        try:
            validate_domain('')
            raise Exception('validate_domain() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_email(self):
        self.assertTrue(validate_email('hari\'sekhon@gmail.com'))
        self.assertTrue(validate_email('hari@LOCALDOMAIN'))

    def test_validate_email_exception(self):
        try:
            validate_email('harisekhon')
            raise Exception('validate_email() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_email_exception_none(self):
        try:
            validate_email(None)
            raise Exception('validate_email() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_email_exception_blank(self):
        try:
            validate_email('')
            raise Exception('validate_email() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_filename(self):
        self.assertTrue(validate_filename('../HariSekhonUtils.py', 'name'))
        self.assertTrue(validate_filename('some_File.txt'))
        self.assertTrue(validate_filename('/tmp/te-st'))
        self.assertTrue(validate_filename('/tmp/test.txt'))

    def test_validate_filename_exception(self):
        try:
            validate_filename('\@me')
            raise Exception('validate_filename() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_filename_exception_none(self):
        try:
            validate_filename(None)
            raise Exception('validate_filename() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_filename_exception_blank(self):
        try:
            validate_filename('')
            raise Exception('validate_filename() failed to raise exception for blank')
        except InvalidOptionException:
            pass


# ============================================================================ #

    def test_validate_file(self):
        self.assertTrue(validate_file(self.libfile, 'name'))
        if isLinuxOrMac():
            self.assertTrue(validate_file('/etc/passwd'))

    def test_validate_file_exception(self):
        try:
            validate_file('/etc/nonexistentfile')
            raise Exception('validate_file() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_file_exception_none(self):
        try:
            validate_file(None)
            raise Exception('validate_file() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_file_exception_blank(self):
        try:
            validate_file('')
            raise Exception('validate_file() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_float(self):
        self.assertTrue(validate_float(2, 'two', 0, 10))
        self.assertTrue(validate_float(-2, 'minus two', -10, 10))
        self.assertTrue(validate_float(2.1, 'two point one', 0, 10))
        self.assertTrue(validate_float(6.8, 'six point eight', 5, 10))
        self.assertTrue(validate_float(-6, 'minus six', -6, 0))


    def test_validate_float_exception_noname(self):
        try:
            validate_float(-6, '', -6, 0)
            raise Exception('validate_float() failed to raise exception for no name')
        except CodingErrorException:
            pass

    def test_validate_float_exception_min(self):
        try:
            validate_float(-6, 'name', 'blah', 0)
            raise Exception('validate_float() failed to raise exception for invalid min')
        except CodingErrorException:
            pass

    def test_validate_float_exception_max(self):
        try:
            validate_float(-6, 'name', -6, 'blah')
            raise Exception('validate_float() failed to raise exception for invalid max')
        except CodingErrorException:
            pass

    def test_validate_float_exception(self):
        try:
            validate_float(2, 'two', 3, 10)
            raise Exception('validate_float() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_float_exception_none(self):
        try:
            validate_float(None, 'none', 3, 10)
            raise Exception('validate_float() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_float_exception_blank(self):
        try:
            validate_float('', 'blank', 3, 10)
            raise Exception('validate_float() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_fqdn(self):
        self.assertTrue(validate_fqdn('www.harisekhon.com', 'name'))
        self.assertTrue(validate_fqdn('myhost.local'))

    def test_validate_fqdn_exception(self):
        try:
            validate_fqdn('b@ddomain.local')
            raise Exception('validate_fqdn() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_fqdn_exception_none(self):
        try:
            validate_fqdn(None)
            raise Exception('validate_fqdn() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_fqdn_exception_blank(self):
        try:
            validate_fqdn('')
            raise Exception('validate_fqdn() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_host(self):
        self.assertTrue(validate_host('harisekhon.com', 'name'))
        self.assertTrue(validate_host('harisekhon'))
        self.assertTrue(validate_host('ip-172-31-1-1'))
        self.assertTrue(validate_host('10.10.10.1'))
        self.assertTrue(validate_host('10.10.10.10'))
        self.assertTrue(validate_host('10.10.10.100'))
        self.assertTrue(validate_host('10.10.10.0'))
        self.assertTrue(validate_host('10.10.10.255'))

    def test_validate_host_exception_ip(self):
        try:
            validate_host('10.10.10.256')
            raise Exception('validate_host() failed to raise exception for 10.10.10.256')
        except InvalidOptionException:
            pass

    def test_validate_host_exception_a256(self):
        try:
            validate_host('a' * 256)
            raise Exception('validate_host() failed to raise exception for a * 256')
        except InvalidOptionException:
            pass

    def test_validate_host_exception_none(self):
        try:
            validate_host(None)
            raise Exception('validate_host() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_host_exception_blank(self):
        try:
            validate_host('')
            raise Exception('validate_host() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_hostname(self):
        self.assertTrue(validate_hostname('harisekhon.com', 'name'))
        self.assertTrue(validate_hostname('harisekhon'))
        self.assertTrue(validate_hostname('a'))
        self.assertTrue(validate_hostname('1'))
        self.assertTrue(validate_hostname('harisekhon1.com'))
        self.assertTrue(validate_hostname('1harisekhon.com'))
        self.assertTrue(validate_hostname('a' * 63))

    def test_validate_hostname_exception_help(self):
        try:
            self.assertTrue(validate_hostname('-help'))
            raise Exception('validate_hostname() failed to raise exception for -help')
        except InvalidOptionException:
            pass

    def test_validate_hostname_exception_64(self):
        try:
            self.assertTrue(validate_hostname('a' * 64))
            raise Exception('validate_hostname() failed to raise exception for a * 64')
        except InvalidOptionException:
            pass

    def test_validate_hostname_exception_tilda(self):
        try:
            self.assertTrue(validate_hostname('hari~sekhon'))
            raise Exception('validate_hostname() failed to raise exception for tilda')
        except InvalidOptionException:
            pass

    def test_validate_hostname_exception_none(self):
        try:
            validate_hostname(None)
            raise Exception('validate_hostname() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_hostname_exception_blank(self):
        try:
            validate_hostname('')
            raise Exception('validate_hostname() failed to raise exception for blank')
        except InvalidOptionException:
            pass


# ============================================================================ #

    def test_validate_int(self):
        self.assertTrue(validate_int(2, 'two', 0,10))
        self.assertTrue(validate_int(-2, 'minus-two', -10,10))
        self.assertTrue(validate_int(6,'six', 5, 10))
        self.assertTrue(validate_int(-6,'minus-six', -6, 0))
        self.assertTrue(validate_int(2,'two', 0, 10))
        self.assertTrue(validate_int(6,'six', 5, 7))

    def test_validate_int_exception_noname(self):
        try:
            validate_int(6,'', 5, 7)
            raise Exception('validate_int() failed to raise exception for no name')
        except CodingErrorException:
            pass

    def test_validate_int_exception_invalid_min(self):
        try:
            validate_int(6, 'name', 'blah', 7)
            raise Exception('validate_int() failed to raise exception for invalid min')
        except CodingErrorException:
            pass

    def test_validate_int_exception_invalid_max(self):
        try:
            validate_int(6, 'name', 5, 'blah')
            raise Exception('validate_int() failed to raise exception for invalid max')
        except CodingErrorException:
            pass

    def test_validate_int_exception_boundary(self):
        try:
            validate_int(3, 'three', 4, 10)
            raise Exception('validate_int() failed to raise exception for boundary')
        except InvalidOptionException:
            pass

    def test_validate_int_exception_float(self):
        try:
            validate_int(2.1, 'two-float', 0, 10)
            raise Exception('validate_int() failed to raise exception for float')
        except InvalidOptionException:
            pass

    def test_validate_int_exception_none(self):
        try:
            validate_int(None, 'blah', 0, 10)
            raise Exception('validate_int() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_int_exception_blank(self):
        try:
            validate_int('', 'blah2', 1, 5)
            raise Exception('validate_int() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_interface(self):
        self.assertTrue(validate_interface('eth0'))
        self.assertTrue(validate_interface('bond3'))
        self.assertTrue(validate_interface('lo'))
        self.assertTrue(validate_interface('docker0'))
        self.assertTrue(validate_interface('vethfa1b2c3'))

    def test_validate_interface_exception_boundary(self):
        try:
            validate_interface('vethfa1b2z3')
            raise Exception('validate_interface() failed to raise exception for vethfa1b2z3')
        except InvalidOptionException:
            pass

    def test_validate_interface_exception_float(self):
        try:
            validate_interface('b@interface')
            raise Exception('validate_interface() failed to raise exception for b@interface')
        except InvalidOptionException:
            pass

    def test_validate_interface_exception_none(self):
        try:
            validate_interface(None)
            raise Exception('validate_interface() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_interface_exception_blank(self):
        try:
            validate_interface('')
            raise Exception('validate_interface() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_ip(self):
        self.assertTrue(validate_ip('10.10.10.1', 'name'))
        self.assertTrue(validate_ip('10.10.10.10'))
        self.assertTrue(validate_ip('10.10.10.100'))
        self.assertTrue(validate_ip('254.0.0.254'))
        self.assertTrue(validate_ip('255.255.255.254'))
        # may be entirely valid depending on the CIDR subnet mask
        self.assertTrue(validate_ip('10.10.10.0'))
        self.assertTrue(validate_ip('10.10.10.255'))

    def test_validate_ip_exception_boundary(self):
        try:
            validate_ip('10.10.10.256')
            raise Exception('validate_ip() failed to raise exception for 10.10.10.256')
        except InvalidOptionException:
            pass

    def test_validate_ip_exception_x(self):
        try:
            validate_ip('x.x.x.x')
            raise Exception('validate_ip() failed to raise exception for x.x.x.x')
        except InvalidOptionException:
            pass

    def test_validate_ip_exception_none(self):
        try:
            validate_ip(None)
            raise Exception('validate_ip() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_ip_exception_blank(self):
        try:
            validate_ip('')
            raise Exception('validate_ip() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_krb5_princ(self):
        self.assertTrue(validate_krb5_princ('tgt/HARI.COM@HARI.COM', 'name'))
        self.assertTrue(validate_krb5_princ('hari'))
        self.assertTrue(validate_krb5_princ('hari@HARI.COM'))
        self.assertTrue(validate_krb5_princ('hari/my.host.local@HARI.COM'))
        self.assertTrue(validate_krb5_princ('cloudera-scm/admin@REALM.COM'))
        self.assertTrue(validate_krb5_princ('cloudera-scm/admin@SUB.REALM.COM'))
        self.assertTrue(validate_krb5_princ('hari@hari.com'))

    def test_validate_krb5_princ_exception(self):
        try:
            validate_krb5_princ('hari$HARI.COM')
            raise Exception('validate_krb5_princ() failed to raise exception for x.x.x.x')
        except InvalidOptionException:
            pass

    def test_validate_krb5_princ_exception_none(self):
        try:
            validate_krb5_princ(None)
            raise Exception('validate_krb5_princ() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_krb5_princ_exception_blank(self):
        try:
            validate_krb5_princ('')
            raise Exception('validate_krb5_princ() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_krb5_realm(self):
        self.assertTrue(validate_krb5_realm('localDomain', 'name'))
        self.assertTrue(validate_krb5_realm('domain.local'))
        self.assertTrue(validate_krb5_realm('harisekhon.com'))
        self.assertTrue(validate_krb5_realm('1harisekhon.com'))
        self.assertTrue(validate_krb5_realm('com'))
        self.assertTrue(validate_krb5_realm('a' * 63 + '.com'))
        self.assertTrue(validate_krb5_realm('compute.internal'))
        self.assertTrue(validate_krb5_realm('eu-west-1.compute.internal'))

    def test_validate_krb5_realm_exception(self):
        try:
            validate_krb5_realm('harisekhon')
            raise Exception('validate_krb5_realm() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_krb5_realm_exception64(self):
        try:
            validate_krb5_realm('a' * 64)
            raise Exception('validate_krb5_realm() failed to raise exception for 64 char')
        except InvalidOptionException:
            pass

    def test_validate_krb5_realm_exception_none(self):
        try:
            validate_krb5_realm(None)
            raise Exception('validate_krb5_realm() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_krb5_realm_exception_blank(self):
        try:
            validate_krb5_realm('')
            raise Exception('validate_krb5_realm() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_label(self):
        self.assertTrue(validate_label('st4ts_used (%)'))

    def test_validate_label_exception(self):
        try:
            validate_label('b@dlabel')
            raise Exception('validate_label() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_label_exception_none(self):
        try:
            validate_label(None)
            raise Exception('validate_label() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_label_exception_blank(self):
        try:
            validate_label('')
            raise Exception('validate_label() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_ldap_dn(self):
        self.assertTrue(validate_ldap_dn('uid=hari,cn=users,cn=accounts,dc=local'))
        self.assertTrue(validate_ldap_dn('uid=hari,cn=users,cn=accounts,dc=local', 'name'))

    def test_validate_ldap_dn_exception(self):
        try:
            validate_ldap_dn('hari\@LOCAL')
            raise Exception('validate_ldap_dn() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_ldap_dn_exception_none(self):
        try:
            validate_ldap_dn(None)
            raise Exception('validate_ldap_dn() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_ldap_dn_exception_blank(self):
        try:
            validate_ldap_dn('')
            raise Exception('validate_ldap_dn() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_nosql_key(self):
        self.assertTrue(validate_nosql_key('HariSekhon:check_riak_write.pl:riak1:1385226607.02182:20abc'))
        self.assertTrue(validate_nosql_key('HariSekhon:check_riak_write.pl:riak1:1385226607.02182:20abc', 'name'))

    def test_validate_nosql_key_exception(self):
        try:
            validate_nosql_key('HariSekhon@check_riak_write.pl')
            raise Exception('validate_nosql_key() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_nosql_key_exception_none(self):
        try:
            validate_nosql_key(None)
            raise Exception('validate_nosql_key() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_nosql_key_exception_blank(self):
        try:
            validate_nosql_key('')
            raise Exception('validate_nosql_key() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_port(self):
        self.assertTrue(validate_port(1, 'name'))
        self.assertTrue(validate_port(80))
        self.assertTrue(validate_port(65535))

    def test_validate_port_exception_65535(self):
        try:
            validate_port(65536)
            raise Exception('validate_port() failed to raise exception for 655356')
        except InvalidOptionException:
            pass

    def test_validate_port_exception_alpha(self):
        try:
            validate_port('a')
            raise Exception('validate_port() failed to raise exception for alpha')
        except InvalidOptionException:
            pass

    def test_validate_port_exception_negative(self):
        try:
            validate_port(-1)
            raise Exception('validate_port() failed to raise exception for negative')
        except InvalidOptionException:
            pass

    def test_validate_port_exception_zero(self):
        try:
            validate_port(0)
            raise Exception('validate_port() failed to raise exception for zero')
        except InvalidOptionException:
            pass

    def test_validate_port_exception_none(self):
        try:
            validate_port(None)
            raise Exception('validate_port() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_port_exception_blank(self):
        try:
            validate_port('')
            raise Exception('validate_port() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_process_name(self):
        self.assertTrue(validate_process_name('../my_program', 'name'))
        self.assertTrue(validate_process_name('ec2-run-instances'))
        self.assertTrue(validate_process_name('sh <defunct>'))

    def test_validate_process_name_exception_init(self):
        try:
            validate_process_name('[init] 3')
            raise Exception('validate_process_name() failed to raise exception for init')
        except InvalidOptionException:
            pass

    def test_validate_process_name_exception_badfile(self):
        try:
            validate_process_name('./b\@dfile')
            raise Exception('validate_process_name() failed to raise exception for badfile')
        except InvalidOptionException:
            pass

    def test_validate_process_name_exception_none(self):
        try:
            validate_process_name(None)
            raise Exception('validate_process_name() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_process_name_exception_blank(self):
        try:
            validate_process_name('')
            raise Exception('validate_process_name() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_password(self):
        self.assertTrue(validate_password('wh@tev3r', 'name'))
        self.assertTrue(validate_password('wh@tev3r'))

    def test_validate_password_exception_backticks(self):
        try:
            validate_password('`danger`')
            raise Exception('validate_password() failed to raise exception for backticks')
        except InvalidOptionException:
            pass

    def test_validate_password_exception_subshell(self):
        try:
            validate_password('$(hari)')
            raise Exception('validate_password() failed to raise exception for subshell')
        except InvalidOptionException:
            pass

    def test_validate_password_exception_double_quotes(self):
        try:
            validate_password('"hari"')
            raise Exception('validate_password() failed to raise exception for double quotes')
        except InvalidOptionException:
            pass

    def test_validate_password_exception_single_quotes(self):
        try:
            validate_password("O'Reilly")
            raise Exception('validate_password() failed to raise exception for single quotes')
        except InvalidOptionException:
            pass

    def test_validate_password_exception_none(self):
        try:
            validate_password(None)
            raise Exception('validate_password() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_password_exception_blank(self):
        try:
            validate_password('')
            raise Exception('validate_password() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_units(self):
        self.assertTrue(validate_units('s', 'name'))
        self.assertTrue(validate_units('ms'))
        self.assertTrue(validate_units('us'))
        self.assertTrue(validate_units('B'))
        self.assertTrue(validate_units('KB'))
        self.assertTrue(validate_units('MB'))
        self.assertTrue(validate_units('GB'))
        self.assertTrue(validate_units('TB'))
        self.assertTrue(validate_units('c'))
        self.assertTrue(validate_units('%'))

    def test_validate_units_exception(self):
        try:
            validate_units('a')
            raise Exception('validate_units() failed to raise exception for "a"')
        except InvalidOptionException:
            pass

    def test_validate_units_exception_none(self):
        try:
            validate_units(None)
            raise Exception('validate_units() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_units_exception_blank(self):
        try:
            validate_units('')
            raise Exception('validate_units() failed to raise exception for blank')
        except InvalidOptionException:
            pass


# ============================================================================ #

    def test_validate_url(self):
        self.assertTrue(validate_url('www.google.com', 'name'))
        self.assertTrue(validate_url('http://www.google.com'))
        self.assertTrue(validate_url('https://gmail.com'))
        self.assertTrue(validate_url('1'))
        self.assertTrue(validate_url('http://cdh43:50070/dfsnodelist.jsp?whatNodes=LIVE'))

    def test_validate_url_exception(self):
        try:
            validate_url('-help')
            raise Exception('validate_url() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_url_exception_none(self):
        try:
            validate_url(None)
            raise Exception('validate_url() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_url_exception_blank(self):
        try:
            validate_url('')
            raise Exception('validate_url() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_url_path_suffix(self):
        self.assertTrue(validate_url_path_suffix('/', 'name'))
        self.assertTrue(validate_url_path_suffix('/?var=something'))
        self.assertTrue(validate_url_path_suffix('/dir1/file.php?var=something+else&var2=more%20stuff'))
        self.assertTrue(validate_url_path_suffix('/*'))
        self.assertTrue(validate_url_path_suffix('/~hari'))

    def test_validate_url_path_suffix_exception(self):
        try:
            validate_url_path_suffix('hari')
            raise Exception('validate_url_path_suffix() failed to raise exception')
        except InvalidOptionException:
            pass

    def test_validate_url_path_suffix_exception_none(self):
        try:
            validate_url_path_suffix(None)
            raise Exception('validate_url_path_suffix() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_url_path_suffix_exception_blank(self):
        try:
            validate_url_path_suffix('')
            raise Exception('validate_url_path_suffix() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_validate_user(self):
        self.assertTrue(validate_user('hadoop', 'name'))
        self.assertTrue(validate_user('hari1'))
        self.assertTrue(validate_user('mysql_test'))
        self.assertTrue(validate_user('cloudera-scm'))

    def test_validate_user_exception_dashfirst(self):
        try:
            validate_user('-hari')
            raise Exception('validate_user() failed to raise exception for dashfirst')
        except InvalidOptionException:
            pass

    def test_validate_user_exception_numfirst(self):
        try:
            validate_user('9hari')
            raise Exception('validate_user() failed to raise exception for numfirst')
        except InvalidOptionException:
            pass

    def test_validate_user_exception_none(self):
        try:
            validate_user(None)
            raise Exception('validate_user() failed to raise exception for none')
        except InvalidOptionException:
            pass

    def test_validate_user_exception_blank(self):
        try:
            validate_user('')
            raise Exception('validate_user() failed to raise exception for blank')
        except InvalidOptionException:
            pass

# ============================================================================ #

    def test_vlog(self):
        vlog('vlog test')

    def test_vlog2(self):
        vlog2('vlog2 test')

    def test_vlog3(self):
        vlog3('vlog2 test')

    def test_vlog_option(self):
        vlog_option('vlog_option', 'test')


# ============================================================================ #

    if isLinuxOrMac():
        def test_which(self):
            self.assertTrue(which('/bin/sh'))
            self.assertTrue(which('sh'))

        def test_which_exception_non_executable(self):
            try:
                which('/etc/hosts')
                raise Exception('which() failed to raise non executable exception for /etc/hosts')
            except FileNotExecutableException:
                pass

    def test_which_exception_non_found(self):
        try:
            which('/etc/nonexistent')
            raise Exception('which() failed to raise exception for nonexistent file')
        except FileNotFoundException:
                pass

    def test_which_exception_invalid_filename(self):
        try:
            which('b@dfile')
            raise Exception('which() failed to raise exception for dashfirst')
        except InvalidFilenameException:
            pass

    def test_which_exception_numfirst(self):
        try:
            which('9hari')
            raise Exception('which() failed to raise exception for numfirst')
        except FileNotFoundException:
            pass

    def test_which_exception_none(self):
        try:
            which(None)
            raise Exception('which() failed to raise exception for none')
        except InvalidFilenameException:
            pass

    def test_which_exception_blank(self):
        try:
            which('')
            raise Exception('which() failed to raise exception for blank')
        except InvalidFilenameException:
            pass

# ============================================================================ #

# def test_validate_user_exists(self):
#     if isLinuxOrMac():
#         self.assertTrue(validate_user_exists('root'))
#
# def test_validate_user_exists_exception(self):
#     try:
#         validate_user_exists('noexistentuser')
#         raise Exception('validate_user_exists() failed to raise exception for nonexistentuser')
#     except InvalidOptionException:
#         pass
#
# def test_validate_user_exists_exception_none(self):
#     try:
#         validate_user_exists(None)
#         raise Exception('validate_user_exists() failed to raise exception for none')
#     except InvalidOptionException:
#         pass
#
# def test_validate_user_exists_exception_blank(self):
#     try:
#         validate_user_exists('')
#         raise Exception('validate_user_exists() failed to raise exception for blank')
#     except InvalidOptionException:
#         pass

# ============================================================================ #

if __name__ == '__main__':
    # increase the verbosity
    # verbosity Python >= 2.7
    #unittest.main(verbosity=2)
    log.setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(test_HariSekhonUtils)
    unittest.TextTestRunner(verbosity=2).run(suite)
