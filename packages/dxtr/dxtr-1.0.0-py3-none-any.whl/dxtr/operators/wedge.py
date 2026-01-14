# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.operators.wedge
#
# Contains an implementation of the wedge operator acting on cochains.
# Some useful methods (for the wedge definition) are also included:
# - _are_valid()
# - _wedge_coefficients()
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
from scipy.special import factorial

from dxtr import logger
from dxtr.cochains import Cochain


def wedge(cochain_1:Cochain, cochain_2:Cochain) -> Optional[Cochain]:
    """Implements the wedge product between two `Cochain` objects.

    Parameters
    ----------
    cochain_1
        The first `Cochain` to consider.
    cochain_2
        The second `Cochain` to consider.

    Returns
    -------
    Cochain or None
        The sought `Cochain` corresponding to the wedge product between the 
        two inputs.
    
    Notes
    -----
      * If the topological dimensions of the two provided `Cochains` sum up to 
        a value above the topological dimension of the supporting complex, we
        return the null `Cochain` defined on the top simplices. 
      * For now, the wedge operator is restricted to scalar-valued, primal 
        `Cochain` only.
    
    See also
    --------
      * Section 3.8 of [Melvin Leok's Phd Thesis](https://thesis.library.caltech.edu/831/1/01_thesis_double_sided_mleok.pdf) 
      about the discretization of the Wedge product was seminal for the 
      development of this operator.
        
    """
    
    if not _are_valid(cochain_1, cochain_2): return None

    cplx = cochain_1.complex
    n, k, l = cplx.dim, cochain_1.dim, cochain_2.dim

    if k+l > n: 
        values = np.zeros(cplx[n].size)
    else:
        values = _wedge_coefficients(cochain_1, cochain_2)

    return Cochain(cplx, dim=min(k+l, n), values=values)


# ################# #
# Usefull functions #
# ################# #


def _are_valid(c1:Cochain, c2:Cochain) -> bool:
    """Checks that the inputs given to the wedge operator are correct.

    Returns
    -------
        True if the inputs meet the requirements, False otherwise.
    
    Notes
    -----
    The requirements are:
      * The inputs must be `Cochain` instances.
      * They must be scalar-valued.
      * They must be defined on the same `SimplicialComplex`. 
      * They must have the same duality. 
      * They must be primal `Cochain` instances. 
    """
    
    try:
        for i, c in enumerate([c1, c2]):
            assert isinstance(c, Cochain), f'Input #{i+1} is not a `Cochain`.'
            assert not c.isvectorvalued, f'Input #{i+1} is vector-valued.'
        
        assert c1.complex is c2.complex, (
            'Inputs not defined on the same `SimplicialComplex`.')
        assert c1.isdual == c2.isdual, 'Inputs must have the same duality.'
        assert not c1.isdual, 'Only primal `Cochain` accepted.'

        return True
    
    except AssertionError as msg:
        logger.warning(msg)
        return False


def _wedge_coefficients(cochain_1:Cochain, cochain_2:Cochain
                        ) -> Optional[np.array[float]]:
    """Computes discrete wedge coefficients between k- & l-cochains.

    Parameters
    ----------
    cochain_1
        The first `Cochain` instance to consider.
    cochain_2
        The second `Cochain` instance to consider.

    Returns
    -------
       A (N_kl,)-array containing the sought values, where N_kl = number of 
       (k+l)-simplices within the considered complex.
    
    Notes
    -----
      * We assume that the first cochain is of higher dimension (k) than the 
        second one (l), *i.e.* k >= l >= 0.
      * The tricky part is to pair properly for each (k+l)-simplex, the k- &
        l-faces to pair together.
      * In the case l==0, we chose to simply average the 0-cochain values over
        the k-cofaces. This might not be the best option and could/should be 
        reconsidered maybe later. 
    
    See also
    --------
      * `_neighbor_through_vertices` in the same module to see how we set the 
        k-/l-simplex pairing.
    """

    complex = cochain_1.complex
    k, l = cochain_1.dim, cochain_2.dim

    adj_tsr = complex.adjacency_tensor(k, l)
    coefs = np.einsum('ijk,j,k->i',adj_tsr, cochain_1.values, cochain_2.values)

    return factorial(max(k,l)) * coefs.todense() / factorial(k+l+1)


