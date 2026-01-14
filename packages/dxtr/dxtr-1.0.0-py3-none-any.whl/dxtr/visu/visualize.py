# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.visu.visualize
#
# In this submodule we define a function to visualize the various objects 
# of the dxtr library. This function calls more specific ones, stored in the 
# pyvista and plotly submodules, depending on the type of visualization 
# that we want.
#
#       File author(s):
#           Olivier Ali <olivier.ali@inria.fr>
#
#       File contributor(s):
#           Olivier Ali <olivier.ali@inria.fr>
#           Florian Gascon <florian.gascon@inria.fr>
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
from typing import Optional

from dxtr.complexes import Simplex, SimplicialComplex
from dxtr.cochains import Cochain
from dxtr.utils import typecheck
from .visu_plotly import visualize_with_plotly
from .visu_pyvista import visualize_with_pyvista


@typecheck([Simplex, SimplicialComplex, Cochain])
def visualize(object: Simplex|SimplicialComplex|Cochain,
              library: Optional[str]=None, **kwargs) -> None:
    """Draw the provided object with the considered library.

    Parameters
    ----------
    object : Simplex, SimplicialComplex, or Cochain
        The structure to visualize, should be an instance of `Simplex`, 
        `SimplicialComplex` or `Cochain`.
    library : str, optional
        The name of the visualization library to use. If specified, should be 
        either 'plotly' or 'pyvista'. Default is None.

    Other Parameters
    ----------------
    degrees : int, list of int, or str, optional
        The (list of) simplex degree(s) to display. Default is 'all'.
    show : str, optional
        What complex(es) to display. Should be in ['primal', 'dual', 'all']. Default is 'primal'.
    highlight : dict, optional
        Subset of simplices to highlight. If given as dict:
            - keys : int. simplex degrees.
            - values : list of int. collection of simplex indices.

    Notes
    -----
    If no library is specified at calling, the choice will be made depending 
    on the type of the first argument: If object is an instance of 
    `SimplicialComplex`, the `plotly`-based method will be called. If object 
    is of type `Cochain`, the `pyvista`-based method will be called.

    Use the `plotly`-based method for exploration of `SimplicialComplex` 
    objects for `plotly`-based methods are interactive; therefore better 
    suited to explore visually the objects.

    Use the `pyvista`-based methods to visualize `Cochain` objects.

    See Also
    --------
    visualize_with_plotly : The `_visualize_with_plotly()` function from the 
        `visualize_plotly` sub-module, for details and specific keyword 
        arguments listing.
    visualize_with_pyvista : The `_visualize_with_pyvista()` function from the 
        `visualize_pyvista` sub-module, for details and specific keyword 
        arguments listing.
    """
    if library is None:
        library = 'pyvista' if isinstance(object, Cochain) else 'plotly'
    
    if library == 'plotly':
        return visualize_with_plotly(object, **kwargs)
    
    elif library == 'pyvista':
        return visualize_with_pyvista(object, 
                               fig=kwargs.get('fig', None), 
                               scaling_factor=kwargs.get('scaling_factor', 1), 
                               data_range=kwargs.get('data_range', None),
                               display=kwargs.get('display', True), 
                               layout_parameters=kwargs.get('layout_parameters', {}))

