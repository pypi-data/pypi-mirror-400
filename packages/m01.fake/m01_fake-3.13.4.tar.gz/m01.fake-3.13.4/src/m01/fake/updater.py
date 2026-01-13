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
__docformat__ = 'restructuredtext'

import copy

import bson
import pymongo.errors

import m01.fake.finder


###############################################################################
#
# updater

def setUpdater(doc, key, value):
    if isinstance(value, (tuple, list)):
        value = copy.deepcopy(value)
    if isinstance(doc, dict):
        doc[key] = value


def incUpdater(doc, key, value):
    if isinstance(doc, dict):
        doc[key] = doc.get(key, 0) + value


# XXX: implement sum updater
def sumUpdater(doc, key, current, result):
    if isinstance(doc, dict):
        result = current + doc.get[key, 0]
        return result


###############################################################################
#
# document handler

def getSubDoc(doc, spec, nested_field_list):
    """This method retrieves the sub document of the doc.nested_field_list.

    It uses the spec to filter through the items. It will continue to grab
    nested documents until it can go no further. It will then return the
    subdocument that was last saved.
    '$' is the positional operator, so we use the $elemMatch in the spec to
    find the right subdocument in the array.
    """
    # current document in view
    doc = doc
    # previous document in view
    subdocument = doc
    # current spec in view
    subspec = spec
    # walk down the dictionary
    for subfield in nested_field_list:
        if subfield == '$':
            # positional element should have the equivalent elemMatch in the
            # query
            subspec = subspec['$elemMatch']
            for item in doc:
                # iterate through
                if m01.fake.finder.checkFilter(item, subspec):
                    # found the matching item save the parent
                    subdocument = doc
                    # save the item
                    doc = item
                    break
            continue

        subdocument = doc
        doc = doc[subfield]
        if subfield not in subspec:
            break
        subspec = subspec[subfield]

    return subdocument


def doUpdateDocumentField(doc, key, value, updater):
    parts = key.split(".")
    for part in parts[:-1]:
        if isinstance(doc, list):
            try:
                if part == '$':
                    doc = doc[0]
                else:
                    doc = doc[int(part)]
                continue
            except ValueError:
                pass
        elif isinstance(doc, dict):
            doc = doc.setdefault(part, {})
        else:
            return
    key = parts[-1]
    if isinstance(doc, list):
        try:
            doc[int(key)] = value
        except IndexError:
            pass
    else:
        updater(doc, key, value)


def doManipulateDocumentField(doc, spec, key, value, updater, subdoc):
    parts = key.split('.')
    if not subdoc:
        current = doc
        subspec = spec
        for part in parts[:-1]:
            if part == '$':
                subspec = subspec.get('$elemMatch', subspec)
                for item in current:
                    if m01.fake.finder.checkFilter(item, subspec):
                        current = item
                        break
                continue

            new_spec = {}
            for el in subspec:
                if el.startswith(part):
                    if len(el.split(".")) > 1:
                        new_spec[".".join(
                            el.split(".")[1:])] = subspec[el]
                    else:
                        new_spec = subspec[el]
            subspec = new_spec
            current = current[part]

        subdoc = current
        if (parts[-1] == '$' and isinstance(subdoc, list)):
            for i, doc in enumerate(subdoc):
                if m01.fake.finder.checkFilter(doc, subspec):
                    subdoc[i] = value
                    break
            return

    updater(subdoc, parts[-1], value)


def doUpdateDocumentFields(doc, fields, filter, updater, subdoc=None):
    """Implements the $set behavior on an existing document"""
    for k, v in list(fields.items()):
        if k.startswith('$'):
            subdoc = doManipulateDocumentField(doc, filter, k, v, updater,
                subdoc)
        else:
            # otherwise, we handle it the standard way
            doUpdateDocumentField(doc, k, v, updater)
    return subdoc


###############################################################################
#
# operators

def doSet(storage, doc, subdoc, filter, document):
    """$set operator"""
    k = '$set'
    v = document[k]
    subdoc = doUpdateDocumentFields(doc, v, filter, setUpdater, subdoc)
    return subdoc


def doUnSet(storage, doc, subdoc, filter, document):
    """$unset operator"""
    k = '$unset'
    v = document[k]
    for field, value in list(v.items()):
        if field in doc:
            # XXX: manipulate real doc
            del doc[field]
    return subdoc


def doInc(storage, doc, subdoc, filter, document):
    """$inc operator"""
    k = '$inc'
    v = document[k]
    subdoc = doUpdateDocumentFields(doc, v, filter, incUpdater, subdoc)
    return subdoc


def doAddToSet(storage, doc, subdoc, filter, document):
    """$addToSet operator"""
    k = '$addToSet'
    v = document[k]
    for field, value in list(v.items()):
        nested_field_list = field.rsplit('.')
        if len(nested_field_list) == 1:
            if field not in doc:
                doc[field] = []
            # document should be a list append to it
            if isinstance(value, dict):
                if '$each' in value:
                    # append the list to the field
                    doc[field] += [
                        obj for obj in list(value['$each'])
                        if obj not in doc[field]]
                    continue
            if value not in doc[field]:
                doc[field].append(value)
            continue
        # push to array in a nested attribute
        else:
            # create nested attributes if they do not exist
            subdoc = doc
            for field in nested_field_list[:-1]:
                if field not in subdoc:
                    subdoc[field] = {}

                subdoc = subdoc[field]

            # we're pushing a list
            push_results = []
            if nested_field_list[-1] in subdoc:
                # if the list exists, then use that list
                push_results = subdoc[
                    nested_field_list[-1]]

            if isinstance(value, dict) and '$each' in value:
                push_results += [
                    obj for obj in list(value['$each'])
                    if obj not in push_results]
            elif value not in push_results:
                push_results.append(value)

            subdoc[nested_field_list[-1]] = push_results
    return subdoc


def doPull(storage, doc, subdoc, filter, document):
    """$addToSet operator"""
    k = '$pull'
    v = document[k]
    for field, value in list(v.items()):
        nested_field_list = field.rsplit('.')
        # nested fields includes a positional element
        # need to find that element
        if '$' in nested_field_list:
            if not subdoc:
                subdoc = getSubDoc(doc, filter, nested_field_list)

            # value should be a dictionary since we're pulling
            pull_results = []
            # and the last subdoc should be an array
            for obj in subdoc[nested_field_list[-1]]:
                if isinstance(obj, dict):
                    for pull_key, pull_value in list(value.items()):
                        if obj[pull_key] != pull_value:
                            pull_results.append(obj)
                    continue
                if obj != value:
                    pull_results.append(obj)

            # cannot write to doc directly as it doesn't save to
            # doc
            subdoc[nested_field_list[-1]] = pull_results
        else:
            arr = doc
            for field in nested_field_list:
                if field not in arr:
                    break
                arr = arr[field]
            if not isinstance(arr, list):
                continue

            if isinstance(value, dict):
                for idx, obj in enumerate(arr):
                    if m01.fake.finder.checkFilter(obj, value):
                        del arr[idx]
            else:
                for idx, obj in enumerate(arr):
                    if value == obj:
                        del arr[idx]
    return subdoc


def doPullAll(storage, doc, subdoc, filter, document):
    """$pullAll operator"""
    k = '$pullAll'
    v = document[k]
    for field, value in list(v.items()):
        nested_field_list = field.rsplit('.')
        if len(nested_field_list) == 1:
            if field in doc:
                arr = doc[field]
                doc[field] = [
                    obj for obj in arr if obj not in value]
            continue
        else:
            subdoc = doc
            for nested_field in nested_field_list[:-1]:
                if nested_field not in subdoc:
                    break
                subdoc = subdoc[nested_field]

            if nested_field_list[-1] in subdoc:
                arr = subdoc[nested_field_list[-1]]
                subdoc[nested_field_list[-1]] = [
                    obj for obj in arr if obj not in value]
    return subdoc


def doPush(storage, doc, subdoc, filter, document):
    """$push operator"""
    k = '$push'
    v = document[k]
    for field, value in list(v.items()):
        nested_field_list = field.rsplit('.')
        if len(nested_field_list) == 1:
            if field not in doc:
                doc[field] = []
            # document should be a list
            # append to it
            if isinstance(value, dict):
                if '$each' in value:
                    # append the list to the field
                    doc[field] += list(value['$each'])
                    continue
            doc[field].append(value)
            continue
        # nested fields includes a positional element
        # need to find that element
        elif '$' in nested_field_list:
            if not subdoc:
                subdoc = getSubDoc(doc, filter, nested_field_list)

            # we're pushing a list
            push_results = []
            if nested_field_list[-1] in subdoc:
                # if the list exists, then use that list
                push_results = subdoc[nested_field_list[-1]]

            if isinstance(value, dict):
                # check to see if we have the format
                # { '$each': [] }
                if '$each' in value:
                    push_results += list(value['$each'])
                else:
                    push_results.append(value)
            else:
                push_results.append(value)

            # cannot write to doc directly as it doesn't save to
            # doc
            subdoc[nested_field_list[-1]] = push_results
        # push to array in a nested attribute
        else:
            # create nested attributes if they do not exist
            subdoc = doc
            for field in nested_field_list[:-1]:
                if field not in subdoc:
                    subdoc[field] = {}
                subdoc = subdoc[field]

            # we're pushing a list
            push_results = []
            if nested_field_list[-1] in subdoc:
                # if the list exists, then use that list
                push_results = subdoc[nested_field_list[-1]]

            if isinstance(value, dict) and '$each' in value:
                push_results += list(value['$each'])
            else:
                push_results.append(value)

            subdoc[nested_field_list[-1]] = push_results
    return subdoc


def doReplace(storage, doc, filter, document, k):
    """Replace entire document"""
    for key in list(document.keys()):
        if key.startswith('$'):
            # can't mix modifiers with non-modifiers in
            # update
            raise ValueError('field names cannot start with $ [{}]'.format(k))
    _id = filter.get('_id', doc.get('_id'))
    doc.clear()
    if _id:
        doc['_id'] = _id
    data = dict((k, copy.deepcopy(v)) for k, v in list(document.items()))
    doc.update(data)
    if doc['_id'] != _id:
        raise pymongo.errors.OperationFailure(
            "The _id field cannot be changed from {0} to {1}".format(
                doc['_id'], _id))


OPERATORS = {
    '$set': doSet,
    '$unset': doUnSet,
    '$inc': doInc,
    '$addToSet': doAddToSet,
    '$pull': doPull,
    '$pullAll': doPullAll,
    '$push': doPush,
}


def doUpdateDocument(collection, storage, doc, filter, document):
    """Update one document (ignore upsert)"""
    first = True
    subdoc = None
    nModified = 0
    for k in list(document.keys()):
        nModified = 1
        operator = OPERATORS.get(k)
        if operator is not None:
            subdoc = operator(storage, doc, subdoc, filter, document)
        elif k == '$setOnInsert':
            # ignore optional upsert data on update operation
            pass
        else:
            if first:
                # replace first document if no $ operator is given
                doReplace(storage, doc, filter, document, k)
                break
            else:
                # can't mix modifiers with non-modifiers in update
                raise ValueError('Invalid modifier specified: {}'.format(k))
        first = False
    return nModified


def doSetOnInsert(doc, filter, document):
    """$setOnInsert operator"""
    k = '$setOnInsert'
    data = document.get(k)
    if data:
        doUpdateDocumentFields(doc, data, filter, setUpdater)


def doUpsertDocumentValues(storage, doc, filter, document):
    """Processes operators for upsert"""
    for k in list(document.keys()):
        operator = OPERATORS.get(k)
        if operator is not None:
            operator(storage, doc, None, filter, document)


def doUpsertDocument(collection, storage, filter, document):
    """Upsert document"""
    doc = dict((k, v) for k, v in list(document.items()) if not k.startswith("$"))
    _db = collection.database
    doc = _db._apply_incoming_manipulators(doc, collection)
    doc = _db._apply_incoming_copying_manipulators(doc, collection)
    doUpsertDocumentValues(storage, doc, filter, document)
    doSetOnInsert(doc, filter, document)
    # get _id after upsert, the _id is probably a part of $setOnInsert
    oid = doc.get('_id')
    if oid is None:
        oid = bson.ObjectId()
        doc[u'_id'] = oid
    storage[oid] = doc
    return oid


###############################################################################
#
# api

def doUpdateDocuments(collection, filter, document, upsert=False, multi=False):
    """Update documents"""
    nModified = 0
    upserted = None

    storage = collection.getDocumentStorage()
    docs = m01.fake.finder.getFilteredDocuments(collection, filter,
        multi=multi, deepcopy=False)
    if len(docs):
        counter = len(docs)
        # update existing docs
        for doc in docs:
            nModified += doUpdateDocument(collection, storage, doc, filter,
                document)
            if not multi:
                # no multi
                break
    elif upsert:
        counter = 1
        # upsert if no docs get found
        upserted = doUpsertDocument(collection, storage, filter, document)
    else:
        counter = 0

    # Add the updatedExisting field for compatibility.
    if nModified and not upserted:
        updatedExisting = True
    else:
        updatedExisting = False

    ok = 1.0
    res = {
        'n': counter,
        'ok': ok,
        'nModified': nModified,
        'updatedExisting': updatedExisting,
        }
    if upserted:
        res[u'upserted'] = upserted
    return res
