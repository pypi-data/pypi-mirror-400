# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.examples.complexes_and_manifolds
#
# This file contains generator functions to produce quickly simple
# data structures of interest.
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
from typing import Optional
import pathlib as pl
import numpy as np
from numpy import linalg as lng
from numpy import random as rnd

from dxtr import logger
from dxtr.utils.logging import mutelogging
from dxtr.cochains import Cochain
from dxtr.complexes.example_complexes import (icosahedron, sphere, 
                                              triangular_grid)


@mutelogging
def unit_cochain(complex_name: str = 'icosa', dim: int = 1, dual: bool = False, 
                 manifold: bool = False) -> Cochain:
    """
    Generates a 1-valued k-`Cochain`.

    Parameters
    ----------
    complex_name : str, optional
        The name of the `SimplicialComplex` we want to compute the normal field on. 
        Should either be 'icosa' or 'sphere'. Default is 'icosa'.

    dim : int, optional
        The topological dimension of the desired Cochain. Should be in (0, 1, 2). Default is 1.

    dual : bool, optional
        If True, returns a dual cochain. Default is False.

    manifold : bool, optional
        If True, the supporting domain is a `SimplicialManifold` instance; Otherwise it is a `SimplicialComplex` instance. Default is False.

    Returns
    -------
    Cochain
        The generated cochain.
    """
    if complex_name == 'icosa':
        cplx = icosahedron(manifold=manifold)
    elif complex_name == 'sphere':
        cplx = sphere(manifold=manifold)
    else: 
        logger.error('Can only generate cochains on icosahedron and sphere.')
        return None

    n = cplx.dim 
    Nk = cplx.shape[n-dim] if dual else cplx.shape[dim]

    return Cochain(cplx, dim=dim, values=np.ones(Nk), dual=dual)

@mutelogging
def random_cochain(complex_name: str = 'icosa', dim: int = 1, dual: bool = False,
                   manifold: bool = False, interval: tuple[float] = (0, 1)) -> Cochain:
    """
    Generates a random scalar-valued k-`Cochain`.

    Parameters
    ----------
    complex_name : str, optional
        The name of the `SimplicialComplex` we want to compute the normal field on. 
        Should either be 'icosa' or 'sphere'. Default is 'icosa'.

    dim : int, optional
        The topological dimension of the desired Cochain. Should be in (0, 1, 2). Default is 1.

    dual : bool, optional
        If True, returns a dual cochain. Default is False.

    manifold : bool, optional
        If True, the supporting domain is a `SimplicialManifold` instance; Otherwise it is a `SimplicialComplex` instance. Default is False.

    interval : tuple[float], optional
        The interval within to draw the random values. Default is (0, 1).

    Returns
    -------
    Cochain
        The generated cochain.

    Notes
    -----
    The random values are generated with the `numpy.random.uniform` function. 
    The random values can include interval[0] but exclude interval[-1].
    """
    
    if dual: manifold=True

    if complex_name == 'icosa':
        cplx = icosahedron(manifold=manifold)
    elif complex_name == 'sphere':
        cplx = sphere(manifold=manifold)
    else: 
        logger.error('Can only generate cochains on icosahedron or sphere.')
        return None
    
    n = cplx.dim 
    Nk = cplx.shape[n-dim] if dual else cplx.shape[dim]
    values = rnd.uniform(low=interval[0], high=interval[-1], size=Nk)
    duality = 'dual' if dual else 'primal'

    return Cochain(cplx, dim=dim, values=values, dual=dual, 
                   name=f'Random {duality} {dim}-Cochain')

@mutelogging
def normal_vector_field(manifold_name: str = 'icosa', dual: bool = True) -> Optional[Cochain]:
    """
    Generates a unit vector-valued `Cochain` normal to a `SimplicialManifold`.

    Parameters
    ----------
    manifold_name : str, optional
        The name of the manifold we want to compute the normal field on. Should either be 'hexa', 'sphere' or 'icosa'. Default is 'icosa'.
    dual : bool, optional
        If True, the normal vectors correspond to the normals to the top (primal) simplices. If False, the normal vectors correspond to normals to the top (dual) cells. Default is True.

    Returns
    -------
    Optional[Cochain]
        The generated cochain.

    Notes
    -----
    * The returned `Cochain` is either a dual or a primal 0-`Cochain`, depending on the value of the `dual` argument.
    * In the case of the sphere, the computation is performed on the small one, *i.e.* the number of vectors will be 3420.
    """
    
    if manifold_name == 'hexa':
        mfld = triangular_grid(manifold=True)
        
        k = -1 if dual else 0
        Nk = mfld.shape[k]
        normals = np.array([[0,0,1]*Nk]).reshape(Nk, 3)
        
        return Cochain(complex=mfld, values=normals, dim=0, 
                       dual=dual)
    
    elif manifold_name == 'sphere':
        mfld = sphere(manifold=True)
    
    elif manifold_name == 'icosa':
        mfld = icosahedron(manifold=True)

    else:
        logger.error('Can only generate normals on `icosa`,`hexa` or `sphere`.')
        return None
    
    if dual:
        cctrs = mfld[-1].circumcenters
    else:
        cctrs = mfld[0].vertices
    
    origin = cctrs.mean(axis=0)
    cctrs -= origin
    normals = np.array([x/lng.norm(x) for x in cctrs])
    
    return Cochain(complex=mfld, values=normals, dim=0, dual=dual, 
                   name='Normal vector field')

