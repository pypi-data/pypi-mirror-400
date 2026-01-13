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
from six.moves import map
__docformat__ = 'restructuredtext'

import re
import doctest
import pprint as pp

import bson
import bson.son
import pymongo.cursor
#from bson.py3compat import string_type
try:
    string_type = basestring  # Python 2
except NameError:
    string_type = str

from m01.fake.database import FakeDatabase
from m01.fake.collection import FakeCollection
from m01.fake.cursor import FakeCursor
from m01.fake.client import FakeMongoClient
from collections import OrderedDict
from pprint import PrettyPrinter


###############################################################################
#
# test helper methods
#
###############################################################################

# SON to dict converter
def dictify(data):
    """Recursive replace SON items with dict in the given data structure.

    Compared to the SON.to_dict method, this method will also handle tuples
    and keep them intact.

    """
    if isinstance(data, bson.son.SON):
        data = dict(data)
    if isinstance(data, dict):
        d = {}
        for k, v in list(data.items()):
            # replace nested SON items
            d[k] = dictify(v)
    elif isinstance(data, (tuple, list)):
        d = []
        for v in data:
            # replace nested SON items
            d.append(dictify(v))
        if isinstance(data, tuple):
            # keep tuples intact
            d = tuple(d)
    else:
        d = data
    return d


class CustomOrderedDict(OrderedDict):
    """Custom OrderedDict that displays as {...}"""
    def __repr__(self):
        items = []
        for key, value in self.items():
            items.append("{}: {}".format(repr(key), repr(value)))  # Use .format() for compatibility
        return "{" + ", ".join(items) + "}"


def sorted_struture(data, level=0, max_level=3):
    """ The P2 adn P3 have different outputs (pprint) for lists and dictionaries.
    We ordered the lists and use OrderedDict to have the same output.
    """
    if level > max_level:
        return data

    if isinstance(data, list):
        # try to sort lists
        try:
            sorted_data = sorted(data)
        except TypeError:
            # Can't compare objects, order as str
            sorted_data = sorted(data, key=lambda x: str(x))
        # try to sort the elements of the list
        return [sorted_struture(item, level + 1, max_level) for item in sorted_data]
    elif isinstance(data, dict):
        # sort with OrderedDict
        sorted_dict = CustomOrderedDict()
        for key in sorted(data.keys()):
            sorted_dict[key] = sorted_struture(data[key], level + 1, max_level)
        return sorted_dict
    else:
        return data

def pprint(data):
    """Can pprint a bson.son.SON instance like a dict"""

    # convert the structure to lists and dicts
    newStruct = dictify(data)
    # P2P3 output compatibility using OrderedDict and sorted lists
    newStruct = sorted_struture(newStruct)
    pp.pprint(newStruct)


class RENormalizer(doctest.OutputChecker):
    """Normalizer which can convert text based on regex patterns"""

    def __init__(self, patterns):
        self.patterns = patterns
        self.transformers = list(map(self._cook, patterns))

    def __add__(self, other):
        if not isinstance(other, RENormalizing):
            return NotImplemented
        return RENormalizing(self.transformers + other.transformers)

    def _cook(self, pattern):
        if callable(pattern):
            return pattern
        regexp, replacement = pattern
        return lambda text: regexp.sub(replacement, text)

    def addPattern(self, pattern):
        patterns = list(self.patterns)
        patterns.append(pattern)
        self.transformers = list(map(self._cook, patterns))
        self.patterns = patterns

    def __call__(self, data):
        """Recursive normalize a SON instance, dict or text"""
        if not isinstance(data, string_type):
            data = pp.pformat(dictify(data))
        for normalizer in self.transformers:
            data = normalizer(dictify(data))
        return data

    def check_output(self, want, got, optionflags):
        if got == want:
            return True

        for transformer in self.transformers:
            want = transformer(want)
            got = transformer(got)

        return doctest.OutputChecker.check_output(self, want, got, optionflags)

    def output_difference(self, example, got, optionflags):

        want = example.want

        # If want is empty, use original outputter. This is useful
        # when setting up tests for the first time.  In that case, we
        # generally use the differencer to display output, which we evaluate
        # by hand.
        if not want.strip():
            return doctest.OutputChecker.output_difference(
                self, example, got, optionflags)

        # Dang, this isn't as easy to override as we might wish
        original = want

        for transformer in self.transformers:
            want = transformer(want)
            got = transformer(got)

        # temporarily hack example with normalized want:
        example.want = want
        result = doctest.OutputChecker.output_difference(
            self, example, got, optionflags)
        example.want = original

        return result

    def pprint(self, data):
        """Pretty print data"""
        if isinstance(data, (pymongo.cursor.Cursor, FakeCursor)):
            for item in data:
                print((self(item)))
        else:
            print((self(data)))


# see testing.txt for a sample usage
reNormalizer = RENormalizer([
    # Remove "u" prefix for Unicode strings (Python 2 compatibility)
    (re.compile(r"u('.*?')"), r"\1"),
    (re.compile(r'u(r".*?")'), r"\1"),

    # Dates
    (re.compile(r"(\d\d\d\d)-(\d\d)-(\d\d)[tT](\d\d):(\d\d):(\d\d)"),
     r"NNNN-NN-NNTNN:NN:NN"),
    (re.compile(r"(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)"),
     r"NNNN-NN-NN NN:NN:NN"),

    # Replace pymongo FixedOffset with UTC
    (re.compile(r"tzinfo=FixedOffset\(datetime.timedelta\(0\), 'UTC'\)"),
     "tzinfo=UTC"),
    (re.compile(r"tzinfo=<bson.tz_util.FixedOffset[a-zA-Z0-9 ]+>\)"),
     "tzinfo=UTC)"),

    # ObjectId and Timestamp
    (re.compile(r"ObjectId\(\'[a-zA-Z0-9]+\'\)"), r"ObjectId('...')"),
    (re.compile(r"Timestamp\([a-zA-Z0-9, ]+\)"), r"Timestamp('...')"),
    (re.compile(r"datetime\([a-z0-9, ]+\)"), r"datetime(...)"),

    # Replace memory addresses
    (re.compile(r"object at 0x[a-zA-Z0-9]+"), r"object at ..."),

    # Remove "Fake" from class names
    (re.compile(r'FakeMongoClient'), r'MongoClient'),
    (re.compile(r'FakeDatabase'), r'Database'),
    (re.compile(r'FakeCollection'), r'Collection'),

    # Remove MongoDB client attributes
    (re.compile(r', document_class=dict'), r''),
    (re.compile(r', tz_aware=True'), r''),
    (re.compile(r', tz_aware=False'), r''),
    (re.compile(r', connect=True'), r''),
    (re.compile(r', connect=False'), r''),

    # Class representation
    (re.compile(r"MongoClient\(host=\['127.0.0.1:27017'\]\)"),
     "MongoClient(host=['localhost:45017'])"),
    (re.compile(r"MongoClient\('localhost', 27017\)"),
     "MongoClient(host=['localhost:27017'])"),
    (re.compile(r"45017"), r"27017"),
    (re.compile(r"localhost"), r"127.0.0.1"),
])


def getObjectId(secs=0):
    """Knows how to generate similar ObjectId based on integer (counter)

    Note: this method can get used if you need to define similar ObjectId
    in a non persistent environment if need to bootstrap mongo containers.
    """
    return bson.ObjectId(("%08x" % secs) + "0" * 16)


# single shared MongoClient instance
fakeMongoClient = FakeMongoClient()
