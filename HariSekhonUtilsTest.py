#
#  Author: Hari Sekhon
#  Date: 2013-01-06 01:25:55 +0000 (Sun, 06 Jan 2013)
#
#  http://github.com/harisekhon
#
#  License: see accompanying LICENSE file
#

# PyUnit Tests for HariSekhonUtils

import os
import sys
import unittest
sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))
from HariSekhonUtils import *

class HariSekhonUtilsTest(unittest.TestCase):

    # XXX: must prefix with test_ in order for the tests to be called

# ============================================================================ #
#                           Status Codes
# ============================================================================ #

    # Python 2.7+
    #@unittest.skip('skipping test codes')
    def test_status_codes(self):
        self.assertEqual(ERRORS['OK'], 0)
        self.assertEqual(ERRORS['WARNING'], 1)
        self.assertEqual(ERRORS['CRITICAL'], 2)
        self.assertEqual(ERRORS['UNKNOWN'], 3)

    # self.assertTrue($port, undef, 'port is undef');

# ============================================================================ #
# self.assertTrue(set_timeout_range(5,50),   50,   'set_timeout_range(1,50)');
# self.assertTrue($timeout_min, 5,  '$timeout_min eq 5');
# self.assertTrue($timeout_max, 50, '$timeout_max eq 50');
# self.assertTrue(set_timeout_max(200),     'set_timeout_max(200)');
# self.assertTrue($timeout_max, 200, '$timeout_max eq 200');
# self.assertTrue(set_timeout_default(100), 'set_timeout_default(100)');
# self.assertTrue($timeout_default, 100, '$timeout_default eq 100');

    #def test_current_status(self):
    #    self.assertEqual(status, 'UNKNOWN')

    # def test_get_status_code(self):
    #     self.assertEqual(get_status_code(status), 3)
    #     self.assertEqual(get_status_code(), 3)

# # ============================================================================ #
# $status = 'OK';
# self.assertTrue(status(),  0, 'status() eq 0');
# self.assertTrue(status2(), 0, 'status() eq 0');
# self.assertTrue(status3(), 0, 'status() eq 0');
# self.assertTrue(is_ok,        'is_self.assertTrue()');
# self.assertTrue(!is_warning,  'is_warning() fail on OK');
# self.assertTrue(!is_critical, 'is_critical() fail on OK');
# self.assertTrue(!is_unknown,  'is_unknown() fail on OK');
#
# # ============================================================================ #
# self.assertTrue(unknown, 'UNKNOWN', 'unknown()');
# self.assertTrue(status(),  3, 'status() eq 3');
# self.assertTrue(status2(), 3, 'status() eq 3');
# self.assertTrue(status3(), 3, 'status() eq 3');
# self.assertTrue(is_unknown,   'is_unknown()');
# self.assertTrue(!is_ok,       'is_self.assertTrue() fail on UNKNOWN');
# self.assertTrue(!is_warning,  'is_warning() fail on UNKNOWN');
# self.assertTrue(!is_critical, 'is_critical() fail on UNKNOWN');
#
# # ============================================================================ #
# self.assertTrue(warning, 'WARNING', 'warning()');
# self.assertTrue(status(),  1, 'status() eq 1');
# self.assertTrue(status2(), 1, 'status() eq 1');
# self.assertTrue(status3(), 1, 'status() eq 1');
# self.assertTrue(unknown, '',  'unknown() doesn't set \$status when WARNING');
# self.assertTrue(is_warning,   'is_warning()');
# self.assertTrue(!is_ok,       'is_self.assertTrue() fail on WARNING');
# self.assertTrue(!is_critical, 'is_critical() fail on WARNING');
# self.assertTrue(!is_unknown,  'is_unknown() fail on WARNING');
#
# # ============================================================================ #
# self.assertTrue(critical, 'CRITICAL', 'critical()');
# self.assertTrue(status(),  2, 'status() eq 2');
# self.assertTrue(status2(), 2, 'status() eq 2');
# self.assertTrue(status3(), 2, 'status() eq 2');
# self.assertTrue(unknown, '',  'unknown() doesn't set \$status when CRITICAL');
# self.assertTrue(warning, '',  'warning() doesn't set \$status when CRITICAL');
# self.assertTrue(is_critical,  'is_critical()');
# self.assertTrue(!is_ok,       'is_self.assertTrue() fail on CRITICAL');
# self.assertTrue(!is_warning,  'is_warning() fail on CRITICAL');
# self.assertTrue(!is_unknown,  'is_unknown() fail on CRITICAL');
#
# # ============================================================================ #
# self.assertTrue(get_status_code('OK'),         0, 'get_status_code(OK) eq 0');
# self.assertTrue(get_status_code('WARNING'),    1, 'get_status_code(WARNING) eq 1');
# self.assertTrue(get_status_code('CRITICAL'),   2, 'get_status_code(OK) eq 2');
# self.assertTrue(get_status_code('UNKNOWN'),    3, 'get_status_code(UNKNOWN) eq 3');
# self.assertTrue(get_status_code('DEPENDENT'),  4, 'get_status_code(DEPENDENT) eq 4');
# # This code errors out now
# #self.assertTrue(get_status_code('NONEXISTENT'),  undef, 'get_status_code(NONEXISTENT) eq undef');
#
# # This should cause compilation failure
# #self.assertTrue(critical('blah'), 'critical('blah')');
#
# # ============================================================================ #
# $verbose++;
# # TODO: This only checks the sub runs and returns success, should really check it outputs the right thing but not sure how to check the stdout from this sub
# self.assertTrue(status(), 'status()');

# ============================================================================ #
#                           O S   H e l p e r s
# ============================================================================ #
# self.assertTrue(isOS($^O),    'isOS($^O)');

    def test_isOS(self):
        self.assertEqual(isOS(platform.system()), isOS(platform.system()))

    if isLinux():
        def test_isLinux_string(self):
            self.assertEqual(platform.system(), 'Linux')
        def test_isLinux(self):
            self.assertTrue(isLinux())
        def test_isMac(self):
            self.assertFalse(isMac())
        def test_linux_only(self):
            self.assertTrue(linux_only())

    if isMac():
        def test_isMac_string(self):
            self.assertEqual(platform.system(), 'Darwin')
        def test_isLinux(self):
            self.assertFalse(isLinux())
        def test_isLinux(self):
            self.assertTrue(isMac())
        def test_mac_only(self):
            self.assertTrue(mac_only())

    if isLinux() or isMac():
        def test_isLinuxOrMac(self):
            self.assertTrue(isLinuxOrMac())
        def test_linux_mac_only(self):
            self.assertTrue(linux_mac_only())


# ============================================================================ #
    #def test_check_string(self):
    #    self.assertTrue()

# self.assertTrue(check_string('test', 'test'),    1,      'check_string('test', 'test') eq 1');
# self.assertTrue(check_string('test', 'testa'),    undef,  '!check_string('test', 'testa') eq undef');
# self.assertTrue(check_regex('test', '^test$'),   1,      'check_regex('test', '^test$') eq 1');
# self.assertTrue(check_regex('test', '^tes$'),    undef,  'check_regex('test', '^tes$') eq undef');

    def test_min_value(self):
        self.assertEquals(min_value(1, 4), 4)
        self.assertEquals(min_value(3, 1), 3)
        self.assertEqual(min_value(3,4), 4)

# # ============================================================================ #
# self.assertTrue(human_units(1023),               '1023 bytes',   'human_units(1023) eq '1023 bytes'');
# self.assertTrue(human_units(1023*(1024**1)),     '1023KB',       'human_units KB');
# self.assertTrue(human_units(1023.1*(1024**2)),   '1023.1MB',    'human_units MB');
# self.assertTrue(human_units(1023.2*(1024**3)),   '1023.2GB',    'human_units GB');
# self.assertTrue(human_units(1023.31*(1024**4)),  '1023.31TB',    'human_units TB');
# self.assertTrue(human_units(1023.012*(1024**5)), '1023.01PB',    'human_units PB');
# self.assertTrue(human_units(1023*(1024**6)), '1023EB', 'human_units EB'');
#
# # ============================================================================ #
# self.assertTrue(month2int('Jan'),  0, 'month2int(Jan)');
# self.assertTrue(month2int('Feb'),  1, 'month2int(Feb)');
# self.assertTrue(month2int('Mar'),  2, 'month2int(Mar)');
# self.assertTrue(month2int('Apr'),  3, 'month2int(Apr)');
# self.assertTrue(month2int('May'),  4, 'month2int(May)');
# self.assertTrue(month2int('Jun'),  5, 'month2int(Jun)');
# self.assertTrue(month2int('Jul'),  6, 'month2int(Jul)');
# self.assertTrue(month2int('Aug'),  7, 'month2int(Aug)');
# self.assertTrue(month2int('Sep'),  8, 'month2int(Sep)');
# self.assertTrue(month2int('Oct'),  9, 'month2int(Oct)');
# self.assertTrue(month2int('Nov'), 10, 'month2int(Nov)');
# self.assertTrue(month2int('Dec'), 11, 'month2int(Dec)');

# # ============================================================================ #

    def test_perf_suffix(self):
        self.assertEqual(perf_suffix('blah_in_bytes'), 'b')
        self.assertEqual(perf_suffix('blah_in_millis'), 'ms')
        self.assertEqual(perf_suffix('blah.bytes'), 'b')
        self.assertEqual(perf_suffix('blah.millis'), 'ms')
        self.assertEqual(perf_suffix('blah.blah2'), '')

# # ============================================================================ #

    def test_isAlNum(self):
        self.assertTrue(isAlNum('ABC123efg'))
        self.assertTrue(isAlNum('0'))
        self.assertFalse(isAlNum('1.2'))
        self.assertFalse(isAlNum(''))
        self.assertFalse(isAlNum('hari\@domain.com'))

    def test_isAwsAccessKey(self):
        self.assertTrue(isAwsAccessKey('A' * 20))
        self.assertTrue(isAwsAccessKey('1' * 20))
        self.assertTrue(isAwsAccessKey('A1' * 10))
        self.assertFalse(isAwsAccessKey('@' * 20))
        self.assertFalse(isAwsAccessKey('A' * 40))
        self.assertFalse(isAwsAccessKey('1' * 40))

    def test_isAwsSecretKey(self):
        self.assertTrue(isAwsSecretKey('A' * 40))
        self.assertTrue(isAwsSecretKey('1' * 40))
        self.assertFalse(isAwsSecretKey('@' * 40))
        self.assertFalse(isAwsSecretKey('A' * 20))

    # def test_isChars(self):
    #     self.assertTrue(isChars('Alpha-01_', 'A-Za-z0-9_-'))
    #     self.assertFalse(isChars('Alpha-01_*', 'A-Za-z0-9_-'))

    def test_isCollection(self):
        self.assertTrue(isCollection('students.grades'))
        self.assertFalse(isCollection('wrong\@.grades'))

    def test_isDatabaseName(self):
        self.assertTrue(isDatabaseName('mysql1'))
        self.assertFalse(isDatabaseName('my@sql'))

    def test_isDatabaseColumnName(self):
        self.assertTrue(isDatabaseColumnName('myColumn_1'))
        self.assertFalse(isDatabaseColumnName("'column'"))

    # rely on this for MySQL field by position
    def test_isDatabaseFieldName(self):
        self.assertTrue(isDatabaseFieldName('age'))
        self.assertTrue(isDatabaseFieldName(2))
        self.assertTrue(isDatabaseFieldName('count(*)'))
        self.assertFalse(isDatabaseFieldName('\@something'))

    def test_isDatabaseTableName(self):
        self.assertTrue(isDatabaseTableName('myTable_1'))
        self.assertFalse(isDatabaseTableName("'table'"))
        self.assertTrue(isDatabaseTableName('default.myTable_1', True))
        self.assertFalse(isDatabaseTableName('default.myTable_1', False))
        self.assertFalse(isDatabaseTableName('default.myTable_1'))

    def test_isDatabaseViewName(self):
        self.assertTrue(isDatabaseViewName('myView_1'))
        self.assertFalse(isDatabaseViewName("'View'"))
        self.assertTrue(isDatabaseViewName('default.myView_1', True))
        self.assertFalse(isDatabaseViewName('default.myView_1', False))
        self.assertFalse(isDatabaseViewName('default.myView_1'))

    def test_isDirname(self):
        self.assertTrue(isDirname('test_Dir'))
        self.assertTrue(isDirname('/tmp/test'))
        self.assertTrue(isDirname('./test'))
        self.assertFalse(isDirname('\@me'))

# self.assertTrue(validate_directory('./t'),       './t',      'validate_directory('./t')');
# if(isLinuxOrMac()){
#     self.assertTrue(validate_directory('/etc'),      '/etc',     'validate_directory('/etc')');
#     self.assertTrue(validate_directory('/etc/'),     '/etc/',    'validate_directory('/etc/')');
#     self.assertTrue(validate_dir('/etc/'),           '/etc/',    'validate_dir('/etc/')');
# }
# self.assertTrue(validate_directory('b@ddir', 1), undef,      'validate_directory(b@ddir)');
# # cannot validate dir not existing here as it terminates program

    # def test_isCollection(self):
    #     self.assertTrue()
    #     self.assertFalse()

    def test_isDomain(self):
        self.assertTrue(isDomain('localDomain'))
        self.assertTrue(isDomain('domain.local'))
        self.assertTrue(isDomain('harisekhon.com'))
        self.assertTrue(isDomain('1harisekhon.com'))
        self.assertTrue(isDomain('com'))
        self.assertTrue(isDomain('a' * 63 + '.com'))
        self.assertFalse(isDomain('a' * 64))
        self.assertFalse(isDomain('harisekhon'))
        self.assertTrue(isDomain('compute.internal'))
        self.assertTrue(isDomain('eu-west-1.compute.internal'))
        self.assertTrue(isDomainStrict('123domain.com'))
        self.assertTrue(isDomainStrict('domain.local'))
        self.assertFalse(isDomainStrict('com'))
        self.assertTrue(isDomainStrict('domain.com'))
        self.assertTrue(isDomainStrict('domain.local'))
        self.assertTrue(isDomainStrict('domain.localDomain'))

    def test_isDnsShortname(self):
        self.assertTrue(isDnsShortname('myHost'))
        self.assertFalse(isDnsShortname('myHost.domain.com'))

    def test_isEmail(self):
        self.assertTrue(isEmail("hari'sekhon@gmail.com"))
        self.assertTrue(isEmail('hari@LOCALDOMAIN'))
        self.assertFalse(isEmail('harisekhon'))

    def test_isFilename(self):
        self.assertTrue(isFilename('some_File.txt'))
        self.assertTrue(isFilename('/tmp/test'))
        self.assertFalse(isFilename('@me'))

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

    def test_isFqdn(self):
        self.assertTrue(isFqdn('hari.sekhon.com'))
        # denying this results in failing host.local as well
        self.assertFalse(isFqdn('hari@harisekhon.com'))

    def test_isHex(self):
        self.assertTrue(isHex('0xAf09b'))
        self.assertFalse(isHex('0xhari'))
        self.assertTrue(isHex(0))
        self.assertFalse(isHex('g'))

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

    def test_isAwsHostname(self):
        self.assertTrue(isAwsHostname('ip-172-31-1-1'))
        self.assertTrue(isAwsHostname('ip-172-31-1-1.eu-west-1.compute.internal'))
        self.assertFalse(isAwsHostname('harisekhon'))
        self.assertFalse(isAwsHostname('10.10.10.1'))

    def test_isAwsFqdn(self):
        self.assertTrue(isAwsFqdn('ip-172-31-1-1.eu-west-1.compute.internal'))
        self.assertFalse(isAwsFqdn('ip-172-31-1-1'))

    def test_isHostname(self):
        self.assertTrue(isHostname('harisekhon.com'))
        self.assertTrue(isHostname('harisekhon'))
        self.assertTrue(isHostname('a'))
        self.assertTrue(isHostname('1'))
        self.assertTrue(isHostname('harisekhon1.com'))
        self.assertTrue(isHostname('1harisekhon.com'))
        self.assertFalse(isHostname('-help'))
        self.assertTrue(isHostname('a' * 63))
        self.assertFalse(isHostname('a' * 64))
        self.assertFalse(isHostname('hari~sekhon'))

    def test_isInt(self):
        self.assertTrue(isInt(0))
        self.assertTrue(isInt(1))
        self.assertFalse(isInt(-1))
        self.assertFalse(isInt(1.1))
        self.assertFalse(isInt('a'))

    def test_isInterface(self):
        self.assertTrue(isInterface('eth0'))
        self.assertTrue(isInterface('bond3'))
        self.assertTrue(isInterface('lo'))
        self.assertTrue(isInterface("docker0"))
        self.assertTrue(isInterface('vethfa1b2c3'))
        self.assertFalse(isInterface('vethfa1b2z3'))
        self.assertFalse(isInterface('b@interface'))

    def test_isIP(self):
        self.assertTrue(isIP('10.10.10.1'))
        self.assertTrue(isIP('10.10.10.10'))
        self.assertTrue(isIP('10.10.10.100'))
        self.assertTrue(isIP('254.0.0.254'))
        self.assertTrue(isIP('255.255.255.254'))
        # may be entirely valid depending on the CIDR subnet mask
        self.assertTrue(isIP('10.10.10.0'))
        self.assertTrue(isIP('10.10.10.255'))
        self.assertFalse(isIP('10.10.10.256'))
        self.assertFalse(isIP('x.x.x.x'))

    def test_isJavaException(self):
        self.assertTrue(isJavaException('        at org.apache.ambari.server.api.services.stackadvisor.StackAdvisorRunner.runScript(StackAdvisorRunner.java:96)'))
        self.assertFalse(isJavaException('blah'))

    def test_isKrb5Princ(self):
        self.assertTrue(isKrb5Princ('tgt/HARI.COM@HARI.COM'))
        self.assertTrue(isKrb5Princ('hari'))
        self.assertTrue(isKrb5Princ('hari@HARI.COM'))
        self.assertTrue(isKrb5Princ('hari/my.host.local@HARI.COM'))
        self.assertTrue(isKrb5Princ('cloudera-scm/admin@REALM.COM'))
        self.assertTrue(isKrb5Princ('cloudera-scm/admin@SUB.REALM.COM'))
        self.assertTrue(isKrb5Princ('hari@hari.com'))
        self.assertFalse(isKrb5Princ('hari$HARI.COM'))

    def test_isLabel(self):
        self.assertTrue(isLabel('st4ts_used (%)'))
        self.assertFalse(isLabel('b@dlabel'))

    def test_isLdapDn(self):
        self.assertTrue(isLdapDn('uid=hari,cn=users,cn=accounts,dc=local'))
        self.assertFalse(isLdapDn('hari@LOCAL'))

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

    def test_isNoSqlKey(self):
        self.assertTrue(isNoSqlKey('HariSekhon:check_riak_write.pl:riak1:1385226607.02182:20abc'))
        self.assertFalse(isNoSqlKey('HariSekhon@check_riak_write.pl'))

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

    # def test_isPort(self):
    #     self.assertTrue(isPort(1))
    #     self.assertTrue(isPort(80))
    #     self.assertTrue(isPort(65535))
    #     self.assertFalse(isPort(65536))
    #     self.assertFalse(isPort('a'))
    #     self.assertFalse(isPort(-1))
    #     self.assertFalse(isPort(0))

    def test_isProcessName(self):
        self.assertTrue(isProcessName('../my_program'))
        self.assertTrue(isProcessName('ec2-run-instances'))
        self.assertTrue(isProcessName('sh <defunct>'))
        self.assertFalse(isProcessName('./b\@dfile'))
        self.assertFalse(isProcessName('[init] 3'))

    def test_isPythonTraceback(self):
        self.assertTrue(isPythonTraceback('  File "/var/lib/ambari-server/resources/scripts/stack_advisor.py", line 154, in <module>'))
        self.assertTrue(isPythonTraceback('... Traceback (most recent call last):'))
        self.assertFalse(isPythonTraceback('blah'))

# self.assertTrue(isRegex('.*'),   '.*',   'isRegex('.*') eq '.*'');
# self.assertTrue(isRegex('(.*)'), '(.*)', 'isRegex('(.*)') eq '(.*)'');
# self.assertTrue(isRegex('(.*'),  undef,  'isRegex('(.*') eq undef');

    def test_isScientific(self):
        self.assertTrue(isScientific('1.2345E10'))
        self.assertTrue(isScientific('1e-10'))
        self.assertFalse(isScientific('-1e-10'))
        self.assertTrue(isScientific('-1e-10', True))

    def test_isUrl(self):
        self.assertTrue(isUrl('www.google.com'))
        self.assertTrue(isUrl('http://www.google.com'))
        self.assertTrue(isUrl('https://gmail.com'))
        self.assertTrue(isUrl(1))
        self.assertFalse(isUrl('-help'))
        self.assertTrue(isUrl('http://cdh43:50070/dfsnodelist.jsp?whatNodes=LIVE'))

    def test_isUrlPathSuffix(self):
        self.assertTrue(isUrlPathSuffix('/'))
        self.assertTrue(isUrlPathSuffix('/?var=something'))
        self.assertTrue(isUrlPathSuffix('/dir1/file.php?var=something+else&var2=more%20stuff'))
        self.assertTrue(isUrlPathSuffix('/*'))
        self.assertTrue(isUrlPathSuffix('/~hari'))
        self.assertFalse(isUrlPathSuffix('hari'))

    def test_isUser(self):
        self.assertTrue(isUser('hadoop'))
        self.assertTrue(isUser('hari1'))
        self.assertTrue(isUser('mysql_test'))
        self.assertTrue(isUser('cloudera-scm'))
        self.assertFalse(isUser('-hari'))
        self.assertFalse(isUser('1983hari'))

    def test_isVersion(self):
        self.assertTrue(isVersion(1))
        self.assertTrue(isVersion('2.1.2'))
        self.assertTrue(isVersion('2.2.0.4'))
        self.assertTrue(isVersion('3.0'))
        self.assertFalse(isVersion('a'))
        self.assertFalse(isVersion('3a'))
        self.assertFalse(isVersion('1.0-2'))
        self.assertFalse(isVersion('1.0-a'))

# # ============================================================================ #
# self.assertTrue(isXml('<blah></blah>'), 'isXML()');
# self.assertTrue(!isXml('<blah>'), '!isXml()');

    def test_isYes(self):
        self.assertTrue(isYes('yEs'))
        self.assertTrue(isYes('y'))
        self.assertTrue(isYes('Y'))
        self.assertFalse(isYes('yE'))
        self.assertFalse(isYes('no'))
        self.assertFalse(isYes('n'))
        self.assertFalse(isYes('N'))
        self.assertFalse(isYes(''))

    # def test_pkill(self):
    #     self.assertFalse(pkill('nonexistentprogram'))

    def test_plural(self):
        self.assertEqual(plural(1), '')
        self.assertEqual(plural(2), 's')

# # ============================================================================ #
# like(random_alnum(20),  qr/^[A-Za-z0-9]{20}$/,                      'random_alnum(20)');
# like(random_alnum(3),  qr/^[A-Za-z0-9][A-Za-z0-9][A-za-z0-9]$/,     'random_alnum(3)');

    def test_sec2human(self):
        self.assertEqual(sec2human(1),     '1 sec')
        self.assertEqual(sec2human(10),    '10 secs')
        self.assertEqual(sec2human(61),    '1 min 1 sec')
        self.assertEqual(sec2human(3676),  '1 hour 1 min 16 secs')

    def skip_java_output(self):
        self.assertTrue(skip_java_output('Class JavaLaunchHelper is implemented in both'))
        self.assertTrue(skip_java_output('SLF4J'))
        self.assertFalse(skip_java_output('aSLF4J'))

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

    # def test_sec2min(self):
        # self.assertTrue(sec2min(65),     '1:05',     'sec2min(65) eq '1:05'');
        # self.assertTrue(sec2min(30),     '0:30',     'sec2min(30) eq '0:30'');
        # self.assertTrue(sec2min(3601),   '60:01',    'sec2min(3601) eq '60:01'');
        # self.assertTrue(sec2min(-1),     undef,      'sec2min(-1) eq undef');
        # self.assertTrue(sec2min('aa'),   undef,      'sec2min('aa') eq undef');
        # self.assertTrue(sec2min(0),      '0:00',     'sec2min(0) eq 0:00');
        #

        
if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(HariSekhonUtilsTest)
    unittest.TextTestRunner(verbosity=2).run(suite)