#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-11-22 16:52:53 +0000 (Tue, 22 Nov 2016)
#
#  https://github.com/harisekhon/pylib
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback to help steer this or other code I publish
#
#  https://www.linkedin.com/in/harisekhon
#

"""

Rest API Version Check Specialization of NagiosPlugin

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import os
import re
import sys
import traceback
# Python 2.6+ only
from abc import ABCMeta #, abstractmethod
srcdir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.join(srcdir, 'pylib')
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from harisekhon.utils import log, qquit, support_msg_api, isList
    from harisekhon.utils import validate_regex, isVersion, isVersionLax
    from harisekhon.nagiosplugin import RestNagiosPlugin
except ImportError as _:
    print(traceback.format_exc(), end='')
    sys.exit(4)

__author__ = 'Hari Sekhon'
__version__ = '0.4'


class RestVersionNagiosPlugin(RestNagiosPlugin):

    __version__ = __version__
    # abstract class
    __metaclass__ = ABCMeta

    def __init__(self):
        # Python 2.x
        super(RestVersionNagiosPlugin, self).__init__()
        # Python 3.x
        # super().__init__()
        self.expected = None
        self.msg = 'version unknown - no message defined'
        self.lax_version = False

    def add_options(self):
        super(RestVersionNagiosPlugin, self).add_options()
        self.add_expected_version_option()

    def add_expected_version_option(self):
        self.add_opt('-e', '--expected', help='Expected version regex (optional)')

    def process_options(self):
        super(RestVersionNagiosPlugin, self).process_options()
        self.process_expected_version_option()

    def process_expected_version_option(self):
        self.expected = self.get_opt('expected')
        if self.expected is not None:
            validate_regex(self.expected)
            log.info('expected version regex: %s', self.expected)

    def run(self):
        version = self.get_version()
        log.info("got version '%s'", version)
        self.check_version(version)
        extra_info = self.extra_info()
        if extra_info:
            self.msg += extra_info

    def check_version(self, version):
        name = self.name
        if isList(name):
            name = name[0]
        log.info("checking version '%s'", version)
        if not version:
            qquit('UNKNOWN', '{0} version not found. {1}'.format(name, support_msg_api()))
        if self.lax_version and isVersionLax(version):
            pass
        elif not isVersion(version):
            qquit('UNKNOWN', '{0} version unrecognized \'{1}\'. {2}'\
                             .format(name, version, support_msg_api()))
        self.msg = '{0} version = {1}'.format(name, version)
        if self.expected is not None:
            log.info("verifying version against expected regex '%s'", self.expected)
            if re.match(self.expected, version):
                log.info('version regex matches retrieved version')
            else:
                log.info('version regex does not match retrieved version')
                self.msg += " (expected '{0}')".format(self.expected)
                self.critical()

    def get_version(self):
        req = self.query()
        if self.json:
            version = self.process_json(req.content)
        else:
            version = self.parse(req)
        return version

    def extra_info(self):
        pass
