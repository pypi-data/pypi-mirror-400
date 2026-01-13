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
"""Cursor

$Id:$
"""
from __future__ import absolute_import
from builtins import next
from builtins import object
__docformat__ = 'restructuredtext'

import copy
import collections
import itertools

import bson.son
import bson.code
import pymongo
import pymongo.common
import pymongo.cursor
from pymongo.read_preferences import ReadPreference

import m01.fake.finder
from m01.fake.helpers import asdict

try:
    # Python 2
    integer_types = (int, long)
    string_type = basestring
except NameError:
    # Python 3
    integer_types = (int,)
    string_type = str


# ###############################################################################
# #
# # helper

# def sortByAttribute(name, order):
#     def sort(d1, d2):
#         v1 = d1.get(name, None)
#         v2 = d2.get(name, None)
#         try:
#             res = cmp(v1, v2)
#         except TypeError:
#             res = -1
#         if order:
#             return res
#         else:
#             return -res
#     return sort

# helpers
def _index_document(sort):
    if not isinstance(sort, list):
        raise TypeError("sort must be a list of (key, direction) pairs")
    return dict(sort)


def _index_list(key_or_list, direction=pymongo.ASCENDING):
    """Macht aus einem Index-Argument eine Liste von (key, direction)-Tupeln"""
    if isinstance(key_or_list, str):
        return [(key_or_list, direction)]
    elif isinstance(key_or_list, list):
        if all(isinstance(el, str) for el in key_or_list):
            return [(k, direction) for k in key_or_list]
        elif all(isinstance(el, tuple) and len(el) == 2 for el in key_or_list):
            return key_or_list
    raise TypeError(
        "index must be a string, list of strings, or list of (key, direction) "
        "tuples")


###############################################################################
#
# fake cursor

class FakeCursor(object):
    """Fake mongoDB cursor."""

    def __init__(self, collection, filter=None, projection=None, skip=0,
        limit=0, no_cursor_timeout=False,
        cursor_type=pymongo.cursor.CursorType.NON_TAILABLE,
        sort=None, allow_partial_results=False, oplog_replay=False,
        modifiers=None, batch_size=0, manipulate=True):
        self.__id = None

        spec = filter
        if spec is None:
            spec = {}

        pymongo.common.validate_is_mapping("filter", spec)
        if not isinstance(skip, int):
            raise TypeError("skip must be an instance of int")
        if not isinstance(limit, int):
            raise TypeError("limit must be an instance of int")
        pymongo.common.validate_boolean("no_cursor_timeout", no_cursor_timeout)
        if cursor_type not in (
            pymongo.cursor.CursorType.NON_TAILABLE,
            pymongo.cursor.CursorType.TAILABLE,
            pymongo.cursor.CursorType.TAILABLE_AWAIT,
            pymongo.cursor.CursorType.EXHAUST):
            raise ValueError("not a valid value for cursor_type")
        pymongo.common.validate_boolean("allow_partial_results",
            allow_partial_results)
        pymongo.common.validate_boolean("oplog_replay",
            oplog_replay)
        if modifiers is not None:
            pymongo.common.validate_is_mapping("modifiers", modifiers)
        if not isinstance(batch_size, integer_types):
            raise TypeError("batch_size must be an integer")
        if batch_size < 0:
            raise ValueError("batch_size must be >= 0")

        if projection is not None:
            if not projection:
                projection = {"_id": 1}
            projection = asdict(projection)

        # filter and setup docs based on given spec
        self.__collection = collection
        self.__spec = spec
        self.__projection = projection
        self.__skip = skip
        self.__limit = limit
        self.__batch_size = batch_size
        self.__modifiers = modifiers and modifiers.copy() or {}
        self.__ordering = sort and _index_document(sort) or None
        self.__max_scan = None
        self.__explain = False
        self.__hint = None
        self.__comment = None
        self.__max_time_ms = None
        self.__max = None
        self.__min = None
        self.__manipulate = manipulate

        # Exhaust cursor support
        self.__exhaust = False
        self.__exhaust_mgr = None
        if cursor_type == pymongo.cursor.CursorType.EXHAUST:
            if self.__collection.database.client.is_mongos:
                raise pymongo.errors.InvalidOperation(
                    'Exhaust cursors are not supported by mongos')
            if limit:
                raise pymongo.errors.InvalidOperation(
                    "Can't use limit and exhaust together.")
            self.__exhaust = True

        # This is ugly. People want to be able to do cursor[5:5] and
        # get an empty result set (old behavior was an
        # exception). It's hard to do that right, though, because the
        # server uses limit(0) to mean 'no limit'. So we set __empty
        # in that case and check for it when iterating. We also unset
        # it anytime we change __limit.
        self.__empty = False

        self.__data = collections.deque()
        self.__address = None
        self.__retrieved = 0
        self.__killed = False

        self.__codec_options = collection.codec_options
        self.__read_preference = collection.read_preference

        self.__query_flags = cursor_type
        if self.__read_preference != ReadPreference.PRIMARY:
            self.__query_flags |= pymongo.cursor._QUERY_OPTIONS["slave_okay"]
        if no_cursor_timeout:
            self.__query_flags |= pymongo.cursor._QUERY_OPTIONS["no_timeout"]
        if allow_partial_results:
            self.__query_flags |= pymongo.cursor._QUERY_OPTIONS["partial"]
        if oplog_replay:
            self.__query_flags |= pymongo.cursor._QUERY_OPTIONS["oplog_replay"]

    def _query(self, collection, filter, projection=None, skip=0, limit=0,
        sort=None):
        return m01.fake.finder.getFilteredDocuments(collection, filter=filter,
            projection=projection, skip=skip, limit=limit, multi=True,
            sort=sort, deepcopy=True)

    @property
    def collection(self):
        return self.__collection

    @property
    def retrieved(self):
        """The number of documents retrieved so far"""
        return self.__retrieved

    def __del__(self):
        if self.__id and not self.__killed:
            self.__die()

    def rewind(self):
        """Rewind this cursor to its unevaluated state"""
        self.__data = collections.deque()
        self.__id = None
        self.__address = None
        self.__retrieved = 0
        self.__killed = False

    def clone(self):
        """Get a clone of this cursor"""
        return self._clone(True)

    def _clone(self, deepcopy=True):
        """Internal clone helper."""
        clone = self._clone_base()
        values_to_clone = ("spec", "projection", "skip", "limit",
                           "max_time_ms", "comment", "max", "min",
                           "ordering", "explain", "hint", "batch_size",
                           "max_scan", "manipulate", "query_flags",
                           "modifiers")
        data = dict((k, v) for k, v in iteritems(self.__dict__)
                    if k.startswith('_Cursor__') and k[9:] in values_to_clone)
        if deepcopy:
            data = self._deepcopy(data)
        clone.__dict__.update(data)
        return clone

    def _clone_base(self):
        """Creates an empty Cursor object for information to be copied into"""
        return FakeCursor(self.__collection)

    def __die(self):
        """Closes this cursor"""
        if self.__id and not self.__killed:
            if self.__exhaust and self.__exhaust_mgr:
                # If this is an exhaust cursor and we haven't completely
                # exhausted the result set we *must* close the socket
                # to stop the server from sending more data.
                self.__exhaust_mgr.sock.close()
            else:
                self.__collection.database.client.close_cursor(self.__id,
                                                               self.__address)
        if self.__exhaust and self.__exhaust_mgr:
            self.__exhaust_mgr.close()
        self.__killed = True

    def close(self):
        """Explicitly close / kill this cursor"""
        self.__die()

    def close(self):
        """Explicitly close / kill this cursor"""
        self.__die()

    def __check_okay_to_chain(self):
        """Check if it is okay to chain more options onto this cursor"""
        if self.__retrieved or self.__id is not None:
            raise pymongo.errors.InvalidOperation(
                "cannot set options after executing query")

    def add_option(self, mask):
        """Set arbitrary query flags using a bitmask"""
        if not isinstance(mask, int):
            raise TypeError("mask must be an int")
        self.__check_okay_to_chain()

        if mask & pymongo.cursor._QUERY_OPTIONS["exhaust"]:
            if self.__limit:
                raise pymongo.errors.InvalidOperation(
                    "Can't use limit and exhaust together.")
            if self.__collection.database.client.is_mongos:
                raise pymongo.errors.InvalidOperation(
                    'Exhaust cursors are not supported by mongos')
            self.__exhaust = True

        self.__query_flags |= mask
        return self

    def remove_option(self, mask):
        """Unset arbitrary query flags using a bitmask"""
        if not isinstance(mask, int):
            raise TypeError("mask must be an int")
        self.__check_okay_to_chain()

        if mask & pymongo.cursor._QUERY_OPTIONS["exhaust"]:
            self.__exhaust = False

        self.__query_flags &= ~mask
        return self

    def limit(self, limit):
        if not isinstance(limit, integer_types):
            raise TypeError("limit must be an integer")
        if self.__exhaust:
            raise pymongo.errors.InvalidOperation(
                "Can't use limit and exhaust together.")
        self.__check_okay_to_chain()

        self.__empty = False
        self.__limit = limit
        return self

    def batch_size(self, batch_size):
        """Limits the number of documents returned in one batch"""
        if not isinstance(batch_size, integer_types):
            raise TypeError("batch_size must be an integer")
        if batch_size < 0:
            raise ValueError("batch_size must be >= 0")
        self.__check_okay_to_chain()

        self.__batch_size = batch_size == 1 and 2 or batch_size
        return self

    def skip(self, skip):
        self._skip = skip
        # raises TypeError: sequence index must be integer, not 'slice'
        # self.__data = collections.deque(self.__data[skip:])
        dd = list(itertools.islice(self.__data, skip, None))
        self.__data = collections.deque(dd)
        return self

    def max_time_ms(self, max_time_ms):
        """Specifies a time limit for a query operation"""
        if (not isinstance(max_time_ms, integer_types)
                and max_time_ms is not None):
            raise TypeError("max_time_ms must be an integer or None")
        self.__check_okay_to_chain()
        self.__max_time_ms = max_time_ms
        return self

    def __getitem__(self, index):
        """Get a single document or a slice of documents from this cursor"""
        self.__check_okay_to_chain()
        self.__empty = False
        if isinstance(index, slice):
            if index.step is not None:
                raise IndexError("Cursor instances do not support slice steps")

            skip = 0
            if index.start is not None:
                if index.start < 0:
                    raise IndexError("Cursor instances do not support"
                                     "negative indices")
                skip = index.start

            if index.stop is not None:
                limit = index.stop - skip
                if limit < 0:
                    raise IndexError("stop index must be greater than start"
                                     "index for slice %r" % index)
                if limit == 0:
                    self.__empty = True
            else:
                limit = 0

            self.__skip = skip
            self.__limit = limit
            return self

        if isinstance(index, integer_types):
            if index < 0:
                raise IndexError("Cursor instances do not support negative"
                                 "indices")
            clone = self.clone()
            clone.skip(index + self.__skip)
            clone.limit(-1)  # use a hard limit
            for doc in clone:
                return doc
            raise IndexError("no such item for Cursor instance")
        raise TypeError("index %r cannot be applied to Cursor "
                        "instances" % index)

    def max_scan(self, max_scan):
        """Limit the number of documents to scan when performing the query"""
        self.__check_okay_to_chain()
        self.__max_scan = max_scan
        return self

    def max(self, spec):
        """Adds `max` operator that specifies upper bound for specific index"""
        if not isinstance(spec, (list, tuple)):
            raise TypeError("spec must be an instance of list or tuple")

        self.__check_okay_to_chain()
        self.__max = bson.son.SON(spec)
        return self

    def min(self, spec):
        """Adds `min` operator that specifies lower bound for specific index"""
        if not isinstance(spec, (list, tuple)):
            raise TypeError("spec must be an instance of list or tuple")

        self.__check_okay_to_chain()
        self.__min = bson.son.SON(spec)
        return self

    # def sort(self, name, order):
    #     sorter = sortByAttribute(name, order)
    #     docs = list(self.__data)
    #     docs.sort(sorter)
    #     self.__data = collections.deque(docs)
    #     return self

    def sort(self, key_or_list, direction=None):
        self.__check_okay_to_chain()
        keys = _index_list(key_or_list, direction)
        self.__ordering = _index_document(keys)
        return self

    def count(self, with_limit_and_skip=False):
        pymongo.common.validate_boolean("with_limit_and_skip",
            with_limit_and_skip)
        if with_limit_and_skip:
            skip = self.__skip
            limit = self.__limit
        else:
            skip = 0
            limit = 0
        return len(self._query(self.__collection, self.__spec,
            projection=self.__projection, skip=skip, limit=limit))

    def distinct(self, key):
        """Get a list of distinct values for `key` among all documents
        in the result set of this query
        """
        options = {}
        if self.__spec:
            options["query"] = self.__spec
        if self.__max_time_ms is not None:
            options['maxTimeMS'] = self.__max_time_ms
        if self.__comment:
            options['$comment'] = self.__comment
        return self.__collection.distinct(key, **options)

    def explain(self):
        """Returns an explain plan record for this cursor"""
        c = self.clone()
        c.__explain = True

        # always use a hard limit for explains
        if c.__limit:
            c.__limit = -abs(c.__limit)
        return next(c)

    def hint(self, index):
        """Adds a 'hint', telling Mongo the proper index to use for the query"""
        self.__check_okay_to_chain()
        if index is None:
            self.__hint = None
            return self
        if isinstance(index, string_type):
            self.__hint = index
        else:
            self.__hint = _index_document(index)
        return self

    def comment(self, comment):
        """Adds a 'comment' to the cursor"""
        self.__check_okay_to_chain()
        self.__comment = comment
        return self

    def where(self, code):
        """Adds a $where clause to this query"""
        self.__check_okay_to_chain()
        if not isinstance(code, bson.code.Code):
            code = bson.code.Code(code)

        self.__spec["$where"] = code
        return self

    def _refresh(self):
        """Refreshes the cursor with more data from Mongo.

        Returns the length of self.__data after refresh. Will exit early if
        self.__data is already non-empty. Raises OperationFailure when the
        cursor cannot be refreshed due to an error on the query.
        """
        if len(self.__data) or self.__killed:
            return len(self.__data)
        if self.__id is None:
            # query documents live including projectionm skip, limit and sort
            data = self._query(self.__collection,
                self.__spec, projection=self.__projection, skip=self.__skip,
                limit=self.__limit, sort=self.__ordering)
            self.__data = collections.deque(data)
            # set cursor to zero
            self.__id = 0
        else:
            # Cursor id is zero nothing else to return
            self.__killed = True

        return len(self.__data)

    @property
    def alive(self):
        """Does this cursor have the potential to return more data?"""
        return bool(len(self.__data) or (not self.__killed))

    @property
    def cursor_id(self):
        """Returns the id of the cursor"""
        return self.__id

    @property
    def address(self):
        """The (host, port) of the server used, or None"""
        return self.__address

    def __iter__(self):
        return self

    def __next__(self):
        if self.__empty:
            raise StopIteration
        db = self.__collection.database
        if len(self.__data) or self._refresh():
            if self.__manipulate:
                return db._fix_outgoing(self.__data.popleft(),
                    self.__collection)
            else:
                return self.__data.popleft()
        else:
            raise StopIteration

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__die()

    def __copy__(self):
        """Support function for `copy.copy()`"""
        return self._clone(deepcopy=False)

    def __deepcopy__(self, memo):
        """Support function for `copy.deepcopy()`"""
        return self._clone(deepcopy=True)

    def _deepcopy(self, x, memo=None):
        """Deepcopy helper for the data dictionary or list"""
        if not hasattr(x, 'items'):
            y, is_list, iterator = [], True, enumerate(x)
        else:
            y, is_list, iterator = {}, False, iteritems(x)

        if memo is None:
            memo = {}
        val_id = id(x)
        if val_id in memo:
            return memo.get(val_id)
        memo[val_id] = y

        for key, value in iterator:
            if isinstance(value, (dict, list)) and not isinstance(value,
                bson.son.SON):
                value = self._deepcopy(value, memo)
            elif not isinstance(value, RE_TYPE):
                value = copy.deepcopy(value, memo)

            if is_list:
                y.append(value)
            else:
                if not isinstance(key, RE_TYPE):
                    key = copy.deepcopy(key, memo)
                y[key] = value
        return y
