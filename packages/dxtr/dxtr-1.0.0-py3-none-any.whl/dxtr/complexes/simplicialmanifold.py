# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.objects
#
# This file contains one class:
#     - `SimplicialManifold`
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
from typing import Optional, Tuple, Iterable

import numpy as np
import numpy.linalg as lng

from dxtr import logger
from dxtr.utils.typecheck import typecheck
from dxtr.complexes.simplicialcomplex import (SimplicialComplex, 
                                            primal_edge_vectors)
from dxtr.math.geometry import (circumcenter, volume_polytope, angle_defect, 
                                circumcenter_barycentric_coordinates, 
                                dihedral_angle)
from dxtr.math.topology import (complex_simplicial_partition,
                                cell_simplicial_partition)

class SimplicialManifold(SimplicialComplex):
    """Embodies the concept of simplicial manifold."""

    def __init__(self, simplices: list[list[int]], 
                 vertices: Iterable[Iterable[float]], 
                 name: Optional[str]=None)-> None:
        """Initializes a `SimplicialManifold` object.

        Parameters
        ----------
        simplices : list of list of int
            The list of vertex indices forming the highest degree simplices.
        vertices : iterable of iterable of float, optional
            The coordinates of the vertices. Default is None.
        name : str, optional
            A name for the manifold. Default is None.
        """
        super().__init__(simplices, vertices, name)

        if _isvalid_for_dualization(self):
            self.build_dual_geometry()

    def __str__(self):
        """Returns a string representation of the manifold.

        Returns
        -------
        str
            A string representation of the manifold.
        """
        description = f'{self.dim}D Simplicial Manifold of '
        description += f'shape {self.shape}, '
        description += f'embedded in R^{self.emb_dim}.'
        return description

    @property
    def name(self) -> str:
        """Name of the manifold."""
        if self._name is None:
            return self.__str__()[:22]
        else:
            return self._name
    
    @name.setter
    def name(self, new_name:str) -> None:
        """Sets a custom name for the manifold."""
        self._name = new_name

    @property
    def deficit_angles(self) -> Optional[np.ndarray[float]]:
        """Returns the deficit angles computed on all (n-2)-simplices.

        Notes
        -----
        The deficit angle is a discrete version of the gaussian curvature.
        """
        return self[self.dim-2]._deficit_angles
    
    @property
    def dihedral_angles(self) -> Optional[np.ndarray[float]]:
        """Returns the dihedral angles computed on all (n-1)-simplices.
        """
        return self[self.dim-1]._dihedral_angles

    @classmethod
    def from_file(cls, path: str, 
                  name: Optional[str]=None) -> SimplicialManifold:
        """Instantiates a `SimplicialManifold` from a `.ply` file.

        Parameters
        ----------
        path : str
            The path to the `.ply` file.
        name : str, optional
            A name for the manifold. Default is None.

        Returns
        -------
        SimplicialManifold
            The instantiated simplicial manifold.
        """
        
        from dxtr.io import read_ply
        
        indices, vertices = read_ply(path)

        return cls(indices, vertices, name)

    def build_dual_geometry(self) -> None:
        """Computes 0-cells positions, covolumes, deficit & dihedral angles.

        Notes
        -----
        Position vectors of 0-cells/n-simplices are taken as
        the circumcenter of the position vectors of the surrounding
        n-cells/0-simplices.
        Sign of mtrx_inv is set to satisfy: mtrx_inv * mtrx = -1 ^(k*(n-k))
        """
        _compute_circumcenters(self)
        _compute_covolumes(self)
        _compute_deficit_angles(self)
        _compute_dihedral_angles(self)


    def update_geometry(self, displacement:dict[int,np.ndarray[float]]) -> None:
        """Updates some vertices and the corresponding geometrical properties.

        Parameters
        ----------
        displacement : dict of int to np.ndarray of float
            The displacement to add to the selected vertices.
            - keys: The indices of the vertices to move.
            - values: The displacement to add to the selected vertices.

        Notes
        -----
        The `SimplicialManifold` version of this method calls the one from
        the mother class `SimplicialComplex` to update the positions of 
        the vertices and the volumes of the simplices.
        In this specific version, circumcenters and covolumes are also
        updated.
        Deficit angles are updated through a specific method:
        `update_deficit_angle()`.
        """

        super().update_geometry(displacement)

        moved_vids = list(displacement.keys())

        _compute_circumcenters(self, surrounding=moved_vids)
        _compute_covolumes(self, surrounding=moved_vids)
        _compute_deficit_angles(self, surrounding=moved_vids)
        _compute_dihedral_angles(self, surrounding=moved_vids)



# ################# #
# Usefull functions #
# ################# #

def _isvalid_for_dualization(complex:SimplicialComplex) -> None:
    """Checks if the considered complex can be dualized.

    Notes
    -----
    The complex needs to be pure.
    The complex needs to be everywhere homeomorphic to a nD sphere.
    """
    try:
        n = complex.dim
        assert complex.ispure, 'The considered complex is not pure.'
        assert np.all([len(cfcs)<=2 for cfcs in complex.cofaces(n-1)]), (
        'The considered complex is not homeomorphic to a sphere everywhere.')

        logger.info('Computing Dual Cells Complex.')
        return True

    except AssertionError as msg:
        logger.warning(msg)
        return False


def _compute_circumcenters(complex:SimplicialComplex,
                          surrounding:Optional[list[int]]=None) -> None:
    """Computes the circumcenters of all the simplices within a complex.

    Parameters
    ----------
    complex : SimplicialComplex
        The simplicial complex to compute the circumcenters for.
    surrounding : list of int, optional
        The indices of the vertices to consider. Default is None.

    Notes
    -----
    If surrounding is None, circumcenters are computed for all top simplices within the manifold.
    """
    if surrounding is None:
        for k, mdl in enumerate(complex):
            if k == 0:
                ccenters = mdl.vertices
            else:
                ccenters = np.array([circumcenter(vtcs) 
                                     for vtcs in mdl.vertices])

            mdl.set('circumcenters', ccenters)
    else:
        for k, mdl in enumerate(complex):
            if k==0:
                mdl._circumcenters[surrounding] = mdl.vertices[surrounding]
            
            else:
                sids = complex.star(surrounding, 0)[k]
                vids = np.array([complex.closure({k: idx})[0] 
                                for idx in range(mdl.size)])[sids]

                mdl._circumcenters[sids] = np.array([circumcenter(pts)
                                        for pts in complex[0]._vertices[vids]])


def _compute_covolumes(complex:SimplicialComplex,
                       surrounding:Optional[list[int]]=None) -> None:
    """Computes the covolumes of all simplices within a complex.

    Parameters
    ----------
    complex : SimplicialComplex
        The simplicial complex to compute the covolumes for.
    surrounding : list of int, optional
        The indices of the vertices to consider. Default is None.

    Notes
    -----
    To be valid in any dimension, we partition the dual cells of the 
    considered simplices into simplices of their own. Then, we 
    compute the volume of these simplices and add them together.
    """
    n = complex.dim

    if surrounding is None:
        chain_cplx = complex._chain_complex

        dual_cplx_partition = complex_simplicial_partition(chain_cplx)
        ill_cntred = _detect_ill_centered_cofaces(complex)
        
        for k, mdl in enumerate(complex):
            if k == n:
                covolumes = np.ones(mdl.size)
            else:                
                positions = [complex[i].circumcenters for i in range(k, n+1)]

                # Splitting the list of indices into cells
                cids = dual_cplx_partition[k]
                cut_indices = np.where(np.diff(cids[:, 0])==1)[0]+1
                dual_cell_indices = np.split(cids, cut_indices) 

                covolumes = np.array([
            volume_polytope(positions, ids, 
                            ill_centered_simplices=ill_cntred[k])
                            for ids in dual_cell_indices])

            mdl.set('covolumes', covolumes)

    else:
        for k in range(n):
            sids = complex.closure(complex.star(surrounding, 0))[k]
            dual_cell_indices = [cell_simplicial_partition(
                                    complex._chain_complex, sid, k)
                                    for sid in sids]
                    
            pos = [complex[i].circumcenters for i in range(k, n+1)]

            complex[k]._covolumes[sids] = np.array([volume_polytope(pos, ids)
                                for ids in dual_cell_indices])


def _detect_ill_centered_cofaces(complex:SimplicialComplex
                                  ) -> list[Optional[np.array[int]]]:
    """Gets couples of k-simplex and (k+1)-coface that are ill-centered.

    Parameters
    ----------
    complex : SimplicialComplex
        The simplicial complex to detect ill-centered cofaces for.

    Returns
    -------
    list of Optional[np.array[int]]
        A list of (N, 2)-shaped arrays where N = number of ill-centered 
        (k+1)-cofaces. Each row of the arrays contains 2 integer:
        - first one is the index of the k-simplices with an ill-centered coface.
        - second one is the index of the (k+1)-coface that is ill-centered. 
        See Notes for more details.
    
    Notes
    -----
    When all k-simplices have well-centered (k+1)-cofaces, 
    the kth element of the returned list is set to None.
    0-simplices always have well-centered 1-cofaces for segments have their
    circumcenters within them by construction.
    Similarly, the computation is irrelevant for n-simplices. 
    Consequently, the first and last entries of the returned list are 
    always None.
    The negative barycentric coordinate is related to the opposite summit.
    To get the idx of the ill-(k-1)-simplex, we check which (k-1) face 
    does not feature this summit as a face.
    Detecting simplices with ill-centered cofaces is crutial to properly 
    compute covolumes.
    """
    
    ill_centered_splcs_faces = [None]
    
    for k in range(2, complex.dim+1):
        mdl, fids, ffids = complex[k], complex.faces(k), complex.faces(k-1)

        sid_fid_couples = []
        for sid, vcts in enumerate(mdl.vertices):
            bary_coords = circumcenter_barycentric_coordinates(vcts)
            
            if np.any(bary_coords < 0):
                ill_vid = mdl[sid].indices[bary_coords.argmin()]

                idx = [ill_vid not in ffids[fid] 
                       for fid in fids[sid]].index(True)

                sid_fid_couples.append((fids[sid][idx], sid))
        
        if len(sid_fid_couples) == 0:
            ill_centered_splcs_faces.append(None)
        else:  
          ill_centered_splcs_faces.append(np.asarray(sid_fid_couples))
    
    ill_centered_splcs_faces.append(None)
    
    return ill_centered_splcs_faces


def _compute_deficit_angles(complex:SimplicialComplex,
                            surrounding:Optional[list[int]]=None) -> None:
    """Computes the deficit angles within a n-simplicial complex.

    Parameters
    ----------
    complex : SimplicialComplex
        The simplicial complex to compute the deficit angles for.
    surrounding : list of int, optional
        The indices of the vertices to consider. Default is None.

    Notes
    -----
    Deficit angle:
    is computed for (n-2)-simplices.
    is defined as 2*pi - sum(defect angle).
    If the considered manifold is not closed, the computed values 
    on the boundaries should be double checked.
    TODO: Look at what happends on open manifold boundaries.
    """
    k = complex.dim - 2

    faces_and_cofaces = (complex.faces(k+2),
                         complex.cofaces(k),
                         complex.cofaces(k, k+2))
    
    if surrounding is None:
        all_blades = [_blades_around_hinge(complex, hidx, faces_and_cofaces) 
                      for hidx, _ in enumerate(complex[k])]
        
        deficit_angles = np.array([angle_defect(blades)
                                  for blades in all_blades])
        
        complex[k].set('deficit angles', deficit_angles)
    
    else:
        hids_to_update = complex.closure(complex.star(surrounding, 0))[k]
        
        moved_blades = [_blades_around_hinge(complex, hidx, faces_and_cofaces) 
                        for hidx in hids_to_update]

        complex[k]._deficit_angles[hids_to_update] = np.array([
            angle_defect(blades) for blades in moved_blades])


def _blades_around_hinge(complex:SimplicialComplex, hinge_idx: int, 
                        faces_and_cofaces:Tuple[list[int]],
                        hinge_dim: Optional[int]=None
                        ) -> Optional[np.ndarray[float]]:
    """Lists the (k+1)-blades around a k-hinge within a simplicial complex.

    Parameters
    ----------
    complex : SimplicialComplex
        The SimplicialComplex to work on.
    hinge_idx : int
        The index of the k-simplex to consider as an hinge.
    faces_and_cofaces : tuple of list of int
        A tuple of three list, in order:
        * faces: The faces of all the (k+2)-simplices
        within the complex. N.B: k = hinge topological dimension.
        * cfaces: The cofaces of all k-simplices within the complex.
        * ccfaces: The second order cofaces of all  k-simplices 
        within the complex.
    hinge_dim : int, optional
        Default is None. The topological dimension of hinge to 
        consider, noted k after. If None, it is set to complex.dim - 2.
    
    Returns
    -------
    np.ndarray of float, optional
        A (N * 2 * (k+1) * D) array containing the N couples of k+1 edges vector 
        of dimension D (= the embedding dimension) defining the 2 (k+1)-blades.

    Notes
    -----
    The hinge topological dimension is optional because the main purpose 
    of this method is to compute deficit angles and scalar curvature. Such
    things always corresponds to hinge of dimension (n-2) in complexes of 
    dimension n.
    """
    n = complex.dim
    k = n-2  if hinge_dim is None else hinge_dim
    
    faces, cfaces, ccfaces = faces_and_cofaces

    # Organizing the ids of consecutive cofaces of the hinge two-by-two.
    hinge_coface_ids = [list(set(faces[ccfid]) & set(cfaces[hinge_idx]))
                        for ccfid in ccfaces[hinge_idx]]

    # Substituing the coface ids by the list of ids of their vertices.
    hinge_coface_vtx_ids = [complex[k+1][idx].indices 
                            for row in hinge_coface_ids
                            for idx in row]
    
    # Ordering the vertex ids so that all blades have the same orientation.
    hinge_vtx_ids = list(complex[k][hinge_idx].indices)
    
    nbr_hinge_ccf = len(hinge_coface_ids)

    ordered_hinge_coface_vtx_ids = np.array([
        hinge_vtx_ids + list((set(vtx_ids) - set(hinge_vtx_ids)))
    for vtx_ids in hinge_coface_vtx_ids]).reshape(nbr_hinge_ccf, 2, k+2)

    # Injecting the vertex position vectors and computing the blades.
    vtcs = complex._vertices[ordered_hinge_coface_vtx_ids]

    return vtcs[:,:,1:,:] - vtcs[:,:,:1,:]


def _compute_dihedral_angles(complex:SimplicialComplex,
                             surrounding:Optional[list[int]]=None) -> None:
    """Computes dihedral angles btwn top-simplices of a `SimplicialManifold`.

    Parameters
    ----------
    complex : SimplicialComplex
        The simplicial complex to compute the dihedral angles for.
    surrounding : list of int, optional
        The indices of the vertices to consider. Default is None.

    Returns
    -------
    np.ndarray of float, optional
        An array of shape (N,) where N = the number of inner (n-1)-simplices 
        of the considered n-simplicial complex.
    
    Notes
    -----
    If the provided `SimplicialComplex` is not closed, the computation is
    only performed on its interior.
    If the `SimplicialComplex` is only composed of 1 top-simplex, the 
    _dihedral_angles attribute remains to None.
    TODO: Check that this is working properly on open manifolds... I suspect
    that the computed dihedral angles arrray is not correct. (missing zeros)
    The part updating partially the values has not been tested. TODO !!!

    See also
    --------
    `_orient_top_simplex_couples()`
    `dihedral_angle` from `dxtr.math.geometry`.
    """
    n = complex.dim
    k = n - 1

    if complex[n].size == 1: return None

    top_splx_ids = _orient_top_simplex_couples(complex)
    top_splx_vtcs = complex[0].vertices[top_splx_ids]
    blade_couples = top_splx_vtcs[:,:,1:] - top_splx_vtcs[:,:,:1]

    if surrounding is None:    
        dihedral_angles = np.array([dihedral_angle(*blade_couple) 
                                    for blade_couple in blade_couples])

        complex[k].set('dihedral angles', dihedral_angles)
    
    else:
        eids_to_update = complex.closure(complex.star(surrounding, dim=0))[k]
        moved_bld_cpls = blade_couples[eids_to_update]
        changed_dihedral_angles= np.array([dihedral_angle(*blade_couple) 
                                           for blade_couple in moved_bld_cpls])
        
        complex[k]._dihedral_angles[eids_to_update] = changed_dihedral_angles


def _orient_top_simplex_couples(complex:SimplicialComplex
                                 ) -> np.ndarray[float]:
    """Formats the top-simplex vertex indices in a specific manner.

    Parameters
    ----------
    complex : SimplicialComplex
        The simplicial complex to format the top-simplex vertex indices for.

    Returns
    -------
    np.ndarray of float
        An array of integers of shape (N, 2, n+1) where: n is the complex 
        dimension and N is the number of inner (n-1)-simplices. See Notes for 
        further explanation.

    Notes
    -----
    The purpose of this function is to format the order of vertex indices
    around n-simplices to ease the computation of dihedral angles at 
    (n-1)-simplices.
    This algorithm only runs on the inner (n-1)-simplices to avoid problems
    in the case of open `SimplicialComplex`.
    Explanation of the output array:
    Axis 0 corresponds to (n-1)-simplices.
    For each one of them there is a couple of n+1 integers, 
    corresponding to the list of vertex indices of their two n-cofaces.
    These vertex indices are given in a precise order: The n-first ones 
    correspond to the vertex indices of the (n-1)-simplex.
    This is necessary so when the corresponding blades are computed, 
    the n-1 first edge vectors of the two neighboring blades are the 
    same. This is a requirement of the `dihedral_angle()` function.
    
    See also
    --------
    `dihedral_angle` from `dxtr.math.geometry`.
    """
    
    k = complex.dim - 1

    if complex.isclosed:
        Nk = complex.shape[k]
        sids = np.arange(Nk)
    else:
        sids = complex.interior()[k]
        Nk = len(sids)

    hinge_vtx_ids = np.repeat(complex[k].vertex_indices[sids], 2, axis=0
                              ).reshape((Nk, 2, k+1))
    sum_hinge_vtx_ids = hinge_vtx_ids.sum(axis=-1)

    all_coface_ids = complex.cofaces(k)
    hinge_coface_ids = [all_coface_ids[sid] for sid in sids]
    splx_vtx_ids = complex[k+1].vertex_indices
    sum_splx_vtx_ids = splx_vtx_ids[hinge_coface_ids].sum(axis=-1)
    
    third_splx_vxt_idx = np.subtract(sum_splx_vtx_ids, 
                                     sum_hinge_vtx_ids).reshape(Nk, 2, 1)

    return np.concatenate((hinge_vtx_ids, third_splx_vxt_idx), axis=-1)


@typecheck(SimplicialManifold)
def dual_edge_vectors(of:SimplicialManifold, 
                      normalized:bool=False) -> np.ndarray[float]:
    """Computes vectors along the dual 1-cells of a `SimplicialManifold`.

    Parameters
    ----------
    of : SimplicialManifold
        The `SimplicialManifold` to work on.
    normalized : bool, optional
        If True, returned unit vectors. Default is False.

    Returns
    -------
    np.ndarray of float
        A (N,D) array with N = number of (n-1)-simplices, 
        D = the dimension of the embedding space.
    
    Notes
    -----
    In the case of a non-closed manifold, the outer dual edges are 
    oriented outward from the circumcenters of the top-simplices toward
    the circumcenters of the (n-1)-simplices on the border.
    """
    
    mfld = of
    
    vertices = mfld[-1].circumcenters
    edges = mfld[-1].boundary @ vertices
    
    if not mfld.isclosed:
        in_eids = mfld.interior()[1]
        inner_edges = dict(zip(in_eids, edges[in_eids]))

        brd_eids = mfld.border()[1]
        brd_vertices = mfld[-2].circumcenters[brd_eids]

        brd_tids = [mfld.cofaces(mfld.dim-1)[eid][0] for eid in brd_eids]
        
        outer_edges = brd_vertices - vertices[brd_tids]
        outer_edges = dict(zip(brd_eids, outer_edges))

        all_edges = inner_edges | outer_edges
        edges = np.asarray([edge for _, edge in sorted(all_edges.items())])
    
    if normalized:
        edges /= lng.norm(edges, axis=-1).reshape(*edges.shape[:-1], 1)

        # to deal with the edges of length 0.
        if np.isnan(edges).any(): 
            nul_edids = np.where(np.isnan(edges))[0]
            edges[nul_edids] = 0
            logger.warning(f'There are {len(nul_edids)} vanishing dual edges.')

    return edges


@typecheck(SimplicialComplex)
def edge_vectors(manifold:SimplicialManifold|SimplicialComplex, 
                 dual:bool=False, normalized:bool=False) -> np.ndarray[float]:
    """Computes edge vectors on `SimplicialComplex` or `SimplicialManifold`.

    Parameters
    ----------
    manifold : SimplicialManifold or SimplicialComplex
        The `SimplicialManifold` to work on.
    dual : bool, optional
        If True, the computation is performed on the dual complex. 
        Else, it is performed on the primal one. Default is False.
    normalized : bool, optional
        If True, the computed vectors are of unit norm. Default is False.

    Returns
    -------
    np.ndarray of float
        A (N,D) array with N = number of (n-1)-simplices if on==True else
        number of 0-simplices, D = the dimension of the embedding space.
    
    Notes
    -----
    Can only compute dual edges on `SimplicialManifold` not on
    `SimplicialComplex`.
    """
    if dual:
        if not isinstance(manifold, SimplicialManifold):
            logger.warning(
                'Cannot compute dual edge vectors on `SimplicialComplex`.')
            return None
        else:
            return dual_edge_vectors(manifold, normalized=normalized)
    else:
        return primal_edge_vectors(manifold, normalized=normalized)


