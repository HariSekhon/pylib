#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2014-09-15 20:49:22 +0100 (Mon, 15 Sep 2014)
#
#  https://github.com/HariSekhon/pylib
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn and optionally send me feedback
#  to help improve or steer this or other code I publish
#
#  https://www.linkedin.com/in/HariSekhon
#

"""
# ============================================================================ #
#                   PyUnit Tests for HariSekhon.RequestHandler
# ============================================================================ #
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals

import logging
import os
import sys
import unittest
# inspect.getfile(inspect.currentframe()) # filename
import requests
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(libdir)
# pylint: disable=wrong-import-position
from harisekhon.utils import log, CriticalError
from harisekhon import RequestHandler


class RequestHandlerTester(unittest.TestCase):

    # must prefix with test_ in order for the tests to be called

    # Not using assertRaises >= 2.7 and maintaining compatibility with Python 2.6 servers

    def test_request_handler(self):
        req = RequestHandler().get('www.google.com')
        self.assertTrue(isinstance, requests.Response)
        RequestHandler(req)

    @staticmethod
    def test_request_handler_failure():
        try:
            RequestHandler().get('127.0.0.1:1')
            raise AssertionError('failed to raise exception for RequestHandler.get(127.0.0.1:1)')
        except CriticalError:
            pass

    @staticmethod
    def test_request_handler_failure2():
        request_handler = RequestHandler()
        request_handler.req = lambda: {'status': 500, 'content': {'message': 'fake message BadStatusLine'}}
        try:
            RequestHandler().get('127.0.0.1:2')
            raise AssertionError('failed to raise exception for RequestHandler.get(127.0.0.1:2)')
        except CriticalError:
            pass

    @staticmethod
    def test_request_handler_failure3():
        request_handler = RequestHandler()
        request_handler.req = lambda: {'status': 500, 'content': {'message': 'fake message unknown protocol'}}
        try:
            RequestHandler().get('https://127.0.0.1:3')
            raise AssertionError('failed to raise exception for RequestHandler.get(https://127.0.0.1:3)')
        except CriticalError:
            pass

    @staticmethod
    def test_request_handler_failure4():
        request_handler = RequestHandler()
        request_handler.req = lambda: 'fake error'
        try:
            RequestHandler().get('https://127.0.0.1:4')
            raise AssertionError('failed to raise exception for RequestHandler.get(https://127.0.0.1:4)')
        except CriticalError:
            pass


def main():
    # increase the verbosity
    # verbosity Python >= 2.7
    #unittest.main(verbosity=2)
    log.setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(RequestHandlerTester)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()
