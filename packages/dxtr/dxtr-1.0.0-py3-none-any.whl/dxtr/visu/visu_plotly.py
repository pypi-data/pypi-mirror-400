# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.visu.plotly
#
# This submodule gathers some functions to ease the visualization of
# Simplicial Complexes within jupyter notebooks based on the plotly library.
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
import numpy as np
import numpy.linalg as lng
from collections.abc import Iterable
import plotly.graph_objects as go
import plotly.express as px

from itertools import combinations
from scipy.special import binom

from dxtr import logger
from dxtr.complexes import Simplex, SimplicialComplex, SimplicialManifold
from dxtr.utils import typecheck


@typecheck([Simplex, SimplicialComplex])
def visualize_with_plotly(input: Simplex|SimplicialComplex,
                          degrees: int|list[int]|str='all',
                          display:bool=True,
                          highlight: Optional[dict]=None, 
                          **kwargs) -> go.Figure:
    """Display simplicial complexes with the plotly library.

    Parameters
    ----------
    input : Simplex or SimplicialComplex
        The structure to display.
    degrees : int, list of int, or str, optional
        The (list of) simplex degree(s) to display. Default is 'all'.
    display : bool, optional
        If True, the figure is automatically displayed. Default is True.
    highlight : dict, optional
        Subset of simplices to highlight. If given as dict:
            - keys : int. simplex degrees.
            - values : list of int. collection of simplex indices.

    Other Parameters
    ----------------
    show_grid : bool, optional
        If True, reveals the Euclidean grid. Default is False.
    background : tuple of int, optional
        RGB color code for the background. Each value should be between 0 and 255. Default is (255, 255, 255).
    title : str, optional
        The title of the graph to display. Default is None.
    show : str, optional
        What complex(es) to display. Should be in ['primal', 'dual', 'all']. Default is 'primal'.
    color : str, optional
        The main color of the graph. Default is 'darkblue'.
    color_accent : str, optional
        The color of the highlighted subset. Default is 'orange'.
    size : int, optional
        Size of the glyph representing 0-simplices. Default is 10.
    width : int, optional
        Thickness of lines representing 1-simplices. Default is 2.
    scaling : float, optional
        Scaling factor to visualize property values. Useful when plotting cochains. Default is 1.
    window_size : tuple of int, optional
        The width and height in pixels of the display window. Default is None.

    Returns
    -------
    go.Figure
        The plotly figure object.

    See Also
    --------
    _generate_plot_data_manifold : Generates plot data for simplicial manifolds.
    _generate_plot_data_complex : Generates plot data for simplicial complexes.
    _generate_plot_data_simplex : Generates plot data for simplices.
    """
    
    show_grid = kwargs.get('show_grid', False)
    background = kwargs.get('background', (255, 255, 255))
    title = kwargs.get('title', None)

    generate_plot_data = {Simplex: _generate_plot_data_simplex,
                          SimplicialComplex: _generate_plot_data_complex,
                          SimplicialManifold: _generate_plot_data_manifold}
    
    data = generate_plot_data[type(input)](input, degrees=degrees, 
                                           subset=highlight, **kwargs)

    layout = go.Layout(scene_xaxis_visible=show_grid,
                        scene_yaxis_visible=show_grid,
                        scene_zaxis_visible=show_grid,
                        paper_bgcolor='rgb'+str(background),
                        scene=dict(aspectmode="data"),
                        margin=dict(l=40, r=40, t=40, b=40),
                        width=kwargs.get('window_size', [None, None])[0], 
                        height=kwargs.get('window_size', [None, None])[1],
                        title=title)

    fig = go.Figure(data, layout)
    if display: fig.show()

    return fig

# ################# #
# Usefull functions #
# ################# #

@typecheck(SimplicialManifold)
def _generate_plot_data_manifold(manifold: SimplicialManifold, 
                                 degrees: int|list[int]|str='all',
                                 subset: Optional[dict]=None, 
                                 **kwargs) -> list[go.Mesh3D]:
    """Generates plot data for simplicial manifolds.

    Parameters
    ----------
    manifold
        The `SimplicialManifold` to display.
    degrees
        Optional (default is 'all'). The (list of) simplex degree(s) to show.
    subset
        Optional (default is None). Subset of simplices to highlight.
        - keys : int. simplex degrees.
        - values : list(int). collection of simplex indices.

    Other parameters
    ----------------
    show : str
        Optional (default is 'Primal'). States what sub-complex to visualize.
        Should be in ['primal', 'dual', 'all']. If 'primal' only the primal
        simplicial complex is visualizen, if 'dual' only the dual cellular complex
        is visualizen, if 'both', well... Both are visualizen.
    color : str (or color plotly code)
        Optional (default is 'darkblue'). The main color of the graph.
    color_accent : str (or color plotly code)
        Optional (default is 'orange'). The color of the highlighted subset.
    point_size : int
        Optional (default is 10). Size of the glyph representing 0-simplices.
    edge_width : int
        Optional (default is 2). Thickness of lines representing 1-simplices.

    See also
    --------
        _generate_plot_data_complex() in the same module.

    Returns
    -------
        Plotly data structure to ready to be displayed.
    """
    show = kwargs.get('show', 'primal')

    data = []
    if show in ['primal', 'all']:
        data += _generate_plot_data_complex(manifold, degrees=degrees,
                                            subset=subset, **kwargs)

    if show in ['dual', 'all']:
        data += _generate_plot_data_complex(manifold, degrees=degrees,
                                            subset=subset,  #None
                                            dual=True,
                                            color='orange', symbol='square',
                                            color_accent=kwargs.get(
                                                'color_accent', 'darkblue'),
                                            size=kwargs.get('size', 10),
                                            width=kwargs.get('width', 5)) 
    
    return data

@typecheck(SimplicialComplex)
def _generate_plot_data_complex(complex: SimplicialComplex, 
                               degrees: int|list[int]|str='all',
                               subset: Optional[dict]=None,
                               dual: bool=False,
                               **kwargs) -> list[go.Mesh3D]:
    """Generates plot data for simplicial complexes.

    Parameters
    ----------
    complex
        The structure to display.
    degrees
        Optional (default is 'all'). The (list of) simplex degree(s) to show.
    subset
        Optional (default is None). Subset of simplices to highlight.
        - keys : int. simplex degrees.
        - values : list(int). collection of simplex indices.
    dual
        Optional (default is False). If true, plot the cellular complex.

    Other parameters
    ----------------
    color : str (or color plotly code)
        Optional (default is 'darkblue'). The main color of the graph.
    color_accent : str (or color plotly code)
        Optional (default is 'orange'). The color of the highlighted subset.
    point_size : int
        Optional (default is 10). Size of the glyph representing 0-simplices.
    edge_width : int
        Optional (default is 2). Thickness of lines representing 1-simplices.

    Returns
    -------
        Plotly data structure ready to be displayed.
    """
    
    n = complex.dim
    
    if degrees == 'all':
        degrees = np.arange(n+1)
    elif not isinstance(degrees, Iterable):
        degrees = [degrees]

    data = []
    if subset is None:
        if 0 in degrees:
            data.append(_generate_point_data(complex, dual=dual, **kwargs))
        if 1 in degrees:
            data.append(_generate_wireframe_data(complex, dual=dual, **kwargs))
        if 2 in degrees and not dual:
            data.append(_generate_surface_data(complex, **kwargs))

    else:
        color = kwargs.get('color', 'darkblue')
        color_accent = kwargs.get('color_accent', 'orange')
        size = kwargs.get('size', 10)
        width = kwargs.get('width', 5)

        main_subset = {k: list(set(np.arange(complex.shape[k]))
                                 - set(subset[k]))
                       if k in subset.keys()
                       else np.arange(complex.shape[k])
                       for k in np.arange(n+1)}

        if 0 in degrees:
            data.append(_generate_point_data(complex, subset=main_subset[0],
                                            dual=dual, color=color, size=size))
            if 0 in subset.keys():
                data.append(_generate_point_data(complex, subset=subset[0],
                                                dual=dual,
                                                color=color_accent,
                                                size=size,
                                                name='0-simplices, subset'))

        if 1 in degrees:
            data.append(_generate_wireframe_data(complex, subset=main_subset[1],
                                                dual=dual,
                                                color=color,
                                                width=width))
            if 1 in subset.keys():
                data.append(_generate_wireframe_data(complex, subset=subset[1],
                                                    dual=dual,
                                                    color=color_accent,
                                                    width=width,
                                                    name='1-simplices, subset')
                            )

        if 2 in degrees and not dual:
            data.append(_generate_surface_data(complex, subset=main_subset[2],
                                               color=color, opacity=.33))
            if 2 in subset.keys():
                data.append(_generate_surface_data(complex, subset=subset[2],
                                                  color=color_accent,
                                                  opacity=.33,
                                                  name='2-simplices, subset'))
    
    return data

@typecheck(Simplex)
def _generate_plot_data_simplex(simplex: Simplex, **kwargs) -> list[go.Mesh3D]:
    """Generates simplex visualization data.

    Parameters
    ----------
    simplex
        The `Simplex` instance to visualize.

    Other parameters
    ----------------
    surface_color: plotly color code
        Default is 'darkblue'. Color of the surface.
    scaling: float
        Default is 1. Scaling factor to visualize property the values.

    Returns
    -------
    list(go.Mesh3D)
        Plotly data structure to ready to display.
    """
    degrees = np.arange(simplex.dim + 1)

    data = []
    if 0 in degrees:
        data.append(_generate_point_data(simplex, **kwargs))
    if 1 in degrees:
        data.append(_generate_wireframe_data(simplex, **kwargs))
    if 2 in degrees:
        data.append(_generate_surface_data(simplex, **kwargs))

    return data


def _generate_point_data(input: SimplicialComplex|Simplex, 
                         subset: Optional[Iterable[int]]=None, 
                         dual: bool=False, 
                         name: Optional[str]=None,
                         **kwargs) -> go.Scatter3D:
    """Plots 0-simplices.

    Parameters
    ----------
    input
        The structure to visualize.
    subset
        Optional (default is None). The subset of nodes to visualize.
    dual
        Optional (default is False). If True, plots vertices of dual complex,
        else plot nodes of the primal complex.
    name
        Optional (default is '0-simplices'). Name to display on graph.

    Other parameters
    ----------------
    size: int
        Default is 10. Size of the markers.
    color: plotly color code
        Default is 'darkblue'. Color of the markers.
    symbol: str (plotly marker name)
        Default is 'circle'. Type of marker to use.
    edge_width: int
        Default is 0. The thickness of the marker edge.

    Returns
    -------
    Plotly.graph_object.scatter3D
        The plot object to visualize.
    """

    if isinstance(input, Simplex):
        coord = input.vertices
        if name is None: name = 'vertices' 
        elmt_name = 'vertex'
    
    elif dual:
        coord = input[-1].circumcenters
        if name is None: name = '0-cells' 
        elmt_name = 'vertex'
    
    else:
        coord = input[0].vertices
        if name is None: name = '0-simplices' 
        elmt_name = 'node'
    
    if subset is not None:
        coord = coord[subset]

    legend = [f'{elmt_name} # {i}'
              + f' at position {round(x, 2), round(y, 2), round(z, 2)}'
              for i, (x, y, z) in enumerate(coord)]

    return go.Scatter3d(x=coord[:, 0], y=coord[:, 1], z=coord[:, 2],
                        mode='markers',
                        name=name,
                        marker={'size': kwargs.get('size', 10),
                                'color': kwargs.get('color', 'darkblue'),
                                'colorscale': kwargs.get('colormap','viridis'),
                                'opacity':  kwargs.get('opacity', 1),
                                'symbol': kwargs.get('symbol', 'circle'),
                                'line': {'color':'white', 
                                         'width':kwargs.get('edge_width', 0)}},
                        text=legend,
                        hoverinfo='text')


def _generate_wireframe_data(imput: SimplicialComplex|Simplex,
                             subset: Optional[Iterable[int]]=None,
                             dual: bool=False, 
                             name: Optional[str]=None,
                             **kwargs) -> go.Scatter3D:
    """Plots 1-simplices.

    Parameters
    ----------
    imput
        The structure to visualize.
    subset
        Optional (default is None). The subset of edges to visualize.
    dual
        Optional (default is False). If True, plots vertices of dual complex,
        else plot nodes of the primal complex.
    name
        Optional (default is '1-simplices'). Name to display on graph.

    Other parameters
    ----------------
    color : plotly color code
        Default is 'darkblue'. Color of the markers.
    width : int
        Default is 5. Thickness of the lines.

    Returns
    -------
        The plot object to visualize.
    """

    if isinstance(imput, Simplex):
        coord = imput.vertices
        if name is None: name = 'edges'

        nbr_vtcs = imput.dim + 1
        nbr_edge = int(binom(nbr_vtcs, 2))

        indices = np.arange(nbr_vtcs)

        bnd = np.zeros((nbr_edge, nbr_vtcs), dtype=int)
        for i, (j, k) in enumerate(combinations(indices, 2)):
            
            bnd[i,j] = 1
            bnd[i,k] = 1
        bnd = bnd.T

    elif dual:
        n = imput.dim
        coord = imput[-1].circumcenters
        bnd = imput[n-1].coboundary
        
        if not imput.isclosed:
            inner_sids = imput.interior()[n-1]
            bnd = bnd[:, inner_sids]

        if name is None: name = '1-cells'

    else: 
        coord = imput[0].vertices
        bnd = imput[1].boundary
        if name is None: name = '1-simplices'
        
    if subset is not None: bnd = bnd[:, subset]

    pids, eids = bnd.nonzero()
    
    line_border_ids = np.vstack([pids[np.where(eids == idx)[0]]
                                 for idx in set(eids)])
    
    line_borders = coord[line_border_ids]
    

    if dual and not imput.isclosed:
        outer_line_borders = _compute_border_lines(imput)
        line_borders = np.vstack((line_borders, outer_line_borders))
    
    Xe, Ye, Ze = [], [], []
    for L in line_borders:
        Xe.extend([L[k % 2][0] for k in range(3)] + [None])
        Ye.extend([L[k % 2][1] for k in range(3)] + [None])
        Ze.extend([L[k % 2][2] for k in range(3)] + [None])
    
    return go.Scatter3d(x=Xe, y=Ye, z=Ze,
                        mode='lines',
                        name=name,
                        line=dict(color=kwargs.get('color', 'darkblue'),
                                  width=kwargs.get('width', 5)))


def _generate_surface_data(input: SimplicialComplex|Simplex, 
                           subset: Optional[Iterable[int]]=None, 
                           name: str='2-simplices', 
                           **kwargs) -> None:
    """Plots 2-simplices.

    Parameters
    ----------
    input
        The structure to visualize.
    subset
        Optional (default is None). The subset of edges to visualize.
    name
        Optional (default is '2-simplices'). Name to display on graph.

    Other parameters
    ----------------
    intensity:np.ndarray[float]
        The intensity values to apply to each element. 
        Used to visualize 2-Cochains.
    colormap: str
        Default is 'Viridis'. The name of the colormap to use, 
        see Notes for available colormaps.
    legend:bool
        Default is True. If True Generates plot data for the name associated
        with the 2D elements within the legend.
    color:plotly color code
        Default is 'darkblue'. Color of the markers.
    opacity:float
        Default is .33. Must be between 0 and 1.
        The opacity level of the surfaces.

    Returns
    -------
        Plotly.graph_object.Mesh3d : The plot object to visualize.
    """

    if isinstance(input, Simplex):
        coord = input.vertices
        name = 'faces'

        nbr_vtcs = input.dim + 1
        nbr_face = int(binom(nbr_vtcs, 3))

        indices = np.arange(nbr_vtcs)

        bnd = np.zeros((nbr_face, nbr_vtcs), dtype=int)
        for i, (j, k, l) in enumerate(combinations(indices, 3)):
            bnd[i,j] = 1
            bnd[i,k] = 1
            bnd[i,l] = 1
        
        bnd = bnd.T
    
    else:
        coord = input[0].vertices
        bnd = abs(input[1].boundary) @ abs(input[2].boundary)

    if subset is not None: bnd = bnd[:,subset]

    pids, tids = bnd.nonzero()

    triangles = np.vstack([pids[np.where(tids == idx)[0]]
                           for idx in set(tids)]).astype(int)

    intensity = kwargs.get('intensity', None)
    if intensity is not None:
        return go.Mesh3d(x=coord[:, 0], y=coord[:, 1], z=coord[:, 2],
                        i=triangles[:, 0], j=triangles[:, 1], k=triangles[:, 2],
                        name=name,
                        showlegend=kwargs.get('legend', True),
                        flatshading=True,
                        intensitymode='cell',
                        intensity=intensity,
                        colorscale=kwargs.get('colormap', None),
                        cmax = kwargs.get('color_range', [None, None])[-1],
                        cmin = kwargs.get('color_range', [None, None])[0],
                        opacity=kwargs.get('opacity', 1),
                        hoverinfo='all')
    
    else:
        return go.Mesh3d(x=coord[:, 0], y=coord[:, 1], z=coord[:, 2],
                        i=triangles[:, 0], j=triangles[:, 1], k=triangles[:, 2],
                        name=name,
                        showlegend=kwargs.get('legend', True),
                        flatshading=True,
                        color=kwargs.get('color', 'darkblue'),
                        opacity=kwargs.get('opacity', .33),
                        hoverinfo='all')

@typecheck(SimplicialManifold)
def _compute_border_lines(manifold: SimplicialManifold) -> np.ndarray[float]:
    """Computes the boundaries of an open `SimplicialManifold`.

    Returns
    -------
        (2N,2,3)-array containing 2N couples of 3D position vectors.
    
    Notes
    -----
      * This methods should only works with 2D open manifolds.
      * Each couple of 3D vectors corresponds to the end points of an edge.
      * The first N couples correspond to the N edges forming the outer ring.
      * While the last N couples corresponds to the N edges orthogonal to them,
        from the center of a edge of the outer ring to the center of the 
        adjacent triangle.
    """
    n = manifold.dim
    sids = manifold.border()[n-1]
    pts = [mdl.circumcenters for mdl in manifold]

    cbnd = manifold[n-2].coboundary
    cbnd_ids = cbnd[sids, :].nonzero()[1].reshape((len(sids), 2))
    outer_ring = pts[n-2][cbnd_ids]

    bnd = manifold[n].boundary
    bnd_ids = bnd[sids, :].nonzero()[1]
    orthogonal_edges = np.stack((pts[n][bnd_ids], pts[n-1][sids]), axis=1)

    return np.vstack((outer_ring, orthogonal_edges))

