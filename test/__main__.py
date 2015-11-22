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

from __future__ import print_function

__author__  = 'Hari Sekhon'
__version__ = '0.1'

import glob
import inspect
import os
import subprocess
import sys
## using optparse rather than argparse for servers still on Python 2.6
#from optparse import OptionParser
libdir = os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), '..')
# sys.path.append(libdir)
# try:
#    from HariSekhonUtils import *
# except ImportError, e:
#    print('module import failed: %s' % e)
#    sys.exit(3)
# except Exception, e:
#    print('exception encountered during module import: %s' % e)
#    sys.exit(3)

def main():
    print('running unit tests')
    for x in glob.glob(libdir + "/test/test_*.py"):
        print('running %s' % x)
        #os.system('python ' + x)
        if not subprocess.call(['python', x]):
            sys.exit(2)

if __name__ == '__main__':
    main()
