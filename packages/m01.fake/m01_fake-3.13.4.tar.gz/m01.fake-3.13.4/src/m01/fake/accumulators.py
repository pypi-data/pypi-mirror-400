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
Aggregation Group Accumulators

This module implements MongoDB aggregation group accumulators used in
the $group pipeline stage.

$Id$
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math

from m01.fake.expressions import resolve_expression


###############################################################################
#
# Accumulator Base

class Accumulator(object):
    """Base class for group accumulators."""
    
    def __init__(self, expr):
        self.expr = expr
    
    def initialize(self):
        """Initialize accumulator state."""
        raise NotImplementedError()
    
    def accumulate(self, state, doc, variables):
        """Accumulate a document into state."""
        raise NotImplementedError()
    
    def finalize(self, state):
        """Finalize and return result."""
        raise NotImplementedError()


###############################################################################
#
# Core Accumulators

class SumAccumulator(Accumulator):
    """$sum - Sum of numeric values."""
    
    def initialize(self):
        return 0
    
    def accumulate(self, state, doc, variables):
        val = resolve_expression(self.expr, doc, variables)
        if val is None:
            return state
        if isinstance(val, (int, float)):
            return state + val
        # $sum: 1 counts documents
        if self.expr == 1:
            return state + 1
        return state
    
    def finalize(self, state):
        return state


class AvgAccumulator(Accumulator):
    """$avg - Average of numeric values."""
    
    def initialize(self):
        return {'sum': 0, 'count': 0}
    
    def accumulate(self, state, doc, variables):
        val = resolve_expression(self.expr, doc, variables)
        if val is not None and isinstance(val, (int, float)):
            state['sum'] += val
            state['count'] += 1
        return state
    
    def finalize(self, state):
        if state['count'] == 0:
            return None
        return state['sum'] / state['count']


class MinAccumulator(Accumulator):
    """$min - Minimum value."""
    
    def initialize(self):
        return None
    
    def accumulate(self, state, doc, variables):
        val = resolve_expression(self.expr, doc, variables)
        if val is None:
            return state
        if state is None:
            return val
        return min(state, val)
    
    def finalize(self, state):
        return state


class MaxAccumulator(Accumulator):
    """$max - Maximum value."""
    
    def initialize(self):
        return None
    
    def accumulate(self, state, doc, variables):
        val = resolve_expression(self.expr, doc, variables)
        if val is None:
            return state
        if state is None:
            return val
        return max(state, val)
    
    def finalize(self, state):
        return state


class FirstAccumulator(Accumulator):
    """$first - First value in group."""
    
    def initialize(self):
        return {'value': None, 'set': False}
    
    def accumulate(self, state, doc, variables):
        if not state['set']:
            state['value'] = resolve_expression(self.expr, doc, variables)
            state['set'] = True
        return state
    
    def finalize(self, state):
        return state['value']


class LastAccumulator(Accumulator):
    """$last - Last value in group."""
    
    def initialize(self):
        return None
    
    def accumulate(self, state, doc, variables):
        return resolve_expression(self.expr, doc, variables)
    
    def finalize(self, state):
        return state


class PushAccumulator(Accumulator):
    """$push - Array of all values."""
    
    def initialize(self):
        return []
    
    def accumulate(self, state, doc, variables):
        val = resolve_expression(self.expr, doc, variables)
        state.append(val)
        return state
    
    def finalize(self, state):
        return state


class AddToSetAccumulator(Accumulator):
    """$addToSet - Array of unique values."""
    
    def initialize(self):
        return set()
    
    def accumulate(self, state, doc, variables):
        val = resolve_expression(self.expr, doc, variables)
        if val is not None:
            # Convert unhashable types to string for set
            try:
                state.add(val)
            except TypeError:
                # Unhashable (dict, list) - convert to string
                state.add(str(val))
        return state
    
    def finalize(self, state):
        return list(state)


class CountAccumulator(Accumulator):
    """$count - Count documents in group."""
    
    def initialize(self):
        return 0
    
    def accumulate(self, state, doc, variables):
        return state + 1
    
    def finalize(self, state):
        return state


###############################################################################
#
# Extended Accumulators

class MergeObjectsAccumulator(Accumulator):
    """$mergeObjects - Merge all objects in group."""
    
    def initialize(self):
        return {}
    
    def accumulate(self, state, doc, variables):
        val = resolve_expression(self.expr, doc, variables)
        if val is not None and isinstance(val, dict):
            state.update(val)
        return state
    
    def finalize(self, state):
        return state


class StdDevPopAccumulator(Accumulator):
    """$stdDevPop - Population standard deviation."""
    
    def initialize(self):
        return {'values': []}
    
    def accumulate(self, state, doc, variables):
        val = resolve_expression(self.expr, doc, variables)
        if val is not None and isinstance(val, (int, float)):
            state['values'].append(val)
        return state
    
    def finalize(self, state):
        values = state['values']
        if len(values) == 0:
            return None
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)


class StdDevSampAccumulator(Accumulator):
    """$stdDevSamp - Sample standard deviation."""
    
    def initialize(self):
        return {'values': []}
    
    def accumulate(self, state, doc, variables):
        val = resolve_expression(self.expr, doc, variables)
        if val is not None and isinstance(val, (int, float)):
            state['values'].append(val)
        return state
    
    def finalize(self, state):
        values = state['values']
        if len(values) < 2:
            return None
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)


class FirstNAccumulator(Accumulator):
    """$firstN - First N values in group."""
    
    def __init__(self, expr, n):
        super(FirstNAccumulator, self).__init__(expr)
        self.n = n
    
    def initialize(self):
        return []
    
    def accumulate(self, state, doc, variables):
        if len(state) < self.n:
            val = resolve_expression(self.expr, doc, variables)
            state.append(val)
        return state
    
    def finalize(self, state):
        return state


class LastNAccumulator(Accumulator):
    """$lastN - Last N values in group."""
    
    def __init__(self, expr, n):
        super(LastNAccumulator, self).__init__(expr)
        self.n = n
    
    def initialize(self):
        return []
    
    def accumulate(self, state, doc, variables):
        val = resolve_expression(self.expr, doc, variables)
        state.append(val)
        if len(state) > self.n:
            state.pop(0)
        return state
    
    def finalize(self, state):
        return state


class MaxNAccumulator(Accumulator):
    """$maxN - N maximum values in group."""
    
    def __init__(self, expr, n):
        super(MaxNAccumulator, self).__init__(expr)
        self.n = n
    
    def initialize(self):
        return []
    
    def accumulate(self, state, doc, variables):
        val = resolve_expression(self.expr, doc, variables)
        if val is not None:
            state.append(val)
        return state
    
    def finalize(self, state):
        state.sort(reverse=True)
        return state[:self.n]


class MinNAccumulator(Accumulator):
    """$minN - N minimum values in group."""
    
    def __init__(self, expr, n):
        super(MinNAccumulator, self).__init__(expr)
        self.n = n
    
    def initialize(self):
        return []
    
    def accumulate(self, state, doc, variables):
        val = resolve_expression(self.expr, doc, variables)
        if val is not None:
            state.append(val)
        return state
    
    def finalize(self, state):
        state.sort()
        return state[:self.n]


class TopAccumulator(Accumulator):
    """$top - Top element by sort order."""
    
    def __init__(self, output, sort_by):
        self.output = output
        self.sort_by = sort_by
    
    def initialize(self):
        return {'docs': []}
    
    def accumulate(self, state, doc, variables):
        state['docs'].append(doc)
        return state
    
    def finalize(self, state):
        if not state['docs']:
            return None
        
        # Sort documents
        docs = state['docs']
        for field, direction in reversed(list(self.sort_by.items())):
            docs.sort(
                key=lambda d: d.get(field) if d.get(field) is not None else '',
                reverse=(direction == -1)
            )
        
        return resolve_expression(self.output, docs[0], {})


class TopNAccumulator(Accumulator):
    """$topN - Top N elements by sort order."""
    
    def __init__(self, output, sort_by, n):
        self.output = output
        self.sort_by = sort_by
        self.n = n
    
    def initialize(self):
        return {'docs': []}
    
    def accumulate(self, state, doc, variables):
        state['docs'].append(doc)
        return state
    
    def finalize(self, state):
        if not state['docs']:
            return []
        
        # Sort documents
        docs = state['docs']
        for field, direction in reversed(list(self.sort_by.items())):
            docs.sort(
                key=lambda d: d.get(field) if d.get(field) is not None else '',
                reverse=(direction == -1)
            )
        
        return [resolve_expression(self.output, d, {}) for d in docs[:self.n]]


class BottomAccumulator(Accumulator):
    """$bottom - Bottom element by sort order."""
    
    def __init__(self, output, sort_by):
        self.output = output
        self.sort_by = sort_by
    
    def initialize(self):
        return {'docs': []}
    
    def accumulate(self, state, doc, variables):
        state['docs'].append(doc)
        return state
    
    def finalize(self, state):
        if not state['docs']:
            return None
        
        # Sort documents (reverse of top)
        docs = state['docs']
        for field, direction in reversed(list(self.sort_by.items())):
            docs.sort(
                key=lambda d: d.get(field) if d.get(field) is not None else '',
                reverse=(direction == 1)  # Reverse direction
            )
        
        return resolve_expression(self.output, docs[0], {})


class BottomNAccumulator(Accumulator):
    """$bottomN - Bottom N elements by sort order."""
    
    def __init__(self, output, sort_by, n):
        self.output = output
        self.sort_by = sort_by
        self.n = n
    
    def initialize(self):
        return {'docs': []}
    
    def accumulate(self, state, doc, variables):
        state['docs'].append(doc)
        return state
    
    def finalize(self, state):
        if not state['docs']:
            return []
        
        # Sort documents (reverse of topN)
        docs = state['docs']
        for field, direction in reversed(list(self.sort_by.items())):
            docs.sort(
                key=lambda d: d.get(field) if d.get(field) is not None else '',
                reverse=(direction == 1)  # Reverse direction
            )
        
        return [resolve_expression(self.output, d, {}) for d in docs[:self.n]]


###############################################################################
#
# Accumulator Factory

def create_accumulator(op, spec):
    """Create an accumulator instance from operator and specification.
    
    Args:
        op: The accumulator operator (e.g., '$sum', '$avg')
        spec: The accumulator specification
    
    Returns:
        Accumulator instance
    """
    if op == '$sum':
        return SumAccumulator(spec)
    elif op == '$avg':
        return AvgAccumulator(spec)
    elif op == '$min':
        return MinAccumulator(spec)
    elif op == '$max':
        return MaxAccumulator(spec)
    elif op == '$first':
        return FirstAccumulator(spec)
    elif op == '$last':
        return LastAccumulator(spec)
    elif op == '$push':
        return PushAccumulator(spec)
    elif op == '$addToSet':
        return AddToSetAccumulator(spec)
    elif op == '$count':
        return CountAccumulator(spec)
    elif op == '$mergeObjects':
        return MergeObjectsAccumulator(spec)
    elif op == '$stdDevPop':
        return StdDevPopAccumulator(spec)
    elif op == '$stdDevSamp':
        return StdDevSampAccumulator(spec)
    elif op == '$firstN':
        n = spec.get('n', 1) if isinstance(spec, dict) else 1
        input_expr = spec.get('input') if isinstance(spec, dict) else spec
        return FirstNAccumulator(input_expr, n)
    elif op == '$lastN':
        n = spec.get('n', 1) if isinstance(spec, dict) else 1
        input_expr = spec.get('input') if isinstance(spec, dict) else spec
        return LastNAccumulator(input_expr, n)
    elif op == '$maxN':
        n = spec.get('n', 1) if isinstance(spec, dict) else 1
        input_expr = spec.get('input') if isinstance(spec, dict) else spec
        return MaxNAccumulator(input_expr, n)
    elif op == '$minN':
        n = spec.get('n', 1) if isinstance(spec, dict) else 1
        input_expr = spec.get('input') if isinstance(spec, dict) else spec
        return MinNAccumulator(input_expr, n)
    elif op == '$top':
        output = spec.get('output')
        sort_by = spec.get('sortBy', {})
        return TopAccumulator(output, sort_by)
    elif op == '$topN':
        output = spec.get('output')
        sort_by = spec.get('sortBy', {})
        n = spec.get('n', 1)
        return TopNAccumulator(output, sort_by, n)
    elif op == '$bottom':
        output = spec.get('output')
        sort_by = spec.get('sortBy', {})
        return BottomAccumulator(output, sort_by)
    elif op == '$bottomN':
        output = spec.get('output')
        sort_by = spec.get('sortBy', {})
        n = spec.get('n', 1)
        return BottomNAccumulator(output, sort_by, n)
    else:
        raise NotImplementedError('Accumulator not implemented: %s' % op)


###############################################################################
#
# Accumulator Registry

ACCUMULATORS = {
    # Core accumulators
    '$sum': SumAccumulator,
    '$avg': AvgAccumulator,
    '$min': MinAccumulator,
    '$max': MaxAccumulator,
    '$first': FirstAccumulator,
    '$last': LastAccumulator,
    '$push': PushAccumulator,
    '$addToSet': AddToSetAccumulator,
    '$count': CountAccumulator,
    
    # Extended accumulators
    '$mergeObjects': MergeObjectsAccumulator,
    '$stdDevPop': StdDevPopAccumulator,
    '$stdDevSamp': StdDevSampAccumulator,
    '$firstN': FirstNAccumulator,
    '$lastN': LastNAccumulator,
    '$maxN': MaxNAccumulator,
    '$minN': MinNAccumulator,
    '$top': TopAccumulator,
    '$topN': TopNAccumulator,
    '$bottom': BottomAccumulator,
    '$bottomN': BottomNAccumulator,
}
