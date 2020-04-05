#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-03-13 21:47:07 +0000 (Sun, 13 Mar 2016)
#
#  https://github.com/harisekhon/pylib
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback
#
#  https://www.linkedin.com/in/harisekhon
#

"""

Number of Live Nodes Check Specialization of NagiosPlugin

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import os
import sys
# Python 2.6+ only
from abc import ABCMeta, abstractmethod
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(libdir)
# pylint: disable=wrong-import-position
from harisekhon.utils import UnknownError, CodingError, qquit, plural
from harisekhon.utils import get_topfile, validate_host, validate_port
from harisekhon.nagiosplugin import NagiosPlugin

__author__ = 'Hari Sekhon'
__version__ = '0.3.1'


class LiveNodesNagiosPlugin(NagiosPlugin):
    """
    Number of Live Nodes Checker Nagios Plugin
    """

    __version__ = __version__
    # abstract class
    __metaclass__ = ABCMeta

    def __init__(self):
        # Python 2.x
        super(LiveNodesNagiosPlugin, self).__init__()
        # Python 3.x
        # super().__init__()
        self.default_host = 'localhost'
        self.default_port = None
        self.host = None
        self.port = None
        self.name = None
        self.agent_name = 'node'
        self.state = 'online'
        self.node_count = None
        self.additional_info = ''
        self.additional_perfdata = ''
        topfile = get_topfile()
        if 'workers' in topfile:
            self.agent_name = 'worker'
        elif 'slaves' in topfile:
            self.agent_name = 'slave'
        elif 'agents' in topfile:
            self.agent_name = 'agent'

    def add_options(self):
        if not self.name:
            raise CodingError("didn't name check, please set self.name in __init__()")
        self.add_hostoption(self.name, default_host=self.default_host, default_port=self.default_port)
        self._add_options()

    def _add_options(self):
        self.add_thresholds(name=self.agent_name, default_warning=3, default_critical=2)

    def process_args(self):
        if not self.name:
            raise CodingError("didn't name check, please set self.name in __init__()")
        self.no_args()
        self.host = self.get_opt('host')
        self.port = self.get_opt('port')
        validate_host(self.host)
        validate_port(self.port)
        self._process_args()

    def _process_args(self):
        self.validate_thresholds(self.agent_name, simple='lower')

    def run(self):
        self.ok()
        self.node_count = self.get_nodecount()

    @abstractmethod
    def get_nodecount(self):
        pass

    def end(self):
        if self.node_count is None:
            raise UnknownError('node count is not set!')
        self.msg = '{0} {1}{2} {3}'.format(self.node_count, self.agent_name, plural(self.node_count), self.state)
        self.check_thresholds(self.node_count)
        if self.additional_info:
            self.msg += ', {0}'.format(self.additional_info)
        self.msg += ' | {0}s_{1}={2:d}s{3}'.format(self.agent_name, self.state,
                                                   self.node_count, self.get_perf_thresholds())
        if self.additional_perfdata:
            self.msg += ' {0}'.format(self.additional_perfdata)
        qquit(self.status, self.msg)
