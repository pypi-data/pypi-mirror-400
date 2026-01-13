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
from builtins import next
__docformat__ = 'restructuredtext'

import copy
import re
import types
import collections
import itertools
import warnings

#from bson.py3compat import string_type
try:
    string_type = basestring  # Python 2
except NameError:
    string_type = str

try:
    from collections.abc import Mapping
    from collections.abc import MutableMapping
except ImportError:
    from collections import Mapping
    from collections import MutableMapping

from six import iteritems
from six import iterkeys
from six import itervalues
from six import string_types
from six import text_type

import bson
import bson.son
import pymongo.common
import pymongo.collection
import pymongo.results
import pymongo.write_concern


import m01.fake.finder
import m01.fake.updater
from m01.fake.cursor import FakeCursor
from m01.fake.helpers import toUnicode
from m01.fake.helpers import asdict


###############################################################################
#
# fake collection

class FakeCollection(pymongo.common.BaseObject):
    """Fake mongoDB collection"""

    def __init__(self, database, name, create=False, codec_options=None,
        read_preference=None, write_concern=None, read_concern=None, **kwargs):
        super(FakeCollection, self).__init__(
            codec_options or database.codec_options,
            read_preference or database.read_preference,
            write_concern or database.write_concern,
            read_concern or database.read_concern)

        if not isinstance(name, string_type):
            raise TypeError("name must be an instance "
                            "of %s" % (string_type.__name__,))

        if not name or ".." in name:
            raise InvalidName("collection names cannot be empty")
        if "$" in name and not (name.startswith("oplog.$main") or
                                name.startswith("$cmd")):
            raise InvalidName("collection names must not "
                              "contain '$': %r" % name)
        if name[0] == "." or name[-1] == ".":
            raise InvalidName("collection names must not start "
                              "or end with '.': %r" % name)
        if "\x00" in name:
            raise InvalidName("collection names must not contain the "
                              "null character")

        self.__database = database
        self.__name = toUnicode(name)
        self.__full_name = '%s.%s' % (self.__database.name, self.__name)

    def getCollectionStorage(self):
        return self.__database.getCollectionStorage()

    def getDocumentStorage(self):
        storage = self.getCollectionStorage()
        return storage.getDocumentStorage(self)

    def __getattr__(self, name):
        """Get a sub-collection of this collection by name (e.g. gridfs)"""
        if name.startswith('_'):
            full_name = u"%s.%s" % (self.name, name)
            raise AttributeError(
                "Collection has no attribute %r. To access the %s"
                " collection, use database['%s']." % (
                    name, full_name, full_name))
        return self.__getitem__(name)

    def __getitem__(self, name):
        """Get a sub-collection of this collection by name (e.g. gridfs)"""
        return self.__database[self.name + '.' + name]

    def __eq__(self, other):
        if isinstance(other, FakeCollection):
            return (self.database == other.database and
                    self.name == other.name)
        return NotImplemented

    def __ne__(self, other):
        return not self == other

    @property
    def full_name(self):
        """The full name of this :class:`Collection`.

        The full name is of the form `database_name.collection_name`.
        """
        return self.__full_name

    @property
    def name(self):
        """The name of this :class:`Collection`."""
        return self.__name

    @property
    def database(self):
        """The :class:`~pymongo.database.Database` that this
        :class:`Collection` is a part of.
        """
        return self.__database

    def with_options(self, codec_options=None, read_preference=None,
        write_concern=None):
        """Get a clone of this collection changing the specified settings"""
        return FakeCollection(self.database, self.name, False,
            codec_options or self.codec_options,
            read_preference or self.read_preference,
            write_concern or self.write_concern)

    # NotImplementedError
    def initialize_unordered_bulk_op(self):
        """Initialize an unordered batch of write operations"""
        raise NotImplementedError()

    # NotImplementedError
    def initialize_ordered_bulk_op(self):
        """Initialize an ordered batch of write operations"""
        raise NotImplementedError()

    # NotImplementedError
    def bulk_write(self, requests, ordered=True):
        """Send a batch of write operations to the server"""
        raise NotImplementedError()

    def _insert(self, docs, ordered=True, check_keys=True, manipulate=False,
        write_concern=None):
        """Internal insert helper"""
        return_one = False
        if isinstance(docs, MutableMapping):
            return_one = True
            docs = [docs]

        ids = []
        if manipulate:
            def gen():
                """Generator that applies SON manipulators to each document
                and adds _id if necessary.
                """
                _db = self.__database
                for doc in docs:
                    # Apply user-configured SON manipulators. This order of
                    # operations is required for backwards compatibility,
                    # see PYTHON-709.
                    doc = _db._apply_incoming_manipulators(doc, self)
                    if '_id' not in doc:
                        doc['_id'] = bson.ObjectId()
                    doc = _db._apply_incoming_copying_manipulators(doc, self)
                    ids.append(doc['_id'])
                    yield doc
        else:
            def gen():
                """Generator that only tracks existing _ids."""
                for doc in docs:
                    ids.append(doc.get('_id'))
                    yield doc

        storage = self.getDocumentStorage()
        for doc in gen():
            oid  = doc['_id']
            storage[oid] = doc

        if return_one:
            return ids[0]
        else:
            return ids

    def insert_one(self, document):
        """Insert a single document"""
        pymongo.common.validate_is_document_type("document", document)
        if "_id" not in document:
            document["_id"] = bson.ObjectId()
        oid = self._insert(document)
        return pymongo.results.InsertOneResult(oid,
            self.write_concern.acknowledged)

    def insert_many(self, documents, ordered=True):
        """Insert a list of documents"""
        if not isinstance(documents, list) or not documents:
            raise TypeError("documents must be a non-empty list")
        for document in documents:
            pymongo.common.validate_is_document_type("document", document)
            if "_id" not in document:
                document["_id"] = bson.ObjectId()
        ids = self._insert(documents)
        return pymongo.results.InsertManyResult(ids,
            self.write_concern.acknowledged)

    # deprecated in pymongo >= 3.0.0
    def save(self, to_save, manipulate=True, check_keys=True, **kwargs):
        warnings.warn("save is deprecated. Use insert_one or replace_one "
                      "instead", DeprecationWarning, stacklevel=2)
        if not isinstance(to_save, dict):
            raise TypeError("cannot save object of type %s" % type(to_save))

        if "_id" not in to_save:
            write_concern = None
            return self._insert(to_save, True, check_keys=check_keys,
                manipulate=manipulate)
        else:
            self.update_one({"_id": to_save["_id"]}, to_save, upsert=True,
                manipulate=manipulate, safe=safe,
                check_keys=check_keys, **kwargs)
            return to_save.get("_id", None)

    def _update(self, filter, document, upsert=False, check_keys=True,
        multi=False, manipulate=False, write_concern=None, op_id=None,
        ordered=True):
        """Internal update / replace helper."""
        pymongo.common.validate_boolean("upsert", upsert)
        if not isinstance(document, dict):
            raise TypeError("document must be an instance of dict")
        if manipulate:
            document = self.__database._fix_incoming(document, self)
        return m01.fake.updater.doUpdateDocuments(self, filter, document,
            upsert=upsert, multi=multi)

    def replace_one(self, filter, replacement, upsert=False):
        """Replace a single document matching the filter"""
        pymongo.common.validate_is_mapping("filter", filter)
        pymongo.common.validate_ok_for_replace(replacement)
        result = self._update(filter, replacement, upsert)
        return pymongo.results.UpdateResult(result,
            self.write_concern.acknowledged)

    def update_one(self, filter, update, upsert=False):
        """Update a single document matching the filter"""
        pymongo.common.validate_is_mapping("filter", filter)
        pymongo.common.validate_ok_for_update(update)
        result = self._update(filter, update, upsert, check_keys=False)
        return pymongo.results.UpdateResult(result,
            self.write_concern.acknowledged)

    def update_many(self, filter, update, upsert=False):
        """Update one or more documents that match the filter"""
        pymongo.common.validate_is_mapping("filter", filter)
        pymongo.common.validate_ok_for_update(update)
        result = self._update(filter, update, upsert, check_keys=False,
            multi=True)
        return pymongo.results.UpdateResult(result,
            self.write_concern.acknowledged)

    def drop(self):
        # remove FakeCollection
        del self.database._cols[self.name]
        # remove CollectionStorage
        storage = self.getCollectionStorage()
        del storage[self.name]

    def remove(self, spec_or_id=None, multi=True, **kwargs):
        """Remove a document(s) from this collection.

        **DEPRECATED** - Use :meth:`delete_one` or :meth:`delete_many` instead.

        .. versionchanged:: 3.0
           Removed the `safe` parameter. Pass ``w=0`` for unacknowledged write
           operations.
        """
        warnings.warn("remove is deprecated. Use delete_one or delete_many "
                      "instead.", DeprecationWarning, stacklevel=2)
        if spec_or_id is None:
            spec_or_id = {}
        if not isinstance(spec_or_id, Mapping):
            spec_or_id = {"_id": spec_or_id}
        response = {"n": 0, "ok": 1}
        storage = self.getDocumentStorage()
        for doc in self.find(spec_or_id):
            del storage[toUnicode(doc['_id'])]
            response['n'] += 1
        return response

    def _delete(self, filter, multi, write_concern=None):
        """Internal delete helper."""
        pymongo.common.validate_is_mapping("filter", filter)
        concern = (write_concern or self.write_concern).document
        safe = concern.get("w") != 0
        n = 0
        storage = self.getDocumentStorage()
        for doc in self.find(filter):
            if not multi and n >= 1:
                break
            del storage[toUnicode(doc['_id'])]
            n += 1
        return {'ok': 1.0, 'n': n}

    def delete_one(self, filter):
        """Delete a single document matching the filter"""
        return pymongo.results.DeleteResult(self._delete(filter, False),
            self.write_concern.acknowledged)

    def delete_many(self, filter):
        """Delete one or more documents matching the filter"""
        return pymongo.results.DeleteResult(self._delete(filter, True),
            self.write_concern.acknowledged)

    def find_one(self, filter=None, *args, **kwargs):
        """Get a single document from the database"""
        if (filter is not None and not
                isinstance(filter, Mapping)):
            filter = {"_id": filter}
        max_time_ms = kwargs.pop("max_time_ms", None)
        cursor = self.find(filter, *args, **kwargs).max_time_ms(max_time_ms)
        for result in cursor.limit(-1):
            return result
        return None

    def find(self, *args, **kwargs):
        return FakeCursor(self, *args, **kwargs)

    # NotImplementedError
    def parallel_scan(self, num_cursors):
        """Scan this entire collection in parallel"""
        raise NotImplementedError()

    def count_documents(self, filter, session=None, **kwargs):
        """Get the number of documents in this collection"""
        if filter is not None:
            if "query" in kwargs:
                raise pymongo.errors.ConfigurationError(
                    "can't pass both filter and query")
        elif "query" in kwargs:
            filter = kwargs["query"]
        else:
            filter = {}

        limit = kwargs.get('limit')
        skip = kwargs.get('skip')
        docs = m01.fake.finder.getFilteredDocuments(self, filter, multi=True)

        total = len(docs)
        if skip is not None:
            total = total - skip
        if limit is not None and total > limit:
            total = limit
        return total

    # we do not use indexes
    def create_indexes(self, indexes):
        """Create one or more indexes on this collection"""
        storage = self.getDocumentStorage()
        return storage.indexes.createIndexes(indexes)

    def create_index(self, keys, **kwargs):
        """Creates an index on this collection"""
        storage = self.getDocumentStorage()
        return storage.indexes.createIndex(keys, **kwargs)

    # def ensure_index(self, key_or_list, cache_for=300, **kwargs):
    #     warnings.warn("ensure_index is deprecated. Use create_index instead.",
    #                   DeprecationWarning, stacklevel=2)
    #     storage = self.getDocumentStorage()
    #     return storage.indexes.ensureIndex(key_or_list, cache_for=cache_for,
    #         **kwargs)

    def drop_indexes(self, session=None, **kwargs):
        """Drops all indexes on this collection"""
        storage = self.getDocumentStorage()
        storage.indexes.dropIndexes()

    def drop_index(self, index_or_name, session=None, **kwargs):
        """Drops the specified index on this collection"""
        storage = self.getDocumentStorage()
        storage.indexes.dropIndex(index_or_name)

    def reindex(self, session=None, **kwargs):
        """Rebuilds all indexes on this collection"""
        storage = self.getDocumentStorage()
        return storage.indexes.reIndex()

    def list_indexes(self, session=None):
        """Get a cursor over the index documents for this collection"""
        storage = self.getDocumentStorage()
        return storage.indexes.listIndexes()

    def index_information(self, session=None):
        """Get information on this collection's indexes"""
        storage = self.getDocumentStorage()
        return storage.indexes.getIndexInformation()

    # we do not provide collection options
    def options(self, session=None):
        """Get the options set on this collection"""
        return {}

    def aggregate(self, pipeline, session=None, **kwargs):
        """Perform an aggregation using the aggregation framework on this
        collection.
        
        Supports most common pipeline stages including:
        - $match, $project, $group, $sort, $limit, $skip
        - $unwind, $count, $addFields, $set, $unset
        - $lookup, $facet, $bucket, $out, $merge
        - $replaceRoot, $replaceWith, $sortByCount, $sample
        
        See AGGREGATION.txt for full documentation.
        """
        from m01.fake.aggregation import execute_pipeline
        return execute_pipeline(self, pipeline, **kwargs)

    def aggregate_raw_batches(self, pipeline, session=None, **kwargs):
        """Perform an aggregation and retrieve batches of raw BSON.
        """
        raise NotImplementedError()

    def watch(self,
        pipeline=None,
        full_document=None,
        resume_after=None,
        max_await_time_ms=None,
        batch_size=None,
        collation=None,
        start_at_operation_time=None,
        session=None,
        start_after=None,
        ):
        """Watch changes on this collection."""
        raise NotImplementedError()

    # NotImplementedError
    def group(self, key, condition, initial, reduce, finalize=None, **kwargs):
        """Perform a query similar to an SQL *group by* operation"""
        raise NotImplementedError()

    def rename(self, new_name, session=None, **kwargs):
        """Rename this collection"""
        if not isinstance(new_name, string_type):
            raise TypeError("new_name must be an "
                            "instance of %s" % (string_type.__name__,))

        if not new_name or ".." in new_name:
            raise pymongo.errors.InvalidName(
                "collection names cannot be empty")
        if new_name[0] == "." or new_name[-1] == ".":
            raise pymongo.errors.InvalidName(
                "collecion names must not start or end with '.'")
        if "$" in new_name and not new_name.startswith("oplog.$main"):
            raise pymongo.errors.InvalidName(
                "collection names must not contain '$'")

        self.database.doRenameFakeCollection(self.__name, new_name)

        # del storage[self.__name]
        self.__name = toUnicode(new_name)
        self.__full_name = '%s.%s' % (self.__database.name, new_name)
        return {'ok': 1.0}

    def distinct(self, key, filter=None, session=None, **kwargs):
        """Get a list of distinct values for `key` among all documents
        in this collection
        """
        if not isinstance(key, string_type):
            raise TypeError("key must be an "
                            "instance of %s" % (string_type.__name__,))
        query = kwargs.get("query")
        if filter is not None and query is not None:
            raise pymongo.errors.ConfigurationError(
                "can't pass both filter and query")
        filer = filter and filter or query
        values = set()
        for doc in self.find(filter):
            values.add(doc.get(key))
        return values

    # NotImplementedError
    def map_reduce(self, map, reduce, out, full_response=False, session=None, **kwargs):
        """Perform a map/reduce operation on this collection"""
        raise NotImplementedError()

    # NotImplementedError
    def inline_map_reduce(self, map, reduce, full_response=False, session=None, **kwargs):
        """Perform an inline map/reduce operation on this collection"""
        raise NotImplementedError()

    def find_one_and_delete(self, filter, projection=None, sort=None,
        hint=None, session=None, **kwargs):
        """Finds a single document and deletes it, returning the document"""
        doc = self.find_one(filter, projection=projection, sort=sort)
        self.delete_one(filter)
        return doc

    def find_one_and_replace(
        self,
        filter,
        replacement,
        projection=None,
        sort=None,
        upsert=False,
        return_document=pymongo.collection.ReturnDocument.BEFORE,
        hint=None,
        session=None,
        **kwargs):
        pymongo.common.validate_ok_for_replace(replacement)
        doc = self.find_one(filter, projection=projection, sort=sort)
        if doc is not None:
            doc = copy.deepcopy(doc)
            storage = self.getDocumentStorage()
            _id = doc['_id']
            if replacement.get('_id') is not None and replacement['_id'] != _id:
                rid = replacement['_id']
                msg = ("command SON([('findAndModify', u'%(collection)s'), "
                    "('query', %(query)s), ('new', False), "
                    "('update', %(replace)s), ('upsert', False)]) on namespace "
                    "%(db)s.$cmd failed: exception: The _id field cannot be "
                    "changed from {_id: %(_id)s} to {_id: %(rid)s}." % {
                        'collection': self.name,
                        'query': filter,
                        'replace': replacement ,
                        'db': self.database.name,
                        '_id': _id.__repr__(),
                        'rid': rid.__repr__(),
                    })
                raise pymongo.errors.OperationFailure(msg)
            # use the same _id
            replacement['_id'] = _id
            key = toUnicode(_id)
            del storage[key]
            storage[key] = replacement
        if return_document is pymongo.collection.ReturnDocument.BEFORE:
            return doc
        else:
            return replacement

    # def find_one_and_update(self, filter, update, projection=None, sort=None,
    #     upsert=False, return_document=pymongo.collection.ReturnDocument.BEFORE,
    #     **kwargs):
    #     pymongo.common.validate_ok_for_update(update)
    #     doc = self.find_one(filter, projection=projection, sort=sort)
    #     _id = None
    #     rv = None
    #     if doc is not None:
    #         _id = doc['_id']
    #         if return_document is pymongo.collection.ReturnDocument.BEFORE:
    #             rv = copy.deepcopy(doc)
    #     storage = self.getDocumentStorage()
    #     if doc is None and upsert:
    #         # insert new document
    #         res = self.insert_one(filter)
    #         _id = res.inserted_id
    #         key = toUnicode(_id)
    #         doc = storage[key]
    #     if doc is not None:
    #         # update doc
    #         result = self._update(filter, update, upsert)
    #     # return before or after doc
    #     if return_document is pymongo.collection.ReturnDocument.BEFORE:
    #         return rv
    #     else:
    #         if _id is not None:
    #             key = toUnicode(_id)
    #             return storage.get(key)
    #         else:
    #             # no id no after document
    #             return None

    def find_one_and_update(self,
        filter,
        update,
        projection=None,
        sort=None,
        upsert=False,
        return_document=pymongo.collection.ReturnDocument.BEFORE,
        array_filters=None,
        hint=None,
        session=None,
        **kwargs):
        pymongo.common.validate_ok_for_update(update)
        doc = self.find_one(filter, projection=projection, sort=sort)
        _id = None
        rv = None
        if doc is not None:
            _id = doc['_id']
            if return_document is pymongo.collection.ReturnDocument.BEFORE:
                rv = copy.deepcopy(doc)
        res = self.update_one(filter, update, upsert)
        # return before or after doc
        if return_document is pymongo.collection.ReturnDocument.BEFORE:
            return rv
        else:
            if _id is None:
                _id = res.upserted_id
            if _id is not None:
                storage = self.getDocumentStorage()
                key = toUnicode(_id)
                return storage.get(key)
            else:
                # no id no after document
                return None

    def insert(self, doc_or_docs, manipulate=True, check_keys=True,
        continue_on_error=False, **kwargs):
        warnings.warn("insert is deprecated. Use insert_one or insert_many "
                      "instead.", DeprecationWarning, stacklevel=2)
        docs = doc_or_docs
        if isinstance(docs, dict):
            docs = [docs]
        storage = self.getDocumentStorage()
        for doc in docs:
            oid = doc.get('_id')
            if oid is None:
                oid = bson.ObjectId()
                doc[u'_id'] = oid
            d = {}
            for k, v in list(doc.items()):
                # use unicode keys as mongodb does
                d[toUnicode(k)] = v
            storage[toUnicode(oid)] = d

        ids = [doc.get("_id", None) for doc in docs]
        return len(ids) == 1 and ids[0] or ids

    def update(self, spec, document, upsert=False, manipulate=False,
        multi=False, check_keys=True, **kwargs):
        warnings.warn("update is deprecated. Use replace_one, update_one or "
                      "update_many instead.", DeprecationWarning, stacklevel=2)
        pymongo.common.validate_is_mapping("spec", spec)
        pymongo.common.validate_is_mapping("document", document)
        if document:
            # If a top level key begins with '$' this is a modify operation
            # and we should skip key validation. It doesn't matter which key
            # we check here. Passing a document with a mix of top level keys
            # starting with and without a '$' is invalid and the server will
            # raise an appropriate exception.
            first = next(iter(document))
            if first.startswith('$'):
                check_keys = False
        write_concern = None
        if kwargs:
            write_concern = pymongo.write_concern.WriteConcern(**kwargs)
        return self._update(spec, document, upsert, check_keys, multi,
            manipulate, write_concern)

    # NotImplementedError
    def find_and_modify(self,
        query={},
        update=None,
        upsert=False,
        sort=None,
        full_response=False,
        manipulate=False,
        **kwargs):
        """Update and return an object"""
        warnings.warn("find_and_modify is deprecated, use find_one_and_delete"
                      ", find_one_and_replace, or find_one_and_update instead",
                      DeprecationWarning, stacklevel=2)
        raise NotImplementedError()

    def __iter__(self):
        return self

    def __next__(self):
        raise TypeError("'Collection' object is not iterable")

    next = __next__

    def __call__(self, *args, **kwargs):
        """This is only here so that some API misusages are easier to debug.
        """
        if "." not in self.__name:
            raise TypeError("'Collection' object is not callable. If you "
                            "meant to call the '%s' method on a 'Database' "
                            "object it is failing because no such method "
                            "exists." %
                            self.__name)
        raise TypeError("'Collection' object is not callable. If you meant to "
                        "call the '%s' method on a 'Collection' object it is "
                        "failing because no such method exists." %
                        self.__name.split(".")[-1])

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.__database,
            self.__name)
