#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2015-11-29 15:32:25 +0000 (Sun, 29 Nov 2015)
#
#  https://github.com/harisekhon/pytools
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

import coverage
import os
import sys
# using optparse rather than argparse for servers still on Python 2.6
from optparse import OptionParser
sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])) + '/lib')
try:
    from HariSekhonUtils import *
    from HariSekhon import CLI
    from HariSekhon import NagiosPlugin
    spark_home = os.getenv('SPARK_HOME', None)
    if spark_home:
        sys.path.append(os.path.join(spark_home, 'python'))
        # better to use build dir it's more generic as it's not tied to a specific version
        #sys.path.append(os.path.join(spark_home, 'python/lib/py4j-0.8.2.1-src.zip'))
        sys.path.append(os.path.join(spark_home, 'python/build'))
    else:
        warn("SPARK_HOME not set - probably won't find PySpark libs")
    from pyspark import SparkContext
    from pyspark import SparkConf
    from pyspark.sql import SQLContext
except ImportError, e:
    print('module import failed: %s' % e)
    sys.exit(4)

def main():
    cov = coverage.Coverage()
    cov.start()

    

    cov.stop()
    cov.save()

    cov.html_report()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
