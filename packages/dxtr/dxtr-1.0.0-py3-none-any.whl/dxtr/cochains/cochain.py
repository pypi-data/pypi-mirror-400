# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.complexes.cochain
#
# This file contains one class:
#     - `Cochain`
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

from typing import Iterable, Generator, Optional
from copy import deepcopy
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from dxtr import logger
from dxtr.utils.typecheck import valid_input
from dxtr.complexes import SimplicialComplex, SimplicialManifold, Module


class Cochain:
    """A cochain data structure.

    A discrete version of the mathematical notion of differential k-form.
    Defined on a discrete version of the notion of manifold.

    Attributes
    ----------
    _complex : dxtr.complexes.simplicialcomplex
        The simplicial complex the cochain is defined on.
    _dim : int
        The topological dimension at which the cochain is defined.
    _val : numpy.ndarray(float)
        The value of the cochain on the associated simplices.
    _dual : bool
        Default is False. If True the cochain is defined on the dual complex.
    
    Notes
    -----
    * The values of the `Cochain` can be scalars or vectors.
    * We can also define values as sparse matrices but this is mostly used 
      to define differential operators on a whole `SimplicialComplex`.
    """

    def __init__(self, complex: SimplicialComplex, dim: int, 
                 values: Optional[Iterable[float]] = None, dual: bool = False,
                 name: Optional[str] = None) -> None:
        """Instantiates a `Cochain` object.

        Parameters
        ----------
        complex : SimplicialComplex
            The simplicial complex the cochain is defined on.
        dim : int
            The topological dimension at which the cochain is defined.
        values : iterable of float, optional
            The value of the cochain on the associated simplices. Default is None.
        dual : bool, optional
            If True the cochain is defined on the dual complex. Default is False.
        name : str, optional
            The name of the cochain. Default is None.

        Notes
        -----
        * If no dim is specified, we look for the k-Module with
          the same dimension as the provided values.
        """
        
        self._complex:SimplicialComplex = complex
        self._dim = dim
        self._dual = dual
        
        n = complex.dim
        k = np.clip(dim, 0, n)
        mdl = complex[k] if not dual else complex[n-k]
        self._indices, self._values = _format_indices_values(values, mdl)
        
        if name is None:
            self._name = f'Dual ' if self.isdual else 'Primal '
            self._name += f'{self.dim}-cochain'
        else:
            self._name = name

    @classmethod
    def from_file(cls, path: str | Path, name: Optional[str] = None) -> Cochain:
        """Instantiates a `Cochain` from a `.vtk` file.

        Parameters
        ----------
        path : str or Path
            The path to the `.vtk` file.
        name : str, optional
            The name of the cochain. Default is None.

        Notes
        -----
        * For now can only work with primal `Cochain` objects.
        """
        from dxtr.io import read_vtk

        simplices, vertices, property = read_vtk(path)
        manifold = SimplicialManifold(simplices, vertices)

        name = property.name if name is None else name
        dual = False

        return cls(manifold, property.dim, property.values, 
                    dual=dual, name=name)

    @valid_input
    def to_file(self, file_name: str, format: str = '.ply', 
                folder: Optional[str | Path] = None) -> None:
        """
        Saves the `Cochain` instance on disk in the `.vtk` format.

        Parameters
        ----------
        file_name : str
            The name of the file to write on disk.
        format : str, optional
            The type of file to write, see Notes. Default is `.ply`.
        folder : str or Path, optional
            The location where to write the file. Default is the current working directory.
        
        Notes
        -----
        * `Cochain` instances can only be saved in the `vtk` format.
        * If no folder is provided, the file will be recorded in the current working directory.
        """
        from dxtr.io.write import format_path_properly
        from dxtr.utils.wrappers import UGrid

        path = format_path_properly(folder, file_name, '.vtk')

        ugrid = UGrid.generate_from(self)
        ugrid.save(path)


    def __is_compatible_with__(self, other: Cochain) -> bool:
        """Checks if algebraic operations can be performed between two cochains.

        Parameters
        ----------
        other : Cochain
            The other cochain to check compatibility with.

        Returns
        -------
        bool
            True if the cochains are compatible, False otherwise.
        """
        try:
            assert isinstance(other, Cochain), (
                'Addition only implented between Cochains.')
            assert other.complex is self.complex, (
                    'Cochains defined on different complexes.')
            assert other.dim == self.dim, (
                f'Dimensions do not match: {other.dim} != {self.dim}')
            assert other.shape == self.shape, (
                f'Shapes do not match: {other.shape} != {self.shape}')
            assert other.isdual == self.isdual, (
                'Cannot combine primal and dual cochains together.')
            assert isinstance(other.values, type(self.values)), (
                'Cannot add Cochains with values of different types.')
            np.testing.assert_array_equal(other.indices, self.indices, 
                        err_msg='Cochains not defined on the same simplices.') 
            
            return True

        except AssertionError as msg:
            logger.warning(msg)
            return False


    def __str__(self) -> str:
        return f'{self.name}, defined on {self.complex.name}.'


    def __add__(self, other: Cochain) -> Optional[Cochain]:
        """Enables to add two cochains together.

        Parameters
        ----------
        other : Cochain
            The other cochain to add.

        Returns
        -------
        Cochain or None
            The resulting cochain if compatible, None otherwise.
        """
        if not self.__is_compatible_with__(other):
            return None

        if isinstance(self._values, sp.spmatrix):
            new_values = self.values + other.values
        else:
            new_values = dict(zip(self.indices, self.values + other.values))
        
        return Cochain(self.complex, self.dim, values=new_values,
                        dual=self.isdual)


    def __sub__(self, other: Cochain) -> Optional[Cochain]:
        """Enables to subtract two cochains from one another.

        Parameters
        ----------
        other : Cochain
            The other cochain to subtract.

        Returns
        -------
        Cochain or None
            The resulting cochain if compatible, None otherwise.
        """
        if not self.__is_compatible_with__(other):
            return None

        if isinstance(self._values, sp.spmatrix):
            new_values = self.values - other.values
        else:
            new_values = dict(zip(self.indices, self.values - other.values))
        
        return Cochain(self.complex, self.dim, values=new_values,
                        dual=self.isdual)


    def __mul__(self, other: float | int | np.ndarray[float] | Cochain) -> Optional[Cochain]:
        """Enables the multiplication on the right.

        Parameters
        ----------
        other : float, int, np.ndarray of float, or Cochain
            The value or cochain to multiply with.

        Returns
        -------
        Cochain or None
            The resulting cochain if compatible, None otherwise.

        Notes
        -----
        * WARNING: when multiplying a `Cochain` by a `np.ndarray`, one must
          keep the `Cochain` on the left side of the `*` operator: 
          ```C2 = C1 * arr```
          The inverse would not work for the array will try to multiply term 
          by term.
        """
        if isinstance(other, (float, int)):
            if isinstance(self.values, sp.spmatrix):
                new_values = other * self.values
                new_values = new_values.tocsr()
            else: 
                new_values = dict(zip(self.indices, other * self.values))
        
        if isinstance(other, np.ndarray):
            new_values = other * self.values

        elif isinstance(other, Cochain):
            if not self.__is_compatible_with__(other):
                return None

            if isinstance(self.values, sp.spmatrix):
                new_values = self.values @ other.values
            
            else:
                new_vals = np.multiply(self.values, other.values)
                new_values = dict(zip(self.indices, new_vals))

            
        return Cochain(self.complex, self.dim, values=new_values,
                    dual=self.isdual)


    def __rmul__(self, other: float | int | np.ndarray[float] | Cochain) -> Optional[Cochain]:
        """Enables the multiplication with a number on the left.

        Parameters
        ----------
        other : float, int, np.ndarray of float, or Cochain
            The value or cochain to multiply with.

        Returns
        -------
        Cochain or None
            The resulting cochain if compatible, None otherwise.
        """
        return self.__mul__(other)


    def __truediv__(self, other: float | int | np.ndarray[float]) -> Optional[Cochain]:
        """Enables the division on the right.

        Parameters
        ----------
        other : float, int, or np.ndarray of float
            The value to divide by.

        Returns
        -------
        Cochain or None
            The resulting cochain if compatible, None otherwise.

        Notes
        -----
        * The division is not implemented between `Cochain` instances yet.
        """
        if isinstance(other, (float, int, np.ndarray)):
            inv_other = 1 / other
            return self * inv_other
        
        elif isinstance(other, Cochain):
            logger.warning('Cannot divide `Cochains` together for now')
            return None
    
    
    @property
    def complex(self) -> SimplicialComplex:
        """Gets the `SimplicialComplex` on which the `Cochain` is defined.

        Returns
        -------
        SimplicialComplex
            The simplicial complex.
        """
        return self._complex
    
    @property
    def name(self) -> str:
        """Gets the name of the `Cochain`.

        Returns
        -------
        str
            The name of the cochain.
        """
        return self._name
    
    @property
    def dim(self) -> int:
        """The topological dimension of the `Cochain`.

        Returns
        -------
        int
            The topological dimension.
        """
        return self._dim

    @property
    def shape(self) -> tuple[int] | None:
        """Gets the `Cochain` shape.

        Returns
        -------
        tuple of int or None
            The shape of the cochain.

        Notes
        -----
        * The shape is given as a tuple.
          The second number is 0 for a scalar-valued cochain,
          1 for a vector, 2 for a tensor, etc...
        """
        if self._values is None:
            return None
        else:
            return self._values.shape

    @property
    def indices(self) -> list[int]:
        """Gets the indices of the k-simplices where the `Cochain` is defined.

        Returns
        -------
        list of int
            The indices of the k-simplices.
        """
        return self._indices

    @property
    def values(self) -> Optional[np.ndarray[float] | sp.spmatrix | dict]:
        """Gets the values of the `Cochain`.

        Returns
        -------
        np.ndarray of float, sp.spmatrix, or dict, optional
            The values of the cochain.
        """
        return self._values
    
    @property
    def positions(self) -> Optional[np.ndarray[float]]:
        """Gets the vertices of the simplices where cochain values are defined.

        Returns
        -------
        np.ndarray of float, optional
            The vertices of the simplices.

        Notes
        -----
        * Returns None if the `Cochain` is defined on an `AbstractSimplicialComplex`.
        """

        if self.complex.isabstract:
            logger.warning('cochain defined on an abstract simplicial complex.')
            return None
        
        k = self.complex.dim - self.dim if self.isdual else self.dim
        pos = self.complex[k].circumcenters
        
        return pos[self.indices]
        
    @property
    def isdual(self) -> bool:
        """Checks if the `Cochain` is defined on the dual complex.

        Returns
        -------
        bool
            True if the cochain is defined on the dual complex, False otherwise.
        """
        return self._dual
        
    @property
    def isvectorvalued(self) -> bool:
        """Checks if the values of the `Cochain` are vectors.

        Returns
        -------
        bool
            True if the values are vectors, False otherwise.
        """
        if not isinstance(self.values, np.ndarray):
            return False
        else:
            return self.values.ndim == 2


    def items(self) -> Generator[tuple[int, float], None, None]:
        """Enables to iterate over `Cochain` indices and values.

        Yields
        ------
        tuple of int and float
            Indices of the k-simplices where values are defined and the values of the cochain.
        """

        for idx, val in zip(self._indices, self._values):
            yield idx, val

    
    def toarray(self) -> Optional[np.ndarray[float]]:
        """Gets the values of the cochain as a numpy array.

        Returns
        -------
        np.ndarray of float, optional
            The values of the cochain as a numpy array.
        """
        if isinstance(self._values, sp.spmatrix):
            return self._values.toarray()
        else:
            return np.asarray(self._values)
    

    def value_closest_to(self, position: np.ndarray[float]) -> float:
        """Gets the value closest to a provided position.

        Parameters
        ----------
        position : np.ndarray of float
            The position to find the closest value to.

        Returns
        -------
        float
            The value closest to the provided position.
        """
        cplx = self.complex
        dim = self.dim

        sidx = cplx[dim].closest_simplex_to(position, index_only=True)
        
        return self.values[sidx]
    

# ############ #
# cochain base #
# ############ #

def cochain_base(complex: SimplicialComplex, dim: int, 
                 dual: bool = False) -> Optional[Cochain]:
    """Generates The k-cochain base on a given manifold.

    Parameters
    ----------
    complex : SimplicialComplex
        The simplicial manifold to work on.
    dim : int
        The topological dimension (k) of the desired k-cochain base.
    dual : bool, optional
        If True the returned `Cochain` is dual. Default is False.

    Returns
    -------
    Cochain or None
        A k-`Cochain` with the Nk-identity matrix as value. Nk being the number of 
        k-cochains in the provided simplicial manifold.

    Notes
    -----
    * The identity matrix is implemented as a `scipy.sparse.identity()` one.
    """

    try:
        if dual:
            assert isinstance(complex, SimplicialManifold), (
            'dual `Cochain` can only be defined on a `SimplicialManifold`.')
        
        assert dim is not None, 'Please specify a dimension.'
        
        k, n = dim, complex.dim
        Nk = complex.shape[n-k] if dual else complex.shape[k]

        return Cochain(complex, k, sp.identity(Nk), dual=dual)

    except AssertionError as msg:
        logger.warning(msg)
        return None



# ################# #
# Usefull functions #
# ################# #


def _format_indices_values(input: Iterable, simplices: Module
                           ) -> Optional[np.ndarray[float] |
                                         tuple[np.ndarray[int], sp.spmatrix]]:
    """Formats the input values.

    Parameters
    ----------
    input : iterable
        The data to construct the `Cochain` from.
    simplices : Module
        The `Module` object containing the k-simplices 
        on which we want to construct the `Cochain`.

    Returns
    -------
    np.ndarray of float or tuple of np.ndarray of int and sp.spmatrix, optional
        The formatted indices and values.
    """
    
    Nk = simplices.size
    simplex_indices = np.arange(Nk)
    
    if isinstance(input, (sp.spmatrix, np.ndarray)):
        return simplex_indices, input
    
    elif isinstance(input, dict):
        ids, vals = [], []
        for idx, val in sorted(input.items()):
            ids.append(idx)
            vals.append(val)
        return np.asarray(ids, dtype=int), np.asarray(vals)
    
    elif isinstance(input, list):
        return np.asarray((simplex_indices, input))
    
    elif isinstance(input, (float, int)):
        return simplex_indices, input * np.ones(Nk)
    
    else:
        logger.warning(f'Input type {type(input).__name__} not supported.')
        return None, None