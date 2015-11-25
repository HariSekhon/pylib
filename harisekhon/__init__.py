#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2015-11-14 12:21:54 +0000 (Sat, 14 Nov 2015)
#
#  https://github.com/harisekhon/pylib
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn and optionally send me feedback to help improve or steer this or other code I publish
#
#  http://www.linkedin.com/in/harisekhon
#

# Would make this package com.linkedin.harisekhon like my Java library but it goes against convention in Python

from harisekhon.utils import *
# enables 'from HariSekhon import CLI'
from harisekhon.cli import CLI

# pulls submodules in to 'from com.linkedin.harisekhon import *'
# __all__ = [ 'submodule1', 'submodule2' ]