# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.utils.quality_control
#
# This submodule contains useful functions to assess the quality
# of the simplices forming a simplicial complex.
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

from typing import Tuple

import numpy as np
import numpy.linalg as lng

import pandas as pd

from dxtr import logger
from dxtr.complexes import SimplicialComplex, SimplicialManifold, Simplex
from dxtr.math.geometry import circumcenter_barycentric_coordinates


def simplex_shape_regularity_score(splx: Simplex) -> float:
    """Quantifies the regularity of a simplex.
    
    Parameters
    ----------
    splx : Simplex
        The simplex to analyze.
    
    Returns
    -------
    float
        A float between 0 and 1 defined as: 
        1 - std(edge_lengths) / mean(edge_lengths)

    Notes
    -----
    A score of 1 corresponds to the most regular simplex; i.e. one with
    all its edges of equal length.

    This measure is meaningful only for k-simplices with k >= 2.
    Therefore, we return 1 for all k-simplices with k < 2.
    """

    if splx.dim < 2: return 1

    edges = splx.vertices - np.vstack((splx.vertices[1:],
                                       splx.vertices[:1]))

    edge_lengths = lng.norm(edges, axis=1)

    avg_edge_length = edge_lengths.mean()
    std_edge_length = edge_lengths.std()
    
    if np.isclose(avg_edge_length, 0):
        return 0
    else:
        return 1 - std_edge_length / avg_edge_length


def shape_regularity_score(cplx: SimplicialComplex, 
                           return_scores: bool = False
                           ) -> Tuple[float] | np.ndarray[float, int]:
    """Quantifies the regularity of a simplicial complex.

    Parameters
    ----------
    cplx : SimplicialComplex
        The n-simplicial complex to consider.
    return_scores : bool, optional
        If True, returns an array with the regularity scores of all n-simplices.
        Else returns only the median value and the standard deviation. Default is False.

    Returns
    -------
    tuple of float or np.ndarray
        (Median, standard deviation) or array of all n-simplex regularity scores.
    
    Notes
    -----
    * The computed scores are only relevant for k-simplices with k>=2.
    * The score is based on the comparison of the edge lenghts. A regular k-simplex with edges of the same length will score 1.

    See also
    --------
    The `simplex_shape_regularity_score()` function within the same sub-module.
    """

    scores = np.array([simplex_shape_regularity_score(splx) 
                       for splx in cplx[-1]])

    if return_scores:
        return scores
    else:
        return np.median(scores), scores.std()


def well_centered_score(mfld: SimplicialManifold, 
                        return_scores: bool = False,
                        verbose: bool = False
                        ) -> float | np.ndarray[float, int]:
    """Quantifies how well-centered are simplices within a manifold.
    
    Parameters
    ----------
    mfld : SimplicialManifold
        The simplicial manifold to investigate.
    return_scores : bool, optional
        If True, returns scores of all n-simplices. Default is False.
    verbose : bool, optional
        Prints a summary if True. Default is False.
    
    Returns
    -------
    float or tuple of float and np.ndarray
        The ratio of well-centered n-simplices within the n-manifold and
        the scores (optional).

    Notes
    -----
    We arbitrarily consider well-centered simplices 
    with circumcenter lying on an edge (i.e. one of its 
    barycentric coordinates vanishes). This is debatable.

    In its current version, this method does not quantify how much 
    the ill-centered simplices are ill-centered. The closer it is to zero, the 
    less ill-centered the simplex is.

    The individual score of ill-centered simplices corresponds to the negative 
    barycentric coordinate. The more negative it is, the worse the triangle is.
    """
    nbr_splcs_tot = mfld.shape[-1]
    vertices =  mfld[-1].vertices
    
    ccntr_pos = np.array([circumcenter_barycentric_coordinates(vtcs).min()
                          for vtcs in vertices])

    ill_centered_sids = np.where(ccntr_pos < 0)[0]
    
    nbr_ill_centered = len(ill_centered_sids)
    well_centered_ratio = 1 - nbr_ill_centered / nbr_splcs_tot

    if verbose: 
      logger.info(f'{well_centered_ratio:.1%} of well-centered '
            + f'{mfld.dim}-simplices. {nbr_ill_centered} ill-centered '
            + f'ones over {nbr_splcs_tot} in total.')
    if return_scores:
        return well_centered_ratio, ccntr_pos
    
    else:
        return well_centered_ratio


def complex_quality(complex: SimplicialComplex) -> pd.DataFrame[float]:
    """Computes various regularity estimators on a simplicial complex.

    Parameters
    ----------
    complex : SimplicialComplex
        The n-simplicial complex to analyze.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing regularity estimator values 
        for each n-simplex of the considered n-complex.

    Notes
    -----
    List of the regularity estimators computed:
    * regularity score
    * well-centeredness score
    """

    shape_regularity = shape_regularity_score(complex, return_scores=True)
    wc_ratio, well_centeredness = well_centered_score(complex,
                                                      return_scores=True)
    
    is_well_centered = [score<0 for score in well_centeredness]

    return pd.DataFrame({'Shape regularity score': shape_regularity,
                         'Well-centeredness score': well_centeredness,
                         'Well-centered': is_well_centered
                        })