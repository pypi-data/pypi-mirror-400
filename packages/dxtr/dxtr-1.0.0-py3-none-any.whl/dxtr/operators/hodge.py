# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.operators.hodge_star
#
# Contains the definition of the hodge_star operator acting on cochains.
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

import numpy as np
import scipy.sparse as sp

from dxtr.complexes import SimplicialManifold
from dxtr.cochains import Cochain
from dxtr.utils.typecheck import on_manifold, typecheck
# from dxtr.complexes.simplicialmanifold import edge_vectors


@on_manifold
def hodge_star(cochain:Cochain) -> Optional[Cochain]:
    """Hodge star operator *(.) acting on a `Cochain`.

    Paramters
    ---------
    cochain
        The k-cochain we want to apply the Hodge star on.

    Returns
    -------
        The (n-k)-cochain dual of the former.
    
    Notes
    -----
      * This operator can only be applied on `Cochain` instances defined on 
        a `SimplicialManifold`. This is checked thanks to the `@on_manifold`
        decorator.
      * Should not be mistaken with the topological operator `star` 
        defined in the `topology` sub-module.
    
    See also
    --------
      * `@on_manifold` decorator defined in the `typecheck` module.
    """

    k = cochain.dim
    vals = cochain.values
    dual = cochain.isdual
    mfld = cochain.complex
    n = mfld.dim

    mtrx = _compute_hodge_star_of(mfld, k, dual)
    values = mtrx@vals

    return Cochain(mfld, dim=n-k, dual=not dual, values=values)


# ################# #
# Usefull functions #
# ################# #

@typecheck(SimplicialManifold)
def _compute_hodge_star_of(manifold:SimplicialManifold, dim:int, 
                           dual:bool=False) -> sp.csr_matrix[float]:
        """Computes the (inverse) Hodge star matrix at a given degree.

        Parameters
        ----------
        manifold
            The `SimplicialManifold` to work on.
        dim
            The topological dimension where to compute the Hodge star.
        dual
            It True returns the inverse Hodge star.
        
        Returns
        -------
        The seeked Hodge star matrix in the scipy.sparse.csr_matrix format.

        Notes
        -----
          * The type of the `manifold` argument is verified thanks to the 
            `@typecheck()` decorator.
          * In the cases n-dim primal and 0-dim dual, we multiply the Hodge
            matrix by a (-1)**(n-1) factor. This is done to account for the 
            orientation of the top-simplices.
        
        See also
        --------
          * Concerning the (-1)**(n-1) factor: See Hirani's PhD manuscript, 
            remark 4.1.2, p.41.
        """
        
        n = manifold.dim
        k = np.clip(dim, 0, n)

        if dual:
            hdg_str = manifold[n-k].volumes / manifold[n-k].covolumes
            hdg_str *= (-1)**(k*(n-k))
            if k == 0: hdg_str *= (-1)**(n-1) 
        else:
            hdg_str = manifold[k].covolumes / manifold[k].volumes
            if k == n: hdg_str *= (-1)**(n-1) 

        return sp.diags(hdg_str).tocsr()

