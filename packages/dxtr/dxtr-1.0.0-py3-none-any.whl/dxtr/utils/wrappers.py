# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.io.wrapper
#
# This file contains classes and functions usefull to convert 
# The main data classes of the library into pyvista.UnstructuredGrid objects 
# and to instanciate `dxtr` classes from ply and vtk files.
# 
# The goal is two-fold:
# * Enable the users to save the `SimplicialComplex` and `Cochain` objects 
#   on the disk at the vtk format so they can reuse them easily within 
#.  other frameworks, e.g. Paraview for visualisation purposes.
# * Enable visualization of these objects using the pyvista library, 
#   see the `visu` module.
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
from typing import Optional, Any
from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
import pyvista as pv

from dxtr.cochains.cochain import Cochain
from dxtr.complexes.simplicialcomplex import SimplicialComplex
from dxtr.complexes.simplicialmanifold import SimplicialManifold, edge_vectors
from dxtr.utils.typecheck import typecheck
from dxtr.utils.logging import logger


ELEMENTS = ['vertex', 'edge', 'face', 'volume']

VTK_CELL_TYPES = [pv.CellType.EMPTY_CELL, pv.CellType.LINE, 
                  pv.CellType.TRIANGLE, pv.CellType.TETRA]
VTK_CELL_TYPES_TOPO_DIM = dict(zip(VTK_CELL_TYPES, [0,1,2,3]))
VTK_DUAL_CELL_TYPES = [pv.CellType.EMPTY_CELL, pv.CellType.LINE,
                       pv.CellType.POLYGON, pv.CellType.POLYHEDRON]

class UGrid(pv.UnstructuredGrid):
    """The pyvista.UnstructuredGrid with a useful classmethod on top.

    Notes
    -----
    The only add-on compared to the mother class is the 
    `generate_from` class method that enables to directly instantiate
    an UnstructuredGrid from the `dxtr` own data structures.
    """
    
    def __init__(self, cells, cell_types, points, *args, **kwargs):
        super().__init__(cells, cell_types, points, *args, **kwargs)

    @classmethod
    def generate_from(cls, obj: SimplicialComplex | Cochain, 
                      **kwargs) -> Optional[UGrid]:
        """Instantiates `UnstructuredGrid` from `SimplicialComplex` or `Cochain`.

        Parameters
        ----------
        obj : SimplicialComplex or Cochain
            The object we want to transform into a `pv.UnstructuredGrid`.
        
        Other Parameters
        ----------------
        scaling_factor : float, optional
            A scaling factor to apply to the `Cochain` values to ease the 
            visualization. Default is 1.
        for_visualization : bool, optional
            If True, scalar-valued 1-`Cochain` are converted into vectors in 
            order to be drawn in pyvista. Default is False.

        Returns
        -------
        UGrid or None
            The desired `pv.UnstructuredGrid`.
        """
        
        ugrid_from = {SimplicialComplex: _ugrid_from_simplicialcomplex,
                      SimplicialManifold: _ugrid_from_simplicialcomplex,
                      Cochain: _ugrid_from_cochain}
        
        return ugrid_from[type(obj)](obj, **kwargs)


@dataclass
class Element():
    """A minimalist raw data container.
    """
    name: str
    count: int
    properties: list[str] = field(default_factory=list)
    rawdata: list[str] = field(default=list, repr=False)

    @property
    def dim(self) -> int:
        return ELEMENTS.index(self.name)

    @property
    def is_simplex(self) -> bool:
        return _cells_are_simplices(self.rawdata, self.dim)
    
    def set_rawdata(self, rawdata: str, first_line: int) -> None:
        """Sets the raw data for the element.

        Parameters
        ----------
        rawdata : str
            The raw data as a string.
        first_line : int
            The first line of the raw data to set.
        """
        last_line = first_line + self.count
        self.rawdata = rawdata[first_line: last_line]
    
    def extract_positions(self) -> Optional[np.ndarray[float]]:
        """Extracts position vectors of the vertices from the raw data.

        Returns
        -------
        np.ndarray or None
            A Nx3 array of floats. Where N = number of vertices.
        """

        if not _position_in(self.properties): return None
        
        positions = [[coord for coord in line.split(' ')[:3]] 
                     for line in self.rawdata]
        
        return np.asarray(positions, dtype=float)

    def extract_simplices(self) -> Optional[list[list[int]]]:
        """Extracts highest order simplices from the raw data.

        Returns
        -------
        list of list of int or None
            A list of lists of indices of the vertices forming the summits
            of all the highest order simplices in the structure.
        """
        
        if not _vertices_in(self.properties): 
            return None
        elif not _cells_are_simplices(self.rawdata, self.dim):
            return _simplicies_from_cells(self.rawdata)
        else:
            vtx_nbr = self.dim + 1
            return [[int(vtx_id) for vtx_id in line.split(' ')[1: vtx_nbr+1]] 
                for line in self.rawdata]


@dataclass
class Property():
    """A minimalist container to store property name, type and eventually data.
    """
    name: str
    type: str
    dim: int = field(default=None, repr=False)
    values: Any = field(default=None, repr=False)


# ##################################### #
# Usefull functions for the UGrid class #
# ##################################### #


@typecheck(SimplicialComplex)
def _ugrid_from_simplicialcomplex(complex: SimplicialComplex, 
                                  smallest_cell_dim: int = 0,
                                  dual: bool = False
                                  ) -> Optional[pv.UnstructuredGrid]:
    """Convert a SimplicialComplex into a pv.UnstructuredGrid.

    Parameters
    ----------
    complex : SimplicialComplex
        The simplicial complex to convert.
    smallest_cell_dim : int, optional
        If 0, only the top simplices are recorded. Otherwise, all k-simplices 
        with k in [smallest_cell_dim, complex.dim] are recorded. Default is 0.
    dual : bool, optional
        If True, converts the dual simplicial complex. Default is False.

    Returns
    -------
    pv.UnstructuredGrid or None
        The resulting UnstructuredGrid.

    Notes
    -----
    This argument is useful when recording k-Cochains for we need to define 
    all simplices of higher dim and attribute them a `nan` value.
    """

    if dual: 
        return _ugrid_from_dual_simplicialcomplex(complex, smallest_cell_dim)
    
    n = complex.dim
    k0 = n if smallest_cell_dim == 0 else smallest_cell_dim
    
    points = complex[0].vertices
    
    cells, cell_types = [], []
    for k in range(k0, n+1):
        nbr_cll = complex.shape[k]

        cell_arr = np.array([splx.indices for splx in complex[k]])
        cell_arr = np.hstack(((k+1)*np.ones((nbr_cll, 1)), 
                              cell_arr)).astype(int)
        cells += list(cell_arr.flatten())

        cell_types += [VTK_CELL_TYPES[k]]*nbr_cll
    
    return pv.UnstructuredGrid(cells, cell_types, points)


@typecheck(SimplicialManifold)
def _ugrid_from_dual_simplicialcomplex(manifold: SimplicialManifold,
                                       smallest_cell_dim: int = 0
                                       ) -> Optional[pv.UnstructuredGrid]:
    """Convert a Dual `SimplicialComplex` into a `pv.UnstructuredGrid`.

    Parameters
    ----------
    manifold : SimplicialManifold
        The simplicial manifold to convert.
    smallest_cell_dim : int, optional
        If 0, only the top dual cells are recorded. Otherwise, all k-cells 
        with k in [smallest_cell_dim, manifold.dim] are recorded. Default is 0.

    Returns
    -------
    pv.UnstructuredGrid or None
        The resulting UnstructuredGrid.

    Notes
    -----
    This argument is useful when recording dual k-Cochains for we need to 
    define all simplices of higher dim and attribute them a `nan` value.

    The `elif` condition is meant to deal with boundaries of open simplicial 
    manifold: The dual complex is ill-defined on the border and has n-1 
    cells with only 1 coface. For those, we assign twice their single 
    coface to avoid glitches in the visualization.
    """
    
    n = manifold.dim
    points = manifold[n].circumcenters

    k0 = n if smallest_cell_dim == 0 else smallest_cell_dim

    cells, cell_types = [], []
    for k in range(k0, n+1):
        nbr_cll = manifold.shape[n-k]
        
        if k == n:
          for cell in  manifold.cofaces(0, n, ordered=True):
              cells += [len(cell)]+ cell
        
        elif (k==n-1) & ~manifold.isclosed:
            cofaces = manifold.cofaces(k, n, ordered=True)
            
            for cell in range(nbr_cll):
                if len(cofaces[cell]) == 1:
                    cofaces_ids = 2 * cofaces[cell]
                else:
                    cofaces_ids = cofaces[cell]
                cells += [2] + cofaces_ids

        else:
            cofaces = manifold.cofaces(k, n, ordered=True)
            for cell in range(nbr_cll):
                cells += [len(cofaces[cell])] + cofaces[cell]

        cell_types += [VTK_DUAL_CELL_TYPES[k]]*nbr_cll
  
    return pv.UnstructuredGrid(cells, cell_types, points)


@typecheck(Cochain)
def _ugrid_from_cochain(cochain: Cochain, scaling_factor: float = 1,
                        for_visualization: bool = False) -> Optional[pv.UnstructuredGrid]:
    """Convert a `Cochain` into a `pv.UnstructuredGrid`.

    Parameters
    ----------
    cochain : Cochain
        The cochain to convert.
    scaling_factor : float, optional
        A scaling factor to apply to the `Cochain` values to ease the 
        visualization. Default is 1.
    for_visualization : bool, optional
        If True, scalar-valued 1-`Cochain` are converted into vectors in 
        order to be drawn in pyvista. Default is False.

    Returns
    -------
    pv.UnstructuredGrid or None
        The resulting UnstructuredGrid.

    Notes
    -----
    The `scaling_factor` argument is useful for visualization purposes. 
    Notably, to increase or decrease the size of vectors one wants to
    visualize.
    """
    
    k = cochain.dim
    dual = cochain.isdual
    cplx = cochain.complex
    data_name = '_'.join(cochain.name.split(' '))

    ugrid = _ugrid_from_simplicialcomplex(cplx, smallest_cell_dim=k, dual=dual)
    data = _format_cochain_values(cochain, scaling_factor=scaling_factor, 
                                  for_visualization=for_visualization)

    if k == 0:
        ugrid.point_data[data_name] = data
    else:
        ugrid.cell_data[data_name] = data

    return ugrid
    

def _format_cochain_values(cochain: Cochain, scaling_factor: float = 1,
                           for_visualization: bool = False) -> Optional[np.ndarray[float]]:
    """Formats cochain so they can be used as data for `UnstructuredGrid`. 

    Parameters
    ----------
    cochain : Cochain
        The `Cochain` to format.
    scaling_factor : float, optional
        A multiplicator to apply uniformly to all the values of the `Cochain`. Default is 1.
    for_visualization : bool, optional
        If True, the scalar values on 1-`Cochain` are converted into vectors to enable the drawing of edges. Default is False.

    Returns
    -------
    np.ndarray or None
        The formatted cochain values.

    Notes
    -----
    The `scaling_factor` argument is useful for visualization purposes. 
    Notably, to increase or decrease the size of vectors one wants to
    visualize.

    The purpose of this method: For k-cochains with 0<k<n, 
    their values will be stored as 'cell_data' in the instantiated 
    `UnstructuredGrid`.

    'cell_data' gathers all data that not defined on vertices 
    (i.e. edges data, faces data, volumes data). A cochain contains only one 
    of these types. But we need to provide values for all of them. So this 
    method fills the undesired cell_data to the NAN value.

    Afterwards, when visualizing these cochains in Paraview, one only needs 
    to set the color of NAN values to transparent.
    """

    k = cochain.dim
    vals = scaling_factor * cochain.values
    cplx = cochain.complex
    n = cplx.dim
    Nks = cplx.shape

    if k in [0, n]:
        return np.asarray(vals)
    else:
        nbr_higher_splcs = sum(Nks[:k]) if cochain.isdual else sum(Nks[k+1:])

        if (k == 1) & (not cochain.isvectorvalued):
            N1 = Nks[n-1] if cochain.isdual else Nks[1]
            vals = vals.reshape((N1, 1))
            if for_visualization:
              vals = vals * edge_vectors(cplx, normalized=True, 
                                         dual=cochain.isdual)
        if vals.ndim > 1:
            higher_splx_values_shape = (nbr_higher_splcs, *vals.shape[1:])
        else: 
            higher_splx_values_shape = nbr_higher_splcs
        
        higher_splx_vals = np.empty(higher_splx_values_shape)
        higher_splx_vals[:] = np.nan

        return np.vstack((vals, higher_splx_vals))
    

# ###################################################### #
# Usefull functions for the Element and Property classes #
# ###################################################### #


def _cells_are_simplices(rawdata: list[str], dim: int) -> bool:
    """Checks that the provided cells are simplices.

    Parameters
    ----------
    rawdata : list of str
        The raw data of the cells.
    dim : int
        The dimension of the cells.

    Returns
    -------
    bool
        True if the cells are simplices, False otherwise.
    """
    try:
        simplices_dim = np.array([int(line[0]) for line in rawdata])
        xpct_simplices_dim = (dim + 1) * np.ones(len(rawdata))

        assert (simplices_dim == xpct_simplices_dim).all(), (
                f'{dim}-cells are not simplices.')

        return True
    
    except AssertionError as msg:
        logger.warning(msg)
        return False


def _position_in(properties: list[Property]) -> bool:
    """Checks if coordinates 'x', 'y' & 'z' are listed as properties.

    Parameters
    ----------
    properties : list of Property
        The list of properties.

    Returns
    -------
    bool
        True if coordinates 'x', 'y' & 'z' are listed as properties, False otherwise.
    """
    try:
        for coord in ['x', 'y', 'z']:
            assert coord in [prop.name for prop in properties], (
                f'{coord} is not a listede property.')
        return True

    except AssertionError as msg:
        logger.warning(msg)
        return False


def _vertices_in(properties: list[Property]) -> bool:
    """Checks if 'vertex_indices' is listed as properties.

    Parameters
    ----------
    properties : list of Property
        The list of properties.

    Returns
    -------
    bool
        True if 'vertex_indices' is listed as properties, False otherwise.
    """
    try:
        property_names = [prop.name for prop in properties]
        
        assert (('vertex_indices' in property_names) | 
                ('vertex_index' in property_names)), (
            'vertex_indices/index is not a listed property.')

        return True
    
    except AssertionError as msg:
        logger.warning(msg)
        return False


def _simplicies_from_cells(rawdata: list[str]) -> list[list[int]]:
    """Computes highest order simplices from cells.

    Parameters
    ----------
    rawdata : list of str
        A text containing on each row the number of vertices 
        surrounding the cell and the indices of these vertices.

    Returns
    -------
    list of list of int
        The list of highest simplices, given as a list of indices.

    Notes
    -----
    The returned indices correspond to vertices around primal simplices. 
    Therefore they do not correspond to the vertices provided initially in 
    the .ply file (those are dual vertices for they define n-cells).
    """
    
    mtrx = _cell_vertex_incidence_matrix(rawdata)

    indices = [list(np.nonzero(row)[0]) for row in mtrx.toarray()]

    return [vids for vids in indices if len(vids)==3]


def _cell_vertex_incidence_matrix(rawdata: list[str]) -> sp.coo_matrix[int]:
    """Computes the incidence matrix between cells and vertices.

    Parameters
    ----------
    rawdata : list of str
        A text containing on each row the number of vertices 
        surrounding the cell and the indices of these vertices.

    Returns
    -------
    sp.coo_matrix
        The expected incidence matrix in a sparse format.
    """
    
    rows, cols = [], []
    
    for cid, line in enumerate(rawdata):
        line = line.split(' ')
        vtx_nbr = int(line[0])
        
        rows += list(map(int, line[1: vtx_nbr+1]))
        cols += vtx_nbr*[cid]
        
    data = len(cols)*[1]

    return sp.coo_matrix((data, (rows, cols)))