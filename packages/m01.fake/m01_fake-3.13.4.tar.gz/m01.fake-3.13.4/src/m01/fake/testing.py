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
"""Testing

$Id:$
"""
from __future__ import absolute_import
from builtins import range
from six.moves import range
__docformat__ = 'restructuredtext'

import time
import struct
import calendar
import os.path

import bson
import pymongo

import m01.fake
import m01.fake.client

# mongo db name used for testing
TEST_DB_NAME = 'm01_fake_database'
TEST_COLLECTION_NAME = 'test'
TEST_COLLECTION_FULL_NAME = '%s.%s' % (TEST_DB_NAME, TEST_COLLECTION_NAME)


###############################################################################
#
# test helper methods
#
###############################################################################

_testClient = None

def getTestClient():
    return _testClient


def getTestDatabase():
    client = getTestClient()
    return client[TEST_DB_NAME]


def getTestCollection():
    database = getTestDatabase()
    return database[TEST_COLLECTION_NAME]


def dropTestDatabase():
    client = getTestClient()
    client.drop_database(TEST_DB_NAME)


def dropTestCollection():
    client = getTestClient()
    client[TEST_DB_NAME].drop_collection(TEST_COLLECTION_NAME)


###############################################################################
#
# test setup methods
#
###############################################################################

# fake mongodb setup
def setUpFakeMongo(test=None):
    """Setup fake (singleton) mongo client"""
    global _testClient
    host = 'localhost'
    port = 45017
    storage = m01.fake.client.DatabaseStorage
    _testClient = m01.fake.FakeMongoClient(host, port, storage=storage)


def tearDownFakeMongo(test=None):
    """Tear down fake mongo client"""
    # reset test client
    global _testClient
    _testClient = None


# stub mongodb server
def setUpStubMongo(test=None):
    """Setup pymongo client as test client and setup a real empty mongodb"""
    host = 'localhost'
    port = 45017
    version = '3.6.23'
    sandBoxDir = os.path.join(os.path.dirname(__file__), 'sandbox')
    import m01.stub.testing
    m01.stub.testing.startMongoServer(host, port, sandBoxDir=sandBoxDir,
        version=version)
    # setup pymongo.MongoClient as test client
    global _testClient
    _testClient = pymongo.MongoClient(host, port)


def tearDownStubMongo(test=None):
    """Tear down real mongodb"""
    # stop mongodb server
    sleep = 0.5
    import m01.stub.testing
    m01.stub.testing.stopMongoServer(sleep)
    # reset test client
    global _testClient
    _testClient = None


###############################################################################
#
# testing helper
#
###############################################################################

def getObjectId(secs=0):
    """Knows how to generate similar ObjectId based on integer (counter)

    Note: this method can get used if you need to define similar ObjectId
    in a non persistent environment if need to bootstrap mongo containers.
    """
    time_tuple = time.gmtime(secs)
    ts = calendar.timegm(time_tuple)
    oid = struct.pack(">i", int(ts)) + b"\x00" * 8
    return bson.objectid.ObjectId(oid)


###############################################################################
#
# collection test data
#
###############################################################################

def setUpTestData(one=100, many=100):
    """Apply some test data to the test collection"""
    # first drop previous test data
    dropTestDatabase()
    # sestup new test data
    collection = getTestCollection()
    key = 0
    for n in range(one):
        key += 1
        collection.insert_one({
            'key': key,
            'counter': n,
            'added': True,
            'changed': False,
            'many': False,
            'all': True,
            })
    lot = []
    for n in range(many):
        key += 1
        lot.append({
            'key': key,
            'counter': n,
            'added': True,
            'changed': False,
            'many': True,
            'all': True,
            })
    collection.insert_many(lot)
    return collection
