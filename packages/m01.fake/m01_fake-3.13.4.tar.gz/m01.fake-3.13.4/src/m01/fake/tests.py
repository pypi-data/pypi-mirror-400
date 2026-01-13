##############################################################################
#
# Copyright (c) 2015 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests
$Id:$
"""
from __future__ import absolute_import
from __future__ import print_function

__docformat__ = 'restructuredtext'

import re
import unittest
import doctest

from zope.testing.renormalizing import RENormalizing

import m01.fake
import m01.fake.testing

try:
    import m01.stub
except ImportError:
    has_m01_stub = False
else:
    has_m01_stub = True


def test_suite():
    """This test suite will run the tests with the fake and a real mongodb and
    make sure both output are the same.
    """
    suites = []
    append = suites.append

    # real mongo database tests using m01.stub using level 2 e.g.
    # bin/test -pv1 --all
    allTestNames = [
        'client.txt',
        'collection.txt',
        'collection-update.txt',
        'collection-find.txt',
        'database.txt',
        'index.txt',
        'testing.txt',
    ]
    fakeTestNames = [
        'finder.txt',
        'aggregation.txt',
        'expressions.txt',
        'accumulators.txt',
    ]
    # first, setup non mongodb (m01.stub) based tests
    docTestNames = [
        'README.txt',
    ]
    for name in docTestNames:
        append(
            doctest.DocFileSuite(name,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS |
                    doctest.IGNORE_EXCEPTION_DETAIL,
                checker=m01.fake.reNormalizer),
        )
    # second setup fake mongo database tests using FakeMongoClient
    for name in allTestNames + fakeTestNames:
        append(
            doctest.DocFileSuite(name,
                setUp=m01.fake.testing.setUpFakeMongo,
                tearDown=m01.fake.testing.tearDownFakeMongo,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS |
                    doctest.IGNORE_EXCEPTION_DETAIL,
                checker=m01.fake.reNormalizer),
        )
    # third, setup real mongodb tests using m01.stub (if available)
    if has_m01_stub:
        for name in allTestNames:
            suite = unittest.TestSuite((
                doctest.DocFileSuite(name,
                    setUp=m01.fake.testing.setUpStubMongo,
                    tearDown=m01.fake.testing.tearDownStubMongo,
                    optionflags=doctest.NORMALIZE_WHITESPACE |
                        doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL,
                    checker=m01.fake.reNormalizer),
            ))
            suite.level = 2
            append(suite)

    # return test suite
    return unittest.TestSuite(suites)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
