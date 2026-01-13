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
Aggregation Expression Operators

This module implements MongoDB aggregation expression operators used in
$project, $addFields, $group, and other pipeline stages.

$Id$
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import math
import re

import bson
from six import string_types

from sentinels import NOTHING


###############################################################################
#
# Helper Functions

def get_field_value(doc, path):
    """Get nested field value from document using dot notation.
    
    Args:
        doc: The document to extract value from
        path: Field path (e.g., 'user.name' or 'items.0.price')
    
    Returns:
        The field value or NOTHING if not found
    """
    if doc is None:
        return NOTHING
    
    if not path:
        return doc
    
    parts = path.split('.')
    value = doc
    
    for part in parts:
        if isinstance(value, dict):
            value = value.get(part, NOTHING)
        elif isinstance(value, (list, tuple)):
            # Try numeric index
            try:
                idx = int(part)
                if 0 <= idx < len(value):
                    value = value[idx]
                else:
                    return NOTHING
            except ValueError:
                # Non-numeric key on array - collect from all elements
                results = []
                for item in value:
                    if isinstance(item, dict):
                        v = item.get(part, NOTHING)
                        if v is not NOTHING:
                            results.append(v)
                if results:
                    value = results
                else:
                    return NOTHING
        else:
            return NOTHING
        
        if value is NOTHING:
            return NOTHING
    
    return value


def resolve_expression(expr, doc, variables=None):
    """Resolve an aggregation expression to a value.
    
    Args:
        expr: The expression to resolve (field path, literal, or operator)
        doc: The current document
        variables: Optional dict of variables ($$ROOT, $$NOW, etc.)
    
    Returns:
        The resolved value
    """
    if variables is None:
        variables = {
            'ROOT': doc,
            'CURRENT': doc,
            'NOW': datetime.datetime.utcnow(),
        }
    
    if expr is None:
        return None
    
    # Field path: $fieldName or $nested.field
    if isinstance(expr, string_types):
        if expr.startswith('$$'):
            # System variable
            var_name = expr[2:]
            if '.' in var_name:
                parts = var_name.split('.', 1)
                var_value = variables.get(parts[0], NOTHING)
                if var_value is NOTHING:
                    return None
                return get_field_value(var_value, parts[1])
            return variables.get(var_name)
        elif expr.startswith('$'):
            # Field path
            value = get_field_value(doc, expr[1:])
            return None if value is NOTHING else value
        else:
            # Literal string
            return expr
    
    # Operator expression: {'$operator': args}
    if isinstance(expr, dict):
        # Check for $literal first
        if '$literal' in expr:
            return expr['$literal']
        
        # Find operator
        for key, value in expr.items():
            if key.startswith('$'):
                op_func = EXPRESSION_OPERATORS.get(key)
                if op_func:
                    return op_func(value, doc, variables)
                else:
                    raise NotImplementedError(
                        'Expression operator not implemented: %s' % key)
        
        # No operator - treat as literal document
        # But resolve any expressions within
        result = {}
        for key, value in expr.items():
            result[key] = resolve_expression(value, doc, variables)
        return result
    
    # List - resolve each element
    if isinstance(expr, (list, tuple)):
        return [resolve_expression(e, doc, variables) for e in expr]
    
    # Literal value
    return expr


###############################################################################
#
# Arithmetic Operators

def op_add(args, doc, variables):
    """$add - Add numbers or dates."""
    values = [resolve_expression(a, doc, variables) for a in args]
    
    # Check for date addition
    date_val = None
    number_sum = 0
    for v in values:
        if isinstance(v, datetime.datetime):
            date_val = v
        elif isinstance(v, (int, float)):
            number_sum += v
        elif v is None:
            return None
    
    if date_val:
        # Add milliseconds to date
        return date_val + datetime.timedelta(milliseconds=number_sum)
    
    return number_sum


def op_subtract(args, doc, variables):
    """$subtract - Subtract numbers or dates."""
    if len(args) != 2:
        raise ValueError('$subtract requires exactly 2 arguments')
    
    val1 = resolve_expression(args[0], doc, variables)
    val2 = resolve_expression(args[1], doc, variables)
    
    if val1 is None or val2 is None:
        return None
    
    # Date subtraction
    if isinstance(val1, datetime.datetime) and isinstance(val2, datetime.datetime):
        delta = val1 - val2
        return int(delta.total_seconds() * 1000)  # Return milliseconds
    elif isinstance(val1, datetime.datetime):
        return val1 - datetime.timedelta(milliseconds=val2)
    
    return val1 - val2


def op_multiply(args, doc, variables):
    """$multiply - Multiply numbers."""
    result = 1
    for arg in args:
        val = resolve_expression(arg, doc, variables)
        if val is None:
            return None
        result *= val
    return result


def op_divide(args, doc, variables):
    """$divide - Divide numbers."""
    if len(args) != 2:
        raise ValueError('$divide requires exactly 2 arguments')
    
    val1 = resolve_expression(args[0], doc, variables)
    val2 = resolve_expression(args[1], doc, variables)
    
    if val1 is None or val2 is None:
        return None
    if val2 == 0:
        raise ValueError('$divide: division by zero')
    
    return val1 / val2


def op_mod(args, doc, variables):
    """$mod - Modulo operation."""
    if len(args) != 2:
        raise ValueError('$mod requires exactly 2 arguments')
    
    val1 = resolve_expression(args[0], doc, variables)
    val2 = resolve_expression(args[1], doc, variables)
    
    if val1 is None or val2 is None:
        return None
    
    return val1 % val2


def op_abs(args, doc, variables):
    """$abs - Absolute value."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    return abs(val)


def op_ceil(args, doc, variables):
    """$ceil - Ceiling."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    return int(math.ceil(val))


def op_floor(args, doc, variables):
    """$floor - Floor."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    return int(math.floor(val))


def op_round(args, doc, variables):
    """$round - Round to specified decimal places."""
    if isinstance(args, list):
        val = resolve_expression(args[0], doc, variables)
        places = resolve_expression(args[1], doc, variables) if len(args) > 1 else 0
    else:
        val = resolve_expression(args, doc, variables)
        places = 0
    
    if val is None:
        return None
    
    return round(val, places)


def op_trunc(args, doc, variables):
    """$trunc - Truncate to integer or decimal places."""
    if isinstance(args, list):
        val = resolve_expression(args[0], doc, variables)
        places = resolve_expression(args[1], doc, variables) if len(args) > 1 else 0
    else:
        val = resolve_expression(args, doc, variables)
        places = 0
    
    if val is None:
        return None
    
    if places == 0:
        return int(val)
    
    factor = 10 ** places
    return int(val * factor) / factor


def op_sqrt(args, doc, variables):
    """$sqrt - Square root."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    if val < 0:
        raise ValueError('$sqrt: cannot take square root of negative number')
    return math.sqrt(val)


def op_pow(args, doc, variables):
    """$pow - Raise to power."""
    if len(args) != 2:
        raise ValueError('$pow requires exactly 2 arguments')
    
    base = resolve_expression(args[0], doc, variables)
    exp = resolve_expression(args[1], doc, variables)
    
    if base is None or exp is None:
        return None
    
    return math.pow(base, exp)


def op_exp(args, doc, variables):
    """$exp - Raise e to power."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    return math.exp(val)


def op_ln(args, doc, variables):
    """$ln - Natural logarithm."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    if val <= 0:
        raise ValueError('$ln: argument must be positive')
    return math.log(val)


def op_log(args, doc, variables):
    """$log - Logarithm with specified base."""
    if len(args) != 2:
        raise ValueError('$log requires exactly 2 arguments')
    
    val = resolve_expression(args[0], doc, variables)
    base = resolve_expression(args[1], doc, variables)
    
    if val is None or base is None:
        return None
    
    return math.log(val, base)


def op_log10(args, doc, variables):
    """$log10 - Base-10 logarithm."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    if val <= 0:
        raise ValueError('$log10: argument must be positive')
    return math.log10(val)


###############################################################################
#
# Comparison Operators

def op_cmp(args, doc, variables):
    """$cmp - Compare two values."""
    if len(args) != 2:
        raise ValueError('$cmp requires exactly 2 arguments')
    
    val1 = resolve_expression(args[0], doc, variables)
    val2 = resolve_expression(args[1], doc, variables)
    
    if val1 == val2:
        return 0
    elif val1 is None:
        return -1
    elif val2 is None:
        return 1
    elif val1 < val2:
        return -1
    else:
        return 1


def op_eq(args, doc, variables):
    """$eq - Equal."""
    if len(args) != 2:
        raise ValueError('$eq requires exactly 2 arguments')
    
    val1 = resolve_expression(args[0], doc, variables)
    val2 = resolve_expression(args[1], doc, variables)
    
    return val1 == val2


def op_ne(args, doc, variables):
    """$ne - Not equal."""
    if len(args) != 2:
        raise ValueError('$ne requires exactly 2 arguments')
    
    val1 = resolve_expression(args[0], doc, variables)
    val2 = resolve_expression(args[1], doc, variables)
    
    return val1 != val2


def op_gt(args, doc, variables):
    """$gt - Greater than."""
    if len(args) != 2:
        raise ValueError('$gt requires exactly 2 arguments')
    
    val1 = resolve_expression(args[0], doc, variables)
    val2 = resolve_expression(args[1], doc, variables)
    
    if val1 is None or val2 is None:
        return False
    
    return val1 > val2


def op_gte(args, doc, variables):
    """$gte - Greater than or equal."""
    if len(args) != 2:
        raise ValueError('$gte requires exactly 2 arguments')
    
    val1 = resolve_expression(args[0], doc, variables)
    val2 = resolve_expression(args[1], doc, variables)
    
    if val1 is None or val2 is None:
        return val1 == val2
    
    return val1 >= val2


def op_lt(args, doc, variables):
    """$lt - Less than."""
    if len(args) != 2:
        raise ValueError('$lt requires exactly 2 arguments')
    
    val1 = resolve_expression(args[0], doc, variables)
    val2 = resolve_expression(args[1], doc, variables)
    
    if val1 is None or val2 is None:
        return False
    
    return val1 < val2


def op_lte(args, doc, variables):
    """$lte - Less than or equal."""
    if len(args) != 2:
        raise ValueError('$lte requires exactly 2 arguments')
    
    val1 = resolve_expression(args[0], doc, variables)
    val2 = resolve_expression(args[1], doc, variables)
    
    if val1 is None or val2 is None:
        return val1 == val2
    
    return val1 <= val2


###############################################################################
#
# Boolean Operators

def op_and(args, doc, variables):
    """$and - Logical AND."""
    for arg in args:
        val = resolve_expression(arg, doc, variables)
        if not val:
            return False
    return True


def op_or(args, doc, variables):
    """$or - Logical OR."""
    for arg in args:
        val = resolve_expression(arg, doc, variables)
        if val:
            return True
    return False


def op_not(args, doc, variables):
    """$not - Logical NOT."""
    if isinstance(args, list):
        val = resolve_expression(args[0], doc, variables)
    else:
        val = resolve_expression(args, doc, variables)
    return not val


###############################################################################
#
# Conditional Operators

def op_cond(args, doc, variables):
    """$cond - Conditional expression (if-then-else)."""
    if isinstance(args, list):
        if len(args) != 3:
            raise ValueError('$cond array form requires 3 arguments')
        condition = resolve_expression(args[0], doc, variables)
        then_val = args[1]
        else_val = args[2]
    elif isinstance(args, dict):
        condition = resolve_expression(args.get('if'), doc, variables)
        then_val = args.get('then')
        else_val = args.get('else')
    else:
        raise ValueError('$cond requires array or object')
    
    if condition:
        return resolve_expression(then_val, doc, variables)
    else:
        return resolve_expression(else_val, doc, variables)


def op_ifNull(args, doc, variables):
    """$ifNull - Return first non-null value."""
    if len(args) < 2:
        raise ValueError('$ifNull requires at least 2 arguments')
    
    for arg in args[:-1]:
        val = resolve_expression(arg, doc, variables)
        if val is not None:
            return val
    
    # Return last argument (replacement value)
    return resolve_expression(args[-1], doc, variables)


def op_switch(args, doc, variables):
    """$switch - Switch/case expression."""
    branches = args.get('branches', [])
    default = args.get('default')
    
    for branch in branches:
        case = resolve_expression(branch.get('case'), doc, variables)
        if case:
            return resolve_expression(branch.get('then'), doc, variables)
    
    if default is not None:
        return resolve_expression(default, doc, variables)
    
    raise ValueError('$switch: no matching branch and no default')


###############################################################################
#
# Type Operators

def op_type(args, doc, variables):
    """$type - Return BSON type string."""
    val = resolve_expression(args, doc, variables)
    
    if val is None:
        return 'null'
    elif isinstance(val, bool):
        return 'bool'
    elif isinstance(val, int):
        return 'int'
    elif isinstance(val, float):
        return 'double'
    elif isinstance(val, string_types):
        return 'string'
    elif isinstance(val, datetime.datetime):
        return 'date'
    elif isinstance(val, bson.ObjectId):
        return 'objectId'
    elif isinstance(val, list):
        return 'array'
    elif isinstance(val, dict):
        return 'object'
    elif isinstance(val, bson.Binary):
        return 'binData'
    elif isinstance(val, bson.Regex):
        return 'regex'
    else:
        return 'unknown'


def op_toBool(args, doc, variables):
    """$toBool - Convert to boolean."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    return bool(val)


def op_toInt(args, doc, variables):
    """$toInt - Convert to 32-bit integer."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    return int(val)


def op_toLong(args, doc, variables):
    """$toLong - Convert to 64-bit integer."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    return int(val)


def op_toDouble(args, doc, variables):
    """$toDouble - Convert to double."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    return float(val)


def op_toString(args, doc, variables):
    """$toString - Convert to string."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    if isinstance(val, datetime.datetime):
        return val.isoformat()
    return str(val)


def op_toDate(args, doc, variables):
    """$toDate - Convert to date."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    if isinstance(val, datetime.datetime):
        return val
    if isinstance(val, (int, float)):
        # Milliseconds since epoch
        return datetime.datetime.utcfromtimestamp(val / 1000.0)
    if isinstance(val, string_types):
        # ISO format
        return datetime.datetime.fromisoformat(val.replace('Z', '+00:00'))
    raise ValueError('$toDate: cannot convert value')


def op_toObjectId(args, doc, variables):
    """$toObjectId - Convert to ObjectId."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    if isinstance(val, bson.ObjectId):
        return val
    return bson.ObjectId(val)


def op_convert(args, doc, variables):
    """$convert - Convert value to specified type."""
    input_val = resolve_expression(args.get('input'), doc, variables)
    to_type = args.get('to')
    on_error = args.get('onError')
    on_null = args.get('onNull')
    
    if input_val is None:
        if on_null is not None:
            return resolve_expression(on_null, doc, variables)
        return None
    
    try:
        if to_type == 'bool':
            return bool(input_val)
        elif to_type == 'int':
            return int(input_val)
        elif to_type == 'long':
            return int(input_val)
        elif to_type == 'double':
            return float(input_val)
        elif to_type == 'string':
            return str(input_val)
        elif to_type == 'objectId':
            return bson.ObjectId(input_val)
        elif to_type == 'date':
            return op_toDate(input_val, doc, variables)
        else:
            raise ValueError('$convert: unknown type %s' % to_type)
    except Exception:
        if on_error is not None:
            return resolve_expression(on_error, doc, variables)
        raise


###############################################################################
#
# Date Operators

def op_dateToString(args, doc, variables):
    """$dateToString - Format date as string."""
    if isinstance(args, dict):
        date = resolve_expression(args.get('date'), doc, variables)
        fmt = args.get('format', '%Y-%m-%dT%H:%M:%S.%fZ')
        timezone = args.get('timezone')
        on_null = args.get('onNull')
    else:
        date = resolve_expression(args, doc, variables)
        fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
        on_null = None
    
    if date is None:
        if on_null is not None:
            return resolve_expression(on_null, doc, variables)
        return None
    
    # Convert MongoDB format to Python strftime format
    # We do manual replacement to support both Python 2 and 3
    result = fmt
    result = result.replace('%Y', '%04d' % date.year)
    result = result.replace('%m', '%02d' % date.month)
    result = result.replace('%d', '%02d' % date.day)
    result = result.replace('%H', '%02d' % date.hour)
    result = result.replace('%M', '%02d' % date.minute)
    result = result.replace('%S', '%02d' % date.second)
    result = result.replace('%L', '%03d' % (date.microsecond // 1000))
    result = result.replace('%j', '%03d' % date.timetuple().tm_yday)
    result = result.replace('%w', '%d' % date.weekday())
    
    # ISO week calculation (compatible with Python 2)
    if '%V' in result or '%U' in result:
        iso_calendar = date.isocalendar()
        result = result.replace('%V', '%02d' % iso_calendar[1])
        # %U is week number with Sunday as first day
        # Calculate manually for Python 2 compatibility
        jan1 = date.replace(month=1, day=1)
        week_num = (date.timetuple().tm_yday + jan1.weekday()) // 7
        result = result.replace('%U', '%02d' % week_num)
    
    return result


def op_dateFromString(args, doc, variables):
    """$dateFromString - Parse string to date."""
    date_string = resolve_expression(args.get('dateString'), doc, variables)
    fmt = args.get('format')
    on_error = args.get('onError')
    on_null = args.get('onNull')
    
    if date_string is None:
        if on_null is not None:
            return resolve_expression(on_null, doc, variables)
        return None
    
    try:
        if fmt:
            return datetime.datetime.strptime(date_string, fmt)
        else:
            # ISO format
            return datetime.datetime.fromisoformat(
                date_string.replace('Z', '+00:00'))
    except Exception:
        if on_error is not None:
            return resolve_expression(on_error, doc, variables)
        raise


def op_year(args, doc, variables):
    """$year - Extract year from date."""
    date = resolve_expression(args, doc, variables)
    if date is None:
        return None
    return date.year


def op_month(args, doc, variables):
    """$month - Extract month from date (1-12)."""
    date = resolve_expression(args, doc, variables)
    if date is None:
        return None
    return date.month


def op_dayOfMonth(args, doc, variables):
    """$dayOfMonth - Extract day of month from date (1-31)."""
    date = resolve_expression(args, doc, variables)
    if date is None:
        return None
    return date.day


def op_dayOfWeek(args, doc, variables):
    """$dayOfWeek - Extract day of week from date (1=Sunday, 7=Saturday)."""
    date = resolve_expression(args, doc, variables)
    if date is None:
        return None
    # Python: Monday=0, Sunday=6
    # MongoDB: Sunday=1, Saturday=7
    return (date.weekday() + 2) % 7 or 7


def op_dayOfYear(args, doc, variables):
    """$dayOfYear - Extract day of year from date (1-366)."""
    date = resolve_expression(args, doc, variables)
    if date is None:
        return None
    return date.timetuple().tm_yday


def op_hour(args, doc, variables):
    """$hour - Extract hour from date (0-23)."""
    date = resolve_expression(args, doc, variables)
    if date is None:
        return None
    return date.hour


def op_minute(args, doc, variables):
    """$minute - Extract minute from date (0-59)."""
    date = resolve_expression(args, doc, variables)
    if date is None:
        return None
    return date.minute


def op_second(args, doc, variables):
    """$second - Extract second from date (0-59)."""
    date = resolve_expression(args, doc, variables)
    if date is None:
        return None
    return date.second


def op_millisecond(args, doc, variables):
    """$millisecond - Extract millisecond from date (0-999)."""
    date = resolve_expression(args, doc, variables)
    if date is None:
        return None
    return date.microsecond // 1000


def op_week(args, doc, variables):
    """$week - Extract week of year (0-53)."""
    date = resolve_expression(args, doc, variables)
    if date is None:
        return None
    return int(date.strftime('%U'))


def op_isoWeek(args, doc, variables):
    """$isoWeek - Extract ISO week of year (1-53)."""
    date = resolve_expression(args, doc, variables)
    if date is None:
        return None
    return date.isocalendar()[1]


def op_isoWeekYear(args, doc, variables):
    """$isoWeekYear - Extract ISO week year."""
    date = resolve_expression(args, doc, variables)
    if date is None:
        return None
    return date.isocalendar()[0]


def op_isoDayOfWeek(args, doc, variables):
    """$isoDayOfWeek - Extract ISO day of week (1=Monday, 7=Sunday)."""
    date = resolve_expression(args, doc, variables)
    if date is None:
        return None
    return date.isoweekday()


###############################################################################
#
# String Operators

def op_concat(args, doc, variables):
    """$concat - Concatenate strings."""
    result = ''
    for arg in args:
        val = resolve_expression(arg, doc, variables)
        if val is None:
            return None
        result += str(val)
    return result


def op_substr(args, doc, variables):
    """$substr - Substring (deprecated, use $substrBytes)."""
    if len(args) != 3:
        raise ValueError('$substr requires 3 arguments')
    
    string = resolve_expression(args[0], doc, variables)
    start = resolve_expression(args[1], doc, variables)
    length = resolve_expression(args[2], doc, variables)
    
    if string is None:
        return ''
    
    return string[start:start + length]


def op_substrBytes(args, doc, variables):
    """$substrBytes - Substring by byte index."""
    return op_substr(args, doc, variables)


def op_substrCP(args, doc, variables):
    """$substrCP - Substring by code point index."""
    return op_substr(args, doc, variables)


def op_toLower(args, doc, variables):
    """$toLower - Convert to lowercase."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return ''
    return str(val).lower()


def op_toUpper(args, doc, variables):
    """$toUpper - Convert to uppercase."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return ''
    return str(val).upper()


def op_trim(args, doc, variables):
    """$trim - Trim whitespace or specified characters."""
    if isinstance(args, dict):
        input_val = resolve_expression(args.get('input'), doc, variables)
        chars = args.get('chars', ' ')
    else:
        input_val = resolve_expression(args, doc, variables)
        chars = ' '
    
    if input_val is None:
        return None
    
    return str(input_val).strip(chars)


def op_ltrim(args, doc, variables):
    """$ltrim - Trim from left."""
    if isinstance(args, dict):
        input_val = resolve_expression(args.get('input'), doc, variables)
        chars = args.get('chars', ' ')
    else:
        input_val = resolve_expression(args, doc, variables)
        chars = ' '
    
    if input_val is None:
        return None
    
    return str(input_val).lstrip(chars)


def op_rtrim(args, doc, variables):
    """$rtrim - Trim from right."""
    if isinstance(args, dict):
        input_val = resolve_expression(args.get('input'), doc, variables)
        chars = args.get('chars', ' ')
    else:
        input_val = resolve_expression(args, doc, variables)
        chars = ' '
    
    if input_val is None:
        return None
    
    return str(input_val).rstrip(chars)


def op_split(args, doc, variables):
    """$split - Split string by delimiter."""
    if len(args) != 2:
        raise ValueError('$split requires 2 arguments')
    
    string = resolve_expression(args[0], doc, variables)
    delimiter = resolve_expression(args[1], doc, variables)
    
    if string is None:
        return None
    
    return string.split(delimiter)


def op_strLenBytes(args, doc, variables):
    """$strLenBytes - String length in bytes."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    return len(str(val).encode('utf-8'))


def op_strLenCP(args, doc, variables):
    """$strLenCP - String length in code points."""
    val = resolve_expression(args, doc, variables)
    if val is None:
        return None
    return len(str(val))


def op_strcasecmp(args, doc, variables):
    """$strcasecmp - Case-insensitive string comparison."""
    if len(args) != 2:
        raise ValueError('$strcasecmp requires 2 arguments')
    
    val1 = resolve_expression(args[0], doc, variables)
    val2 = resolve_expression(args[1], doc, variables)
    
    if val1 is None:
        val1 = ''
    if val2 is None:
        val2 = ''
    
    s1 = str(val1).lower()
    s2 = str(val2).lower()
    
    if s1 < s2:
        return -1
    elif s1 > s2:
        return 1
    return 0


def op_indexOfBytes(args, doc, variables):
    """$indexOfBytes - Find substring index."""
    string = resolve_expression(args[0], doc, variables)
    substring = resolve_expression(args[1], doc, variables)
    start = resolve_expression(args[2], doc, variables) if len(args) > 2 else 0
    end = resolve_expression(args[3], doc, variables) if len(args) > 3 else None
    
    if string is None or substring is None:
        return None
    
    try:
        if end:
            return string.index(substring, start, end)
        else:
            return string.index(substring, start)
    except ValueError:
        return -1


def op_indexOfCP(args, doc, variables):
    """$indexOfCP - Find substring index by code point."""
    return op_indexOfBytes(args, doc, variables)


def op_regexMatch(args, doc, variables):
    """$regexMatch - Test if string matches regex."""
    input_val = resolve_expression(args.get('input'), doc, variables)
    regex = args.get('regex')
    options = args.get('options', '')
    
    if input_val is None:
        return False
    
    flags = 0
    if 'i' in options:
        flags |= re.IGNORECASE
    if 'm' in options:
        flags |= re.MULTILINE
    if 's' in options:
        flags |= re.DOTALL
    if 'x' in options:
        flags |= re.VERBOSE
    
    pattern = re.compile(regex, flags)
    return bool(pattern.search(str(input_val)))


def op_regexFind(args, doc, variables):
    """$regexFind - Find first regex match."""
    input_val = resolve_expression(args.get('input'), doc, variables)
    regex = args.get('regex')
    options = args.get('options', '')
    
    if input_val is None:
        return None
    
    flags = 0
    if 'i' in options:
        flags |= re.IGNORECASE
    if 'm' in options:
        flags |= re.MULTILINE
    if 's' in options:
        flags |= re.DOTALL
    if 'x' in options:
        flags |= re.VERBOSE
    
    pattern = re.compile(regex, flags)
    match = pattern.search(str(input_val))
    
    if match:
        return {
            'match': match.group(),
            'idx': match.start(),
            'captures': list(match.groups())
        }
    return None


def op_regexFindAll(args, doc, variables):
    """$regexFindAll - Find all regex matches."""
    input_val = resolve_expression(args.get('input'), doc, variables)
    regex = args.get('regex')
    options = args.get('options', '')
    
    if input_val is None:
        return []
    
    flags = 0
    if 'i' in options:
        flags |= re.IGNORECASE
    if 'm' in options:
        flags |= re.MULTILINE
    if 's' in options:
        flags |= re.DOTALL
    if 'x' in options:
        flags |= re.VERBOSE
    
    pattern = re.compile(regex, flags)
    results = []
    
    for match in pattern.finditer(str(input_val)):
        results.append({
            'match': match.group(),
            'idx': match.start(),
            'captures': list(match.groups())
        })
    
    return results


def op_replaceOne(args, doc, variables):
    """$replaceOne - Replace first occurrence."""
    input_val = resolve_expression(args.get('input'), doc, variables)
    find = resolve_expression(args.get('find'), doc, variables)
    replacement = resolve_expression(args.get('replacement'), doc, variables)
    
    if input_val is None:
        return None
    
    return str(input_val).replace(str(find), str(replacement), 1)


def op_replaceAll(args, doc, variables):
    """$replaceAll - Replace all occurrences."""
    input_val = resolve_expression(args.get('input'), doc, variables)
    find = resolve_expression(args.get('find'), doc, variables)
    replacement = resolve_expression(args.get('replacement'), doc, variables)
    
    if input_val is None:
        return None
    
    return str(input_val).replace(str(find), str(replacement))


###############################################################################
#
# Array Operators

def op_arrayElemAt(args, doc, variables):
    """$arrayElemAt - Get array element at index."""
    if len(args) != 2:
        raise ValueError('$arrayElemAt requires 2 arguments')
    
    array = resolve_expression(args[0], doc, variables)
    index = resolve_expression(args[1], doc, variables)
    
    if array is None or not isinstance(array, list):
        return None
    
    if index < 0:
        index = len(array) + index
    
    if 0 <= index < len(array):
        return array[index]
    
    return None


def op_first_array(args, doc, variables):
    """$first - Get first element of array."""
    array = resolve_expression(args, doc, variables)
    if array is None or not isinstance(array, list) or len(array) == 0:
        return None
    return array[0]


def op_last_array(args, doc, variables):
    """$last - Get last element of array."""
    array = resolve_expression(args, doc, variables)
    if array is None or not isinstance(array, list) or len(array) == 0:
        return None
    return array[-1]


def op_size(args, doc, variables):
    """$size - Get array size."""
    array = resolve_expression(args, doc, variables)
    if array is None:
        return None
    if not isinstance(array, list):
        raise ValueError('$size requires array argument')
    return len(array)


def op_slice(args, doc, variables):
    """$slice - Get array slice."""
    if len(args) == 2:
        array = resolve_expression(args[0], doc, variables)
        n = resolve_expression(args[1], doc, variables)
        if n >= 0:
            return array[:n]
        else:
            return array[n:]
    elif len(args) == 3:
        array = resolve_expression(args[0], doc, variables)
        position = resolve_expression(args[1], doc, variables)
        n = resolve_expression(args[2], doc, variables)
        return array[position:position + n]
    else:
        raise ValueError('$slice requires 2 or 3 arguments')


def op_concatArrays(args, doc, variables):
    """$concatArrays - Concatenate arrays."""
    result = []
    for arg in args:
        array = resolve_expression(arg, doc, variables)
        if array is None:
            return None
        result.extend(array)
    return result


def op_filter(args, doc, variables):
    """$filter - Filter array elements."""
    input_array = resolve_expression(args.get('input'), doc, variables)
    as_var = args.get('as', 'this')
    cond = args.get('cond')
    
    if input_array is None:
        return None
    
    result = []
    for item in input_array:
        # Add item to variables
        item_vars = dict(variables)
        item_vars[as_var] = item
        
        if resolve_expression(cond, doc, item_vars):
            result.append(item)
    
    return result


def op_in(args, doc, variables):
    """$in - Check if value is in array."""
    if len(args) != 2:
        raise ValueError('$in requires 2 arguments')
    
    val = resolve_expression(args[0], doc, variables)
    array = resolve_expression(args[1], doc, variables)
    
    if array is None:
        return False
    
    return val in array


def op_indexOfArray(args, doc, variables):
    """$indexOfArray - Find index of value in array."""
    array = resolve_expression(args[0], doc, variables)
    value = resolve_expression(args[1], doc, variables)
    start = resolve_expression(args[2], doc, variables) if len(args) > 2 else 0
    end = resolve_expression(args[3], doc, variables) if len(args) > 3 else None
    
    if array is None:
        return None
    
    search_array = array[start:end] if end else array[start:]
    
    try:
        return search_array.index(value) + start
    except ValueError:
        return -1


def op_isArray(args, doc, variables):
    """$isArray - Check if value is array."""
    val = resolve_expression(args, doc, variables)
    return isinstance(val, list)


def op_map(args, doc, variables):
    """$map - Apply expression to each array element."""
    input_array = resolve_expression(args.get('input'), doc, variables)
    as_var = args.get('as', 'this')
    in_expr = args.get('in')
    
    if input_array is None:
        return None
    
    result = []
    for item in input_array:
        item_vars = dict(variables)
        item_vars[as_var] = item
        result.append(resolve_expression(in_expr, doc, item_vars))
    
    return result


def op_reduce(args, doc, variables):
    """$reduce - Reduce array to single value."""
    input_array = resolve_expression(args.get('input'), doc, variables)
    initial_value = resolve_expression(args.get('initialValue'), doc, variables)
    in_expr = args.get('in')
    
    if input_array is None:
        return None
    
    value = initial_value
    for item in input_array:
        item_vars = dict(variables)
        item_vars['value'] = value
        item_vars['this'] = item
        value = resolve_expression(in_expr, doc, item_vars)
    
    return value


def op_reverseArray(args, doc, variables):
    """$reverseArray - Reverse array."""
    array = resolve_expression(args, doc, variables)
    if array is None:
        return None
    return list(reversed(array))


def op_sortArray(args, doc, variables):
    """$sortArray - Sort array."""
    input_array = resolve_expression(args.get('input'), doc, variables)
    sort_by = args.get('sortBy')
    
    if input_array is None:
        return None
    
    if isinstance(sort_by, dict):
        # Sort by field
        def sort_key(item):
            keys = []
            for field, direction in sort_by.items():
                val = get_field_value(item, field) if isinstance(item, dict) else item
                if val is None:
                    val = ''
                keys.append((val, direction))
            return keys
        
        return sorted(input_array, key=lambda x: [
            (v if d == 1 else type(v)(-v) if isinstance(v, (int, float)) else v)
            for v, d in sort_key(x)
        ])
    else:
        # Simple sort
        return sorted(input_array, reverse=(sort_by == -1))


def op_range(args, doc, variables):
    """$range - Generate array of integers."""
    start = resolve_expression(args[0], doc, variables)
    end = resolve_expression(args[1], doc, variables)
    step = resolve_expression(args[2], doc, variables) if len(args) > 2 else 1
    
    return list(range(start, end, step))


def op_zip(args, doc, variables):
    """$zip - Zip arrays together."""
    inputs = [resolve_expression(i, doc, variables) for i in args.get('inputs', [])]
    use_longest = args.get('useLongestLength', False)
    defaults = args.get('defaults')
    
    if use_longest:
        max_len = max(len(a) for a in inputs)
        result = []
        for i in range(max_len):
            row = []
            for j, arr in enumerate(inputs):
                if i < len(arr):
                    row.append(arr[i])
                elif defaults and j < len(defaults):
                    row.append(defaults[j])
                else:
                    row.append(None)
            result.append(row)
        return result
    else:
        return [list(t) for t in zip(*inputs)]


def op_arrayToObject(args, doc, variables):
    """$arrayToObject - Convert array to object."""
    array = resolve_expression(args, doc, variables)
    if array is None:
        return None
    
    result = {}
    for item in array:
        if isinstance(item, dict):
            result[item.get('k')] = item.get('v')
        elif isinstance(item, list) and len(item) == 2:
            result[item[0]] = item[1]
    
    return result


def op_objectToArray(args, doc, variables):
    """$objectToArray - Convert object to array."""
    obj = resolve_expression(args, doc, variables)
    if obj is None:
        return None
    
    return [{'k': k, 'v': v} for k, v in obj.items()]


###############################################################################
#
# Object Operators

def op_getField(args, doc, variables):
    """$getField - Get field from object."""
    if isinstance(args, dict):
        field = resolve_expression(args.get('field'), doc, variables)
        input_obj = resolve_expression(args.get('input'), doc, variables)
    else:
        field = resolve_expression(args, doc, variables)
        input_obj = doc
    
    if input_obj is None or not isinstance(input_obj, dict):
        return None
    
    return input_obj.get(field)


def op_setField(args, doc, variables):
    """$setField - Set field in object."""
    field = resolve_expression(args.get('field'), doc, variables)
    input_obj = resolve_expression(args.get('input'), doc, variables)
    value = resolve_expression(args.get('value'), doc, variables)
    
    if input_obj is None:
        input_obj = {}
    
    result = dict(input_obj)
    result[field] = value
    return result


def op_mergeObjects(args, doc, variables):
    """$mergeObjects - Merge multiple objects."""
    if not isinstance(args, list):
        args = [args]
    
    result = {}
    for arg in args:
        obj = resolve_expression(arg, doc, variables)
        if obj is not None and isinstance(obj, dict):
            result.update(obj)
    
    return result


###############################################################################
#
# Operator Registry

EXPRESSION_OPERATORS = {
    # Arithmetic
    '$add': op_add,
    '$subtract': op_subtract,
    '$multiply': op_multiply,
    '$divide': op_divide,
    '$mod': op_mod,
    '$abs': op_abs,
    '$ceil': op_ceil,
    '$floor': op_floor,
    '$round': op_round,
    '$trunc': op_trunc,
    '$sqrt': op_sqrt,
    '$pow': op_pow,
    '$exp': op_exp,
    '$ln': op_ln,
    '$log': op_log,
    '$log10': op_log10,
    
    # Comparison
    '$cmp': op_cmp,
    '$eq': op_eq,
    '$ne': op_ne,
    '$gt': op_gt,
    '$gte': op_gte,
    '$lt': op_lt,
    '$lte': op_lte,
    
    # Boolean
    '$and': op_and,
    '$or': op_or,
    '$not': op_not,
    
    # Conditional
    '$cond': op_cond,
    '$ifNull': op_ifNull,
    '$switch': op_switch,
    
    # Type
    '$type': op_type,
    '$toBool': op_toBool,
    '$toInt': op_toInt,
    '$toLong': op_toLong,
    '$toDouble': op_toDouble,
    '$toString': op_toString,
    '$toDate': op_toDate,
    '$toObjectId': op_toObjectId,
    '$convert': op_convert,
    
    # Date
    '$dateToString': op_dateToString,
    '$dateFromString': op_dateFromString,
    '$year': op_year,
    '$month': op_month,
    '$dayOfMonth': op_dayOfMonth,
    '$dayOfWeek': op_dayOfWeek,
    '$dayOfYear': op_dayOfYear,
    '$hour': op_hour,
    '$minute': op_minute,
    '$second': op_second,
    '$millisecond': op_millisecond,
    '$week': op_week,
    '$isoWeek': op_isoWeek,
    '$isoWeekYear': op_isoWeekYear,
    '$isoDayOfWeek': op_isoDayOfWeek,
    
    # String
    '$concat': op_concat,
    '$substr': op_substr,
    '$substrBytes': op_substrBytes,
    '$substrCP': op_substrCP,
    '$toLower': op_toLower,
    '$toUpper': op_toUpper,
    '$trim': op_trim,
    '$ltrim': op_ltrim,
    '$rtrim': op_rtrim,
    '$split': op_split,
    '$strLenBytes': op_strLenBytes,
    '$strLenCP': op_strLenCP,
    '$strcasecmp': op_strcasecmp,
    '$indexOfBytes': op_indexOfBytes,
    '$indexOfCP': op_indexOfCP,
    '$regexMatch': op_regexMatch,
    '$regexFind': op_regexFind,
    '$regexFindAll': op_regexFindAll,
    '$replaceOne': op_replaceOne,
    '$replaceAll': op_replaceAll,
    
    # Array
    '$arrayElemAt': op_arrayElemAt,
    '$first': op_first_array,
    '$last': op_last_array,
    '$size': op_size,
    '$slice': op_slice,
    '$concatArrays': op_concatArrays,
    '$filter': op_filter,
    '$in': op_in,
    '$indexOfArray': op_indexOfArray,
    '$isArray': op_isArray,
    '$map': op_map,
    '$reduce': op_reduce,
    '$reverseArray': op_reverseArray,
    '$sortArray': op_sortArray,
    '$range': op_range,
    '$zip': op_zip,
    '$arrayToObject': op_arrayToObject,
    '$objectToArray': op_objectToArray,
    
    # Object
    '$getField': op_getField,
    '$setField': op_setField,
    '$mergeObjects': op_mergeObjects,
    
    # Literal
    '$literal': lambda args, doc, vars: args,
}
