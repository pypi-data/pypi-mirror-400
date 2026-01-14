# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.objects.simplex
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
import numpy as np
from dataclasses import dataclass, field
from typing import Optional

from dxtr import logger
from dxtr.math.geometry import circumcenter, volume_simplex


@dataclass(eq=True)
class Simplex(tuple):
    """Implements the concept of simplex.

    Notes
    -----
      * As a subclasse of `tuple`, instances of `Simplex`
        can be compared to np.ndarray[int].
      * The volume property computes the volume when called.
        It might be time consuming on large complexes.
        That is why volumes are also stored within the Module.
      * 0-simplices are assigned a null volume by convention.
      * TODO? Should add a test to be sure that the number
        of vertices matches the number of indices.
    """

    indices: tuple[int] = field(default_factory=tuple, repr=True)
    _vertices: np.array[float] = field(default=None, repr=False)

    @property
    def vertices(self)-> np.ndarray[float]:
        """The position vectors of the nodes."""
        if self.isabstract:
            return None
        else:
            ids = self.indices[0] if self.dim == 0 else list(self.indices)
            return self._vertices[ids]
    
    @property
    def dim(self) -> int:
        """The topological dimension (k) of the k-simplex."""
        return len(self.indices) - 1

    @property
    def volume(self) -> Optional[float]:
        """The k-volume of the k-simplex. 

        Note
        ----
            The volume is set to None if the simplex is abstract.
        """
        if self.isabstract:
            logger.warning('Abstract simplices do not have volumes.')
            return None
        elif self.dim == 0:
            return 0
        else:
            return volume_simplex(self.vertices)

    @property
    def circumcenter(self) -> Optional[np.ndarray[float]]:
        """The circumcenter of the k-simplex.
        
        Note
        ----
            The circumcenter is set to None if the simplex is abstract.
        """
        if self.isabstract:
            return None
        elif self.dim == 0:
            return self.vertices
        else:
            return circumcenter(self.vertices)

    @property
    def isabstract(self) -> bool:
        """True if no position vectors are associated with the nodes."""
        return self._vertices is None

    def set_vertices(self, 
                     vertices:np.ndarray[float]|list[list[float]]) -> None:
        """Sets the positions of the simplex indices.
        
        Parameters
        ----------
        vertices
            The provided position vectors of the vertices. 
        
        Notes
        -----
        * The number of provided position vectors must at least match the 
          number of indices.
        * It can be bigger (e.g. one might provide the list of the position 
          vectors of the whole complex).
        * In this case, the vertices of the simplex are determined by the  
          indices values.
        """

        try:
            assert isinstance(vertices, (list, np.ndarray)), (
        f'{type(vertices).__name__} is not an expected type of vertices.')
            
            vertices = np.asarray(vertices)
            assert vertices.ndim == 2, (
                f'The provided vertices does not have the proper shape.')
            
            vtx_nbr, emb_dim = vertices.shape
            assert vtx_nbr >= self.dim +1, (
        f'Wrong number of provided vertices: {vtx_nbr} < {self.dim+1}.')
            assert self.dim <= emb_dim, (
                f'Cannot embed a {self.dim}-simplex in a {emb_dim}D space.')
            
            sids, vtx_ids = set(self.indices), set(range(vtx_nbr))
            assert sids.issubset(vtx_ids), (f'The indices of the provided' + 
        ' vertices ({vtx_ids}) do not encompass the simplex indices: {sids}')
            
            self._vertices = vertices

        except AssertionError as msg:
            logger.warning(msg)
            self._vertices = None

    def isfaceof(self, another:Simplex) -> bool:
        """Checks if one simplex is the face of another
        
        Notes
        -----
        * We only check the topology here.
        * TODO? Maybe it would be interesting to also check the
          geometry, when relevant (i.e. non abstract) to be sure
          that the vertices are at the same positions.
        """
        return set(self.indices).issubset(set(another.indices)) 
