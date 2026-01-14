# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.objects.whitneymap
#
# This file contains one class:
#     - `WhitneyMap`
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
from dataclasses import dataclass, field
from typing import Optional

import itertools as it
import numpy as np

from dxtr.complexes.simplicialmanifold import SimplicialManifold
from dxtr.math.geometry import (circumcenter_barycentric_coordinates, 
                                gradient_barycentric_coordinates, whitney_form)
from dxtr import logger

@dataclass
class WhitneyMap():
    """A minimalist container for the Whitney k-map on a simplicial complex.
    
    Attributes
    ----------
    base : np.ndarray of float
        (Nfk*Nn, (D,)*k)-array containing the Whitney forms 
        for each couple (n-simplex, k-face), see Notes.
    positions : np.ndarray of float
        (Nn, D)-array containing the position vectors of the circumcenters
        of all the Nn top simplices of the considered n-complex.
    
    Notes
    -----
    * A Whitney k-map, as we envision it here, is the collection of all base 
      k-forms interpolated at the circumcenter of each n-simplex of 
      a simplicial complex/manifold.
    * Each base k-form is the interpolation of the base function associated 
      to a k-simplex. Since a k-simplex (k<n) is shared by several 
      n-simplices, we have one interpolation of each base k-form on each 
      of those.
    * About the shape of the attribute *base*: 
      * Each top simplex is surrounded by Nfk k-faces. We compute 
        a Whitney k-form for each of these k faces, specific to each top 
        simplex. Therefore we compute Nfk*Nn Whitney k-forms in total 
        (Nn being the number of n-simplices).
      * We depict a k-form as a k-degree anti-symmetric tensor in a space 
        of dimension D. 1-forms are encoded as Dd vectors, i.e. (D,)-arrays;
        2-forms as D*D matrices, i.e. (D,D)-arrays -> generalization: 
        k-forms are encoded as (D,..D)-arrays, D being repeated k times. 
        We noted this (D,)*k in the attribute description.
    """

    base: np.ndarray[float] = field(repr=False)
    positions: np.ndarray[float] = field(repr=False)
    _rows: np.ndarray[int] = field(repr=False)
    _cols: np.ndarray[int] = field(repr=False)
    
    def __post_init__(self):
        self.base = np.asarray(self.base)
        self.positions = np.asarray(self.positions)
        
    @property
    def indices(self) -> Optional[list[tuple[int]]]:
        """Returns a (sid, fid) tuple for each value.

        Returns
        -------
        list of tuple of int, optional
            A list of (sid, fid) tuples.
        """
        return [(i,j) for i, j in zip(self._rows, self._cols)]
    
    @property
    def degree(self) -> int:
        """Gets the degree (k) of the base k-forms.

        Returns
        -------
        int
            The degree of the base k-forms.
        """
        return self.base.ndim - 1
    
    @classmethod
    def of(cls, manifold: SimplicialManifold, degree: int, 
           normalized: bool = False) -> Optional[WhitneyMap]:
        """Computes all the Whitney k-forms at the barycenter of top simplices.

        Parameters
        ----------
        manifold : SimplicialManifold
            The n-simplicial manifold to work on.
        degree : int
            The topological degree (k) of the form to compute.
            Should verify 0 <= degree < manifold.dim.
        normalized : bool, optional
            If True the computed Whitney forms are normalized. Default is False.

        Returns
        -------
        WhitneyMap or None
            The base of all Whitney k-forms on the provided n-simplicial 
            manifold, expressed at the circumcenters of all the top simplices.

        Notes
        -----
        * We are constructing a matrix where each row corresponds 
          to a top simplex and each column to a small degree-simplex.
        """
        
        k = degree
        n = manifold.dim

        try:
            assert 0<= k < n, (
                'Condition 0 <= degree < manifold.dim not verified.')
        except AssertionError as msg:
            logger.warning(msg)
            return None
    
        top_simplices = manifold[-1]
        face_indices = manifold.faces(n, k)
        
        rows, cols, values = [], [], []
        for sid, vtcs in enumerate(top_simplices.vertices):
            rows += [sid]*(n+1)
            cols += face_indices[sid]

            phi = circumcenter_barycentric_coordinates(vtcs)
            dphi = gradient_barycentric_coordinates(vtcs) 

            values += [whitney_form(phi, dphi, indices, normalized=normalized) 
                       for indices in it.combinations(range(n+1), (k+1))]

        return cls(values, top_simplices.circumcenters, rows, cols)