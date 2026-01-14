"""
Matrix (not the movie...)

*New in 0.12.0*

---

Copyright (c) 2025 Sakuragasaki46.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
See LICENSE for the specific language governing permissions and
limitations under the License.

This software is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

from __future__ import annotations
from typing import Collection, Iterable, TypeVar
from .functools import deprecated

_T = TypeVar('_T')

class Matrix(Collection[_T]):
    """
    Minimalist reimplementation of matrices in pure Python.
    
    This to avoid adding numpy as a dependency.

    *New in 0.12.0*
    """
    _shape: tuple[int, int]
    _elements: list[_T]

    def shape(self):
        return self._shape

    def __init__(self, iterable: Iterable[_T] | Iterable[Collection[_T]], shape: tuple[int, int] | None = None):
        elements = []
        boundary_x = boundary_y = 0
        for row in iterable:
            if isinstance(row, Collection):
                if not boundary_y:
                    boundary_y = len(row)
                    elements.extend(row)
                    boundary_x += 1
                elif boundary_y != len(row):
                    raise ValueError('row length mismatch')
                else:
                    elements.extend(row)
                    boundary_x += 1
            elif shape:
                if not boundary_x:
                    boundary_x, boundary_y = shape
                elements.append(row)
        self._shape = boundary_x, boundary_y
        self._elements = elements
        assert len(self._elements) == boundary_x * boundary_y

    def __getitem__(self, key: tuple[int, int]) -> _T:
        (x, y), (_, sy) = key, self.shape()
        
        return self._elements[x * sy + y]

    @property
    def T(self):
        sx, sy = self.shape()
        return Matrix(
            [
                [
                    self[j, i] for j in range(sx)
                ] for i in range(sy)
            ]
        )

    def __matmul__(self, other: Matrix) -> Matrix:
        (ax, ay), (bx, by) = self.shape(), other.shape()

        if ay != bx:
            raise ValueError('cannot multiply matrices with incompatible shape')
        
        return Matrix([
            [
                sum(self[i, k] * other[k, j] for k in range(ay)) for j in range(by)
            ] for i in range(ax)
        ])

    def __eq__(self, other: Matrix):
        try:
            return self._elements == other._elements and self._shape == other._shape
        except Exception:
            return False

    def __len__(self):
        ax, ay = self.shape()
        return ax * ay

    @deprecated('please use .rows() or .columns() instead')
    def __iter__(self):
        return iter(self._elements)

    def __contains__(self, x: object, /) -> bool:
        return x in self._elements

    def __repr__(self):
        return f'{self.__class__.__name__}({list(self.rows())})'

    def rows(self):
        sx, sy = self.shape()
        return (
            [self[j, i] for j in range(sy)] for i in range(sx)
        )

    def columns(self):
        sx, sy = self.shape()
        return (
            [self[j, i] for j in range(sx)] for i in range(sy)
        )

    @classmethod
    def as_row(cls, iterable: Iterable):
        return cls([[*iterable]])

    @classmethod
    def as_column(cls, iterable: Iterable):
        return cls([[x] for x in iterable])

    def get_column(self, idx = 0):
        sx, _ = self.shape()
        return [
            self[j, idx] for j in range(sx)
        ]

    def get_row(self, idx = 0):
        _, sy = self.shape()
        return [
            self[idx, j] for j in range(sy)
        ]

__all__ = ('Matrix', )


