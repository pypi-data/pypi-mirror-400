# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.io.write_files
#
# This file contains methods required to save Dxtr data structures on disk.
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
from functools import wraps
from typing import Optional, Any
import numpy as np

from dxtr import logger
# from dxtr import Cochain, SimplicialComplex

# from dxtr.utils.logging import require_pyvista
# from dxtr.utils.wrappers import UGrid, Property
# from dxtr.utils.typecheck import valid_input


# @valid_input
# def write_file(obj:SimplicialComplex|Cochain, file_name:str|Path, 
#                format:str, folder:Optional[str|Path]=None) -> None:
#     """Saves data structures on disk.

#     Parameters
#     ----------
#     obj
#         The data structure to save.
#     folder
#         Optional (default is None). Where to save it.
#     file_name
#         The name to save it under.
#     format
#         The desired format, should either be `.ply` or `.vtk`.
    
#     Returns
#     -------
#     None

#     Notes
#     -----
#       * If no folder is provided, the current working directory is used.
#       * Only `SimplicialComplex` instances can be properly saved as `.ply`.
#       * For `Cochain` instances, please use the `.vtk` format. 
#     """

#     path = format_path_properly(folder, file_name, format)
    
#     if format == '.ply':
#         write_ply(obj, path)
    
#     elif format == '.vtk':
#         write_vtk(obj, path)

#     logger.info(f'Saved {obj.name}, as {path.name}, at location: {path.parent}')


def write_ply(top_simplices: list[list[int]], points: np.ndarray[float], 
              path: str | Path, property: Optional[np.array[float]] = None) -> None:
    """Saves computed data structures on disk in the .ply format.

    Parameters
    ----------
    top_simplices : list of list of int
        The list of vertex indices forming the highest degree simplices.
    points : np.ndarray of float
        The coordinates of the vertices.
    path : str or Path
        The path where to save the file.
    property : np.array of float, optional
        Additional property data to save. Default is None.

    Returns
    -------
    None
    """

    top_splcs = top_simplices
    pprty = property
 
    with open(path, 'w') as file:
        file.write('ply\n')
        file.write('format ascii 1.0\n')
        file.write(f'element vertex {len(points)}\n')
        file.write('property float x\n')
        file.write('property float y\n')
        file.write('property float z\n')
        file.write(f'element face {len(top_splcs)}\n')
        file.write('property list int int vertex_indices\n')

        if pprty is not None: 
            if pprty.dim == 1:
                file.write(f'element edge {len(pprty.values)}\n')
                file.write(f'property int source\n')
                file.write(f'property int target\n')
            file.write(f'property {pprty.type} {pprty.name}\n')
        
        file.write('end_header\n')

        for pts in points:
            file.write(' '.join([str(x) for x in pts])+'\n')
        
        if (pprty is None) or (pprty.dim != 2):
            for splx in top_splcs:
                file.write(str(len(splx)) + ' '
                            + ' '.join([str(v) for v in splx]) + ' \n')
        else:
            for splx, pprty_value in zip(top_splcs, pprty.values):
                file.write(str(len(splx)) + ' '
    + ' '.join([str(v) for v in splx]) + ' ' + str(pprty_value) + ' \n')
        
        if (pprty is not None) and (pprty.dim == 1):
            for splx, pprty_value in enumerate(pprty.values):
                file.write(
        ' '.join([str(v) for v in splx]) + ' ' + str(pprty_value) + ' \n')


# @require_pyvista
# def write_vtk(obj:SimplicialComplex|Cochain, 
#               path:str|Path) -> None:
#     """Saves computed data structures on disk in the .vtk format.

#     Parameters
#     ----------
#     obj
#         The object we want to save. Should be an instance of:
#         `SimplicialComplex`, `SimplicialManifold` or `Cochain`.
#     path
#         Where to save this object.
#     """
#     ugrid = UGrid.generate_from(obj)
#     ugrid.save(path)


# ########################################### #
# Useful functions for the write_file method. #
# ########################################### #

def format_path_properly(folder: Optional[Path | str], file_name: Path | str, 
                         extension: str) -> Optional[Path]:
    """Makes a valid recording path.

    Parameters
    ----------
    folder : Path or str, optional
        The folder where to record the file. Default is None.
    file_name : Path or str
        The name to record the file under.
    extension : str
        The file extension to use. Should be either `.ply` or `.vtk`.

    Returns
    -------
    Path or None
        The proper path to use.
    """

    try:
        assert isinstance(extension, str), 'Extention must be given as strings.'
        assert extension[0] == '.', 'Extention must start with `.`.'
        assert extension in ['.ply','.vtk'], 'Only .ply & .vtk handled for now.'

    except AssertionError as msg:
        logger.warning(msg)
        return None
    
    if folder is None:
        folder = Path().cwd()
    elif isinstance(folder, str):
        folder = Path(folder)

    folder.mkdir(parents=True, exist_ok=True)
    
    if isinstance(file_name, str):
        file_name = Path(file_name)
    
    path = folder / file_name
        
    if path.suffix != extension:
        path = path.with_suffix(extension)
    
    return path


# ########################################## #
# Useful functions for the write_ply method. #
# ########################################## #

# def _vertex_positions(obj:SimplicialComplex|Cochain) -> np.ndarray[float]:
#     """Gets the vertex position vectors of the data structure.
#     """
#     if isinstance(obj, SimplicialComplex):
#         return obj[0].vertices

#     if isinstance(obj, Cochain):
#         return _vertex_positions(obj.complex)
    

# def _top_simplices(obj:SimplicialComplex|Cochain) -> np.ndarray[float]:
#     """Gets the indices of the top simplices within the data structure.
#     """
#     if isinstance(obj, SimplicialComplex):
#         return obj[-1].vertex_indices

#     if isinstance(obj, Cochain):
#         return _top_simplices(obj.complex)
    

# def _extract_property_from(obj:SimplicialComplex|Cochain) -> Optional[Property]:

#     if isinstance(obj, SimplicialComplex):
#         return None

#     elif isinstance(obj, Cochain):
#         return Property(name=obj.name,
#                         type=obj.values.dtype,
#                         dim=obj.dim,
#                         values=obj.values)
    

# # def _edges(obj:Cochain) -> np.ndarray[int]:
# #     """Gets the vertex indices of all 1-simplices."""
# #     return obj.complex[1].vertex_indices

