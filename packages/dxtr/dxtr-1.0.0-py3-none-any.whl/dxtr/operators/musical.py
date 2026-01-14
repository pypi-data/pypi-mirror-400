# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.operators.musical
#
# Contains discrete versions of the classic musical isomorphisms between
# k-vectors and k-forms:
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
import numpy.linalg as lng
import scipy.sparse as sp

from dxtr import logger
from dxtr.utils import typecheck
from dxtr.complexes import SimplicialManifold, SimplicialComplex
from dxtr.cochains import Cochain, WhitneyMap
from dxtr.math.topology import complex_simplicial_partition
from dxtr.math.geometry import volume_polytope
from dxtr.complexes.simplicialmanifold import edge_vectors




def flat(vector_field: np.ndarray[float] | Cochain, 
         manifold: Optional[SimplicialManifold] = None,
         dual: bool = False,
         name: Optional[str] = '1-cochain, flat from vector field'
         ) -> Optional[Cochain]:
    """
    Transforms a vector field into a 1-`Cochain`.

    Parameters
    ----------
    vector_field : np.ndarray or Cochain
        The vector field to convert.
    manifold : SimplicialManifold, optional
        The Simplicial Manifold where the vector field is defined. If the 
        provided vector field is a vector-valued `Cochain`, this argument 
        is not needed. Default is None.
    dual : bool, optional
        If True, a dual 1-`Cochain` is returned; otherwise, it is a primal one. 
        Default is False.
    name : str, optional
        The name to give to the flattened cochain. Default is '1-cochain, flat from vector field'.

    Returns
    -------
    Cochain or None
        The resulting 1-cochain defined on the prescribed manifold.

    Notes
    -----
    The input vector field must be defined on the circumcenters of the 
    top simplices of the considered `SimplicialManifold`.

    This implementation of the discrete flat operator is derived from
    the definitions provided by Anil Hirani in his PhD manuscript.

    We chose to implement two types of discrete flat: one returns a primal 
    1-cochain, the other a dual 1-cochain. The `dual` argument enables the 
    selection of the desired one.

    TODO: Add the ability to flatten a vector field defined on 
    the 0-simplices.

    See Also
    --------
    dual_to_primal_flat : Transforms a vector field into a primal 1-cochain.
    dual_to_dual_flat : Transforms a vector field into a dual 1-cochain.
    """
    if isinstance(vector_field, Cochain):
        manifold = vector_field.complex
        vector_field = vector_field.values

    if not _isvalid_for_flat(vector_field, manifold):
        return None
    elif dual:
        return _dual_to_dual_flat(vector_field, manifold, name)
    else:
        return _dual_to_primal_flat(vector_field, manifold, name)        



def sharp(cochain: Cochain, 
          name: str = 'Discrete vector field') -> Optional[Cochain]:
    """
    Transforms a primal 1-`Cochain` into a discrete vector field.

    Parameters
    ----------
    cochain : Cochain
        The primal 1-`Cochain` to transform into a vector field.
    name : str, optional
        The name to give to the output `Cochain` instance. Default is 'Discrete vector field'.

    Returns
    -------
    Cochain or None
        A dual vector-valued 0-`Cochain` corresponding to the sought vector field.

    Notes
    -----
    In the present version, we can only transform a primal 1-`Cochain`
    into a dual vector-valued 0-`Cochain`.
    """
    if not _isvalid_for_sharp(cochain): return None
    
    vector_field = interpolate_cochain_on_nsimplices(cochain).sum(axis=1)

    return Cochain(cochain.complex, values=vector_field, 
                   dim=0, dual=True, name=name)

        
    

# ################# #
# Usefull functions #
# ################# #

# For the flat operator
# ---------------------
def _isvalid_for_flat(vector_field: np.ndarray[float], 
                      manifold: SimplicialManifold) -> bool:
    """
    Checks if a vector field can be flattened on a given manifold.

    Parameters
    ----------
    vector_field : np.ndarray
        The vector field to check.
    manifold : SimplicialManifold
        The Simplicial Manifold where the vector field is defined.

    Returns
    -------
    bool
        True if the vector field can be flattened, False otherwise.

    Notes
    -----
    The conditions to fulfill are:
      * Must be an instance of numpy.ndarray 
      * Shape must be (Nn, D) where Nn is the number of n-simplices
        within the simplicial manifold and D is the dimension of the
        embedding space.
      * The provided manifold must be an instance of `SimplicialManifold`.

    TODO
    ----
    Maybe it could be wise to check that the provided vector field 
    is indeed tangent everywhere to the n-simplices...
    """
    try:
        assert isinstance(manifold, SimplicialManifold), (
            'Vector fields can only be projected on SimplicialManifold'
            + f'not on {type(manifold)}')
        
        assert isinstance(vector_field, np.ndarray), (
            'Vector field must be provided as numpy.ndarray.')
        
        Nn = manifold[-1].size
        D = manifold.emb_dim
        assert vector_field.shape == (Nn, D), (
            f'Vector field shape ({vector_field.shape}) should be {(Nn, D)}.')

        logger.info(f'Flattening vector field as a 1-cochain.')
        return True

    except AssertionError as msg:
        logger.warning(msg)
        return False


def _dual_to_primal_flat(vector_field: np.ndarray[float], 
                         manifold: SimplicialManifold, name: str
                         ) -> Cochain:
    """
    Transforms a vector field into a primal 1-cochain.

    Parameters
    ----------
    vector_field : np.ndarray
        The vector field to convert.
    manifold : SimplicialManifold
        The `SimplicialManifold` where the vector field is defined.
    name : str
        The name to give to the flattened cochain.

    Returns
    -------
    Cochain
        The resulting primal 1-cochain defined on the prescribed manifold.

    Notes
    -----
    The vector field must be defined at the circumcenters of the n-simplices
    of the considered `SimplicialManifold`.

    As such, it can be seen as a vector-valued dual 0-cochain.

    Being converted into a primal 1-cochain, this explains the name of the
    present algorithm 'dual_to_primal'.

    It corresponds to the DPP-Flat defined in A. Hirani's PhD Thesis.

    See Also
    --------
    A. Hirani's PhD Thesis, section 5.5 (DPP flat, p.49)
    """
    projected_values = project(vector_field, on='primal', of=manifold)
    
    return Cochain(manifold, dim=1, values=projected_values, name=name)


def _dual_to_dual_flat(vector_field: np.ndarray[float], 
                       manifold: SimplicialManifold, name: str
                       ) -> Optional[Cochain]:
    """
    Transforms a vector field into a dual 1-cochain.

    Parameters
    ----------
    vector_field : np.ndarray
        The vector field to convert.
    manifold : SimplicialManifold
        The `SimplicialManifold` where the vector field is defined.
    name : str
        The name to give to the flattened cochain.

    Returns
    -------
    Cochain or None
        The resulting dual 1-cochain defined on the prescribed manifold.

    Notes
    -----
    The vector field must be defined at the circumcenters of the n-simplices
    of the considered `SimplicialManifold`.

    As such, it can be seen as a vector-valued dual 0-cochain.

    Being converted into a dual 1-cochain, this explains the name of the
    present algorithm 'dual_to_dual'.

    See Also
    --------
    A. Hirani's PhD Thesis, section 5.6 (DPD flat, p.54)
    """
    projected_values = project(vector_field, on='dual', of=manifold)

    return Cochain(manifold, dim=1, values=projected_values, 
                   dual=True, name=name)


def project(vector_field: np.array[float], on: str, of: SimplicialManifold
            ) -> np.ndarray[float]:
    """
    Projects a vector field onto the edges of a simplicial/cellular complex.

    Parameters
    ----------
    vector_field : np.ndarray
        The vector field to project.
    on : str
        Should either be 'primal' or 'dual'. Specifies on which complex
        the vector field should be projected: Either on the edges formed
        by the 1-simplices or the edges formed by the dual cells of the 
        (n-1)-simplices.
    of : SimplicialManifold
        The simplicial manifold where to project the vector field.

    Returns
    -------
    np.ndarray
        An array of shape (Nk,); Nk = manifold[n-1].size 
        containing the projected values.

    Notes
    -----
    The provided vector field must be defined as a vector-valued dual 
    0-cochain. Meaning that it must contain 1 vector per top-simplex of 
    the considered `SimplicialManifold`.
    """
    manifold = of
    n = manifold.dim
    
    if on == 'primal':
        edges = edge_vectors(manifold, normalized=True) 
        weights = edge_nsimplex_weight(manifold)

        return np.einsum('ij,ij->i', edges, weights @ vector_field)
    
    elif on == 'dual':
        vectors = [vector_field[cfids] for cfids in manifold.cofaces(n-1)]
        half_edges = _dual_half_edges_vectors(manifold, normalized=True)
        weights = _dual_half_edge_nsimplex_weights(manifold)
        signs = _dual_edges_orientation(manifold, half_edges)

        coefs = [sign * np.einsum('ij, i, ij -> i', hedgs, wghts, vcts) 
                for sign, hedgs, wghts, vcts 
                in zip(signs, half_edges, weights, vectors)]
        
        return np.asarray([coef.sum() for coef in coefs])
        

@typecheck(SimplicialManifold)
def _dual_half_edges_vectors(manifold: SimplicialManifold, 
                             normalized: bool = False, 
                             oriented_toward_nsimplex_centers: bool = False
                             ) -> list[np.ndarray[float]]:
    """
    Computes the vectors between circumcenters of n-1 and n simplices.

    Parameters
    ----------
    manifold : SimplicialManifold
        The `SimplicialManifold` to work on.
    normalized : bool, optional
        If True, returns unit vectors. Default is False.
    oriented_toward_nsimplex_centers : bool, optional
        If True, the half edges are oriented toward the top simplices circumcenters. Default is False.

    Returns
    -------
    list of np.ndarray
        A list of (Ncf, D) arrays. One array per (n-1)-simplex. D corresponds
        to the dimension of the embedding space and Ncf to the number of 
        top-simplices surrounding the considered (n-1)-simplex.

    Notes
    -----
    Ncf is either 1 or 2. 1 for (n-1)-simplices on the border of the 
    `SimplicialManifold` and 2 for the inner ones.

    By constructions the vectors are oriented toward the inside of 
    the top simplices. We use the `oriented_toward_nsimplex_centers` 
    argument to modify (eventually) this.

    Because in the main use case of this function, at least at its creation, 
    we need to align the half edges along the corresponding edges.
    """
    reorient = np.asarray([[-1],[1]])

    n = manifold.dim
    
    splx_centers = manifold[n-1].circumcenters
    top_splx_centers = manifold[n].circumcenters

    half_edge_vectors = []
    for sids, cfids in enumerate(manifold.cofaces(n-1)):
        
        nbr_cofaces = len(cfids)
        
        heads = top_splx_centers[cfids]
        origin = np.repeat(splx_centers[[sids]], repeats=nbr_cofaces, axis=0)
        
        vcts = heads - origin

        if (not oriented_toward_nsimplex_centers) and (vcts.shape[0]==2):
            vcts = np.multiply(reorient, vcts)
        
        if normalized:
            vcts /= lng.norm(vcts, axis=-1).reshape(*vcts.shape[:-1], 1)

        half_edge_vectors.append(vcts)

    return half_edge_vectors


def _dual_half_edge_nsimplex_weights(manifold: SimplicialManifold
                                     ) -> list[np.ndarray[float]]:
    """
    Computes the k-volume of the intersection between n-simplices and their faces.

    Parameters
    ----------
    manifold : SimplicialManifold
        The `SimplicialManifold` to work on.

    Returns
    -------
    list of np.ndarray
        A list of length N (=number of (n-1)-simplices). Each element of this 
        list corresponds to an array containing the sought coefficients.

    Notes
    -----
    The computed coefficients correspond to the 1-volumes of the 
    intersection between the dual 1-cell of a (n-1)-simplex and its 
    cofaces (n-simplices).

    These coefficients are stored as arrays (of ndim=1). The size of the 
    array corresponds to the number of cofaces. So for inner (n-1)-simplices 
    we will have arrays of size 2 and for those on the border of the 
    `SimplicialComplex` we will have arrays of size 1.
    """
    weights = edge_nsimplex_weight(manifold, for_operator='dual_to_primal_flat')
    return  [weights[sid].data for sid in np.unique(weights.nonzero()[0])]


def _dual_edges_orientation(manifold: SimplicialComplex, 
                            half_edges: list[np.ndarray[float]]
                            ) -> np.ndarray[int]:
    """
    Computes the proper signs of the dual `Cochain` coefficients. 

    Parameters
    ----------
    manifold : SimplicialManifold
        The `SimplicialManifold` to work on.
    half_edges : list of np.ndarray
        The list of half edges computed just prior to this.

    Returns
    -------
    np.ndarray
        A (N1,)-array filled with +/- 1.

    Notes
    -----
    This function is meant to be used in the `project()` function
    to compute the coefficient of the flat version of a vector field.
    """
    N1 = manifold[1].size
    full_edges = np.array([he.sum(axis=0) for he in half_edges])
    full_edges /= lng.norm(full_edges,axis=-1).reshape((N1,1))
    
    real_edges = edge_vectors(manifold, normalized=True, dual=True)
    sign = np.einsum('ij,ij->i', full_edges, real_edges)
    
    return np.round(sign).astype('i')

# For the sharp operator
# ---------------------

def _isvalid_for_sharp(cochain: Cochain) -> bool:
    """
    Checks if a cochain can be interpolated into a vector field.

    Parameters
    ----------
    cochain : Cochain
        The cochain to check.

    Returns
    -------
    bool
        True if the cochain can be interpolated, False otherwise.

    Notes
    -----
    The conditions to fulfill are:
      * Must be an instance of Cochain.
      * Must be a primal cochain.
      * Must be a 1-cochain.
      * N.B.: The two previous constraints should be addressed in the future...
      * Must be defined on a `SimplicialManifold` (so n-simplex circumcenters 
        are defined).
    """
    try:
        assert isinstance(cochain, Cochain), (
            'Wrong type of argument, please provide a Cochain as input.')
        
        assert not cochain.isdual, 'Sharp only works on primal cochains.'
        
        k = cochain.dim
        assert k == 1, f'Sharp only works on 1-cochains.'

        cplx = cochain.complex
        assert isinstance(cplx, SimplicialManifold), (
            'cochain can only be interpolated on SimplicialManifold'
            + f'not on {type(cplx)}')
        
        logger.info(f'Sharpening {k}-cochain into discrete vector field.')
        return True
    
    except AssertionError as msg:
        logger.warning(msg)
        return False


def interpolate_cochain_on_nsimplices(cochain: Cochain) -> np.ndarray[float]:
    """
    Interpolates a k-cochain on the circumcenters of the top-simplices.

    Parameters
    ----------
    cochain : Cochain
        The cochain to interpolate.

    Returns
    -------
    np.ndarray
        (Nn, Nk, D)-array containing the corresponding k-vector field.
        Nn: number of n-simplices, Nk: number of k-simplices, 
        D: embedding dimension.

    Notes
    -----
    In the computation we added a factor 2 in order to get the proper 
    results, but we don't know how or why it should be here. 
    We just noticed that without it the sharp(flat(vector_field)) 
    ended up being scaled by a factor 2 for regular complexes.

    TODO: understand where this factor 2 comes from, maybe:
    look into the divergence theorem, see chapter 6 of Hirani's thesis.
    """
    k = cochain.dim
    coef = cochain.values
    cplx = cochain.complex
    
    D = cplx.emb_dim
    Nn = cplx.shape[-1]
    Nk = cplx.shape[k]
    
    w_map = WhitneyMap.of(cplx, k, normalized=True)
    weights = edge_nsimplex_weight(cplx, 'sharp')

    kvct_shape= (D,D) if cochain.isvectorvalued else (1,D)
    kvector_field = np.zeros((Nn, Nk, *kvct_shape)) 
    for (i, j), base_vector in zip(w_map.indices, w_map.base):
        kvector_field[i,j,:] += 2 * np.outer(coef[j], 
                                             weights.T[i,j] * base_vector)
    
    if not cochain.isvectorvalued: kvector_field = kvector_field[:,:,0,:]

    return kvector_field

# For both
# --------

def edge_nsimplex_weight(on: SimplicialManifold, 
                         for_operator: str = 'dual_to_primal_flat'
                         ) -> sp.csr_matrix[float]:
    """
    Computes the edge_nsimplex_weight for each edge-n-Simplex couple.

    Parameters
    ----------
    on : SimplicialManifold
        The simplicial manifold we work on.
    for_operator : str, optional
        A flag to change the normalization factor depending on the use case.
        Should either be 'dual_to_primal_flat', '_dual_to_dual_flat', 'sharp' 
        or 'div'. Default is 'dual_to_primal_flat'.

    Returns
    -------
    sp.csr_matrix
        A (N1 x Nn)-sparse matrix that contains the sought edge_nsimplex_weight.

    Notes
    -----
    All edges (i.e. shared by multiple n-cofaces) have one weight for 
        each of their n-cofaces. 
      * The values of these weights depends on the operator to compute, 
        c.f. See also section for more details.
      * In the sharp and flat cases: For each edge, the sum of its
        edge_nsimplex_weight must egals one.
      * This condition seems validated only if the n-simplices 
        are well-centered.
      * With this definition, the divergence theorem for vector fields defined 
        as vector-values dual 0-forms is verified.

    See also
    --------
    Hirani's PhD Thesis for more details:
      * For the sharp weight formula:  Proposition 5.5.1, p.51. 
      * For the flat weight formula: Definition 5.8.1, p.58.
      * For the div weight formula: Lemma 6.1.2 p.60.
    """
    mfld, operator = on,  for_operator

    n = mfld.dim
    N1 = mfld.shape[1]
    Nn = mfld.shape[-1]
    chn_cplx = mfld._chain_complex

    if operator == 'sharp':
        splx_ids_chains = complex_simplicial_partition(chn_cplx)[0]
        ccenters = [mfld[i].circumcenters for i in range(n+1)]
        top_simplex_volumes = mfld[-1].volumes

    else:
        k = n-1 if operator=='dual_to_dual_flat' else 1

        splx_ids_chains = complex_simplicial_partition(chn_cplx,lowest_dim=k)[0]
        ccenters = [mfld[i].circumcenters for i in range(k, n+1)] 
        edge_covolumes = mfld[k].covolumes

    weight_matrix = sp.lil_matrix((N1, Nn), dtype=float)
    for (eid, nsid) in edge_nsimplex_couples(mfld):
        if operator in ['dual_to_primal_flat', 'dual_to_dual_flat', 'div']:

            ids = np.where((splx_ids_chains[:, 0] == eid) & 
                           (splx_ids_chains[:,-1] == nsid))
            
            covolume_intersection = volume_polytope(ccenters, 
                                                    splx_ids_chains[ids])

            weight_matrix[eid, nsid] = covolume_intersection
            
            if operator != 'div':
                weight_matrix[eid, nsid] /= edge_covolumes[eid]
                  
        elif operator == 'sharp':
            ids = np.where((splx_ids_chains[:, 1] == eid) & 
                           (splx_ids_chains[:,-1] == nsid))

            support_volume_intersection = volume_polytope(ccenters, 
                                                        splx_ids_chains[ids])
        
            weight_matrix[eid, nsid] = support_volume_intersection \
                / top_simplex_volumes[nsid]
        
        else:
            logger.warning(
                'Wrong operator name. Should be either sharp, flat or div.')
            return None

    return weight_matrix.tocsr()


def edge_nsimplex_couples(complex:SimplicialComplex)->np.ndarray[int]:
    """
    Couples together edge ids with their highest-dimensional cofaces ids.

    Parameters
    ----------
    complex : SimplicialComplex
        The SimplicialComplex to work on.

    Returns
    -------
    np.ndarray
        A Nc * 2 arrays each row corresponds to a couple (eid, nsid). 
    
    Note
    ----
    Each edge id (eid) can appear multiple times, depending on 
    its n-valence (i.e. number of n-cofaces). The number of row
    corresponds to the sum of the edge n-valences for all edges.
    """
    n = complex.dim

    eid_nsid_couples = [np.array([[eid]*len(sids), sids]).T
                        for eid, sids in enumerate(complex.cofaces(1, n))]
    
    return np.vstack(eid_nsid_couples)

