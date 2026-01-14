# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.operators.geometry
#
# Contains some geometrical operators, mostly curvature-related. 
# Contrary to other operators, the ones implemented here are applied on
# `SimplicialManifold` instances rather than `Cochain` ones. You will find:
# - positions (generates a vector-valued cochain of vertex positions)
# - normal
# - Gaussian curvature
# - mean curvature
# - extrinsic curvature.
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
#       See acchnompanying file LICENSE.txt or copy at
#           https://www.gnu.org/licenses/lgpl-3.0.en.html
#
# -----------------------------------------------------------------------
from __future__ import annotations
from typing import Optional
from copy import deepcopy
import numpy as np
import numpy.linalg as lng

from dxtr import logger
from dxtr.complexes import SimplicialComplex, SimplicialManifold
from dxtr.cochains import Cochain
from dxtr.utils import typecheck
from .differential import laplacian, exterior_derivative
from .musical import sharp


@typecheck(SimplicialComplex)
def positions(complex: SimplicialComplex, 
              dual: bool=False) -> Optional[Cochain]:
    """Generates a vector-valued 0-`Cochain` of the position vectors.

    Parameters
    ----------
    complex : SimplicialComplex
        The `SimplicialComplex` we want the position vectors of.
    dual : bool, optional
        If True, return a dual 0-`Cochain` containing the top-simplex circumcenters. 
        Else, returns a primal 0-`Cochain` containing the 0-simplex vertices. Default is False.

    Returns
    -------
    Optional[Cochain]
        The seeked `Cochain`.

    Notes
    -----
    * If dual==True, the `complex` argument must be a `SimplicialManifold` instance.
    """
    try:
        if dual: 
            assert isinstance(complex, SimplicialManifold), (
                'dual positions can only be computed on `SimplicialManifold`')
        
        pos = complex[-1].circumcenters if dual else complex[0].vertices
        return Cochain(complex, dim=0, dual=dual, values=pos)
    
    except AssertionError as msg:
        logger.warning(msg)
        return None
    

@typecheck(SimplicialManifold)
def normals(manifold: SimplicialManifold, 
            dual: bool=False) -> Optional[Cochain]:
    """Computes the unit normal vector field on a simplicial manifold.

    Parameters
    ----------
    manifold : SimplicialManifold
        The `SimplicialManifold` to work on.
    dual : bool, optional
        If False, the normal vectors are computed on the vertices of the primal complex. 
        Else, the normal vectors are computed on the circumcenters of the top simplices. Default is False.

    Returns
    -------
    Optional[Cochain]
        A `Cochain` with a (N0, D)-shaped array as value, with N0 = number of 0-simplices or n-simplices 
        (if dual == True) within the considered `SimplicialManifold` and D = the dimension of the embedding space.

    Notes
    -----
    * The returned vectors must be of unit norms.
    * This algo relies on the computation of a discrete version of the normal curvature vector field.
    * In the case of a flat `SimplicialManifold` it will return None.
    * This function will be useful to compute the normal curvature.

    See Also
    --------
    mean_curvature : Computes the mean curvature.
    """
 
    nrl_vct = mean_curvature(manifold, return_vector=True, dual=dual)
    mn_curv = lng.norm(nrl_vct.values, axis=-1)[..., None]
    
    nrl_vct *= 1/mn_curv
    
    nrl_vct._name = 'Unit Normal'

    return nrl_vct


@typecheck(Cochain)
def projector(vector_field: Cochain, 
              normalized: bool=False) -> Cochain:
    """Computes the projector along a vector field.

    Parameters
    ----------
    vector_field : Cochain
        The vector field we want the projector of.
    normalized : bool, optional
        If True, the vector field is normalized prior to the computation of its projector. Default is False.

    Returns
    -------
    Cochain
        A dual tensor-valued 0-`Cochain`.

    Notes
    -----
    * The projector along a vector field is defined as the following symmetric second order tensor:
      $$\boldsymbol{P}(\boldsymbol{v}) = \boldsymbol{v}\otimes\boldsymbol{v}$$
    """
   
    if normalized:
        Nn = vector_field.shape[0]
        vectors = vector_field.values
        vector_field /= lng.norm(vectors, axis=-1).reshape((Nn, 1))
    
    proj_field = np.array([np.outer(vct, vct) for vct in vector_field.values])
    
    return Cochain(vector_field.complex, dim=0, dual=True, values=proj_field)
    

@typecheck(SimplicialManifold)
def gaussian_curvature(manifold: SimplicialManifold) -> Optional[Cochain]:
    """Computes a discrete version of the Gaussian curvature.

    Parameters
    ----------
    manifold : SimplicialManifold
        The n-simplicial manifold to compute the curvature on.

    Returns
    -------
    Optional[Cochain]
        A `Cochain` containing the values of the estimated curvature for each (n-2)-simplices.

    Notes
    -----
    * We define the Gaussian curvature as the deficit angle around hinges of topological dimension n-2, n being the top-simplex dimension.
    * The deficit angle is then divided by the hinge covolume (i.e. surface of the dual 2-cell) to get a value that is indeed the inverse of a surface.
    * The sum(curvature * covolume)/2pi must equal the Euler characteristics.
    """
    
    n = manifold.dim

    gauss = deepcopy(manifold.deficit_angles)
    gauss /= manifold[n-2].covolumes
    
    return Cochain(manifold, n-2, values=gauss, name='Gaussian curvature')


@typecheck(SimplicialManifold)
def mean_curvature(manifold: SimplicialManifold, 
                   dual: bool=False, 
                   return_vector: bool=False) -> Optional[Cochain]:
    """Computes a discrete version of the Mean curvature.

    Parameters
    ----------
    manifold : SimplicialManifold
        The simplicial manifold to compute the mean curvature of.
    dual : bool, optional
        If True, compute the mean curvature on the dual complex. Default is False.
    return_vector : bool, optional
        If True, return the mean curvature as a vector. Default is False.

    Returns
    -------
    Optional[Cochain]
        A `Cochain` containing the values of the estimated curvature for each 0-simplex.

    Notes
    -----
    * We define the Mean curvature as the norm of the Laplacian operator applied to position vectors.
    * In the primal case, the position vectors correspond to the positions of the 0-simplices. 
    * In the dual case, the position vectors correspond to the circumcenters of the n-simplices.

    See also
    --------
    K. Crane course, section 5.2.1, p.88.
    """

    x = positions(manifold, dual=dual)
    mn_curv_nrl = -.5 * laplacian(x)
    mn_curv_nrl._name = 'Mean Curvature Normal Vector Field'

    if not return_vector:
        mn_curv_nrl._values = lng.norm(mn_curv_nrl._values, axis=-1)
        mn_curv_nrl._name = 'Mean Curvature'
    
    return mn_curv_nrl


@typecheck(SimplicialManifold)
def extrinsic_curvature(manifold: SimplicialManifold, 
                        dual: bool=False) -> Cochain:
    """Computes the extrinsic curvature of a 2-D `SimplicialManifold`.

    Parameters
    ----------
    manifold : SimplicialManifold
        The `SimplicialManifold` to work on.
    dual : bool, optional
        If True the extrinsic curvature is computed from the normals to the top simplices. 
        Else, it is computed from the normals at the 0-simplices. Default is False.

    Returns
    -------
    Cochain
        A vector-valued 1-`Cochain` containing the seeked values. 

    Notes
    -----
    * This implementation is based on the Weingarten formula, relating the extrinsic curvature to the spatial derivative of the normal vector field: 
      $$\kappa_{ij} = \tau_i\cdot\nabla_j(n).$$
    * The idea is to describe a symmetric 2nd-order tensor field as a vector-valued 1-form.
    """
    
    n = manifold.dim
    
    try:
        assert n == 2, 'The provided manifold should be 2D.'
    except AssertionError as msg:
        logger.warning(msg)
        return None
    
    nrls = normals(manifold, dual=dual)
    edge_lengths = manifold[n-1].covolumes if dual else manifold[1].volumes
    weights = (1 / edge_lengths).reshape(*edge_lengths.shape, 1)
    
    return  exterior_derivative(nrls) * weights


@typecheck(Cochain)
def normal_curvature(direction: Cochain) -> Optional[Cochain]:
    """Computes the normal curvature along a vector field.

    Parameters
    ----------
    direction : Cochain
        The vector field along which we want to compute the normal curvature.

    Returns
    -------
    Optional[Cochain]
        A dual 0-`Cochain` containing the seeked values. 

    Notes
    -----
    * The normal curvature along a vector field $\boldsymbol{v}$ is defined as the projection of the extrinsic curvature along this vector field:
      $$\kappa_n = \boldsymbol{\kappa} \colon \hat{\boldsymbol{v}}\otimes\hat{\boldsymbol{v}}$$
    * The vector field must be normalized prior to the projection.
    * This definition is valid for a manifold embedded within a higher-dimensional space.
    * For now it should be limited to the case of 2D surfaces.
    """
    
    if not _isvalid(direction): return None
    
    mfld = direction.complex
    proj = projector(direction, normalized=True).values
    xcurv = sharp(extrinsic_curvature(mfld)).values
    ncurv = np.einsum('ijk, ijk -> i', xcurv, proj)

    return Cochain(mfld, dim=0, dual=True, values=ncurv)


# ####### #
# Aliases #
# ####### #

def Kg(manifold: SimplicialManifold) -> Optional[Cochain]:
    """An alias for the `gaussian_curvature()` operator.

    See also
    --------
    gaussian_curvature : Computes the Gaussian curvature.
    """
    return gaussian_curvature(manifold)

def Km(manifold: SimplicialManifold, 
       dual: bool=False, 
       return_vector: bool=False) -> Optional[Cochain]:
    """An alias for the `mean_curvature()` operator.

    See also
    --------
    mean_curvature : Computes the mean curvature.
    """
    return mean_curvature(manifold, dual, return_vector)


# ################# #
# Usefull functions #
# ################# #

def _isvalid(vector_field: Cochain) -> bool:
    """Checks normal curvature can be computed along the provided vector field.
    
    Parameters
    ----------
    vector_field : Cochain
        A vector-valued dual 0-`Cochain` containing the vector field we want to compute the normal curvature along.
    
    Returns
    -------
    bool
        True if the vector field is valid, False otherwise.

    Notes
    -----
    Tested properties:
    * Input must be a vector-valued dual 0-`Cochain` embedded in R^3.
    * The supporting domain must be a `SimplicialManifold` of dim = 2.
    """

    try:
        assert vector_field.isdual, 'Input must be a dual `Cochain`.'
        assert vector_field.dim == 0, 'Input  must be a 0-`Cochain`.'
        assert vector_field.isvectorvalued, (
            'Input `Cochain` is not vector-valued.')
        mfld = vector_field.complex
        Nn, D = mfld.shape[-1], mfld.emb_dim
        assert vector_field.values.shape == (Nn, D), (
            'Input values have a wrong shape.')
        assert isinstance(mfld, SimplicialManifold), (
    'The provided direction field must be defined on a `SimplicialComplex`.')
        assert mfld.dim == 2, 'The supporting `SimplicialComplex` must be 2D.'
        return True
    
    except AssertionError as msg:
        logger.warning(msg)
        return False

