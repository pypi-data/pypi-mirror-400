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
"""Find filter

$Id:$
"""
from __future__ import absolute_import
from past.builtins import cmp
from builtins import str
__docformat__ = 'restructuredtext'

import re
import copy
import operator
import collections

import datetime
import bson
import bson.son
import bson.binary
import bson.code
import bson.objectid
import bson.timestamp
import bson.regex
import bson.int64
import bson.min_key
import bson.max_key

from sentinels import NOTHING
from six import iteritems
from six import string_types

import pymongo.errors
from functools import cmp_to_key
import copy

RE_OPTIONS = {
    "i": re.I,
    "l": re.L,
    "m": re.M,
    "s": re.S,
    "u": re.U,
    "x": re.X,
}


###############################################################################
#
# helpers

def getDocumentValueFormArray(key, array):
    """Get nested document value by the key from given document array

    :param array: a list to be searched for candidates for our key
    :param key: the string key to be matched
    """
    keyParts = key.split(".")
    sKey = keyParts.pop(0)
    rKey = ".".join(keyParts)
    try:
        sKeyIndex = int(sKey)
    except ValueError:
        sKeyIndex = None

    if sKeyIndex is None:
        # subkey is not an integer...
        res =  []
        append = res.append
        for sDoc in array:
            if isinstance(sDoc, dict) and sKey in sDoc:
                append(getDocumentValue(rKey, sDoc[sKey]))
        return res
    else:
        # subkey is an index
        if sKeyIndex >= len(array):
            # index out of range
            return []
        sDoc = doc[sKeyIndex]
        if keyParts:
            return getDocumentValue(".".join(keyParts), sDoc)
        return [sDoc]


def getDocumentValue(key, doc):
    """Get nested document values by the key from given document"""
    if doc is None:
        return ()

    if not key:
        return doc

    if isinstance(doc, list):
        return getDocumentValueFormArray(key, doc)

    if not isinstance(doc, dict):
        return ()

    kParts = key.split('.')
    if len(kParts) == 1:
        return doc.get(key, NOTHING)

    sKey = '.'.join(kParts[1:])
    sDoc = doc.get(kParts[0], {})
    return getDocumentValue(sKey, sDoc)


def getNoneForNothing(value):
    """Get None for NOTHING used for compare query selector"""
    if isinstance(value, list):
        return [getNoneForNothing(v) for v in value]
    elif isinstance(value, tuple):
        return tuple([getNoneForNothing(v) for v in value])
    elif value is NOTHING:
        return None
    else:
        return value


def getList(v, useNoneForNothing=False):
    """Get a list of values for simpler iteration"""
    res = v if isinstance(v, (list, tuple)) else [v]
    if useNoneForNothing:
        res = getNoneForNothing(res)
    return res


def checkRegex(dv, regex):
    return any(regex.search(v) for v in getList(dv)
               if isinstance(v, string_types))


###############################################################################
#
# filter processor

def getTextIndex(collection):
    storage = collection.getDocumentStorage()
    return storage.indexes.textIndex

def checkTextOperator(collection, document, key, value, criteria):
    if key == '$text':
        idx = getTextIndex(collection)
        if idx is None:
            raise pymongo.errors.OperationFailure(
                "text index required for $text query, full error: "
                "{u'codeName': u'IndexNotFound', u'code': 27, "
                "u'ok': 0.0, u'errmsg': u'text index required for $text query'}")
        else:
            return idx.checkTextOperator(document, criteria)
    return False

def checkLogicalOperator(collection, document, key, value, criteria):
    if key in LOGICAL_OPERATORS:
        if not criteria:
            raise pymongo.errors.OperationFailure(
                'BadValue $and/$or/$nor must be a non empty array')
        return LOGICAL_OPERATORS[key](collection, document, criteria)
    return False


def checkCriteriaOperator(collection, document, key, value, criteria):
    if isinstance(criteria, dict) and \
        all(op in OPERATORS and OPERATORS[op](collection, document, key, value,
            criteria)
            for op in list(criteria.keys())):
        return True
    return False


def checkCriteriaValue(document, key, value, criteria):
    values = getList(value)
    for dv in values:
        if isinstance(dv, (list, tuple)):
            if criteria in dv or criteria == dv:
                return True
            elif isinstance(criteria, bson.ObjectId) and str(criteria) in dv:
                return True
        elif criteria == dv:
            return True
        elif criteria is None and dv is NOTHING:
            return True
    return False


def checkCriteriaRegex(document, key, value, criteria):
    values = getList(value)
    if isinstance(criteria, dict) and "$regex" in criteria:
        regex = criteria['$regex']
        flags = 0
        # pymongo always adds $options but custom code may not.
        for opt in criteria.get("$options", []):
            flags |= RE_OPTIONS.get(opt, 0)
        reg = re.compile(regex, flags)
        return any(checkRegex(dv, reg) for dv in values)
    elif isinstance(criteria, bson.RE_TYPE):
        return any(checkRegex(dv, reg) for dv in values)

    return False


def checkFilterCriteria(collection, document, key, criteria):
    """Check one filter criteria"""
    value = getDocumentValue(key, document)
    # at least one criteria must match
    if checkTextOperator(collection, document, key, value, criteria):
        return True
    elif checkLogicalOperator(collection, document, key, value, criteria):
        return True
    elif checkCriteriaOperator(collection, document, key, value, criteria):
        return True
    elif checkCriteriaValue(document, key, value, criteria):
        return True
    elif checkCriteriaRegex(document, key, value, criteria):
        return True
    else:
        return False


def checkFilter(collection, document, filter):
    """Check document with given filter

    We will iterator over each filter criteria and check if at least one filter
    criteria is valid. Each document value get validated with the corresponding
    operator.

    """
    if filter is None:
        return True
    elif isinstance(filter, bson.ObjectId):
        filter = {'_id': filter}
    elif not isinstance(filter, dict):
        raise pymongo.errors.OperationFailure(
            'Filter must be None, a mapping or an ObjectId')

    for key, criteria in list(filter.items()):
        if not checkFilterCriteria(collection, document, key, criteria):
            # one filter didn't match
            return False

    # all criteria match or no filter criteria was given
    return True


###############################################################################
#
# query operator

def NOT(collection, document, key, value, criterias):
    k = '$not'
    criteria = criterias[k]
    if isinstance(criteria, dict):
        for key in list(criteria.keys()):
            if key == '$regex':
                raise pymongo.errors.OperationFailure(
                    'BadValue $not cannot have a regex')
            if key not in OPERATORS and key not in LOGICAL_OPERATORS:
                raise pymongo.errors.OperationFailure(
                    'BadValue $not needs a regex or a document')
    elif isinstance(criteria, type(re.compile(''))):
# XXX: regex support or not with $not operator???
        pass
    else:
        raise pymongo.errors.OperationFailure(
            'BadValue $not needs a regex or a document')
    return not checkFilter(collection, document, {key: criteria})


def EQ(collection, document, key, value, criterias):
    k = '$eq'
    cv = criterias[k]
    values = getList(value, useNoneForNothing=True)
    return any(operator.eq(dv, cv) for dv in values)


def NE(collection, document, key, value, criterias):
    k = '$ne'
    cv = criterias[k]
    values = getList(value, useNoneForNothing=True)
    if not cv and not values:
        return True
    else:
        return any(operator.ne(dv, cv) for dv in values)


def GT(collection, document, key, value, criterias):
    k = '$gt'
    cv = criterias[k]
    values = getList(value, useNoneForNothing=True)
    return any(dv is not None and operator.gt(dv, cv) for dv in values)


def GTE(collection, document, key, value, criterias):
    k = '$gte'
    cv = criterias[k]
    values = getList(value, useNoneForNothing=True)
    return any(dv is not None and operator.ge(dv, cv) for dv in values)


def LT(collection, document, key, value, criterias):
    k = '$lt'
    cv = criterias[k]
    values = getList(value, useNoneForNothing=True)
    return any(dv is not None and operator.lt(dv, cv) for dv in values)


def LTE(collection, document, key, value, criterias):
    k = '$lte'
    cv = criterias[k]
    values = getList(value, useNoneForNothing=True)
    return any(dv is not None and operator.le(dv, cv) for dv in values)


def ALL(collection, document, key, value, criterias):
    k = '$all'
    cv = criterias[k]
    values = getList(value, useNoneForNothing=True)
    if all(criteria in values for criteria in cv):
        return True
    else:
        return False


def IN(collection, document, key, value, criterias):
    k = '$in'
    cv = criterias[k]
    values = getList(value, useNoneForNothing=True)
    for dv in values:
        if any(v in cv for v in getList(dv, useNoneForNothing=True)):
            return True
    return False


def NIN(collection, document, key, value, criterias):
    k = '$nin'
    cv = criterias[k]
    values = getList(value, useNoneForNothing=True)
    for dv in values:
        # None is a valid selector for compare mssing values
        if all(v not in cv for v in getList(dv, useNoneForNothing=True)):
            return True
    return False


def EXISTS(collection, document, key, value, criterias):
    k = '$exists'
    cv = criterias[k]
    values = getList(value, useNoneForNothing=True)
    if not cv and not values:
        return True
    for dv in values:
        if bool(cv) == (dv is not None):
            return True
    return False


def REGEX(collection, document, key, value, criterias):
    k = '$regex'
    cv = criterias[k]
    values = getList(value, useNoneForNothing=True)
    for dv in values:
        if dv is not NOTHING and checkRegex(dv, re.compile(cv)):
            return True
    return False


def checkMatchFilter(collection, key, value, op, criteria):
    if not isinstance(value, dict):
        # build a dict for check the filter
        doc = {key: value}
    else:
        doc = value
    if op.startswith('$'):
        filter = {key: {op: criteria}}
    else:
        filter = {op: criteria}
    return checkFilter(collection, doc, filter)

def ELEMMATCH(collection, document, key, value, criterias):
    k = '$elemMatch'
    criteria = criterias[k]
    values = getList(value, useNoneForNothing=True)
    for dv in values:
        if all(checkMatchFilter(collection, key, dv, op, cv)
               for op, cv in list(criteria.items())):
            return True
    return False


def SIZE(collection, document, key, value, criterias):
    k = '$size'
    criteria = criterias[k]
    if isinstance(value, list) and len(value) == int(criteria):
        return True
    return False


BSON_TYPES = {
    1: float, # Double
    2: string_types, # String  2
    3: (dict, bson.son.SON), # Object  3
    4: list, # Array   4
    5: bson.binary.Binary, # Binary data 5
    # 6: Undefined Deprecated.
    7: bson.objectid.ObjectId, # Object id   7
    8: bool, # Boolean 8
    9: datetime.date, # Date    9
    10: None, # Null    10
    11: bson.regex.Regex, # Regular Expression  11
    13: bson.code.Code, # JavaScript  13
    #14: # Symbol  14
    15: bson.code.Code, # JavaScript (with scope) 15
    16: int, # 32-bit integer  16
    17: bson.timestamp.Timestamp, # Timestamp   17
    18: bson.int64.Int64, # 64-bit integer  18
    -1: bson.min_key.MinKey, # Min key 255 Query with -1.
    127: bson.max_key.MaxKey, # Max key 127
}


def TYPE(collection, document, key, value, criterias):
    k = '$type'
    cv = criterias[k]
    types = BSON_TYPES.get(cv)
    if cv == 4 and isinstance(value, list):
        # array
        return True
    for dv in getList(value, useNoneForNothing=True):
        # make list and check each value in list. This will check single values
        # and values in an array
        if cv == 2:
            if not isinstance(dv, (bson.binary.Binary, bson.code.Code)) and \
                isinstance(dv, types):
                # we don't like binary and code
                return True
        elif cv == 10:
            if dv is None:
                return True
        elif cv in [13, 15]:
            if isinstance(dv, bson.code.Code) and \
                (cv == 13 and not dv.scope or cv == 15 and dv.scope):
                return True
        elif cv == 16:
            # True, False are also numbers, skip them
            if dv not in [True, False] and isinstance(dv, types):
                return True
        elif types is not None:
            if isinstance(dv, types):
                return True
    return False


def MOD(collection, document, key, value, criterias):
    k = '$mod'
    cv = criterias[k]
    values = getList(value, useNoneForNothing=True)
    for dv in values:
        if isinstance(dv, int):
            if len(cv) == 0:
                error = "bad query: BadValue malformed mod, not enough elements"
                code = 16810
                raise pymongo.errors.OperationFailure(error, code)
            if len(cv) < 2:
                error = "bad query: BadValue malformed mod, not enough elements"
                code = 16810
                raise pymongo.errors.OperationFailure(error, code)
            elif len(cv) > 2:
                error = "bad query: BadValue malformed mod, too many elements"
                code = 16810
                raise pymongo.errors.OperationFailure(error, code)
            else:
                # modulo compare with remainder
                divisor, remainder = cv
                if dv % divisor == remainder:
                    return True
    return False


OPERATORS = {
    # comparsion query operator
    '$eq': EQ,
    '$gt': GT,
    '$gte': GTE,
    '$in': IN,
    '$lt': LT,
    '$lte': LTE,
    '$ne': NE,
    '$nin': NIN,
    # element query operator
    '$exists': EXISTS,
    '$type': TYPE,
    # evaluation query operator
    '$mod': MOD,
    '$regex':REGEX,
    # '$where': WHERE,
    # geospatial query operator
    # '$geoWithin': GEOWITHIN,
    # '$geoIntersects': GEOINTERSECT,
    # '$near': NEAR,
    # '$nearSphere': NEARSPHERE,
    # array query operator
    '$all': ALL,
    '$elemMatch': ELEMMATCH,
    '$size': SIZE,
    # logical query operator
    '$not': NOT,
}


###############################################################################
#
# logical operators

def AND(collection, doc, query):
    return all(checkFilter(collection, doc, q) for q in query)


def NOR(collection, doc, query):
    return all(not checkFilter(collection, doc, q) for q in query)


def OR(collection, doc, query):
    return any(checkFilter(collection, doc, q) for q in query)


def NOT_TOP_LEVEL(collection, doc, query):
    # raise pymongo.errors.OperationFailure(
    #     "database error: Can't canonicalize query: "
    #     "BadValue unknown top level operator: $not")
    raise pymongo.errors.OperationFailure(
        "unknown top level operator: $not, full error: "
        "{u'codeName': u'BadValue', u'code': 2, u'ok': 0.0, "
        "u'errmsg': u'unknown top level operator: $not'}")

LOGICAL_OPERATORS = {
    # logical operator
    '$or': OR,
    '$and': AND,
    '$nor': NOR,
    '$not': NOT_TOP_LEVEL,
}


###############################################################################
#
# filter api

def doSort(criteria):
    def sorter(a, b):
        for key, direction in list(criteria.items()):
            part = cmp(a.get(key), b.get(key))
            if part:
                return part * direction
        return 0
    return sorter


def doProjection(doc, projection=None):
    if projection:
        projected = {'_id': doc['_id']}
        for k in projection:
            v = doc.get(k)
            if v:
                projected[k] = v
        doc = projected
    return doc


def getFilteredDocument(collection, doc, filter):
    if checkFilter(collection, doc, filter):
        return doc
    else:
        return None


def getFilteredDocuments(collection, filter=None, projection=None, skip=0,
                         limit=0, sort=None, multi=True, deepcopy=True):
    """Returns documents for given filter arguments"""
    storage = collection.getDocumentStorage()

    docs = []
    append = docs.append

    # filter all relevant documents
    for doc in list(storage.values()):
        doc = getFilteredDocument(collection, doc, filter)
        if doc is not None:
            if projection is not None:
                # do projection
                doc = doProjection(doc, projection)
            elif deepcopy:
                # or deepcopy
                doc = copy.deepcopy(doc)
            append(doc)

    # sort result
    if len(docs) > 1 and sort:
        docs = sorted(docs, key=cmp_to_key(doSort(sort)))

    if skip:
        # skip values from start
        docs = docs[skip:]

    if limit:
        # limit result to end, use positive number
        docs = docs[:abs(limit)]

    # get one or all after sort
    if len(docs) > 0 and not multi:
        # return only one document
        docs = [docs[0]]

    return docs