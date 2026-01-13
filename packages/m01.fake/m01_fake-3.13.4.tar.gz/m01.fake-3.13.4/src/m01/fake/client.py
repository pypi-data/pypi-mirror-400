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
from builtins import object
__docformat__ = 'restructuredtext'

import copy
import pprint as pp
import re
import six
import sys
import types
import collections
import warnings

import bson.objectid
import bson.son
import pymongo.common
import pymongo.cursor
import pymongo.errors
import pymongo.collection
import pymongo.database
import pymongo.results
import pymongo.client_options
import pymongo.operations
from pymongo.server_type import SERVER_TYPE
from pymongo.read_preferences import ReadPreference
from pymongo.server_selectors import writable_preferred_server_selector
from pymongo.server_selectors import writable_server_selector

try:
    # Python 2
    integer_types = (int, long)
    string_type = basestring
except NameError:
    # Python 3
    integer_types = (int,)
    string_type = str

from m01.fake.helpers import toUnicode
from m01.fake.database import FakeDatabase


###############################################################################
#
# helper

def _gen_index_name(keys):
    return "_".join(["%s_%s" % (k, d) for k, d in keys])

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


class FakeTopologySettings(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


###############################################################################
#
# helper object and methods

class FakeDatabases(collections.OrderedDict):
    """FakeDatabase storage"""


class DatabaseStorage(collections.OrderedDict):
    """Single shared storage for CollectionStorage per FakeDatabase"""

    def __init__(self, client):
        super(DatabaseStorage, self).__init__()
        self.client = client

    def getCollectionStorage(self, database):
        """Returns a collection data storage for given FakeDatabase"""
        try:
            return self[database.name]
        except KeyError:
            self[database.name] = CollectionStorage(database)
        return self[database.name]

    def __repr__(self):
        return "<%s for %r>" % (self.__class__.__name__, self.client.address)


class CollectionStorage(collections.OrderedDict):
    """Storage for DocumentStorage per FakeCollection"""

    def __init__(self, database):
        super(CollectionStorage, self).__init__()
        self.database = database

    def getDocumentStorage(self, collection):
        """Returns a document storage for given FakeCollection"""
        try:
            return self[collection.name]
        except KeyError:
            self[collection.name] = DocumentStorage(collection)
        return self[collection.name]

    def __repr__(self):
        return "<%s for %r>" % (self.__class__.__name__, self.database.name)


class DocumentIndex(object):
    """Document index"""

    def __init__(self, storage, idx):
        self.storage = storage
        self.doc = idx
        self.name = idx['name']
        self.key = idx['key']
        self.clear()

    def clear(self):
        pass

    def index(self, doc):
        """Index document"""
        # we currentyl do not query indexes, see find.py for how we query docs
        pass

    def find(self, query):
        raise NotImplementedError("Find is not implemented for DocumentIndex")


# XXX: implement language namspace
class TextIndex(object):
    """Text index"""

    def __init__(self, storage, idx):
        self.storage = storage
        self.doc = idx
        self.name = idx['name']
        self.key = idx['key']
        self.attrs = []
        for k, v in list(self.key.items()):
            if v == pymongo.TEXT:
                self.attrs.append(k)
        self.clear()

    def clear(self):
        # self.docs = {}
        self.words = {}

    def index(self, doc):
        """Index document"""
        _id = doc['_id']
        key = toUnicode(_id)
        values = []
        append = values.append
        for attr in self.attrs:
            v = doc.get(attr)
            if v is not None:
                append(v)
        if values:
            # self.doc self cs[key] = doc
            self.words[key] = ' '.join(values)

    def checkTextOperator(self, doc, criteria):
        search = criteria.get('$search')
        locale = criteria.get('$language')
        key = toUnicode(doc['_id'])
        if search in self.words.get(key, []):
            return True
        else:
            return False

    # def find(self, criteria):
    #     search = criteria.get('$search')
    #     locale = criteria.get('$language')
    #     keys = []
    #     append = keys.append
    #     for key, text in self.docs.items():
    #         if search in text:
    #             append(key)
    #     return [storage[key] for key in keys]


class DocumentIndexes(collections.OrderedDict):
    """Document index storage"""

    def __init__(self, storage):
        super(DocumentIndexes, self).__init__()
        self.storage = storage
        self.clear()

    def clear(self):
        self.textIndex = None
        for key, idx in list(self.items()):
            idx.clear()
            del self[key]
        idx = pymongo.operations.IndexModel([('_id', pymongo.ASCENDING)],
            name='_id_')
        self.createIndexes([idx])

    def setUpDocumentIndex(self, data):
        """Setup index"""
        key = data['name']
        for k, v in list(data['key'].items()):
            if v == pymongo.TEXT:
                if self.textIndex is not None:
                    raise pymongo.errors.OperationFailure(
                        "duplicated text index")
                idx = TextIndex(self.storage, data)
                self.textIndex = idx
                break
        else:
            idx = DocumentIndex(self.storage, data)
        self[key] = idx
        # index existing documents
        for doc in list(self.storage.values()):
            idx.index(doc)

    def createIndexes(self, indexes):
        """Create one or more indexes on this collection"""
        if not isinstance(indexes, list):
            raise TypeError("indexes must be a list")
        names = []
        def gen_indexes():
            for index in indexes:
                if not isinstance(index, pymongo.operations.IndexModel):
                    raise TypeError("%r is not an instance of "
                                    "pymongo.operations.IndexModel" % (index,))
                document = index.document
                names.append(document["name"])
                yield document
        for idx in list(gen_indexes()):
            self.setUpDocumentIndex(idx)
        return names

    def __create_index(self, keys, index_options):
        """Internal create index helper"""
        kwargs = index_options
        if "name" not in kwargs:
            kwargs["name"] = _gen_index_name(keys)
        model = pymongo.operations.IndexModel(keys, **kwargs)
        self.createIndexes([model])

    def createIndex(self, keys, session=None, **kwargs):
        """Creates an index on this collection"""
        keys = _index_list(keys)
        name = kwargs.setdefault("name", _gen_index_name(keys))
        self.__create_index(keys, kwargs)
        return name

    # def ensureIndex(self, key_or_list, cache_for=300, **kwargs):
    #     warnings.warn("ensure_index is deprecated. Use create_index instead.",
    #                   DeprecationWarning, stacklevel=2)
    #     # The types supported by datetime.timedelta.
    #     if not (isinstance(cache_for, integer_types) or
    #             isinstance(cache_for, float)):
    #         raise TypeError("cache_for must be an integer or float.")

    #     if "drop_dups" in kwargs:
    #         kwargs["dropDups"] = kwargs.pop("drop_dups")

    #     if "bucket_size" in kwargs:
    #         kwargs["bucketSize"] = kwargs.pop("bucket_size")

    #     keys = pymongo.helpers._index_list(key_or_list)
    #     name = kwargs.setdefault("name", _gen_index_name(keys))

    #     try:
    #         self.__create_index(keys, kwargs)
    #         return name
    #     except KeyError:
    #         return None

    def dropIndexes(self):
        """Drops all indexes on this collection"""
        for key in list(self.keys()):
            if key != '_id_':
                # keep _id index intact
                del self[key]

    def dropIndex(self, index_or_name):
        """Drops the specified index on this collection"""
        name = index_or_name
        if isinstance(index_or_name, list):
            name = _gen_index_name(index_or_name)
        if not isinstance(name, string_type):
            raise TypeError("index_or_name must be an index name or list")
        try:
            del self[name]
        except KeyError:
            collection = self.storage.collection
            cname = collection.name
            cmd = bson.son.SON()
            cmd['dropIndexes'] = cname
            cmd['index'] = name
            dbname = collection.database.name
            # raise pymongo.errors.OperationFailure(
            #     "command SON([('dropIndexes', '%(cname)s'), "
            #     "('index', '%(name)s')]) on namespace %(dbname)s.$cmd "
            #     "failed: index not found with name [%(name)s]" % {
            #         'cmd': cmd,
            #         'name': name,
            #         'cname': cname,
            #         'dbname': dbname,
            #     })
            raise pymongo.errors.OperationFailure(
            "index not found with name [%(name)s], "
            "full error: {'codeName': 'IndexNotFound', "
            "'code': 27, 'ok': 0.0, "
            "'errmsg': 'index not found with name [%(name)s]', "
            "'nIndexesWas': 2}" % {
                    'cmd': cmd,
                    'name': name,
                    'cname': cname,
                    'dbname': dbname,
                })

    def reIndex(self):
        """Rebuilds all indexes on this collection"""
        indexes = []
        append = indexes.append
        for idx in list(self.values()):
            doc = idx.doc
            data = {
                "ns": self.storage.collection.full_name,
                "name": doc['name'],
                "key": doc['key'],
                "v": 2,
                }
            append(data)
        return {
            "nIndexes": len(indexes),
            "ok": 1.0,
            "nIndexesWas": len(indexes),
            "indexes": indexes
        }

    def listIndexes(self):
        """Get a cursor over the index documents for this collection"""
        for idx in list(self.values()):
            doc = idx.doc
            data = (
                (u'v', 2),
                (u'key', bson.son.SON(doc['key'])),
                (u'name', doc['name']),
                (u'ns', self.storage.collection.full_name),
                )
            yield bson.son.SON(data)

    def getIndexInformation(self):
        """Get information on this collection's indexes"""
        cursor = self.listIndexes()
        info = {}
        for idx in self.listIndexes():
            idx["key"] = list(idx["key"].items())
            idx = dict(idx)
            info[idx.pop("name")] = idx
        return info

    def doIndex(self, doc):
        """Index document"""
        for idx in list(self.values()):
            idx.index(doc)

    def checkUnique(self, doc):
        """check unique document"""
        keys = list(self.storage.keys())
        docs = list(self.storage.values())
        for idx in list(self.values()):
            notUnique = False
            key = toUnicode(doc['_id'])
            name = idx.doc['name']
            if name == '_id_' and key in keys:
                value =  doc.get('_id')
                notUnique = True
            elif idx.doc.get('unique'):
                # custom unique key
                key = list(idx.doc['key'].keys())[0]
                value = doc.get(key)
                for data in docs:
                    if data.get(key) == value:
                        notUnique = True
                        break
            if notUnique:
                if isinstance(value, string_type):
                    v = '"%s"' % value
                else:
                    v = value
                iname = idx.doc['name']
                raise pymongo.errors.DuplicateKeyError(
                    "E11000 duplicate key error collection: "
                    "%(cname)s index: %(iname)s dup key: { : %(v)s }, "
                    "full error: {u'index': 0, u'code': 11000, "
                    "u'errmsg': u'E11000 duplicate key error collection: "
                    "%(cname)s index: %(iname)s dup key: "
                    "{ : %(v)s }'}"
                    % {
                        'cname': self.storage.collection.full_name,
                        'iname': iname,
                        'v': v
                        }
                    )

class DocumentStorage(collections.OrderedDict):
    """Document storage for FakeCollection"""

    def __init__(self, collection):
        super(DocumentStorage, self).__init__()
        self.collection = collection
        self.indexes = DocumentIndexes(self)

    def clear(self):
        for key in list(self.keys()):
            del self[key]

    def __getitem__(self, key):
        """Get document by key"""
        key = toUnicode(key)
        return super(DocumentStorage, self).__getitem__(key)

    def __setitem__(self, key, item):
        # copy key, values and make sure we don't store the original object
        # also convert keys to unicode
        key = toUnicode(key)
        doc = {}
        for k, v in list(item.items()):
            # use unicode keys as mongodb does
            doc[toUnicode(k)] = copy.deepcopy(v)
        self.indexes.checkUnique(doc)
        super(DocumentStorage, self).__setitem__(key, doc)
        self.indexes.doIndex(doc)
        return doc

    def __repr__(self):
        return "<%s for %r>" % (self.__class__.__name__,
            self.collection.full_name)


###############################################################################
#
# fake client

class FakeMongoClient(pymongo.common.BaseObject):
    """Fake MongoDB MongoClient."""

    HOST = 'localhost'
    PORT = 27017
    _constructor_args = ('document_class', 'tz_aware', 'connect')

    def __init__(self, host=None, port=None, document_class=dict,
        tz_aware=False, connect=True, storage=None,
        skipAdminDatabase=False, skipLocalDatabase=False, **kwargs):
        """Fake MongoDB client."""
        # Apply internal database storage
        self.setStorage(storage)

        # Setup MongoDB client
        if host is None:
            host = self.HOST
        if isinstance(host, string_type):
            host = [host]
        if port is None:
            port = self.PORT
        if not isinstance(port, int):
            raise TypeError("port must be an instance of int")

        seeds = list()
        username = None
        password = None
        dbase = None
        opts = {}

        for entity in host:
            if "://" in entity:
                if entity.startswith("mongodb://"):
                    # Parse the URI using the newer URI parser
                    res = pymongo.uri_parser.parse_uri(entity, port, False)
                    seeds.update(res["nodelist"])
                    username = res["username"] or username
                    password = res["password"] or password
                    dbase = res["database"] or dbase
                    opts = res["options"]
                else:
                    idx = entity.find("://")
                    raise pymongo.errors.InvalidURI("Invalid URI scheme: %s" % (
                        entity[:idx],))
            else:
                seeds.extend(pymongo.uri_parser.split_hosts(entity, port))

        if not seeds:
            raise pymongo.errors.ConfigurationError(
                "Need to specify at least one host")

        # _pool_class, _monitor_class, and _condition_class are for deep
        # customization of PyMongo, e.g. Motor.
        pool_class = kwargs.pop('_pool_class', None)
        monitor_class = kwargs.pop('_monitor_class', None)
        condition_class = kwargs.pop('_condition_class', None)

        # Validate all keyword options
        keyword_opts = kwargs
        keyword_opts['document_class'] = document_class
        keyword_opts['tz_aware'] = tz_aware
        keyword_opts['connect'] = connect
        # Validate all keyword options.
        keyword_opts = dict(pymongo.common.validate(k, v)
                            for k, v in list(keyword_opts.items()))
        opts.update(keyword_opts)

        # Create ClientOptions (credentials are handled internally)
        self.__options = options = pymongo.client_options.ClientOptions(
            username, password, dbase, opts)

        self.__default_database_name = dbase
        self._event_listeners = getattr(
            getattr(options, 'pool_options', None),
            'event_listeners', None)

        self.__nodes = seeds
        self.__host = None
        self.__port = None
        self.__document_class = document_class
        self.__dbs = FakeDatabases()

        # Initialize the base class
        super(FakeMongoClient, self).__init__(
            options.codec_options,
            options.read_preference,
            options.write_concern,
            options.read_concern
        )

        if not skipAdminDatabase:
            dbname = 'admin'
            self.__dbs[dbname] = FakeDatabase(self, dbname)
        if not skipLocalDatabase:
            dbname = 'local'
            self.__dbs[dbname] = FakeDatabase(self, dbname)

        # Handle credentials (updated for PyMongo 3.13.x)
        self.__all_credentials = {}
        if username:
            self._cache_credentials(dbase, username, password)

        self._topology_settings = FakeTopologySettings(
            seeds=seeds,
            replica_set_name=options.replica_set_name,
            pool_class=pool_class,
            pool_options=options.pool_options,
            monitor_class=monitor_class,
            condition_class=condition_class,
            local_threshold_ms=options.local_threshold_ms,
            server_selection_timeout=options.server_selection_timeout)

        if connect:
            # _connect=False is not supported yet because we need to implement
            # some fake host, port setup concept first
            try:
                self.__find_node(seeds)
            except pymongo.errors.AutoReconnect as e:
                # ConnectionFailure makes more sense here than AutoReconnect
                raise pymongo.errors.ConnectionFailure(str(e))

    def setStorage(self, storage=None):
        """Apply an internal database storage"""
        if storage is None:
            storage = DatabaseStorage
        self.__storage = storage(self)

    def getCollectionStorage(self, database):
        return self.__storage.getCollectionStorage(database)

    def _cache_credentials(self, source, username, password, connect=False):
        """Save a set of authentication credentials.

        The credentials are used to login a socket whenever one is created.
        If `connect` is True, verify the credentials on the server first.

        Args:
            source (str): The database to authenticate against.
            username (str): The username for authentication.
            password (str): The password for authentication.
            connect (bool): If True, verify the credentials on the server.
        """
        # Don't let other threads affect this call's data.
        all_credentials = self.__all_credentials.copy()

        if source in all_credentials:
            # Check if the credentials are the same as the cached ones.
            cached_username, cached_password = all_credentials[source]
            if username == cached_username and password == cached_password:
                return  # Nothing to do if the credentials are already cached.

            # Raise an error if another user is already authenticated.
            raise pymongo.errors.OperationFailure(
                'Another user is already authenticated to this database. You '
                'must logout first.')

        # Cache the new credentials.
        self.__all_credentials[source] = (username, password)

        # Optionally verify the credentials on the server.
        if connect:
            self._verify_credentials(source, username, password)


    def __find_node(self, seeds=None):
        # very simple find node implementation
        errors = []
        mongos_candidates = []
        candidates = seeds or self.__nodes.copy()
        for candidate in reversed(candidates):
            node, ismaster, isdbgrid, res_time = self.__try_node(candidate)
            return node

        # couldn't find a suitable host.
        self.close()
        raise pymongo.errors.AutoReconnect(', '.join(errors))

    def __try_node(self, node):
        self.close()
        self.__host, self.__port = node
        # return node and some fake data
        ismaster = True
        isdbgrid = False
        res_time = None
        return node, ismaster, isdbgrid, res_time

    @property
    def storage(self):
        return self.__storage

    @property
    def dbs(self):
        return self.__dbs

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    @property
    def event_listeners(self):
        """The event listeners registered for this client"""
        return []

    @property
    def address(self):
        return '%s:%s' % (self.__host, self.__port)

    @property
    def primary(self):
        """The (host, port) of the current primary of the replica set"""
        return self.address

    @property
    def secondaries(self):
        """The secondary members known to this client"""
        return set()

    @property
    def arbiters(self):
        """Arbiters in the replica set"""
        return set()

    @property
    def is_primary(self):
        """If this client if connected to a server that can accept writes"""
        return True

    @property
    def is_mongos(self):
        """If this client is connected to mongos"""
        return True

    @property
    def max_pool_size(self):
        """The maximum number of sockets the pool will open concurrently"""
        return self.__options.pool_options.max_pool_size

    @property
    def nodes(self):
        """List of all known nodes"""
        return self.__nodes

    @property
    def max_bson_size(self):
        """The largest BSON object the connected server accepts in bytes"""
        return pymongo.common.MAX_BSON_SIZE

    @property
    def max_message_size(self):
        """The largest message the connected server accepts in bytes"""
        return pymongo.common.MAX_MESSAGE_SIZE

    @property
    def max_write_batch_size(self):
        """The maxWriteBatchSize reported by the server"""
        return pymongo.common.MAX_WRITE_BATCH_SIZE

    @property
    def local_threshold_ms(self):
        """The local threshold for this instance."""
        return self.__options.local_threshold_ms

    @property
    def server_selection_timeout(self):
        """The server selection timeout for this instance in seconds."""
        return self.__options.server_selection_timeout

    def close(self):
        pass

    def set_cursor_manager(self, manager_class):
        """Set this client's cursor manager"""
        manager = manager_class(self)
        if not isinstance(manager, CursorManager):
            raise TypeError("manager_class must be a subclass of CursorManager")

    def __eq__(self, other):
        try:
            return self.address == other.address
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(
                "MongoClient has no attribute %r. To access the %s"
                " database, use client[%r]." % (name, name, name))
        return self.__getitem__(name)

    def __getitem__(self, name):
        return self.get_database(name)

    def close_cursor(self, cursor_id, address=None):
        pass

    def kill_cursors(self, cursor_ids, address=None):
        pass

    def server_info(self):
        return {}

    def database_names(self):
        warnings.warn(
            "database_names is deprecated. Use list_database_names instead.",
            DeprecationWarning, stacklevel=2)
        return list(self.__dbs.keys())

    def list_database_names(self):
        return list(self.__dbs.keys())

    def drop_database(self, name_or_database):
        if isinstance(name_or_database, FakeDatabase):
            name = name_or_database.name
        else:
            name = name_or_database
        db = self.__dbs.get(name)
        if db is not None:
            for cname in db.list_collection_names():
                # drop collections
                db.drop_collection(cname)
            del self.__dbs[db.name]
            if db.name in self.__storage:
                # remove storage data
                del self.__storage[db.name]

    def get_default_database(self):
        """Get the database named in the MongoDB connection URI"""
        if self.__default_database_name is None:
            raise pymongo.errors.ConfigurationError(
                "No default database defined")
        return self[self.__default_database_name]

    def get_database(self, name, codec_options=None, read_preference=None,
        write_concern=None):
        """Get a :class:`~pymongo.database.Database` with the given name and
        options
        """
        db = self.__dbs.get(name)
        if db is None:
            db = FakeDatabase(self, name, codec_options=codec_options,
                read_preference=read_preference, write_concern=write_concern)
            self.__dbs[name] = db
        return db

    @property
    def is_locked(self):
        """Is this server locked"""
        # just say no
        return False

    def fsync(self, **kwargs):
        """Flush all pending writes to datafiles"""
        # just ignore
        pass

    def unlock(self):
        """Unlock a previously locked server"""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        raise TypeError("'%s' object is not iterable" % self.__class__.__name__)

    def _repr_helper(self):
        def option_repr(option, value):
            """Fix options whose __repr__ isn't usable in a constructor."""
            if option == 'document_class':
                if value is dict:
                    return 'document_class=dict'
                else:
                    return 'document_class=%s.%s' % (value.__module__,
                                                     value.__name__)
            if "ms" in option:
                return "%s='%s'" % (option, int(value * 1000))

            return '%s=%r' % (option, value)

        # Host first...
        options = ['host=%r' % [
            '%s:%d' % (host, port)
            for host, port in self._topology_settings.seeds]]
        # ... then everything in self._constructor_args...
        options.extend(
            option_repr(key, self.__options._options[key])
            for key in self._constructor_args)
        # ... then everything else.
        options.extend(
            option_repr(key, self.__options._options[key])
            for key in self.__options._options
            if key not in set(self._constructor_args))
        return ', '.join(options)

    def __repr__(self):
        return ("MongoClient(%s)" % (self._repr_helper(),))


# single shared MongoClient instance
fakeMongoClient = FakeMongoClient()
