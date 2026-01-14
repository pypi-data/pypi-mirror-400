# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.math.topology
#
# This submodule contains useful functions to compute
# topological properties on abstract simplicial complexes.
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
#       https://www.gnu.org/licenses/lgpl-3.0.en.html
#
# -----------------------------------------------------------------------
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np
import scipy.sparse as sp
from dxtr import logger


def star(chain_complex: list[sp.csr_matrix[int]], 
         simplices: dict[int, list[int]]) -> dict[int, list[int]]:
    """Gets the list of all coboundaries of a given simplex.

    Parameters
    ----------
    chain_complex : list of scipy.sparse.csr_matrix of int
        The list of incidence matrices forming the chain complex.
    simplices : dict of int to list of int
        The list of simplex indices forming the chain we want the star of.

    Returns
    -------
    dict of int to list of int
        The keys are topological dimensions k.
        The values are lists of the k-simplex indices belonging to 
        the seeked star ensemble.
    """

    cochain_complex = [mtrx.T for mtrx in chain_complex[1:]]
    Nn = chain_complex[-1].shape[1]
    zero_mtrx = sp.csr_matrix((Nn, 1), dtype=int)
    cochain_complex.append(zero_mtrx.T)

    n = len(cochain_complex)
    kmin = min(simplices.keys())

    star = {k: [] for k in range(kmin, n)}

    for k, ids in simplices.items():
        
        if not isinstance(ids, Iterable):
            ids = [ids]
        elif not isinstance(ids, list):
            ids = list(ids)

        star[k] += ids

        coboundary = abs(cochain_complex[k][:, ids])
        for q in range(k+1, n):
            star[q] += list(coboundary.nonzero()[0])
            coboundary = abs(cochain_complex[q]) @ coboundary

    return {k: list(np.unique(cbnd).astype(int))
            for k, cbnd in star.items()
            if len(cbnd) != 0}


def closure(chain_complex: list[sp.csr_matrix[int]], 
            simplices: dict[int, list[int]]) -> dict[int, list[int]]:
    """Gets the smallest simplicial complex containing the given simplices.

    Parameters
    ----------
    chain_complex : list of scipy.sparse.csr_matrix of int
        The list of incidence matrices forming the chain complex.
    simplices : dict of int to list of int
        The list of simplex indices forming the chain we want the closure of.

    Returns
    -------
    dict of int to list of int
        The keys are topological dimensions k.
        The values are lists of the k-simplices indices belonging to 
        the seeked closure ensemble.
    """

    kmax = max(simplices.keys())

    if kmax < 0: return {0: []}

    closure = {k: [] for k in range(kmax+1)}

    for k, ids in sorted(simplices.items())[::-1]:
        
        if not isinstance(ids, Iterable):
            ids = [ids]
        elif not isinstance(ids, list):
            ids = list(ids)

        closure[k] += ids

        boundary = abs(chain_complex[k][:, ids])
        for q in range(k-1, -1, -1):
            closure[q] += list(boundary.nonzero()[0])
            boundary = abs(chain_complex[q]) @ boundary
            
    return {k: list(np.unique(bnd).astype(int))
            for k, bnd in closure.items()}


def link(chain_complex: list[sp.csr_matrix[int]], 
         simplices: dict[int, list[int]]) -> dict[int, list[int]]:
    """Gets the topological sphere surrounding the given simplices.

    Parameters
    ----------
    chain_complex : list of scipy.sparse.csr_matrix of int
        The list of incidence matrices forming the chain complex.
    simplices : dict of int to list of int
        The list of simplex indices forming the chain we want the link of.

    Returns
    -------
    dict of int to list of int
        The keys are topological dimensions k.
        The values are lists of the k-simplices indices belonging to 
        the seeked link ensemble.
    """

    closure_star = closure(chain_complex, star(chain_complex, simplices))
    star_closure = star(chain_complex, closure(chain_complex, simplices))

    link = {k: list(set(closure_star[k]) - set(star_closure[k]))
            for k in closure_star.keys()}

    return {k: sorted(splcs)
            for k, splcs in link.items()
            if len(splcs) > 0}


def border(chain_complex: list[sp.csr_matrix[int]], 
           simplices: dict[int, list[int]]) -> dict[int, list[int]]:
    """Gets the subcomplex boundary of a pure complex.

    Parameters
    ----------
    chain_complex : list of scipy.sparse.csr_matrix of int
        The list of incidence matrices forming the chain complex.
    simplices : dict of int to list of int
        The list of simplex indices forming the chain we want the border of.

    Returns
    -------
    dict of int to list of int
        The keys are topological dimensions k.
        The values are lists of the k-simplices indices belonging to 
        the seeked border ensemble.
    """

    kmax = max(simplices.keys())
    
    top_sids = simplices[kmax]
    top_boundary = chain_complex[kmax][:, top_sids]

    outer_face_ids = np.where(abs(top_boundary.sum(axis=1)) == 1)[0]
    return closure(chain_complex, {kmax-1: outer_face_ids})


def interior(chain_complex: list[sp.csr_matrix[int]], 
             simplices: dict[int, list[int]]) -> dict[int, list[int]]:
    """Computes the interior of a subset of simplices.

    Parameters
    ----------
    chain_complex : list of scipy.sparse.csr_matrix of int
        The list of incidence matrices forming the chain complex.
    simplices : dict of int to list of int
        The list of simplex indices forming the chain we want the interior of.

    Returns
    -------
    dict of int to list of int
        The keys are topological dimensions k.
        The values are lists of the k-simplices indices belonging to 
        the seeked interior ensemble.
    """

    clsr = closure(chain_complex, simplices)
    borders = border(chain_complex, clsr)

    interior = {k: list(set(splcs_ids) - set(borders[k]))
                if k in borders.keys()
                else splcs_ids
                for k, splcs_ids in clsr.items()}

    return {k: int_ids for k, int_ids in interior.items()
            if int_ids}


def complex_simplicial_partition(chain_complex:list[sp.csr_matrix[int]],
                                 lowest_dim:int=0) -> list[np.ndarray[int]]:
    """Partitions the dual cells of the considered simplices into simplices.

    Parameters
    ----------
    chain_complex : list of scipy.sparse.csr_matrix of int
        The list of incidence matrices forming the chain complex.
    lowest_dim : int
        The topological dimension (k) of k-simplicies to start the enumeration with. Optional, the default is 0. 


    Returns
    -------
    list of np.ndarray of int
        The partitioned dual cells.
    """

    indices = []
    
    for bnd in chain_complex[-2:lowest_dim:-1]:
        if len(indices)==0:
            indices.append(np.vstack(bnd.nonzero()).T)
        else:
            new_indices = []
            for ids in np.vstack(bnd.nonzero()).T:
                cfids = np.where(indices[-1][:,0]==ids[-1])[0]
                cfnbr = cfids.shape[0]
                new_indices.append(np.hstack((ids[0]*np.ones((cfnbr, 1),
                                                             dtype=int),
                                              indices[-1][cfids])))
            indices.append(np.vstack(new_indices))

    return indices[::-1]


def cell_simplicial_partition(chain_complex: list[sp.csr_matrix[int]], 
                              simplex_idx: int, simplex_dim: int) -> list[np.ndarray[int]]:
    """Partitions the dual cells of a given simplex into simplices.

    Parameters
    ----------
    chain_complex : list of scipy.sparse.csr_matrix of int
        The list of incidence matrices forming the chain complex.
    simplex_idx : int
        The index of the simplex to partition.
    simplex_dim : int
        The topological dimension of the simplex to partition.

    Returns
    -------
    list of np.ndarray of int
        The partitioned dual cells.
    """

    n = len(chain_complex) - 2

    try:
        assert simplex_dim < n, 'Simplex dim must be strictly smaller than complex dim.'
        assert not isinstance(simplex_idx, Iterable), (
            'Do not support lists of indices as argument.')
    
    except AssertionError as msg:
        logger.warning(msg)
        return None
    
    sids = [simplex_idx]

    while simplex_dim < n:
        new_sids = []
        for idx in sids:
            if not isinstance(idx, Iterable): idx = [idx]

            for cf_id in star(chain_complex, {simplex_dim: idx[-1]})[simplex_dim+1]:
                new_sids.append(idx+[cf_id])

        sids = new_sids
        simplex_dim += 1

    return sids


def count_permutations_between(arr1: list[int], arr2: list[int]) -> int:
    """Counts the number of permutations between two arrays.

    Parameters
    ----------
    arr1 : list of int
        The first array.
    arr2 : list of int
        The second array.

    Returns
    -------
    int
        The number of permutations between the two arrays.
    """

    try:
        nbr_ids = len(arr1)
        assert len(arr2) == nbr_ids, 'Input lists must have the same length.'
        assert np.isin(arr1, arr2).all(), (
                        'Input lists must contain the same elements.')
    except AssertionError as msg:
        logger.warning(msg)
        return None

    index_map = {value: idx for idx, value in enumerate(arr2)}
    target_indices = [index_map[value] for value in arr1]
    
    visited = [False] * nbr_ids
    
    perm_nbr = 0
    for idx in range(nbr_ids):
        if not visited[idx]:
            perm_nbr += permutation_number_in_swap_cycle(target_indices, idx, 
                                                         visited)

    return perm_nbr


def permutation_number_in_swap_cycle(unsorted_indices:list[int],
                                     starting_index:int, 
                                     visited:list[bool])-> int:
    """Computes the number of permutations within a swap cycle.

    Parameters
    ----------
    unsorted_indices
        An unsorted list of the n first integers, starting at 0.
    starting_index
        The place on the list where to test for a swap cycle.
    visited
        A list of boolean values of the same size of `unsorted_indices`, 
        saying if the various starting_indices have ready been tasted.

    Returns
    -------
        The desired number of permutations.

    Notes
    -----
      * A swap cycle corresponds to a series of swaps that enable to put back 
        a series of indices in their rightful places.
        Examples: 
        1. in the following unsorted list of indices [2,1,0] there is a 
           swap cycle of size 1 that permits to put '2' and '0' in their 
           correct place: 2->0
        2. in [2,1,3,0] there is a swap cycle of size 2: 2->3->0.
      * The point of the method is to find out if such a cycle starting a given 
        position (`starting_index`) exist. And if so, to compute the number of 
        permutations required to move the corresponding indices to their 
        sorted position.
    """

    cycle_size = 0
    permutation_number = 0
    idx = starting_index
    
    while not visited[idx]:
        visited[idx] = True
        target_idx = unsorted_indices[idx]
        permutation_number += abs(target_idx-idx)
        cycle_size += 1    
        idx = target_idx
    
    cycle_size -= 1
    
    return permutation_number - cycle_size
