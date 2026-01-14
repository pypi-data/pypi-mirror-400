# -*- python -*-

# -*- coding: utf-8 -*-
#
#       dxtr.objects.Module
#
# This file contains one class:
#     - `Module`
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
from typing import Optional, Iterable

import numpy as np
import numpy.linalg as lng
import scipy.sparse as sp

from collections import UserList

from dxtr import logger
from dxtr.complexes import Simplex


class Module(UserList):
    """A container for all simplices of the same degree.

    Notes
    -----
    * This k-Module object differs a bit from
      the exact mathematical definition: In theory,
      the k-Module of a simplicial complex is composed
      by all the k'-simplices  with k' <= k. Here, 
      our k-Module only contains k-simplices.
    """

    def __init__(self, simplices:np.ndarray[int],
                 chain_complex:list[sp.csr_matrix[int]]) -> None:
        """Instanciates a k-Module"""
        super().__init__([Simplex(tuple(splx)) for splx in simplices])
        
        splx_nbr, splx_dim = simplices.shape

        self._vertex_indices = simplices.reshape(splx_nbr) if splx_dim==1 else simplices
        self._chain_complex = chain_complex
        self._vertices = None
        self._volumes = None
        self._covolumes = None
        self._circumcenters = None
        self._deficit_angles = None
        self._dihedral_angles = None
        self._well_centeredness = None

    @property
    def dim(self) -> int:
        """Topological dimension (k) of the considered k-Module.
        """
        return len(self[0]) - 1

    @property
    def size(self) -> int:
        """Number of simplices within the k-Module.
        """
        return len(self)

    @property
    def boundary(self) -> sp.csr_matrix[int]:
        """Incidence matrix between these k-simplices and their (k-1)-faces.
        """
        return self._chain_complex[self.dim]
    
    @property
    def coboundary(self) -> sp.csc_matrix[int]:
        """Transpose of the incidence matrix between the (k+1)-cofaces 
           and these k-simplices.
        """
        return self._chain_complex[self.dim+1].T.tocsr(copy=False)

    @property
    def adjacency(self) -> Optional[sp.csc_matrix[int]]:
        """Adjacency matrix, computed through the faces.
        """
        try:
            bnd = self.boundary
            assert bnd.data.shape[0] != 0, ('Cannot compute adjacency '
                + 'for 0-simplices, try the `coadjacency` method instead.')
            
            adj = bnd.T @ bnd
            adj -= sp.diags(adj.diagonal(), dtype=int)
            return adj
        
        except AssertionError as msg:
            logger.warning(msg)
            return None
    
    @property
    def coadjacency(self) -> Optional[sp.csr_matrix[int]]:
        """Coadjacency matrix, i,e. adjacency computed through the cofaces.
        """
        try:
            cbnd = self.coboundary
            assert cbnd.data.shape[0] != 0, ('Cannot compute co-adjacency '
                + 'for n-simplices, try the `adjacency` method instead.')
            
            cadj = cbnd.T @ cbnd
            cadj -= sp.diags(cadj.diagonal(), dtype=int)
            return cadj
        
        except AssertionError as msg:
            logger.warning(msg)
            return None

    @property
    def vertex_indices(self) -> np.ndarray[int]:
        """Indices of all the k-simplices within the Module."""
        return self._vertex_indices
    
    @property
    def vertices(self) -> Optional[np.ndarray[float]]:
        """Position vectors of all the vertices around each k-simplex.
        
        Note
        -----
        * The returned array is of shape N*(k+1)*D where:
            - N is the number of k-simplices.
            - k+1 is the number of vertices defining a k-simplex
            - D is the dimension of the embedding euclidean space.
        * These positions are computed by the `build_geometry` method 
          within the `SimplicialComplex` Class.
        * Returns None, in the case of an `AbstractSimplicialComplex`.
        """
        if self._vertices is None:
            return None
        else:
            return self._vertices[self._vertex_indices]

    @property
    def volumes(self) -> Optional[np.ndarray[float]]:
        """Volumes of all k-simplices.
        
        Note
        -----
        * These volumes are computed by the `build_geometry` method
          within the `SimplicialComplex` class.
        """
        return self._volumes

    @property
    def covolumes(self) -> Optional[np.ndarray[float]]:
        """Covolumes of all k-simplices.
        
        Note
        -----
        * These covolumes are computed by the `build_dual_geometry` method 
          within the `SimplicialComplex` class.
        """
        return self._covolumes

    @property
    def circumcenters(self) -> Optional[np.ndarray[float]]:
        """Circumcenter position vectors for all k-simplex.
        
        Note
        -----
        * The returned array is of shape N*D where:
            - N is the number of k-simplices.
            - D is the dimension of the embedding euclidean space.
        * These circumcenters are computed by the `build_dual_geometry` method 
          within the `SimplicialManifold` Class.
        """
        return self._circumcenters
    
    @property
    def deficit_angles(self) -> Optional[np.ndarray[float]]:
        """Gaussian curvature for all k-simplices.

        Notes
        -----
          * For now, gaussian curvature can only be computed for 
            0- & 1-simplices.
        """
        return self._deficit_angles
    
    @property
    def dihedral_angles(self) -> Optional[np.ndarray[float]]:
        """Gaussian curvature for all k-simplices.

        Notes
        -----
          * For now, gaussian curvature can only be computed for 
            0- & 1-simplices.
        """
        return self._dihedral_angles
    
    @property
    def well_centeredness(self) -> np.ndarray[bool]:
        """Well-centeredness for all k-simplices.

        Notes
        -----
          * The 'well-centeredness' of a k-simplex corresponds to the fact 
            that its circumcenter lies within its volume.
          * It is a measure of the *quality* of the complex.
          * By construction, 0- and 1-simplices are always well-centered.
          * This property is important to compute the covolumes of the faces of 
            the simplices.
        """
        return self._well_centeredness

    def closest_simplex_to(self, target:Iterable, 
                           index_only:bool=False) -> Optional[int|Simplex]:
        """Gets the k-simplex closest to a given position.

        Parameters
        ----------
        target
            The desired position.
        index_only 
            Optional (default is False)
            If True, only the index of the simplex within the provided Module 
            is returned otherwise, the Simplex instance is returned.

        Returns
        -------
            The seeked Simplex or its index.
        """

        target = np.asarray(target)
        positions = self.circumcenters
        n = positions.shape[-1]

        if not _has_proper_shape(target, n): 
            return None

        distance_to_target = lng.norm(positions - target, axis=1)

        sidx = distance_to_target.argmin()

        if index_only:
            return sidx
        else:
            return self[sidx]

    def set(self, property_name:str, values:np.ndarray[float]) -> None:
        """Sets the values of the simplex geometrical properties.
        
        Notes
        -----
          * Property_name should either be `vertices`, `volumes`, 
            `covolumes`, `circumcenters`, `deficit angles`, `dihedral angles` 
            or 'well-centeredness'.
        """
        try:
            assert property_name in ['vertex indices', 'vertices', 'volumes',
                                     'covolumes', 'circumcenters', 
                                     'deficit angles', 'dihedral angles', 
                                     'well-centeredness'], (
                f'The provided property ({property_name}) is not supported.')

            if property_name == 'vertex indices':
                self._vertex_indices = values

            if property_name == 'vertices':
                self._vertices = values

                for splx in self:
                    splx._vertices = values

            elif property_name == 'volumes':
                self._volumes = values
            
            elif property_name == 'covolumes':
                self._covolumes = values

            elif property_name == 'circumcenters':
                self._circumcenters = values
            
            elif property_name == 'deficit angles':
                self._deficit_angles = values
            
            elif property_name == 'dihedral angles':
                self._dihedral_angles = values
            
            elif property_name == 'well-centeredness':
                self._well_centeredness = values     
        
        except AssertionError as msg:
            logger.warning(msg)
            return None



# ################# #
# USefull functions #
# ################# #

def _has_proper_shape(arr:np.array[float], dim) -> bool:
    """Checks that an array has the proper shape.
    """
    n = arr.shape[0]
    
    try:
        assert arr.ndim == 1, f'{arr} must be a single position vector.'
        assert n == dim, f'{arr} should be a {dim}D vector, not {n}D.'
        return True
    
    except AssertionError as msg:
        logger.warning(msg)
        return False
    