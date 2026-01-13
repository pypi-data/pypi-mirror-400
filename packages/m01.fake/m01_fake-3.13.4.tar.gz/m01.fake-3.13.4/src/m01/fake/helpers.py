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
"""Helpers

$Id:$
"""
from __future__ import absolute_import
from future import standard_library
import six
standard_library.install_aliases()
from builtins import str
from six import string_types
__docformat__ = 'restructuredtext'

from six import PY2


if PY2:
    str = str
    from six import string_types
else:
    str = str
    six.string_types = (str, bytes)


def toUnicode(s):
    try:
        return str(s)
    except:
        pass
    return s if isinstance(s, str) else s.decode()


def asdict(fields):
    """Takes a list of field names and returns a matching dictionary.

    ["a", "b"] becomes {"a": 1, "b": 1}

    and

    ["a.b.c", "d", "a.c"] becomes {"a.b.c": 1, "d": 1, "a.c": 1}
    """
    as_dict = {}
    for field in fields:
        if not isinstance(field, six.string_types):
            raise TypeError(
                "fields must be a list of key names, each an instance of %s" % (
                    six.string_types.__name__,))
        as_dict[field] = 1
    return as_dict
