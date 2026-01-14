# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.complexes.abstractsimplicialcomplex
#
# This file contains one class:
#     - `AbstractSimplicialComplex`
# and aslo some housekeeping functions used within this class.
#
#       File author(s):
#           Olivier Ali <olivier.ali@inria.fr>
#
#       File contributor(s):
#           Olivier Ali <olivier.ali@inria.fr>
#           Chao Huang <chao.huang@inria.fr>
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
import scipy.sparse.csgraph as csgraph
import sparse as sprs
from collections import UserList
from collections.abc import Iterable

from dxtr import logger
from dxtr.complexes import Module
from dxtr.math.topology import (star, closure, link, border, interior, 
                                count_permutations_between)


class AbstractSimplicialComplex(UserList):
    """Embodies the concept of abstract simplicial complex.
    
    Abstract Simplicial Complexes, ASC, are closed set of elements
    that are topologically related. No geometrical properties are
    considered here.
    """

    def __init__(self, indices: list[list[int]], 
                 name: Optional[str]=None) -> None:
        """Initializes an `AbstractSimplicialComplex` object.

        Parameters
        ----------
        indices : list of list of int
            The list of vertex indices forming the highest degree simplices.
        name : str, optional
            A name for the complex.
        """
        self.data = []
        self._top_simplex_orientations = None
        self._0_simplex_orientations = None
        self._chain_complex = []
        self._name = name
        self._adjacency_tensors = {}
        

        if _top_simplices_are_well_defined(indices):
            self.build_topology(indices)

    def __str__(self) -> str:
        """Returns the name of the complex.

        Returns
        -------
        str
            The name of the complex.
        """
        return self.name

    @property
    def name(self) -> str:
        """Gets the name of the complex.

        Returns
        -------
        str
            The name of the complex.
        """
        if self._name is None:
            return (
        f'{self.dim}D Abstract Simplicial Complex of shape {self.shape}.')
        else: 
            return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        """Sets a custom name for the complex.

        Parameters
        ----------
        new_name : str
            The new name for the complex.
        """
        self._name = new_name

    def __contains__(self, other: AbstractSimplicialComplex) -> bool:
        """Checks if one abstract simplicial complex contains another one.

        Parameters
        ----------
        other : AbstractSimplicialComplex
            The other abstract simplicial complex to check.

        Returns
        -------
        bool
            True if the other abstract simplicial complex is contained, False otherwise.

        Examples
        --------
        >>> asc0 = AbstractSimplicialComplex([[1,2,3,4]])
        >>> asc1 = AbstractSimplicialComplex([[1,2,4]])
        >>> asc1 in asc0
        True
        """
        if self.dim < other.dim:
            return False
        else:
            other_splcs = np.array(other.data[-1])
            self_splcs = np.array(self.data[other.dim])
            for other_splx in other_splcs:
                if (other_splx == self_splcs).all(1).any()  == False:
                    return False
            return True

    @property
    def isclosed(self) -> bool:
        """Tests if the n-complex is homeomorphic to a n-ball.

        Returns
        -------
        bool
            True if the complex is homeomorphic to a n-ball, False otherwise.
        
        Notes
        -----
        * The name of this property is confusing for it tests if the complex 
          is homeomorphic to a ball. For instance, a torus would return False.
        * Maybe a better definition would be based on Betty numbers?
        * The Euler characteristics of a n-dimensional ball is 1 + (-1)**n.
        
        See also
        --------
        * The wikipedia page on euler characteristics,  
          [its a start...](https://en.wikipedia.org/wiki/Euler_characteristic)
        """
        n = self.dim 
        return self.euler_characteristic == 1 + (-1) ** n

    @property
    def ispure(self) -> bool:
        """Checks if the considered simplicial complex is pure.

        Returns
        -------
        bool
            True if the complex is pure, False otherwise.
        
        Notes
        -----
        * A simplicial n-complex is said pure iff
            every k-simplices within it is a face of at least one n-simplex.
        * For more insight, see:
          [course by Keenan Crane](https://brickisland.net/DDGSpring2019/).
        """
        if self.dim == 0:
            return True

        for mtrx in self._chain_complex[1:-1]:
            vct = abs(mtrx).sum(axis=1)

            if np.any(vct == 0):
                return False

        return True

    @property
    def dim(self) -> int:
        """Gets the topologic dimension of the complex.

        Returns
        -------
        int
            The topologic dimension of the complex.
        """
        return len(self) - 1

    @property
    def shape(self) -> tuple[int]:
        """Gets the numbers of simplices for each dimension.

        Returns
        -------
        tuple of int
            The numbers of simplices for each dimension.
        """
        return tuple([mdl.size for mdl in self])

    @property
    def euler_characteristic(self) -> int:
        """Computes the Euler characteristic of the complex.

        Returns
        -------
        int
            The Euler characteristic of the complex.

        Notes
        -----
        * The Euler characteristic (chi) of a CW-complex is given by:
                         chi = sum_i((-1)^i * #splx_i)
        """
        return sum([(-1) ** i * nbr for i, nbr in enumerate(self.shape)])


    def get_indices(self, splcs: list[list[int]]) -> list[int]:
        """Gets the indices of the given simplices.

        Parameters
        ----------
        splcs : list of list of int
            The list of k-simplices to get the indices of, 
            all the simplices should have the same dimensions

        Returns
        -------
        list of int
            The indices of the given simplices
        """
        idxs = []
        dim = len(splcs[0])-1
        splcs = np.sort(splcs)
        for i, splx_self in enumerate(self.data[dim]._vertex_indices):
            if len(np.where((splcs == splx_self).all(axis=1))[0])!=0:
                idxs.append(i)
        return idxs


    def orientation(self, dim:Optional[int]=None) -> Optional[np.ndarray[int]]:
        """Returns the orientation of highest or lowest degree simplices.
        
        Parameters
        ----------
        dim : int, optional
            The topological dimension of the simplices we want the orientation of. 
            Should be either `self.dim` or 0. If None, the orientation of the top simplices is returned.
        
        Returns
        -------
        numpy.ndarray of int, optional
            An (N,)-shape array filled with 1 and -1.
        """

        if (dim is None) or (dim == self.dim):
            return self._top_simplex_orientations
        elif dim == 0:
            return self._0_simplex_orientations
        else:
            logger.warning('Orientation only defined on highest simplices.')
            return None


    def build_topology(self, indices: list[list[int]]) -> None:
        """Computes all faces and incidence matrices from the given simplices.

        Parameters
        ----------
        indices : list of list of int
            List of the vertex indices forming the highest degree simplices.

        Notes
        -----
        * This method is the heart of the `AbstractSimplicialComplex` class.
        * It computes the simplices of all degrees from the list of 
          the highest degree ones.
        * It also computes a coherent orientation for the top simplices.
        """

        simplices = []
        highest_splcs, *smlr_splcs = _format_simplices(indices)

        n = len(highest_splcs[0]) - 1

        logger.info(f'Building a {n}-Abstract Simplicial Complex with '
                    + f'{len(highest_splcs)} {n}-simplices')

        simplices.append(highest_splcs)
        
        k = n
        while k >= 1:
            faces = _compute_faces(simplices[0])

            if (len(smlr_splcs)!=0) and (len(smlr_splcs[0][0])==k):
                faces = add_lower_level_simplices_to_faces(faces, smlr_splcs)
            
            mtrx = _compute_incidence_matrix(faces)
            
            if k == n:
                self._top_simplex_orientations = _compute_orientation(mtrx)
                # We multiply each column of the incidence matrix by the
                # orientation of the top-simplices so for each row (i.e. face)
                # we have one +1 entry and one -1 entry.
                mtrx = mtrx.multiply(self._top_simplex_orientations).tocsr()


            self._chain_complex.insert(0, mtrx)
            if k == 1:
                self._0_simplex_orientations = _compute_orientation(mtrx.T)

            trimed_faces = remove_duplicated_simplices(faces)
            simplices.insert(0, trimed_faces)

            k -= 1

        add_null_incidence_matrices(self._chain_complex, simplices)

        self.data = _format_complex(simplices, self._chain_complex)


    def star(self, simplices:dict[int, list[int]]|list[int]|int,
             dim:Optional[int]=None) -> dict[int, list[int]]:
        """Gets the list of all coboundaries of a given simplex.
        
        Parameters
        ----------
        simplices : dict of int to list of int or list of int or int
            The list of simplex indices forming the chain we want the star of.
        dim : int, optional
            The topological dimension of the simplices we want the star of.

        Returns
        -------
        dict of int to list of int
            The keys are topological dimensions k.
            The values are lists of the k-simplex indices belonging to 
            the seeked star ensemble.

        Notes
        -----
        * See the `.math.topology` module for details.
        """

        if isinstance(simplices, dict):
            return star(self._chain_complex, simplices)
        elif dimension_is_specified(dim):
            return star(self._chain_complex, {dim: simplices})
        else:
            return None
            

    def closure(self, simplices:dict[int, list[int]]|list[int]|int,
                dim:Optional[int]=None) -> dict[int, list[int]]:
        """Gets the smallest simplicial complex containing the given simplices.

        Parameters
        ----------
        simplices : dict of int to list of int or list of int or int
            The list of simplex indices forming the chain we want the closure of.
        dim : int, optional
            The topological dimension of the simplices we want the closure of.

        Returns
        -------
        dict of int to list of int
            The keys are topological dimensions k.
            The values are lists of the k-simplex indices belonging to 
            the seeked closure ensemble.

        Notes
        -----
        * See the `.math.topology` module for details.
        """

        if isinstance(simplices, dict):
            return closure(self._chain_complex, simplices)
        elif dimension_is_specified(dim):
            return closure(self._chain_complex, {dim: simplices})
        else:
            return None


    def link(self, simplices:dict[int, list[int]]|list[int]|int,
            dim:Optional[int]=None) -> dict[int, list[int]]:
        """Gets the topological sphere surrounding the given simplices.

        Parameters
        ----------
        simplices : dict of int to list of int or list of int or int
            The list of simplex indices forming the chain we want the link of.
        dim : int, optional
            The topological dimension of the simplices we want the link of.

        Returns
        -------
        dict of int to list of int
            The keys are topological dimensions k.
            The values are lists of the k-simplex indices belonging to 
            the seeked link ensemble.

        Notes
        -----
        * See the `.math.topology` module for details.
        """

        if isinstance(simplices, dict):
            return link(self._chain_complex, simplices)
        elif dimension_is_specified(dim):
            return link(self._chain_complex, {dim: simplices})
        else:
            return None


    def border(self, simplices:Optional[dict[int, list[int]]]=None
               ) -> Optional[dict[int, list[int]]]:
        """Gets the subcomplex boundary of a pure complex.

        Parameters
        ----------
        simplices : dict of int to list of int, optional
            The list of simplex indices forming the chain we want the border of.
            If None, the whole ASC is considered.

        Returns
        -------
        dict of int to list of int, optional
            The keys are topological dimensions k.
            The values are lists of the k-simplex indices belonging to 
            the seeked border ensemble.

        Notes
        -----
        * If no simplices are specified, the whole ASC is considered.
        * To simplicify we only compute borders for pure complexes.
        * The provided indices should specify a pure (sub-)complex.
        * 0-simplices are considered to be their own borders.
        * If the provided complex is closed, the output is None.
        """

        if simplices is None:
            if self.isclosed:
                return None
            else:
                simplices = {self.dim: [i for i,_ in enumerate(self[-1])]}

        return border(self._chain_complex, simplices)


    def interior(self, simplices:Optional[dict[int, list[int]]]=None
                 ) -> dict[int, list[int]]:
        """Computes the interior of a subset of simplices.

        Parameters
        ----------
        simplices : dict of int to list of int, optional
            The list of simplex indices forming the chain we want the interior of.
            If None, the whole ASC is considered.

        Returns
        -------
        dict of int to list of int
            The keys are topological dimensions k.
            The values are lists of the k-simplex indices belonging to 
            the seeked interior ensemble.

        Notes
        -----
        * If no simplices are specified, the whole ASC is considered.
        * The provided indices should specify a pure (sub-)complex.
        * 0-simplices have no interior. In this case the output is set to None.
        """

        if simplices is None:
            simplices = {self.dim: [i for i,_ in enumerate(self[-1])]}

        return interior(self._chain_complex, simplices)


    def faces(self, simplex_dim:int,
              face_dim:Optional[int]=None) -> list[list[int]]:
        """Returns the list of face indices for all k-simplices.
        
        Parameters
        ----------
        simplex_dim : int
            The topological dimension of the considered simplices.
        face_dim : int, optional
            The topological dimension of the desired faces. 
            If None, the method consider `face_dim = simplex_dim-1`.

        Returns
        -------
        list of list of int
            The list of face indices for all simplices in the considered 
            k-Module.
        
        Notes
        -----
        * The parameters must verify: 0 <= face_dim <= simplex_dim <=self.dim.
        * If face_dim == simplex_dim, the list of simplex indices is returned.
        * This method may seem redundant with the `closure` method.
          Actualy, it is meant to be applied globally on the whole complex
          while the `closure` method is restricted to small subsets of
          simplices.
        * Its design makes it much faster and therefore suitable for processing
          the whole structure at once, especially during instantiation.
        """
        
        face_dim = face_dim if face_dim is not None else simplex_dim-1

        if not _dimensions_are_well_ordered(face_dim, simplex_dim, self.dim):
            return None
        
        if face_dim == simplex_dim:
            N = self[simplex_dim].size
            return np.arange(N).reshape(N, 1)
        
        nbr_splx = self.shape[simplex_dim]
        mtrx = sp.identity(nbr_splx, dtype=int)

        k = simplex_dim
        while k > face_dim:
            mtrx = abs(self[k].boundary) @ mtrx / (k+1)
            k -= 1

        faces = [[] for _ in range(mtrx.shape[1])]
        for fid, sid  in zip(mtrx.nonzero()[0], mtrx.nonzero()[1]):
            faces[sid].append(fid)
        
        if not isinstance(faces[0], Iterable): faces = [[fid] for fid in faces]

        return faces


    def cofaces(self, simplex_dim:int, 
                coface_dim:Optional[int]=None, 
                ordered:bool=False) -> list[list[int]]:
        """Returns the list of k'-coface indices for all k-simplices (k'>k).
        
        Parameters
        ----------
        simplex_dim : int
            The topological dimension of the considered simplices.
        coface_dim : int, optional
            The topological dimension of the desired cofaces.
            Default is simplex_dim+1. 
        ordered : bool, optional
            If True, for each simplex, the coface indices 
            are returned in the following order so we can loop around from one 
            coface to the neighboring one. Default is False.

        Returns
        -------
        list of list of int
            The list of coface indices for all simplices
            in the considered k-Module.
        
        Notes
        -----
        * The parameters must verify: 0<=simplex_dim<=coface_dim<=self.dim
        * This method may seem redundant with the `star` method.
          Actually, it is meant to be applied globally on the whole complex
          while the `star` method is designed to be applied on small subsets 
          of simplices.
        * Its design makes it much faster and therefore suitable for 
          processing the whole structure at once, especially during 
          instantiation.
        """
        
        coface_dim = coface_dim if coface_dim is not None else simplex_dim+1
        
        if not _dimensions_are_well_ordered(simplex_dim, coface_dim, self.dim):
            return None

        nbr_splx = self.shape[simplex_dim]
        mtrx = sp.identity(nbr_splx, dtype=int)
        
        k = simplex_dim
        while k < coface_dim:
            mtrx = abs(self[k].coboundary) @ mtrx / (k+1)
            k += 1

        cofaces = [[] for _ in range(mtrx.shape[1])]
        for cfid, sid  in zip(mtrx.nonzero()[0], mtrx.nonzero()[1]):
            cofaces[sid].append(cfid)
        
        if ordered:
            return ordered_splx_ids_loops(cofaces, self[coface_dim].adjacency)
        else:
            return cofaces


    def incidence_matrix(self, top_dim:int, low_dim:int
                         ) -> Optional[sp.csr_matrix[int]]:
        """Computes the incidence matrix between k-simplices and l-simplices.

        Parameters
        ----------
        top_dim : int
            The highest topological dimension (k) of the simplices to consider.
        low_dim : int
            The smallest topological dimension (l) of the simplices to consider.

        Returns
        -------
        scipy.sparse.csr_matrix of int, optional
            A sparse matrix of shape (Nl, Nk), filled with 0s and 1s, where Nl 
            and Nk are respectively the numbers of l-simplices and k-simplices.
        
        Notes
        -----
        * The (i,j)-element is 1 if the 0-simplex of index i is a l-face of 
          the k-simplex of index j.
        * If the 2 dimension are egal, the identity matrix is returned. 
        """
        try:
            assert low_dim <= top_dim, 'low_dim must be smaller than top_dim.'
        except AssertionError as msg:
            logger.warning(msg)
            return None
        
        if low_dim == top_dim:
            return sp.identity(self[top_dim].size, dtype=int).tocsr()

        mtrx = abs(self[top_dim].boundary)
        k = top_dim - 1
        while k > low_dim:
            mtrx = abs(self[k].boundary) @ mtrx / (k+1)
            k -= 1

        return mtrx.astype(bool).astype(int)


    def adjacency_tensor(self, k:int, l:int) -> sprs.COO[int]:
        """Returns the vertex-based adjacency between k, l & k+l simplices.

        Parameters
        ----------
        k : int
            The first topological dimension to consider.
        l : int
            The second topological dimension to consider.

        Returns
        -------
        sparse.COO of int
            A 3rd-order tensor filled with 0, 1 & -1
        
        Notes
        -----
        * This method is needed to compute the wedge product between `Cochain` 
          instances.
        * This method uses the `COO` class from the `sparse` library. Because 
          implementing such a tensor in its dense version in `numpy` would have 
          been too costing for large structures and higher-order sparse arrays 
          at not yet available in `scpipy.sparse`.
        """
        key = k, l
        
        if self._adjacency_tensors.get(key) is None:
            self._adjacency_tensors[key] = _compute_adjacency_tensor(self, k, l)
            
            if k != l :
                self._adjacency_tensors[key[::-1]] = \
                    self._adjacency_tensors[key].transpose((0, 2, 1))
        
        return self._adjacency_tensors[key]


# ################# #
# Usefull functions #
# ################# #

def _top_simplices_are_well_defined(indices: Iterable[int]) -> bool:
    """Checks that the provided indices are in the proper format.

    Parameters
    ----------
    indices : iterable of int
        The list of vertex indices forming the highest degree simplices.

    Returns
    -------
    bool
        True if the indices are well defined, False otherwise.
    """
    try:
        assert isinstance(indices, Iterable), (
            'A list of lists of indices must be provided.')

        for i, ids in enumerate(indices):
            assert isinstance(ids, Iterable), (
                    f'the {i}th element ({ids}) in the provided'
                    + 'list of top simplices is not iterable.')

        return True

    except AssertionError as msg:
        logger.warning(msg)
        return False


def _format_simplices(vals: list[list[int]]) -> list[np.ndarray]:
    """Converts raw input variables into usable structures.

    Parameters
    ----------
    vals : list of list of int
        A collection of groups of indices corresponding to the top simplices
        within the `AbstractSimplicialComplex` to build.

    Returns
    -------
    list of numpy.ndarray

    Notes
    -----
    * All items (i.e. list of indices) in the input list do not necesseraly
      have the same length. This means that the provided top-simplices might 
      not have the same degree. In such a case, the generated complex will not 
      be *pure*.
    
    See also
    --------
    * For details about *purity* of simplicial complexes, see 
      [course by Keenan Crane](https://brickisland.net/DDGSpring2019/).
    """

    degrees = list(set(map(len, vals)))
    degrees.sort(reverse=True)

    simplices = [np.sort(np.asarray([x for x in vals if len(x) == s],
                                    dtype=int),
                         axis=1) for s in degrees]

    # Simplices lexicographic sorting
    ordered_simplices = []
    for splcs in simplices:
        splx_dim = splcs.shape[1]
        sorting_order = [splcs[:, i] for i in np.arange(splx_dim)[::-1]]
        ordered_simplices.append(splcs[np.lexsort(sorting_order), :])

    # To remove the duplicates in the highest simplices
    ordered_simplices = [np.unique(x, axis=0) for x in ordered_simplices]

    return ordered_simplices


def _compute_faces(simplices: np.ndarray[int]) -> np.ndarray[int]:
    """Computes the (K-1)-faces of a set of N  K-simplices.

    Parameters
    ----------
    simplices : numpy.ndarray of int
        Each of the N rows contains the K+1 indices
        of a K-simplex and its orientation (+/-1).

    Returns
    -------
    numpy.ndarray of int
        Each of the N*(K+1) rows contains the K indices of a (K-1)-face
        with its orientation (+/-1) and the index of the corresponding K-simplex.

    Notes
    -----
    * Faces common to two simplices will appear twice.
    * This seems to work fine to construct the Simplicial Complexes. 
      However, the fact that shared faces are duplicated could be 
      not satisfactionary, one could add a boolean switch to control this...
    """
    splx_nbr = simplices.shape[0]
    splx_dim = simplices.shape[1]

    # Compute faces, relative orientation & coboundary indices.
    orientation = np.ones((splx_nbr, 1), dtype=int)
    indices = np.arange(splx_nbr).reshape(splx_nbr, 1)
    faces = [np.hstack((np.delete(simplices, i, axis=1),
                        orientation * (-1) ** i,
                        indices))
             for i in np.arange(splx_dim)]

    faces = np.vstack(faces)

    # Final lexicographic Re-sorting
    sorting_order = [faces[:, i] for i in np.arange(splx_dim)[::-1]]

    return faces[np.lexsort(sorting_order), :]


def add_lower_level_simplices_to_faces(faces:np.ndarray[int], 
                              smlr_splcs:list[int]) -> np.ndarray[int]:
    """Add lower degree simplices provided as input to the complex.

    Parameters
    ----------
    faces : numpy.ndarray of int
        The array of faces to which lower degree simplices will be added.
    smlr_splcs : list of int
        The list of lower degree simplices to add.

    Returns
    -------
    numpy.ndarray of int
        The updated array of faces with lower degree simplices added.
    """
    splcs = smlr_splcs.pop(0)
    splx_nbr = splcs.shape[0]
    
    splcs = np.hstack((splcs, np.zeros((splx_nbr, 2),
                                        dtype=int)))
    
    return np.vstack((faces, splcs))


def _compute_incidence_matrix(faces: np.ndarray[int]) -> sp.csr_matrix[int]:
    """Computes the incidence matrix between  M K- & N (K-1)-simplices.

    Parameters
    ----------
    faces : numpy.ndarray of int
        (N*M) * (K+2) array: Each row = one face.
        K first columns = (K-1)-simplex indices.
        K+1 column = relative orientation, value in {-1, 0, 1}.
        last column = indice of the related (K+1)-simplex.

    Returns
    -------
    scipy.sparse.csr_matrix of int
        N*M sparse matrix, format = (data, (row_ids, col_ids)).
        rows_ids = indices the (K-1)-simplices (faces).
        col_ids = indices of the K-simplices.
        data = relative orientation between them, values in {-1, 0, 1}.
    """

    faces, orient, splx_ids = np.split(faces, [-2, -1], axis=1)

    _, face_ids = np.unique(faces, return_inverse=True, axis=0)

    orient = orient.flatten()
    splx_ids = splx_ids.flatten()

    return sp.csr_matrix((orient, (face_ids, splx_ids)))


def _compute_orientation(mtrx:sp.csr_matrix[int]) -> np.ndarray[int]:
    """Computes the orientation of a k-Module from its incidence matrix.

    Parameters
    ----------
    mtrx : scipy.sparse.csr_matrix of int
        The M*N incidence matrix between N simplices and their M faces.

    Returns
    -------
    numpy.ndarray of int
        An array of shape (Nk, 1), filled with {-1, 1}. Corresponds to the 
        orientation of the Nk k-simplices that will generate a proper 
        computation of their incidence matrix.
    
    Notes
    -----
    * For k-Module containing disjoint 'sub-Modules' (this can happen in 
      non-manifold-like complexes), we need to  initialize the `orient` array 
      to 1 for each 'sub-Modules'. This is done using the 
      `csgraph.connected_components()` method to find the 'sub-Module'.
    """
    
    adj_mtrx = - mtrx.T @ mtrx
    adj_mtrx -= sp.diags(adj_mtrx.diagonal())

    splx_nbr = adj_mtrx.shape[0]

    # To calculate the connected components, the orientations in different 
    # components will be considered separately.
    num_components, labels = csgraph.connected_components(adj_mtrx)

    orient = np.zeros(splx_nbr)
    for label in range(num_components):
        orient[np.where(labels==label)[0][0]] = 1

    while list(orient).count(0) > 0:
        orient += adj_mtrx.dot(orient)
        orient = np.array([int(x / abs(x)) if x != 0 else x
                           for x in orient])
    return orient.astype(int)


def remove_duplicated_simplices(faces: np.ndarray[int]) -> np.ndarray[int]:
    """Remove simplices that could have been generated twice.

    Parameters
    ----------
    faces : numpy.ndarray of int
        The array of faces from which duplicated simplices will be removed.

    Returns
    -------
    numpy.ndarray of int
        The updated array of faces with duplicated simplices removed.
    """
    _, ids = np.unique(faces[:, :-2], axis=0, return_index=True)

    return faces[ids, :-2]


def add_null_incidence_matrices(chain_complex: list[sp.csr_matrix[int]],
                                simplices: np.array[int]) -> None:
    """Add null matrices on both sides of the chain complex.

    Parameters
    ----------
    chain_complex : list of scipy.sparse.csr_matrix of int
        The list of incidence matrices forming the chain complex.
    simplices : numpy.ndarray of int
        The array of simplices in the complex.
    
    Notes
    -----
    In order to compute properly the differential operators, we need to be able
    to send 0-simplices to 0 with the `boundary` function and the n-simplices as 
    well with the `coboundary` one.
    """

    for k in [0, -1]:
        Nk = simplices[k].shape[0]
        mtrx = sp.csr_matrix((Nk, Nk), dtype=int)

        if k == 0:
            chain_complex.insert(0, mtrx)
        else:
            chain_complex.append(mtrx.T)


def _format_complex(simplices, chain_complex) -> list[Module]:
    """Organize the complex into a list of k-chains.

    Parameters
    ----------
    simplices : list of numpy.ndarray
        The list of simplices in the complex.
    chain_complex : list of scipy.sparse.csr_matrix of int
        The list of incidence matrices forming the chain complex.

    Returns
    -------
    list of Module
        The list of k-chains forming the complex.
    """
    return [Module(splcs, chain_complex) for splcs in simplices]


def dimension_is_specified(dim: Optional[int]) -> bool:
    """Checks that the parameter `dim` is not None.

    Parameters
    ----------
    dim : int, optional
        The dimension to check.

    Returns
    -------
    bool
        True if the dimension is specified, False otherwise.
    """
    try:
        assert dim is not None, 'A dimension must be specified.'
        return True

    except AssertionError as msg:
        logger.warning(msg)
        return False


def _dimensions_are_well_ordered(lower_dim: int, upper_dim: int,
                                complex_dim: int) -> bool:
    """Checks simplex/face dimensions are properly hierarchized.

    Parameters
    ----------
    lower_dim : int
        The lower dimension to check.
    upper_dim : int
        The upper dimension to check.
    complex_dim : int
        The dimension of the complex.

    Returns
    -------
    bool
        True if the dimensions are well ordered, False otherwise.
    """
    try:
        assert 0 <= lower_dim <= upper_dim <= complex_dim, (
                f'Cannot get {lower_dim}-faces of {upper_dim}-cofaces ' +
                f'in a {complex_dim}-complex.')
        return True

    except AssertionError as msg:
        logger.warning(msg)
        return False


def ordered_splx_ids_loops(indices:list[list[int]], 
                           adjacency:sp.csr_matrix[int]) -> list[list[int]]:
    """Organizes face/coface indices in following order.

    Parameters
    ----------
    indices : list of list of int
        All the lists of the k-simplex indices to sort.
    adjacency : scipy.sparse.csr_matrix of int
        The adjacency matrix of the corresponding k-simplices.

    Returns
    -------
    list of list of int
        Same as the input but each element is now in following order.
    """
    rows, cols = adjacency.nonzero()

    return [order_index_loop(ids, rows, cols) for ids in indices]


def order_index_loop(indices: list[int],
                     rows: np.ndarray[int],
                     cols: np.ndarray[int]) -> list[int]:
    """Sorts a list of simplex indices forming a loop in a following order.

    Parameters
    ----------
    indices : list of int
        List of indices to order.
    rows : numpy.ndarray of int
        Rows of nonzero elements in the simplex adjacency matrix.
    cols : numpy.ndarray of int
        Columns of nonzero elements in the simplex adjacency matrix.

    Returns
    -------
    list of int
        The seeked sorted list.
    
    Notes
    -----
    * Prior to running this function, an adjacency matrix must be computed.
    * The attributes rows and cols are extracted from such a matrix:
        `cols, rows = adjacency.nonzero()`
    """

    ordered_indices = [indices.pop(0)]

    while len(indices) > 1:
        next_cfid = list(set(rows[cols == ordered_indices[-1]]) &
                         set(indices))[0]
        ordered_indices.append(next_cfid)
        indices.remove(next_cfid)

    ordered_indices += indices

    return ordered_indices


def _compute_adjacency_tensor(complex:AbstractSimplicialComplex, 
                              k:int, l:int) -> sprs.COO[int]:
    """Computes a vertex-based adjacency tensor between k, l and k+l simplices.

    Parameters
    ----------
    complex : AbstractSimplicialComplex
        The `AbstractSimplicialComplex` instance to work on.
    k : int
        The first topological dimension to consider.
    l : int
        The second topological dimension to consider.

    Returns
    -------
    sparse.COO of int
        A 3rd-order tensor filled with 0, 1 & -1
    
    Notes
    -----
    * This method uses the `COO` class from the `sparse` library. Because 
      implementing such a tensor in its dense version in `numpy` would have 
      been too costing for large structures and higher-order sparse arrays 
      at not yet available in `scpipy.sparse`.
    """
    Nkl, Nk, Nl = complex[k+l].size, complex[k].size, complex[l].size
    
    l_neighbors_of_k_simplices = _neighbors_through_vertices(complex, k, l)
    
    nz_indices = _nonzero_element_indices(complex.faces(k+l, k), 
                                          complex.faces(k+l, l), 
                                          l_neighbors_of_k_simplices)

    kl_simplices = complex[k+l].vertex_indices[nz_indices[:, 0]]
    k_simplices = complex[k].vertex_indices[nz_indices[:, 1]]
    l_simplices = complex[l].vertex_indices[nz_indices[:, 2]]

    data = (-1) ** _relative_parity(kl_simplices, k_simplices, l_simplices)

    return sprs.COO(nz_indices.T, data, shape=(Nkl, Nk, Nl))


def _neighbors_through_vertices(complex:AbstractSimplicialComplex, 
                                simplex_dim_1:int, simplex_dim_2:int
                                ) -> list[np.ndarray[int]]:
    """Gets for each k-simplex the l-simplices sharing exactly 1 vertex with it.

    Parameters
    ----------
    complex : AbstractSimplicialComplex
        The `AbstractSimplicialComplex` to work on.
    simplex_dim_1 : int
        The topological dimension (k) of the simplices of interest.
    simplex_dim_2 : int
        The topological dimension (l) of the neighbors of interest.

    Returns
    -------
    list of numpy.ndarray of int
        A list on length Nk (number of k-simplices) where each element is an 
        array containing the indices of the l-simplices sharing exactly 1 
        0-face with it.
    
    Notes
    -----
    * This function is useful for the wedge product algorithm.
    """
    
    k, l = simplex_dim_1, simplex_dim_2

    kl_mtrx = complex.incidence_matrix(l, 0).T @ complex.incidence_matrix(k, 0)
    
    # Keeping only the couples of k- & l-simplices sharing exactly one 0-face.
    kl_mtrx.data[kl_mtrx.data != 1] = 0
    kl_mtrx.eliminate_zeros()

    lsplx_indices, ksplx_indices = kl_mtrx.nonzero()

    return [lsplx_indices[ksplx_indices==idx] for idx in range(complex[k].size)]


def _nonzero_element_indices(k_faces:np.ndarray[int], l_faces:np.ndarray[int], 
                             l_neighbors:list[np.ndarray[int]]
                             ) -> list[list[int]]:
    """Computes the indices of non-zeros elements in the adjacency tensor.

    Parameters
    ----------
    k_faces : numpy.ndarray of int
        The indices of the k-faces of each of the considered (k+l)-simplices. 
    l_faces : numpy.ndarray of int
        The indices of the l-faces of each of the considered (k+l)-simplices. 
    l_neighbors : list of numpy.ndarray of int
        For each k-simplex of the considered complex, the array of all the 
        l-simplices sharing exactly one 0-face with it.

    Returns
    -------
    numpy.ndarray of int
        An array containing the triplex of indices where the adjacency tensor 
        should be either +1 or -1.
    """
    nonzero_elements = []
    for kl_idx, (k_ids, l_ids) in enumerate(zip(k_faces, l_faces)):
    
        l_nghbrs = [list(set(l_neighbors[k_idx]) & set(l_ids)) 
                    for k_idx in k_ids]
        
        nonzero_elements += [[kl_idx, k_idx, l_idx] 
                             for k_idx, l_ids in zip(k_ids, l_nghbrs) 
                             for l_idx in l_ids]
    
    return np.asarray(nonzero_elements)


def _relative_parity(kl_simplices:np.ndarray[int],
                     k_simplices:np.ndarray[int],
                     l_simplices:np.ndarray[int]) -> np.ndarray[int]:
    """Computes the relative parity between k & l faces of k+l simplices.

    Parameters
    ----------
    kl_simplices : numpy.ndarray of int
        A (Nkl, k+l+1)-array where each row corresponds to the vertex indices 
        of all the Nkl considered (k+l)-simplices. 
    k_simplices : numpy.ndarray of int
        A (Nk, k+1)-array where each row corresponds to the vertex indices of 
        all the Nk considered k-simplices.
    l_simplices : numpy.ndarray of int
        A (Nl, l+1)-array where each row corresponds to the vertex indices of 
        all the Nl considered l-simplices.

    Returns
    -------
    numpy.ndarray of int
        A 1D array filled with 0 & 1.
    
    Notes
    -----
    * The 0 & 1 correspond to the relative parity between a k- & a l-faces of 
      a given (k+l)-simplex. This k- & l-faces must share a common 0-face.
    * The parity computation is based on the number of permutations between 
      the list of indices of the (k+l)-simplex and the concatenation of the 
      indices of the k- & l-faces.
    * If this number of permutations is even, the parity is 0 else it is 1.
    * To this number of permutations we add a *shift* that corresponds to the 
      number of required permutations to *"move the k-simplex in the right place within the l-simplex"*.
    """
    
    if kl_simplices.ndim == 1: 
        kl_simplices = kl_simplices.reshape(kl_simplices.shape[0], 1)
    if k_simplices.ndim == 1: 
        k_simplices = k_simplices.reshape(k_simplices.shape[0], 1)
    if l_simplices.ndim == 1: 
        l_simplices = l_simplices.reshape(l_simplices.shape[0], 1)

    parity = []
    for lsplx, ksplx, nsplx in zip(l_simplices, k_simplices, kl_simplices):
        
        idx = np.where(np.isin(lsplx, ksplx))[0][0]
        kl_splx = list(lsplx)[:idx] + list(ksplx) + list(lsplx)[idx+1:]
        
        shift = idx * (len(ksplx) - 1)
        
        parity += [(count_permutations_between(kl_splx, nsplx) + shift) % 2]

    return np.asarray(parity)

