# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.objects.typecheck
#
# This file contains one decorator:
#     - `typecheck`
# Its purpose is to ease the assessment of arguments given to some functions.
#
#       File author(s):
#           Olivier Ali <olivier.ali@inria.fr>
#
#       File contributor(s):
#           Olivier Ali <olivier.ali@inria.fr>
#
#       File maintainer(s):
#           Olivier Ali <olivier.ali@inria.fr>
#
#       Copyright © by Inria
#       Distributed under the LGPL License..
#       See accompanying file LICENSE.txt or copy at
#           https://www.gnu.org/licenses/lgpl-3.0.en.html
#
# -----------------------------------------------------------------------
from __future__ import annotations
from typing import Optional, Any, Iterable

from functools import wraps

def typecheck(expected_types, arg_idx:int=0) -> Optional[Any]:
    """Checks if the arg_idx-th provided argument has the proper type.
    """
    if isinstance(expected_types, Iterable):
        expected_types = tuple(expected_types)
    else:
        expected_types = (expected_types,)

    type_names = [xpct_type.__name__ for xpct_type in expected_types]
    def decorator(func):
        @wraps(func)        
        def wrapper(*args, **kwargs):
            try:
                assert isinstance(args[arg_idx], expected_types), (
        f'Only {type_names} accepted as input for {func.__name__}.')
                result = func(*args, **kwargs)
            
            except AssertionError as msg:
                from dxtr import logger
                logger.warning(msg)
                return None
            
            return result
        return wrapper
    return decorator


def on_manifold(func) -> Optional[Any]:
    """Checks That the provided `Cochain` is defined on a `SimplicialManifold`.

    Notes
    -----
      * This is a decorator...
    """
    @wraps(func)        
    def wrapper(*args, **kwargs):
        try:
            from dxtr import Cochain, SimplicialManifold
            assert isinstance(args[0], Cochain), (
                    'Only `Cochain` accepted as input.')
            assert isinstance(args[0].complex, SimplicialManifold), (
            'The input `Cochain` must be defined on a `SimplicialManifold.`')
            
            result = func(*args, **kwargs)
        
        except AssertionError as msg:
            from dxtr import logger
            logger.warning(msg)
            return None
        
        return result
    return wrapper


def valid_input(func) -> Optional[Any]:
    """Checks that the provided object matches the saving criteria.

    Notes
    -----
      * This is a decorator useful for recording objects on disk.
      * Saving criteria:
        * Instance of `SimplicialManifold` or `Cochain`.
        * 2D complex or manifold as underlying structure.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            from dxtr import Cochain, SimplicialComplex
            EXPECTED_TYPES = (SimplicialComplex, Cochain)
            
            assert isinstance(args[0], EXPECTED_TYPES), (
                f'{type(args[0])} not supporting for saving.')
            
            if isinstance(args[0], SimplicialComplex):
                obj = args[0]
            elif isinstance(args[0], Cochain):
                obj = args[0].complex
            
            n = obj.dim
            assert n == 2, f'{n}D supporting complexes not supported, only 2D.'
            return func(*args, **kwargs)
        
        except AssertionError as msg:
            from dxtr import logger
            logger.warning(msg)
            return None
    return wrapper
