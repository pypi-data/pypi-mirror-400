# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.io.read_files
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
from pathlib import Path
from typing import Optional

import numpy as np
import scipy.sparse as sp
import pyvista as pv

from dxtr import logger
from dxtr.utils.logging import require_pyvista
from dxtr.utils.wrappers import (Element, Property, VTK_CELL_TYPES, 
                                 VTK_CELL_TYPES_TOPO_DIM)


def read_ply(path:str|Path) -> tuple[Optional[list[list[int]]],
                                        Optional[np.ndarray[float]]]:
    """Reader for '.ply' files.

    Parameters
    ----------
    path
        Disc location of the file to read.

    Returns
    -------
    simplices
        list of lists of vertex ids surrounding each cell.
    positions
        A Nx3 array of floats. Where N = number of vertices.

    Notes
    -----
      * In the `.ply` format we tend to save only `SimplicialComplex` objects.
      * `Cochain` objects must be saved in `.vtk` format.
      * TODO: Should also check elements of lower order to see if they contain 
        simplices to extract. So far only pure simplicial complexes are handled.
      * TODO: Should also check and extract other properties 
        in order to read Cochains.
    """

    if not _valid(path): return None, None

    with open(path, 'r') as file:
        content = file.readlines()
        elements = _parse_elements_and_properties(content)

        positions = elements[0].extract_positions()
        simplices = elements[-1].extract_simplices()

        if not elements[-1].is_simplex:
            positions = _cells_circumcenters(positions, content)
        
        return simplices, positions

@require_pyvista
def read_vtk(path:str|Path) -> tuple[Optional[np.ndarray[int]],
                                     Optional[np.ndarray[float]]]:
    """Reader for `.vtk` files of a pure `SimplicialComplex` or `Cochain`.

    Parameters
    ----------
    path
        The location of the file to read.

    Returns
    -------
    simplices
        A (Nn, n+1) array containing the top vertex indices 
        (n+1 indices per n-simplex) for each of the Nn top simplices 
        (of topological dimension n).
    positions
        A (N0, 3) array containing the 3D position vectors of the 
        N0 0-simplices.
    property
        A `Property` object containing the data useful for the `Cochain`
        instanciation.
    
    Notes
    -----
      * Only works so far on Primal scalar-valued Cochain !!!
    """
    
    if not _valid(path): return None, None, None

    ugrid = pv.read(path, file_format='vtk')
    
    positions = ugrid.points
    simplices = _top_simplices_within(ugrid)
    property = _data_within(ugrid)

    return simplices, positions, property

# ######################################### #
# Useful functions for the read_ply method. #
# ######################################### #

def _parse_elements_and_properties(content:list[str]) -> list[Element]:
    """Sort and organize rawdata associated with various topological elements.

    Parameters
    ----------
    content
        The list of each line of text of the .ply file.

    Returns
    -------
        A list of data containers organized by topological dimension.
    """

    header_length = content.index('end_header\n')
    header = content[:header_length]

    first_line = header_length + 1
    
    elements = []
    for line in header:
        words = line.split(' ')

        if words[0] == 'element': 
            elmt = Element(name=words[1], count=int(words[-1]))
            elmt.set_rawdata(content, first_line)
            elements.insert(elmt.dim, elmt)
            first_line += elmt.count

        elif words[0] == 'property':
            prop = Property(name=words[-1][:-1], type=words[1])
            elements[-1].properties.append(prop)
    
    return elements


def _cells_circumcenters(positions:np.ndarray[float],
                        rawdata:list[str]) -> np.ndarray[float]:
    """Computes cells circumcenters.

    Parameters
    ----------
    positions
        array containing all the vertices position vectors.
    rawdata
        list of vertex indices for each cell.

    Returns
    -------
        A Nx3 array of floats. Where N = number of cells.
    """
    
    header_length = rawdata.index('end_header\n')
    nbr_vertices = positions.shape[0]
    first_line_cell_brdr_vids = header_length + 1 + nbr_vertices
    content = rawdata[first_line_cell_brdr_vids:]

    cell_border_vids = _vertex_indices_around_cells(content) 
    cell_vertices = np.array([positions[vids].mean(axis=0) 
                              for vids in cell_border_vids])
    return cell_vertices


def _vertex_indices_around_cells(content:list[str]) -> list[list[int]]:
    """Gets the indices of the vertices surrounding each cells

    Parameters
    ----------
    content
        A text containing on each raw the number of vertices 
        surrounding the cell and the indices of these vertices.

    Returns
    -------
        A list containing for all cell the list of its vertex indices.
    """
    return [[int(vtx_id) for vtx_id in line.split(' ')[1: int(line[0])+1]] 
            for line in content]

# ######################################### #
# Useful functions for the read_vtk method. #
# ######################################### #

def _top_simplices_within(ugrid:pv.UnstructuredGrid) -> np.ndarray[int]:
    """Extract the top simplex indices from an UnstructuredGrid.

    Parameters
    ----------
    ugrid
        The UnstructuredGrid to consider.

    Returns
    -------
        An array of shape (Nn, n+1) where n is the topological dimension of the 
        top simplices (therefore composed by n+1 0-simplices) and Nn is the 
        number of these top simplices.
    
    Notes
    -----
      * The initial goal of this function is to be used to reconstruct 
        `SimplicialManifold` from `.vtk` files written on disk.
      * It therefore assumes that the structure encoded by the input UGrid 
        meets the criteria of a simplicial manifold.
    """
    top_simplex_type = int(ugrid.celltypes.max())
    
    try:
        assert top_simplex_type in VTK_CELL_TYPES, f'Not supported CellType.'
    except AssertionError as msg:
        logger.warning(msg)
        return None
    
    dim = VTK_CELL_TYPES_TOPO_DIM[top_simplex_type]
    top_simplex_nbr = np.count_nonzero(ugrid.celltypes==top_simplex_type)
    cut_limit = top_simplex_nbr * (dim + 2)

    return ugrid.cells[-cut_limit:].reshape((top_simplex_nbr, (dim + 2)))[:,1:]


def _data_within(ugrid:pv.UnstructuredGrid) -> Optional[Property]:
    """_summary_

    Parameters
    ----------
    ugrid
        _description_

    Returns
    -------
        _description_
    
    Notes
    -----
      * TODO: Should check that the data are indeed of type `np.ndarray`.
    """
    
    if _data_is_valid(ugrid.point_data.keys()):
        name = ugrid.point_data.keys()[0]
        return Property(' '.join(name.split('_')), 'np.ndarray', 0,
                        ugrid.point_data[name])
    
    elif _data_is_valid(ugrid.cell_data.keys()):
        name = ugrid.cell_data.keys()[0]
        values = ugrid.cell_data[name]
        name = ' '.join(name.split('_'))
        dim = VTK_CELL_TYPES_TOPO_DIM[ugrid.celltypes.min()]
        return Property(name, 'np.ndarray', dim, values[~np.isnan(values)])
    
    else: 
        logger.warning('the considered file does not contain any valid data,' 
                       +'it will be interpreted as a `SimplicialManifold`')
        return None


def _data_is_valid(data_name:list[str]) -> bool:
    """Checks that the given `pv.UnstructuredGrid` has only one data set.

    Parameters
    ----------
    data_name
        The list of data sets in the considered `pv.UnstructuredGrid`

    Returns
    -------
        True if only one data set, False else.
    """
    
    try:
        assert len(data_name) == 1
        logger.info(f'Extracting {data_name[0]} from file.')
        return True

    except:
        return False

# ################################## #
# Useful functions for both methods. #
# ################################## #

def _valid(path:str|Path) -> bool:
    """Checks if the given path lead to a .ply file.
    """

    try:
        if isinstance(path, Path): path = path.as_posix()

        format = path.split('/')[-1].split('.')[-1]
        assert format in ['ply', 'vtk'], (f'Provided file format (.{format}) '
                    +'not supported; only `.ply` & `.vtk` files are handled.')

        logger.info(f'Extracting Simplicial Complex from {path}.')
        return True

    except AssertionError as msg:
        logger.warning(msg)
        return False
