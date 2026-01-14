# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.visu.pyvista
#
# This submodule gathers some functions to ease the visualization of
# Simplicial Complexes within jupyter notebooks based on the pyvista library.
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
from typing import Optional, Tuple
import numpy as np

try:
    import pyvista as pv
except ImportError as msg:
    err_msg = 'pyvista not properly installed.'
    logger.warning(err_msg)

from dxtr import logger
from dxtr.utils import typecheck
from dxtr.cochains import Cochain
from dxtr.utils.logging import require_pyvista
from dxtr.utils.wrappers import UGrid


@require_pyvista
@typecheck(Cochain)
def visualize_with_pyvista(cochain:Cochain, fig:Optional[pv.Plotter]=None,
                           scaling_factor:float=1, 
                           data_range: Optional[Tuple]=None, display:bool=True, 
                           layout_parameters:dict={}) -> Optional[pv.Plotter]:
    """Generates a pyvista Plotter to visualize a `Cochain`.

    Parameters
    ----------
    cochain
        The cochain to visualize.
    fig
        Optional (default is None). An existing `pv.Plotter` to which
        the `Cochain` is added.
    scaling_factor
        Optional (default is 1). A multiplier to apply to all values of the 
        `Cochain` prior to its visualization. Mostly useful for vector-valued
        cochains.
    data_range
        Optional, default is None. A Tuple (val_min, val_max) to clip the 
        data we want to visualize.
    display
        Optional (default is False). If True, the `pv.Plotter` object 
        containing the data is displayed.
    layout_parameters
        Optional (default is {}). Contains values for rendering parameters, 
        c.f. See Also section.
        * keys: parameter names, should be in:
          ['background_color','window_size', 'title']
        * values: parameters values.

    Returns
    -------
        `pv.Plotter` containing the desired `Cochain`.

    Notes
    -----
      * The argument `display` is used if one wants to add multiple objects to 
        the same visualization. In this case the `display` argument should be 
        set to `False` for all calls except the last one.
      * In the current version vector-valued dual cochains are represented on 
        the primal complex with vectors at the circumcenters of top-simplices.
        Maybe it could be interesting to enable the visualization on the dual 
        cell complex?
      * When a vector-valued `Cochain` is provided, the surface is colored as 
        well, but apparently, this color corresponds to the first component of 
        the vector field, v_x. TODO:This should be changed
    
    See Also
    --------
      * `_set_layout()` function in the same module for details on the
         layout parameters.
    """

    if (data_range is not None) & (not cochain.isvectorvalued):
        clipped_values = np.clip(cochain.values, data_range[0], data_range[-1])
        cochain = Cochain(cochain.complex, cochain.dim, clipped_values,
                          dual=cochain.isdual)

    data = '_'.join(cochain.name.split(' '))
    # data = cochain.name

    if fig is None: fig = pv.Plotter(border=False)
    
    if not _isvalid_for_visualization(cochain, fig): return None
    
    mesh = UGrid.generate_from(cochain, scaling_factor=scaling_factor, 
                               for_visualization=True)

    if (cochain.dim == 1) & (not cochain.isvectorvalued):
        fig.add_mesh(mesh, style='surface', color='w')

        # body = pv.Cylinder(resolution=100, height=.1, radius=.005)
        head = pv.Cone(resolution=100, center=(0,0,0), height=.05, radius=.02)
        
        # arrow_bodies = mesh.glyph(scale=data, orient=data, geom=body)
        arrow_heads = mesh.glyph(scale=data, orient=data, geom=head)
        
        # fig.add_mesh(arrow_bodies, show_scalar_bar=False)
        fig.add_mesh(arrow_heads, show_scalar_bar=False)
    
    elif cochain.isvectorvalued:
        fig.add_mesh(mesh, style='surface', color='w')
        arrows = mesh.glyph(scale=data, orient=data)
        fig.add_mesh(arrows, show_scalar_bar=False,
                     cmap=layout_parameters.get('colormap', 'viridis'))
    
    else:
        cplx_name = cochain.complex.name
        fig.add_mesh(mesh, show_scalar_bar=False, 
                    cmap=layout_parameters.get('colormap', 'viridis'))
        
        if layout_parameters.get('show_colorbar', False):
            fig.add_scalar_bar(f'{data[:1]} on {cplx_name[:1]}',
                               title_font_size=1, fmt='%.1f',)
    
    fig = _set_layout(fig, layout_parameters)

    if display: fig.show()
    
    return fig


def _isvalid_for_visualization(cochain:Cochain, fig:pv.Plotter) -> bool:
    """Check the provided arguments are in order for visualization.

    Parameters
    ----------
    cochain
        The `Cochain` to visualize.
    fig
        The `pv.Plotter` where we want the visualization.

    Returns
    -------
        True if everthing is in order, False otherwise.
    
    Notes
    -----
    The requirements are:
      * The `Cochain` must be of dimension 0, 1 or 2.
      * The values of the `Cochain` must be given as an `np.ndarray`.
      * The `Cochain` must be either scalar- or vector-valued.
      * The fig argument must be a valid `pv.Plotter` instance.
    """

    try:
        k = cochain.dim
        assert k in [0, 1, 2], f'{k}D-cochains not supported.'

        assert isinstance(cochain.values, np.ndarray), (
            f'Unsupported type of cochain.values: {type(cochain.values)}')
        
        assert cochain.values.ndim <= 2, ('Wrong shape of cochain.values:'
            +'only scalar-valued and vector-valued cochains are supported.')
        
        if cochain.values.ndim == 2:
            D = cochain.complex.emb_dim
            assert cochain.values.shape[-1] == D, (
                f'Vector-values cochain must be composed by {D}D vectors.')
        
        assert isinstance(fig, pv.Plotter), (
            f'The `fig` argument must be a `pv.Plotter` instance.')
        
        return True
    
    except AssertionError as msg:
        logger.warning(msg)
        return False


def _set_layout(fig:pv.Plotter, parameters:dict={}) -> pv.Plotter:
    """Sets some visualization parameters.

    Parameters
    ----------
    fig
        the `pv.Plotter()` to tune.
    parameters
        Optional (default is {}), see Notes for details.
        * keys: The properties of the `pv.Plotter` to modify.
        * values: The desired values.

    Returns
    -------
        The updated version of the input `pv.Plotter`.
    
    Notes
    -----
    Accepted parameters:
      * 'background_color', default = (255, 255, 255). 
        Accepted value types: str (e.g. 'k' or 'black'), rgb code tuples
        (e.g. (0,0,0)), hexa code (e.g. #FFFFFF).
      * 'window_size', default = None. Format = (width, height). When set
        to None, the window automatically scales with the display.
      * 'title', default = ''. 
      * 'title_font_size', default = 8. 
      * 'color_range', default is None, should be set as [val_min, val_max].
      * TODO: Add the ability to show a legend.
      * TODO: Add the ability to change the opacity of the surface.
    """

    
    fig.add_title(parameters.get('title', ''), 
                  font_size=parameters.get('title_font_size', 8))
    fig.set_background(parameters.get('background_color', (255, 255, 255)))
    if parameters.get('window_size', None) is not None:
        fig.window_size = parameters['window_size']

    return fig

