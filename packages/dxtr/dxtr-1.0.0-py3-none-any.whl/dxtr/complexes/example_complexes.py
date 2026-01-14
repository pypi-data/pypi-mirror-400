# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.examples.complexes_and_manifolds
#
# This file contains generator functions to produce quickly simple
# data structures of interest.
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

from importlib.resources import files, as_file
from pathlib import Path

import numpy as np

from dxtr import logger
from dxtr.complexes import SimplicialComplex, SimplicialManifold
from dxtr.utils.logging import mutelogging

MESH_PATH = Path(__file__).absolute().parents[1] / 'utils/mesh_examples/'
COMPLEX_SIZES = ['small', 'large', 'massive']

@mutelogging
def load_mesh_from_file(mesh_type: str, 
                        mesh_size: str, 
                        manifold: bool) -> SimplicialComplex | SimplicialManifold:
    """Instantiates `SimplicialComplex` or `SimplicialManifold` from files.

    Parameters
    ----------
    mesh_type : str
        The name of the type of domain to generate. 
        Should be in ['sphere', 'disk'].
    mesh_size : str
        The resolution of the domain to generate.
        Should be in ['small', 'large', 'massive'].
    manifold : bool
        If True, instantiates a `SimplicialManifold`, 
        otherwise a `SimplicialComplex`.

    Returns
    -------
    SimplicialComplex or SimplicialManifold
        The instantiated simplicial complex or manifold.
    """

    try:
        assert mesh_size in COMPLEX_SIZES, (
            f'{mesh_size} is not a valid {mesh_type} size value.' +
            f' Should either be in {COMPLEX_SIZES}.')
        
        root = files('dxtr')
        file_name = f'{mesh_type}_{mesh_size}.ply'
        path = root.joinpath('utils/mesh_examples/').joinpath(file_name)

        with as_file(path) as path_file:
            if manifold:
                return SimplicialManifold.from_file(path_file)
            else:
                return SimplicialComplex.from_file(path_file)

    except AssertionError as msg:
        logger.warning(msg)
        return None 


def disk(size: str = 'small', manifold: bool = False
         ) -> SimplicialComplex | SimplicialManifold:
    """Instantiates a circular `SimplicialComplex` or `SimplicialManifold`.

    Parameters
    ----------
    size : str, optional
        Specifies the resolution of the structure. Should either be 'small', 'large' or 'massive'. Default is 'small'.
    manifold : bool, optional
        Instantiates a SimplicialManifold if True. Default is False.
    
    Returns
    -------
    SimplicialComplex or SimplicialManifold
        The instantiated circular simplicial complex or manifold.

    Notes
    -----
    * These complexes are generated from `.ply` files stored 
      in the `data/meshes/` folder.
    * The various disk respectively contains vertices/edges/triangles:
       - small: (1670, 4881, 3212)
       - large: (19991, 59967, 39978)
       - massive: (41676, 125022, 83348)
    * The radius of the generated structures is always 1.
    """
    return load_mesh_from_file('disk', size, manifold)


def sphere(size: str = 'small', manifold: bool = False
           ) -> SimplicialComplex | SimplicialManifold:
    """Instantiates a spherical `SimplicialComplex` or `SimplicialManifold`.

    Parameters
    ----------
    size : str, optional
        Specifies the resolution of the structure. Should either be 'small', 'large' or 'massive'. Default is 'small'.
    manifold : bool, optional
        Instantiates a SimplicialManifold if True. Default is False.
    
    Returns
    -------
    SimplicialComplex or SimplicialManifold
        The instantiated spherical simplicial complex or manifold.

    Notes
    -----
    * These complexes are generated from `.ply` files stored 
      in the `data/meshes/` folder.
    * The various spheres respectively contains vertices/edges/triangles:
       - small: (1712, 5130, 3420)
       - large: (19991, 59967, 39978)
       - massive: (41676, 125022, 83348)
    * The radius of the generated structures is always 1.
    """
    return load_mesh_from_file('sphere', size, manifold)


@mutelogging
def cube(manifold: bool = False, scale: float = 1.
         ) -> SimplicialComplex | SimplicialManifold:
    """Instantiates a cubic 2D-`SimplicialComplex` or 2D-`SimplicialManifold`.

    Parameters
    ----------
    manifold : bool, optional
        If True instantiates a `SimplicialManifold`, otherwise a `SimplicialComplex`. Default is False.
    scale : float, optional
        A scaling factor to change the size of the structure. Default is 1.

    Returns
    -------
    SimplicialComplex or SimplicialManifold
        The instantiated cubic simplicial complex or manifold.
    """
    indices = [[0, 1, 2], [1, 2, 3], [0, 1, 4], [1, 4, 5],
               [1, 3, 5], [3, 5, 7], [3, 2, 7], [2, 7, 6],
               [2, 0, 6], [0, 4, 6], [4, 5, 6], [5, 6, 7]]

    positions = np.array([[0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1], 
                          [0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]], 
                          dtype=float)
    positions *= scale
    
    if manifold:
        return SimplicialManifold(indices, positions)
    else:
        return SimplicialComplex(indices, positions)


@mutelogging
def icosahedron(manifold: bool = False, scale: float = 1.
                ) -> SimplicialComplex | SimplicialManifold:
    """Instantiates an icosahedron `SimplicialComplex` or `SimplicialManifold`.

    Parameters
    ----------
    manifold : bool, optional
        If True instantiates a SimplicialManifold, otherwise a SimplicialComplex. Default is False.
    scale : float, optional
        A scaling factor to change the size of the structure. Default is 1.

    Returns
    -------
    SimplicialComplex or SimplicialManifold
        The instantiated icosahedron simplicial complex or manifold.
    """

    indices = [[0, 1, 2], [0, 2, 3],
               [0, 3, 4], [0, 4, 5],
               [0, 5, 1], # upper dome ends here
               [1, 7, 2],
               [2, 8, 3], [3, 9, 4],
               [4, 10, 5], [5, 6, 1],  # upper belt ends here
               [7, 2, 8], [8, 3, 9],
               [9, 4, 10], [10, 5, 6],
               [6, 1, 7],  # lower belt ends here 
               [6, 7, 11],
               [7, 8, 11], [8, 9, 11],
               [9, 10, 11], [10, 6, 11]]  # lower dome ends here

    gr = (1 + np.sqrt(5)) / 2

    positions = np.array([[-1, gr, 0], [1, gr, 0],
                          [0, 1, -gr], [-gr, 0, -1],
                          [-gr, 0, 1], [0, 1, gr],
                          [gr, 0, 1], [gr, 0, -1],
                          [0, -1, -gr], [-1, -gr, 0],
                          [0, -1, gr], [1, -gr, 0]])
    positions *= scale
    if manifold:
        return SimplicialManifold(indices, positions)
    else:
        return SimplicialComplex(indices, positions)


@mutelogging
def triangular_grid(edge_number_per_side: int = 3,
                    edge_length: float = 1, 
                    manifold: bool = False
                    ) -> SimplicialComplex | SimplicialManifold:
    """Generates a triangle grid `SimplicialComplex` or `SimplicialManifold`.

    Parameters
    ----------
    edge_number_per_side : int, optional
        The number of 1-simplices on each side. Default is 3.
    edge_length : float, optional
        The total length of one side of the domain. Default is 1.
    manifold : bool, optional
        If True, instantiates a `SimplicialManifold`, otherwise a `SimplicialComplex`. Default is False.

    Returns
    -------
    SimplicialComplex or SimplicialManifold
        The generated triangle grid simplicial complex or manifold.
    """
    
    N = edge_number_per_side
    dL = edge_length

    total_nbr_vtx = (N+1)**2

    indices = np.arange(total_nbr_vtx).reshape((N+1, N+1))[::-1]
    
    triangles = []
    for upper_row, lower_row in zip(indices[:-1], indices[1:]):
        for i, j, k, l  in zip(upper_row[:-1], upper_row[1:], 
                               lower_row[:-1], lower_row[1:]):
            triangles.append([i, j, l])
            triangles.append([i, k, l])
    
    triangles = np.array(triangles)
    theta = np.pi/3
    positions = np.array([[i*dL + j*np.cos(theta)*dL, j*dL*np.sin(theta), 0] 
                           for j in np.arange(N+1) for i in np.arange(N+1)])
    
    if manifold:
        return SimplicialManifold(triangles, positions)
    else:
        return SimplicialComplex(triangles, positions)


@mutelogging
def hexagon(manifold: bool = False, 
            radius: float = 1) -> SimplicialComplex | SimplicialManifold:
    """Generates a simple hexagonal grid.

    Parameters
    ----------
    manifold : bool, optional
        If True, instantiates a `SimplicialManifold`, otherwise a `SimplicialComplex`. Default is False.
    radius : float, optional
        The radius of the hexagon. Default is 1.

    Returns
    -------
    SimplicialComplex or SimplicialManifold
        The generated hexagonal grid simplicial complex or manifold.
    """
    indices = [[0, 1, 2],
               [0, 2, 3],
               [0, 3, 4],
               [0, 4, 5],
               [0, 5, 6],
               [0, 6, 1]]

    center = np.zeros(3)
    outisde_vertices = radius * np.array([[np.cos(2*np.pi*i/6), 
                                           np.sin(2*np.pi*i/6), 
                                           0] for i in range(6)])

    positions = np.vstack((center, *outisde_vertices))
    
    if manifold:
        return SimplicialManifold(indices, positions)
    else:
        return SimplicialComplex(indices, positions)
    

@mutelogging
def triangle(manifold: bool = False, 
             scale: float = 1.) -> SimplicialComplex | SimplicialManifold:
    """Generates a simple triangle.

    Parameters
    ----------
    manifold : bool, optional
        If True instantiates a SimplicialManifold, otherwise a SimplicialComplex. Default is False.
    scale : float, optional
        The length of the edges. Default is 1.

    Returns
    -------
    SimplicialComplex or SimplicialManifold
        The generated triangle simplicial complex or manifold.
    """
    c = np.cos(np.pi/3)
    s = np.sin(np.pi/3)

    indices = [(0, 1, 2)]
    positions = scale * np.array([[0,0,0], [1,0,0], [c,s,0]])
    
    if manifold:
        return SimplicialManifold(indices, positions)
    else:
        return SimplicialComplex(indices, positions)
    

@mutelogging
def tetrahedron(manifold: bool = False, 
                scale: float = 1.) -> SimplicialComplex | SimplicialManifold:
    """Generates a regular tetrahedra within the unit sphere.

    Parameters
    ----------
    manifold : bool, optional
        If True instantiates a `SimplicialManifold`, otherwise a `SimplicialComplex`. Default is False.
    scale : float, optional
        The radius of the circumcentric sphere containing the diamond. Default is 1.

    Returns
    -------
    SimplicialComplex or SimplicialManifold
        The generated tetrahedron simplicial complex or manifold.

    Notes
    -----
    * The upper vertices is at point (0,0,scale)
    * The lower face is parallel to the xy-plane.
    """

    indices = [[0,1,2,3]]

    positions = np.array([[ np.sqrt(8/9),             0, -1/3],
                          [-np.sqrt(2/9),  np.sqrt(2/3), -1/3],
                          [-np.sqrt(2/9), -np.sqrt(2/3), -1/3],
                          [            0,             0,    1]])
    positions *= scale

    if manifold:
        return SimplicialManifold(indices, positions)
    else:
        return SimplicialComplex(indices, positions)



@mutelogging
def diamond(manifold: bool = False, 
            scale: float = 1.) -> SimplicialComplex | SimplicialManifold:
    """Generates a structure composed of two superimposed tetrahedra.

    Parameters
    ----------
    manifold : bool, optional
        If True instantiates a `SimplicialManifold`, otherwise a `SimplicialComplex`. Default is False.
    scale : float, optional
        The radius of the circumcentric sphere containing the diamond. Default is 1.

    Returns
    -------
    SimplicialComplex or SimplicialManifold
        The generated diamond simplicial complex or manifold.

    Notes
    -----
    * This is the only example of a `SimplicialComplex` of topological 
      dimension 3.
    """
    indices = [[0,1,2,3], [1,2,3,4]]

    theta = 2*np.pi/3

    positions = np.array([[0, 0,-1],
                          [1, 0, 0],
                          [np.cos(theta), np.sin(theta),0],
                          [np.cos(2*theta), np.sin(2*theta),0],
                          [0, 0, 1]])
    positions *= scale

    if manifold:
        return SimplicialManifold(indices, positions)
    else:
        return SimplicialComplex(indices, positions)


