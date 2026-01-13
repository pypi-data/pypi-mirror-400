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
__docformat__ = 'restructuredtext'

import collections

#from bson.py3compat import string_type
try:
    string_type = basestring  # Python 2
except NameError:
    string_type = str

import pymongo.common
import pymongo.mongo_client
from bson.codec_options import DEFAULT_CODEC_OPTIONS
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import DEFAULT_WRITE_CONCERN

import m01.fake.helpers
from m01.fake.collection import FakeCollection
from m01.fake.helpers import toUnicode


# helper
class FakeCollections(collections.OrderedDict):
    """FakeCollection storage"""


###############################################################################
#
# fake database

class FakeDatabase(pymongo.common.BaseObject):
    """Fake mongoDB database."""

    def __init__(self, client, name, codec_options=None, read_preference=None,
        write_concern=None, read_concern=None):
        codec_options = codec_options or DEFAULT_CODEC_OPTIONS
        read_preference = read_preference or ReadPreference.PRIMARY
        write_concern = write_concern or DEFAULT_WRITE_CONCERN
        read_concern = read_concern or ReadConcern()
        super(FakeDatabase, self).__init__(
            codec_options,
            read_preference,
            write_concern,
            read_concern)
        self.__name = toUnicode(name)
        self.__client = client
        self.__incoming_manipulators = []
        self.__incoming_copying_manipulators = []
        self.__outgoing_manipulators = []
        self.__outgoing_copying_manipulators = []
        self._cols = FakeCollections()
        # self.create_collection('system.indexes')

    def getCollectionStorage(self):
        return self.__client.getCollectionStorage(self)

    def doRenameFakeCollection(self, oldName, newName):
        # remove from fake collections
        storage = self.getCollectionStorage()
        storage[newName] = storage.pop(oldName)
        self._cols[newName] = self._cols.pop(oldName)

    # NotImplementedError
    @property
    def system_js(self):
        """A :class:`SystemJS` helper for this :class:`Database`"""
        raise NotImplementedError

    @property
    def client(self):
        return self.__client

    @property
    def name(self):
        return self.__name

    @property
    def incoming_manipulators(self):
        """All incoming SON manipulators installed on this instance"""
        return [manipulator.__class__.__name__
                for manipulator in self.__incoming_manipulators]

    @property
    def incoming_copying_manipulators(self):
        """All incoming SON copying manipulators installed on this instance"""
        return [manipulator.__class__.__name__
                for manipulator in self.__incoming_copying_manipulators]

    @property
    def outgoing_manipulators(self):
        """List all outgoing SON manipulators"""
        return [manipulator.__class__.__name__
                for manipulator in self.__outgoing_manipulators]

    @property
    def outgoing_copying_manipulators(self):
        """List all outgoing SON copying manipulators"""
        return [manipulator.__class__.__name__
                for manipulator in self.__outgoing_copying_manipulators]

    def __eq__(self, other):
        if isinstance(other, FakeDatabase):
            return (self.__client == other.client and
                    self.__name == other.name)
        return NotImplemented

    def __ne__(self, other):
        return not self == other

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(
                "Database has no attribute %r. To access the %s"
                " collection, use database[%r]." % (name, name, name))
        return self.__getitem__(name)

    def __getitem__(self, name):
        return self.get_collection(name)

    def get_collection(self, name, codec_options=None,
        read_preference=None, write_concern=None, **kwargs):
        collection = self._cols.get(name)
        if collection is None:
            collection = self.create_collection(name, codec_options,
                read_preference, write_concern, **kwargs)
        return collection

    def create_collection(self, name, codec_options=None, read_preference=None,
        write_concern=None, **kwargs):
        if name in self._cols:
            raise pymongo.errors.CollectionInvalid(
                "collection %s already exists" % name)
        else:
            create = True
            collection = FakeCollection(self, name, create,
                codec_options, read_preference, write_concern, **kwargs)
            self._cols[name] = collection
        return collection

    def _apply_incoming_manipulators(self, son, collection):
        """Apply incoming manipulators to `son`."""
        for manipulator in self.__incoming_manipulators:
            son = manipulator.transform_incoming(son, collection)
        return son

    def _apply_incoming_copying_manipulators(self, son, collection):
        """Apply incoming copying manipulators to `son`."""
        for manipulator in self.__incoming_copying_manipulators:
            son = manipulator.transform_incoming(son, collection)
        return son

    def _fix_incoming(self, son, collection):
        """Apply manipulators to an incoming SON object before it gets stored.

        :Parameters:
          - `son`: the son object going into the database
          - `collection`: the collection the son object is being saved in
        """
        son = self._apply_incoming_manipulators(son, collection)
        son = self._apply_incoming_copying_manipulators(son, collection)
        return son

    def _fix_outgoing(self, son, collection):
        """Apply manipulators to a SON object as it comes out of the database.

        :Parameters:
          - `son`: the son object coming out of the database
          - `collection`: the collection the son object was saved in
        """
        for manipulator in reversed(self.__outgoing_manipulators):
            son = manipulator.transform_outgoing(son, collection)
        for manipulator in reversed(self.__outgoing_copying_manipulators):
            son = manipulator.transform_outgoing(son, collection)
        return son

    def list_collection_names(self, session=None, filter=None, **kwargs):
        """Get a list of all the collection names in this database"""
        names = sorted(self._cols.keys())
        # if not include_system_collections:
        #     names = [name for name in names if not name.startswith("system.")]
        return names

    def drop_collection(self, name_or_collection):
        name = name_or_collection
        if isinstance(name, FakeCollection):
            name = name.name
        if not isinstance(name, string_type):
            raise TypeError("name_or_collection must be an "
                            "instance of %s" % (string_type.__name__,))
        try:
            # the collection knows what's to remove including himself
            col = self._cols[name]
            col.drop()
        except KeyError:
            pass

    # NotImplementedError
    def validate_collection(self, name_or_collection, scandata=False,
        full=False):
        """Validate a collection"""
        raise NotImplementedError()

    # NotImplementedError
    def current_op(self, include_all=False):
        """Get information on operations currently running"""
        raise NotImplementedError()

    # NotImplementedError
    def profiling_level(self):
        """Get the database's current profiling level"""
        raise NotImplementedError()

    # NotImplementedError
    def set_profiling_level(self, level, slow_ms=None):
        """Set the database's profiling level"""
        raise NotImplementedError()

    # NotImplementedError
    def profiling_info(self):
        """Returns a list containing current profiling information"""
        raise NotImplementedError()

    def __iter__(self):
        return self

    def __next__(self):
        raise TypeError("'Database' object is not iterable")

    next = __next__

    # not implemented
    def add_user(self, name, password=None, read_only=None, **kwargs):
        """Create user `name` with password `password`"""
        # silently skip this call
        pass

    # not implemented
    def remove_user(self, name):
        """Remove user `name` from this :class:`Database`"""
        # silently skip this call
        pass

    # not implemented
    def authenticate(self, name, password=None, source=None,
        mechanism='DEFAULT', **kwargs):
        """Authenticate to use this database"""
        # silently skip this call
        pass

    def logout(self):
        """Deauthorize use of this database for this client instance."""
        # silently skip this call
        pass

    # NotImplementedError
    def dereference(self, dbref, **kwargs):
        """Dereference a :class:`~bson.dbref.DBRef`, getting the
        document it points to
        """
        raise NotImplementedError()

    # NotImplementedError
    def eval(self, code, *args):
        """Evaluate a JavaScript expression in MongoDB"""
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        """This is only here so that some API misusages are easier to debug.
        """
        raise TypeError("'Database' object is not callable. If you meant to "
                        "call the '%s' method on a '%s' object it is "
                        "failing because no such method exists." % (
                            self.__name, self.__client.__class__.__name__))

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.__client,
            self.__name)
