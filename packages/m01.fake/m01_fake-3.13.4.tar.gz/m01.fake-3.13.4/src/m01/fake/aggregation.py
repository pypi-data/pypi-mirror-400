##############################################################################
#
# Copyright (c) 2026 Zope Foundation and Contributors.
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
"""
MongoDB Aggregation Framework Implementation

This module implements the MongoDB aggregation pipeline for m01.fake.

$Id$
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import copy
import random
from functools import cmp_to_key

from six import string_types

import m01.fake.finder
from m01.fake.expressions import resolve_expression
from m01.fake.expressions import get_field_value
from m01.fake.accumulators import create_accumulator


###############################################################################
#
# Pipeline Executor

def execute_pipeline(collection, pipeline, **kwargs):
    """Execute an aggregation pipeline on a collection.
    
    Args:
        collection: The FakeCollection to aggregate
        pipeline: List of pipeline stage documents
        **kwargs: Additional options (session, etc.)
    
    Returns:
        Iterator over result documents
    """
    # Start with all documents from collection
    storage = collection.getDocumentStorage()
    docs = [copy.deepcopy(doc) for doc in storage.values()]
    
    # Process each stage
    for stage in pipeline:
        if not isinstance(stage, dict):
            raise ValueError('Pipeline stage must be a document')
        
        stage_name = list(stage.keys())[0]
        stage_spec = stage[stage_name]
        
        processor = PIPELINE_STAGES.get(stage_name)
        if processor is None:
            raise NotImplementedError(
                'Pipeline stage not implemented: %s' % stage_name)
        
        docs = processor(docs, stage_spec, collection)
    
    return iter(docs)


###############################################################################
#
# Pipeline Stages

def stage_match(docs, spec, collection):
    """$match - Filter documents.
    
    Uses the existing finder module for filtering.
    """
    return [doc for doc in docs 
            if m01.fake.finder.checkFilter(collection, doc, spec)]


def stage_project(docs, spec, collection):
    """$project - Reshape documents.
    
    Supports field inclusion/exclusion and expression evaluation.
    """
    result = []
    
    for doc in docs:
        projected = {}
        
        # Check for exclusion mode (all fields are 0 or false)
        has_inclusion = any(
            v for k, v in spec.items() 
            if k != '_id' and v not in (0, False)
        )
        
        # Handle _id field
        if '_id' in spec:
            if spec['_id'] in (1, True):
                projected['_id'] = doc.get('_id')
            elif spec['_id'] not in (0, False):
                # Expression
                projected['_id'] = resolve_expression(spec['_id'], doc)
        elif has_inclusion:
            # _id included by default in inclusion mode
            projected['_id'] = doc.get('_id')
        
        for field, value in spec.items():
            if field == '_id':
                continue
            
            if value in (1, True):
                # Include field
                field_value = get_field_value(doc, field)
                if field_value is not None:
                    _set_nested(projected, field, field_value)
            elif value in (0, False):
                # Exclude field (only in exclusion mode)
                if not has_inclusion:
                    # Copy all fields except excluded ones
                    if not projected:
                        projected = copy.deepcopy(doc)
                    _unset_nested(projected, field)
            else:
                # Expression
                projected[field] = resolve_expression(value, doc)
        
        # In exclusion mode, if no excludes processed yet, copy doc
        if not has_inclusion and not projected:
            projected = copy.deepcopy(doc)
            for field, value in spec.items():
                if value in (0, False) and field != '_id':
                    _unset_nested(projected, field)
        
        result.append(projected)
    
    return result


def stage_addFields(docs, spec, collection):
    """$addFields - Add new fields to documents.
    
    Similar to $project but preserves existing fields.
    """
    result = []
    
    for doc in docs:
        new_doc = copy.deepcopy(doc)
        
        for field, expr in spec.items():
            new_doc[field] = resolve_expression(expr, doc)
        
        result.append(new_doc)
    
    return result


def stage_set(docs, spec, collection):
    """$set - Alias for $addFields."""
    return stage_addFields(docs, spec, collection)


def stage_unset(docs, spec, collection):
    """$unset - Remove fields from documents."""
    # Normalize spec to list
    if isinstance(spec, string_types):
        fields = [spec]
    else:
        fields = spec
    
    result = []
    
    for doc in docs:
        new_doc = copy.deepcopy(doc)
        for field in fields:
            _unset_nested(new_doc, field)
        result.append(new_doc)
    
    return result


def stage_group(docs, spec, collection):
    """$group - Group documents by expression.
    
    Supports all standard accumulators.
    """
    groups = {}  # group_key -> {'_id': key, 'accumulators': {...}, 'states': {...}}
    
    # Parse accumulators
    accumulator_specs = {}
    for field, acc_spec in spec.items():
        if field == '_id':
            continue
        
        if isinstance(acc_spec, dict):
            # Find the accumulator operator
            for op, expr in acc_spec.items():
                if op.startswith('$'):
                    accumulator_specs[field] = create_accumulator(op, expr)
                    break
        else:
            raise ValueError('Invalid accumulator spec for field: %s' % field)
    
    # Group documents
    id_spec = spec.get('_id')
    
    for doc in docs:
        # Calculate group key
        if id_spec is None:
            group_key = None
        elif isinstance(id_spec, string_types) and id_spec.startswith('$'):
            group_key = get_field_value(doc, id_spec[1:])
        elif isinstance(id_spec, dict):
            # Compound key
            group_key = {}
            for k, v in id_spec.items():
                group_key[k] = resolve_expression(v, doc)
            group_key = tuple(sorted(group_key.items()))
        else:
            group_key = id_spec
        
        # Make key hashable
        hashable_key = _make_hashable(group_key)
        
        if hashable_key not in groups:
            groups[hashable_key] = {
                '_id': group_key if not isinstance(group_key, tuple) 
                       else dict(group_key),
                'states': {
                    field: acc.initialize() 
                    for field, acc in accumulator_specs.items()
                }
            }
        
        # Accumulate - provide ROOT and CURRENT variables for $$ROOT support
        variables = {'ROOT': doc, 'CURRENT': doc}
        for field, acc in accumulator_specs.items():
            groups[hashable_key]['states'][field] = acc.accumulate(
                groups[hashable_key]['states'][field], doc, variables
            )
    
    # Finalize and build result documents
    result = []
    for group_key, group_data in groups.items():
        result_doc = {'_id': group_data['_id']}
        
        for field, acc in accumulator_specs.items():
            result_doc[field] = acc.finalize(group_data['states'][field])
        
        result.append(result_doc)
    
    return result


def stage_sort(docs, spec, collection):
    """$sort - Sort documents.
    
    Uses the existing doSort from finder module.
    """
    if not docs:
        return docs
    
    return sorted(docs, key=cmp_to_key(m01.fake.finder.doSort(spec)))


def stage_limit(docs, spec, collection):
    """$limit - Limit number of documents."""
    return docs[:spec]


def stage_skip(docs, spec, collection):
    """$skip - Skip documents."""
    return docs[spec:]


def stage_count(docs, spec, collection):
    """$count - Count documents and return as field."""
    return [{spec: len(docs)}]


def stage_unwind(docs, spec, collection):
    """$unwind - Deconstruct array field.
    
    Creates one document per array element.
    """
    # Normalize spec
    if isinstance(spec, string_types):
        path = spec
        preserve_null = False
        include_index = None
    else:
        path = spec.get('path')
        preserve_null = spec.get('preserveNullAndEmptyArrays', False)
        include_index = spec.get('includeArrayIndex')
    
    if not path.startswith('$'):
        raise ValueError('$unwind path must start with $')
    
    field_path = path[1:]
    result = []
    
    for doc in docs:
        array_value = get_field_value(doc, field_path)
        
        if array_value is None or array_value == []:
            if preserve_null:
                new_doc = copy.deepcopy(doc)
                if array_value is None:
                    _set_nested(new_doc, field_path, None)
                if include_index:
                    new_doc[include_index] = None
                result.append(new_doc)
            continue
        
        if not isinstance(array_value, list):
            # Treat non-array as single element
            array_value = [array_value]
        
        for idx, element in enumerate(array_value):
            new_doc = copy.deepcopy(doc)
            _set_nested(new_doc, field_path, element)
            if include_index:
                new_doc[include_index] = idx
            result.append(new_doc)
    
    return result


def stage_sortByCount(docs, spec, collection):
    """$sortByCount - Group by value, count, and sort descending.
    
    Equivalent to: $group + $sort
    """
    # First group
    grouped = stage_group(docs, {
        '_id': spec,
        'count': {'$sum': 1}
    }, collection)
    
    # Then sort by count descending
    return stage_sort(grouped, {'count': -1}, collection)


def stage_sample(docs, spec, collection):
    """$sample - Random sample of documents."""
    size = spec.get('size', 1)
    if len(docs) <= size:
        return docs
    return random.sample(docs, size)


def stage_replaceRoot(docs, spec, collection):
    """$replaceRoot - Replace document with embedded document."""
    new_root = spec.get('newRoot')
    result = []
    
    for doc in docs:
        new_doc = resolve_expression(new_root, doc)
        if new_doc is not None and isinstance(new_doc, dict):
            result.append(new_doc)
    
    return result


def stage_replaceWith(docs, spec, collection):
    """$replaceWith - Alias for $replaceRoot."""
    return stage_replaceRoot(docs, {'newRoot': spec}, collection)


def stage_lookup(docs, spec, collection):
    """$lookup - Join with another collection.
    
    Supports basic equality match join.
    """
    from_collection_name = spec.get('from')
    local_field = spec.get('localField')
    foreign_field = spec.get('foreignField')
    as_field = spec.get('as')
    
    # Get the foreign collection
    database = collection.database
    foreign_collection = database[from_collection_name]
    foreign_storage = foreign_collection.getDocumentStorage()
    foreign_docs = list(foreign_storage.values())
    
    result = []
    
    for doc in docs:
        local_value = get_field_value(doc, local_field)
        
        # Find matching foreign documents
        matches = []
        for foreign_doc in foreign_docs:
            foreign_value = get_field_value(foreign_doc, foreign_field)
            
            # Handle array values
            if isinstance(local_value, list):
                if foreign_value in local_value:
                    matches.append(copy.deepcopy(foreign_doc))
            elif isinstance(foreign_value, list):
                if local_value in foreign_value:
                    matches.append(copy.deepcopy(foreign_doc))
            elif local_value == foreign_value:
                matches.append(copy.deepcopy(foreign_doc))
        
        new_doc = copy.deepcopy(doc)
        new_doc[as_field] = matches
        result.append(new_doc)
    
    return result


def stage_facet(docs, spec, collection):
    """$facet - Process multiple aggregation pipelines.
    
    Returns a single document with results from each pipeline.
    """
    result_doc = {}
    
    for facet_name, pipeline in spec.items():
        # Execute each sub-pipeline on the same input documents
        facet_docs = copy.deepcopy(docs)
        
        for stage in pipeline:
            stage_name = list(stage.keys())[0]
            stage_spec = stage[stage_name]
            
            processor = PIPELINE_STAGES.get(stage_name)
            if processor is None:
                raise NotImplementedError(
                    'Pipeline stage not implemented in $facet: %s' % stage_name)
            
            facet_docs = processor(facet_docs, stage_spec, collection)
        
        result_doc[facet_name] = facet_docs
    
    return [result_doc]


def stage_bucket(docs, spec, collection):
    """$bucket - Categorize documents into buckets."""
    group_by = spec.get('groupBy')
    boundaries = spec.get('boundaries')
    default_bucket = spec.get('default')
    output = spec.get('output', {'count': {'$sum': 1}})
    
    # Initialize buckets
    buckets = {}
    for i, bound in enumerate(boundaries[:-1]):
        buckets[bound] = {'_id': bound, 'docs': []}
    
    if default_bucket is not None:
        buckets[default_bucket] = {'_id': default_bucket, 'docs': []}
    
    # Categorize documents
    for doc in docs:
        value = resolve_expression(group_by, doc)
        
        # Find bucket
        bucket_key = None
        for i in range(len(boundaries) - 1):
            if boundaries[i] <= value < boundaries[i + 1]:
                bucket_key = boundaries[i]
                break
        
        if bucket_key is None:
            if default_bucket is not None:
                bucket_key = default_bucket
            else:
                continue  # Skip document
        
        buckets[bucket_key]['docs'].append(doc)
    
    # Calculate output for each bucket
    result = []
    for bucket_id, bucket_data in buckets.items():
        if not bucket_data['docs'] and bucket_id != default_bucket:
            continue  # Skip empty buckets (except default)
        
        # Build group spec for this bucket
        group_spec = {'_id': None}
        group_spec.update(output)
        
        bucket_result = stage_group(bucket_data['docs'], group_spec, collection)
        
        if bucket_result:
            result_doc = bucket_result[0]
            result_doc['_id'] = bucket_id
            result.append(result_doc)
    
    return result


def stage_out(docs, spec, collection):
    """$out - Write results to a collection.
    
    Replaces the output collection entirely.
    """
    if isinstance(spec, string_types):
        output_collection_name = spec
    else:
        output_collection_name = spec.get('coll')
    
    database = collection.database
    output_collection = database[output_collection_name]
    
    # Clear existing documents
    storage = output_collection.getDocumentStorage()
    storage.clear()
    
    # Insert new documents
    for doc in docs:
        output_collection.insert_one(copy.deepcopy(doc))
    
    # $out returns no documents
    return []


def stage_merge(docs, spec, collection):
    """$merge - Merge results into a collection.
    
    More flexible than $out - can update, replace, or insert.
    """
    if isinstance(spec, string_types):
        into = spec
        on = '_id'
        when_matched = 'merge'
        when_not_matched = 'insert'
    else:
        into = spec.get('into')
        on = spec.get('on', '_id')
        when_matched = spec.get('whenMatched', 'merge')
        when_not_matched = spec.get('whenNotMatched', 'insert')
    
    if isinstance(into, dict):
        output_collection_name = into.get('coll')
    else:
        output_collection_name = into
    
    database = collection.database
    output_collection = database[output_collection_name]
    
    for doc in docs:
        # Find existing document
        if isinstance(on, list):
            filter_doc = {field: doc.get(field) for field in on}
        else:
            filter_doc = {on: doc.get(on)}
        
        existing = output_collection.find_one(filter_doc)
        
        if existing:
            # Handle match
            if when_matched == 'replace':
                output_collection.replace_one(filter_doc, doc)
            elif when_matched == 'merge':
                merged = copy.deepcopy(existing)
                merged.update(doc)
                output_collection.replace_one(filter_doc, merged)
            elif when_matched == 'keepExisting':
                pass  # Do nothing
            elif when_matched == 'fail':
                raise Exception('$merge: document matched and whenMatched=fail')
        else:
            # Handle no match
            if when_not_matched == 'insert':
                output_collection.insert_one(copy.deepcopy(doc))
            elif when_not_matched == 'discard':
                pass  # Do nothing
            elif when_not_matched == 'fail':
                raise Exception('$merge: document not matched and whenNotMatched=fail')
    
    # $merge returns no documents
    return []


###############################################################################
#
# Helper Functions

def _set_nested(doc, path, value):
    """Set a nested field value using dot notation."""
    parts = path.split('.')
    current = doc
    
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    
    current[parts[-1]] = value


def _unset_nested(doc, path):
    """Remove a nested field using dot notation."""
    parts = path.split('.')
    current = doc
    
    for part in parts[:-1]:
        if part not in current:
            return
        current = current[part]
    
    if parts[-1] in current:
        del current[parts[-1]]


def _make_hashable(value):
    """Convert a value to a hashable type for use as dict key."""
    if value is None:
        return None
    if isinstance(value, dict):
        return tuple(sorted((k, _make_hashable(v)) for k, v in value.items()))
    if isinstance(value, list):
        return tuple(_make_hashable(v) for v in value)
    return value


###############################################################################
#
# Pipeline Stage Registry

PIPELINE_STAGES = {
    # Core stages
    '$match': stage_match,
    '$project': stage_project,
    '$group': stage_group,
    '$sort': stage_sort,
    '$limit': stage_limit,
    '$skip': stage_skip,
    '$count': stage_count,
    '$unwind': stage_unwind,
    
    # Extended stages
    '$addFields': stage_addFields,
    '$set': stage_set,
    '$unset': stage_unset,
    '$replaceRoot': stage_replaceRoot,
    '$replaceWith': stage_replaceWith,
    '$lookup': stage_lookup,
    '$sortByCount': stage_sortByCount,
    '$sample': stage_sample,
    '$facet': stage_facet,
    '$bucket': stage_bucket,
    '$out': stage_out,
    '$merge': stage_merge,
}
