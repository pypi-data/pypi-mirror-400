# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.operators.differential
#
# Contains some differential operators acting on cochains and manifolds:
# - The exterior derivative operator, short-named 'd'
# - The codifferential operator, short-named 'delta'
# - The laplacian operator, short-named 'L'
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
import numpy as np
import scipy.sparse as sp

from dxtr import logger
from dxtr.complexes import SimplicialManifold
from dxtr.cochains import Cochain, cochain_base
from dxtr.operators.hodge import hodge_star
from dxtr.utils.typecheck import on_manifold


def exterior_derivative(cochain:Cochain) -> Cochain:
    """Exterior derivative acting on `Cochain`.

    Paramters
    ---------
    cochain
        The k-cochain we want to compute the exterior derivative of.

    Returns
    -------
        The (k+1)-cochain derived from the former.

    Notes
    -----
      * The exterior derivative can be applied to k-cochains with 
        k > complex.dim, but in these cases, it will return a zero array of
        size N = number of top-simplices in the primal case or number of 
        0-simplices in the dual case.
      * In the case of primal vector-valued 1-cochain, we apply a 'correction'
        to account for the fact that the vectors are not tangent to the primal 
        complex. This correction is necessary for the computation of the 
        mean curvature. 
      * The correction mentioned above might not be always necessary, keep
        that in mind.
    """
    
    cplx = cochain.complex
    n = cplx.dim
    k = cochain.dim
    isdual = cochain.isdual
    vals = cochain.values
    name = f'Exterior derivative of {cochain.name}'

    if 0<=k<=n:
        mtrx = cplx[n-k].boundary if isdual else cplx[k].coboundary
        
        if cochain.isvectorvalued  & (not cochain.isdual) & (k == 1):
            logger.info('A correction is applied to account for the a priori' +
                        ' non-tangent nature of the vector-valued cochain.')
            mtrx = mtrx @ _correction(cplx)

    if n < k:
        Nk = cplx[0].size if isdual else cplx[n].size
        mtrx = sp.diags(Nk*[0])
    if k < 0:
        Nk = cplx[n].size if isdual else cplx[0].size
        mtrx = sp.diags(Nk*[0])

    return Cochain(cplx, dim=k+1, values=mtrx@vals, dual=isdual, name=name)


@on_manifold
def codifferential(cochain:Cochain) -> Optional[Cochain]:
    """Codifferential operator acting on `Cochain`.

    Returns
    -------
        The (k-1)-cochain derived from the former.

    Notes
    -----
      * It can only be applied on `Cochain` defined on a `SimplicialManifold`.
      * The codifferential is mathematically defined as:
                          $$\delta(\cdot) = \star d \star(\cdot)$$
      * For 1-cochain, it corresponds to the divergence of the corresponding vector field.
    """
    n, k = cochain.complex.dim, cochain.dim
    
    sign = (-1)**(1 + n*(k-1))
    
    codiff = sign * hodge_star(exterior_derivative(hodge_star(cochain)))
    codiff._name = f'Codifferential of {cochain.name}'

    return codiff 


def laplacian(obj: Cochain|SimplicialManifold, dim:Optional[int]=None, 
              dual:bool=False, version:str='LdR') -> Optional[Cochain]:
    """Laplacian acting on `Cochain` or `SimplicialManifold`.

    Paramters
    ---------
    obj
        Either the `Cochain` we want to apply the Laplacian on; or the 
        `SimplicialManifold` we want to compute the Laplacian of, see Notes.
    dim
        Optional (Default is None). Should only be specified when the 1st 
        argument is a SimplicialManifold. Corresponds in this case to the 
        topological dimension at which the Laplacian should be computed.
    dual
        Optional (default is False). Should only be specified when the 1st 
        argument is a SimplicialManifold. If true, the generated cochain 
        base is a dual `Cochain`
    version
        Optional (default is 'LdR'). Triggers the formula to use.
        - 'LdR': Laplace-deRham is used.
        - 'LB': Laplace-Beltrami is used.

    Returns
    -------
        A k-`Cochain` representing the laplacian of the input.

    Notes
    -----
      * The Laplace-Beltrami operator is defined as:
                          $$\Delta_{B} = \delta d(\cdot)$$
      * The Laplace-deRham operator is defined as:
                          $$\Delta_{LdR} = \delta d(\cdot) + d\delta(\cdot)$$
      * For 0-cochain the two should match.
      * Accepting `SimplicialManifolds` as inputs is usefull to perform    
        spectral analysis.
      * It is not clear to me if we should allow this operator to be applied on 
        a `SimplicialManifold`... It makes life easier but I feel
    """

    if not isinstance(obj, Cochain):
        try:
            assert isinstance(obj, SimplicialManifold), (
    f'Argument of type {type(obj)} are not supported. Please provide '
    +'a `Cochain` or a `SimplicialManifold`.')
            
            assert dim is not None, (
    'Must specify dimension when applying Laplacian to a `SimplicialManifold`')
            
            cochain = cochain_base(obj, dim, dual=dual)
        
        except AssertionError as msg:
            logger.warning(msg)
            return None
    else:
        try: 
            cochain = obj
            assert isinstance(cochain.complex, SimplicialManifold), (
                'Input `Cochain` must be defined on a `SimplicialManifold`.')
        
        except AssertionError as msg:
            logger.warning(msg)
            return None
        

    if cochain.dim == 0: version = 'LB'

    lpc = delta(d(cochain))

    if version == 'LdR': lpc += d(delta(cochain))

    lpc._name = f'Laplacian of {cochain.name}'

    return lpc

# ####### #
# Aliases #
# ####### #

def d(cochain:Cochain) -> Cochain:
    """An alias for the `exterior_derivative()` operator.

    See also
    --------
      * The `exterior_derivative()` function documentation.
    """
    return exterior_derivative(cochain)

def delta(cochain:Cochain) -> Optional[Cochain]:
    """An alias for the `codifferential()` operator.

    See also
    --------
      * The `codifferential()` function documentation.
    """
    return codifferential(cochain)

def L(obj:Cochain|SimplicialManifold, dim:Optional[int]=None, 
      dual:bool=False, version:str='LdR') -> Optional[Cochain]:
    """An alias for the `laplacian()` operator.

    See also
    --------
      * The `laplacian()` function documentation.
    """
    return laplacian(obj, dim=dim, dual=dual, version=version)

# ################# #
# Usefull functions #
# ################# #

def _correction(manifold:SimplicialManifold) -> sp.diags[float]:
    """Computes a correction due to the curvature of the primal complex.

    Parameters
    ----------
    manifold
        The `SimplicialManifold` to work on.

    Returns
    -------
        A diagonal sparse matrix containing the correction coefficients.
    
    Notes
    -----
      * The correction coefficients correspond to the inverse of the sinus of
        half the dihedral angles between top-simplices.
      * On open manifolds, the coefficients for the border edges are set to one.
    """

    angles = .5 * manifold.dihedral_angles
    weights = 1/np.sin(angles)
    
    if not manifold.isclosed:
        N1 = manifold[1].size
        in_ids = manifold.interior()[1]
        weights = [weights[np.where(in_ids==idx)[0][0]] 
                    if idx in in_ids else 1 for idx in np.arange(N1)]
        
    return sp.diags(weights)

