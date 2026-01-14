# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.math.geometry
#
# This submodule contains useful functions to compute
# geometrical properties on simplicial complexes.
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
from numpy import pi
from scipy.special import factorial

from dxtr import logger


def barycentric_coordinates(vector: np.ndarray[float], vertices: np.ndarray[float]
                            ) -> Optional[np.ndarray[float]]:
    """Computes a vector barycentric coordinates in a given frame.

    Parameters
    ----------
    vector : np.ndarray of float
        The considered position vector given as a (D,)-array.
    vertices : np.ndarray of float
        (n, D)-array, each row corresponds to a vertex position vector.
        These n vertices form the frame in which the barycentric 
        coordinates are computed, see Notes.

    Returns
    -------
    np.ndarray of float, optional
        (n,)-array containing the seeked barycentric coordinates.
        
    Notes
    -----
    * Barycentric coordinates $x_i$ of the vector $v$ within 
      the frame $\{e_1,...,e_n\}$ verify: $v = \sum_i x_i e_i$.
    * Here D refers to the geometrical dimension of the embedding space, 
      usually D=3.
    * Practically, the n vertices form a (n-1)-simplex, a top degree 
      simplex within a (n-1)-simplicial complex embedded in a 
      D-dimensional Euclidean space. Therefore n should verify n <= D.
    * We don't need to compute the last coordinate explicitly as the sum 
      of all coordinates equals one.
    """
    n, D = vertices.shape

    try:
        assert n <= D, f'Too much vertices. Must be <={D} but {n} provided.'
        assert isinstance(vector, np.ndarray), 'Inputs must be np.ndarray.'
        assert vector.shape[-1] == D, f'input vector must be of dim {D}.'

    except AssertionError as msg:
        logger.warning(msg)
        return None
        
    vector.reshape((1, D))

    Vtot = volume_simplex(vertices)

    bary_coord = [volume_simplex(np.vstack((vertices[:i], 
                                            vector,
                                            vertices[i+1:]))) / Vtot 
                for i in np.arange(n-1)]

    bary_coord.append(1 - np.sum(bary_coord))

    return np.array(bary_coord)


def gradient_barycentric_coordinates(vertices: np.ndarray[float]
                                     ) -> np.ndarray[float]:
    """Computes the gradients of the barycentric coordinates of a top simplex.
    
    Parameters
    ----------
    vertices : np.ndarray of float
        (n+1, D)-array containing the position vectors of the simplex vertices.
    
    Returns
    -------
    np.ndarray of float
        (n+1, D)-array containing the seeked gradients.
    
    Notes
    -----
    * The ith row of the returned array corresponds to the gradient 
      of the barycentric coordinate function associated with the vertex
      stored in the ith row of the input array.
    * This algorithm is strongly inspired by the pydec library. 
      See Bell et al (2010), section 9.1 particularly and the
      `pydec.fem.innerproduct.barycentric_gradients()` function within 
      the `pydec` repository.
    * The gradient of a barycentric coordinate function 
      associated to a given vertex is expected to be orthogonal 
      to the (n-1)-simplex facing this very vertex.
    """
    edges = vertices[1:] - vertices[0]

    dbcs = lng.inv(edges @ edges.T) @ edges
    dbc0 = -dbcs.sum(axis=0)

    return np.vstack((dbc0, dbcs))


def circumcenter_barycentric_coordinates(vectors: np.ndarray[float]
                                         ) -> np.ndarray[float]:
    """Computes the barycentric coordinates of a simplex circumcenter.

    Parameters
    ----------
    vectors : np.ndarray of float
        A ((N+1),D)-array where each row corresponds to the position
        vector of a node of the considered N-simplex, within the 
        D-dimensional space.

    Returns
    -------
    np.ndarray of float
        The barycentric coordinates of the circumcenter.

    Notes
    -----
    * Within a D-dimensional embedding space, simplices order are limited to 
      $N \leq D$.
    * This function is a direct recopy of the one in the 
      `pydec.math.circumcenter` submodule.
    * If the circumcenter lies outside of the simplex, at least one of its 
      barycentric coordinates will be negative. 
    * The previous remark can be used as a test to check if a simplex is 
      well-centered or not.
    """
    rows, cols = vectors.shape

    try:
        assert rows <= cols + 1, 'Too many nodes provided.'
    except AssertionError as msg:
        logger.warning(msg)
        return None

    system = np.bmat([[2*np.dot(vectors, vectors.T), np.ones((rows, 1))],
                      [np.ones((rows, 1)).T, np.zeros((1, 1))]])

    rhs = np.hstack([(vectors * vectors).sum(axis=1),
                     np.ones(1)])
   
    bary_coords = lng.solve(system, rhs)[:-1]

    return bary_coords


def circumcenter(vectors: list[np.ndarray[float]], 
                 return_radius: bool = False) -> tuple[np.ndarray[float], float]:
    """Computes the position of the circumcenter of a simplex.

    Parameters
    ----------
    vectors : list of np.ndarray of float
        The position vectors of the simplex nodes.
    return_radius : bool, optional
        If True, returns the circumcenter radius. Default is False.

    Returns
    -------
    np.ndarray of float
        The position vector of the circumcenter.
    float, optional
        The circumcenter radius.

    Notes
    -----
    * This function is a direct recopy of the one in the 
      `pydec.math.circumcenter` submodule.
    """

    if isinstance(vectors, list):
        vectors = np.array(vectors)

    bary_coords = circumcenter_barycentric_coordinates(vectors)

    ccenter = np.dot(bary_coords, vectors)

    if return_radius:
        cradius = lng.norm(vectors[0, :] - ccenter)
        return ccenter, cradius
    else:
        return ccenter


def dot(blade_1: np.ndarray[float],
        blade_2: np.ndarray[float]) -> Optional[float]:
    """Computes the scalar product between two k-blades.
    
    Parameters
    ----------
    blade_1 : np.ndarray of float
        The first k-blade to consider.
    blade_2 : np.ndarray of float
        The second k-blade to consider.

    Returns
    -------
    float, optional
        The seeked scalar value.
    
    Notes
    -----
    * The provided arrays should be of the shape (k, D); 
      k being the simplices topological dimension & D the embedding
      dimension. N.B.: these should verify: $k \leq D$.
    * Each row in these arrays corresponds to an edge of the k-blade.
    * The implemented formula is:
      $$(e_1\\wedge_between\\dots\\wedge_between e_k)
      \\cdot(e^{\\prime}_1\\wedge_between\\dots\\wedge_between e^{\\prime}_k)
      = 1/(n!)^2\\det(e_i\\cdot e^{\\prime}_j)$$
      It is derived from Parandis Kharavi's thesis manuscript (p.19).
    * 1-blades should be provided as arrays of shape (1,D) and not just (D,).
    """
    try:
        assert len(blade_1.shape) == 2, (
            'k-blades must be provided as array of shape k*D.')
        k, D = blade_1.shape
        assert k <= D, (
          'The blades topological dimension'
          + 'should be smaller that the embedding dimension.')
        assert blade_2.shape[0] == k, (
            'Only k-blades of the same degree can be multiplied.')
    except AssertionError as msg:
        logger.warning(msg)
        return None
    
    mtrx = np.inner(blade_1, blade_2)

    return lng.det(mtrx) / factorial(k)**2


def wedge_between(vector_1: np.ndarray[float], 
                  vector_2: np.ndarray[float]) -> Optional[np.ndarray[float]]:
    """Implements the wedge product between two vectors.

    Parameters
    ----------
    vector_1 : np.ndarray of float
        (D,) array representing a vector in a D-dimensional space.
    vector_2 : np.ndarray of float
        (D,) array representing a vector in a D-dimensional space.

    Returns
    -------
    np.ndarray of float, optional
        (D,D) array representing an antisymmetric second order tensor.

    Notes
    -----
    * For now, this wedge product only works with vectors aka 1-blades, 
      but could be extended in a recursive manner... TODO?
    * /!\ This is not a DEC implementation of the wedge_between product in any case.
    """

    try:
        for i, v in enumerate([vector_1, vector_2]):
            assert isinstance(v, np.ndarray), f'Arg_{i} must be numpy.ndarray.'
            assert v.ndim == 1, 'Only vectors supported as input for now.'
    
    except AssertionError as msg:
        logger.warning(msg)
        return None
    
    tsr = np.outer(vector_1, vector_2)
    tsr -= tsr.T
    return tsr 


def volume_blade(blade: np.ndarray[float]) -> float:
    """Computes the volume of a k-blade.

    Parameters
    ----------
    blade : np.ndarray of float
        A (k,D)-array where each row corresponds to an edge vector 
        of the considered k-blade, within the D-dimensional embedding space.
    
    Returns
    -------
    float
        The unsigned volume of the considered k-blade.

    Notes
    -----
    * 1-blades should be provided as arrays of shape (1,D) and not just (D,).
    """
    return np.sqrt(dot(blade, blade))


def volume_simplex(positions: np.ndarray[float]) -> float:
    """Computes the unsigned volume of a k-simplex.

    Parameters
    ----------
    positions : np.ndarray of float
        A ((k+1),D)-array where each row corresponds to the 
        position vector of a vertex of the considered k-simplex, 
        within the D-dimensional embedding space.
    
    Returns
    -------
    float
        The unsigned volume of the considered k-simplex.
    
    Notes
    -----
    * If a single position vector is provided, we assume it corresponds to a
      0-simplex and the corresponding volume is set to 1.

    See also
    --------
    The `volume_blade` method for deeper details.
    """

    k, D = positions.shape
    k -= 1

    try:
        assert k <= D, f'Volume of {k}-simplex cannot be computed in R^{D}.'
    except AssertionError as msg:
        logger.warning(msg)
        return None

    if k == 0:
        return 1.
    else:
        blade = positions[1:] - positions[0]
        return volume_blade(blade)


def volume_polytope(position_vectors: list[np.ndarray[float]], 
                    dual_cell_indices: list[list[int]], 
                    ill_centered_simplices: Optional[np.ndarray[int]] = None
                    ) -> float:
    """Computes the volume of a polytope.

    Parameters
    ----------
    position_vectors : list of np.ndarray of float
        The position vectors of the vertices of the polytope.
    dual_cell_indices : list of list of int
        The indices of the dual cells of the polytope.
    ill_centered_simplices : np.ndarray of int, optional
        The indices of the ill-centered simplices. Default is None.

    Returns
    -------
    float
        The volume of the polytope.
    """
    
    try:
        assert len(dual_cell_indices[0]) == len(position_vectors), (
            'Simplex degree do not match number of vertices.')
        assert isinstance(dual_cell_indices[0], Iterable), (
            'Degenerated polytopes (points) are not handled.')
    except AssertionError as msg:
        logger.warning(msg)
        return None

    covol = 0
    for ids in dual_cell_indices:
        
        vtx_positions = np.array([position_vectors[k][idx] 
                                   for k, idx in enumerate(ids)])
        
        if ill_centered_simplices is None:
            weight = 1
        else:
            weight =(-1)**any((ill_centered_simplices[:]==ids[:2]).all(1))
            
        covol +=  weight * volume_simplex(vtx_positions)
    
    return covol


def dihedral_angle(blade_1: np.ndarray[float], 
                   blade_2: np.ndarray[float]) -> Optional[float]:
    """Computes the dihedral angle between two blades.

    Parameters
    ----------
    blade_1 : np.ndarray of float
        The first blade.
    blade_2 : np.ndarray of float
        The second blade.

    Returns
    -------
    float, optional
        The dihedral angle between the two blades.
    """
    
    try:
        if blade_1.shape[0] > 1:
            np.testing.assert_almost_equal(blade_1[:-1], blade_2[:-1],
            err_msg='Both blades should start by their common hinge.')
        
        volume_blades = volume_blade(blade_1) * volume_blade(blade_2)
        assert volume_blades != 0, 'Degrenerate blades (vol = 0) provided.' 
    
    except AssertionError as msg:
        logger.warning(msg)
        return None

    projection = dot(blade_1, blade_2)
    projection /= volume_blades
    projection = np.clip(projection, -1, 1) # Ensures the value is strictly 
                                            # bounded by +/- 1.
    return np.arccos(projection)


def angle_defect(blades: np.ndarray[float]) -> float:
    """Computes the angle defect at a hinge.

    Parameters
    ----------
    blades : np.ndarray of float
        The blades around the hinge.

    Returns
    -------
    float
        The angle defect at the hinge.
    """   
    angles = [dihedral_angle(*two_blades) for two_blades in blades]
    
    return 2*pi - sum(angles)


def whitney_form(barycentric_coordinates: np.ndarray[float],
                 gradient_barycentric_coordinates: np.ndarray[float], 
                 combinaisons: tuple[int], 
                 normalized: bool = False) -> np.ndarray[float] | float:
    """Computes the Whitney form.

    Parameters
    ----------
    barycentric_coordinates : np.ndarray of float
        The barycentric coordinates.
    gradient_barycentric_coordinates : np.ndarray of float
        The gradient of the barycentric coordinates.
    combinaisons : tuple of int
        The indices of the vertices of the simplex.
    normalized : bool, optional
        If True, the computed Whitney form is normalized. Default is False.

    Returns
    -------
    np.ndarray of float or float
        The Whitney form.
    
    Notes
    -----
    * We can only compute Whitney 0, 1 and 2-forms.
    * The degree of the form is detected from the number of provided indices.
    * 0-forms are depicted as scalars while 1- and 2-forms are depicted as 
      vectors.
    * 2-forms are formalized as pseudo-vectors normal to the corresponding 
      2-simplex.
    * The normalization of the form seems important to build a proper sharp
      operator.
    * We use the definiton of the Whitney form given by eq.(3.1) in
      Lohi et al (2021), cf see also section.
    
    See also
    --------
    * Lohi, J. & Kettunen, L. Whitney forms and their extensions. 
        J. Comput. Appl. Math. 393, 113520 (2021).
    """
    
    k = len(combinaisons) - 1
    phi = barycentric_coordinates
    dphi = gradient_barycentric_coordinates
    
    if k == 0:
        return phi[combinaisons]
    
    elif k == 1:
        i, j = combinaisons
        whitney_1form = np.asarray(phi[i] * dphi[j] - phi[j] * dphi[i] )
        if normalized:
            whitney_1form /= lng.norm(whitney_1form)
        return whitney_1form
    
    elif k == 2:
        i, j, k = combinaisons
        whitney_2form = phi[i] * wedge_between(dphi[j], dphi[k]) \
                      - phi[j] * wedge_between(dphi[i], dphi[k]) \
                      + phi[k] * wedge_between(dphi[i], dphi[j])
        whitney_2form *= 2
        if normalized:
            whitney_2form /= lng.norm(whitney_2form)
        return whitney_2form
    
    else: 
        logger.warning(f'Cannot compute Whitney {k}-form; only for k < 3.')
        return None

