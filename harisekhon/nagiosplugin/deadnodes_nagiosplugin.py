#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-03-13 22:03:13 +0000 (Sun, 13 Mar 2016)
#
#  https://github.com/HariSekhon/pylib
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback
#
#  https://www.linkedin.com/in/HariSekhon
#

"""

Number of Dead Nodes Check Specialization of NagiosPlugin

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
from harisekhon.nagiosplugin import LiveNodesNagiosPlugin

__author__ = 'Hari Sekhon'
__version__ = '0.3.1'


class DeadNodesNagiosPlugin(LiveNodesNagiosPlugin):
    """
    Number of Dead Nodes Checker Nagios Plugin
    """

    __version__ = __version__
    # abstract class
    __metaclass__ = ABCMeta

    def _add_options(self):
        self.add_thresholds(name=self.agent_name, default_warning=0, default_critical=1)

    def _process_args(self):
        self.validate_thresholds(name=self.agent_name, simple='upper')

    @abstractmethod
    def get_nodecount(self):
        pass
