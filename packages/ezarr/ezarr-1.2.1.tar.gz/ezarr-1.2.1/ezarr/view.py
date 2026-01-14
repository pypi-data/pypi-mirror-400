from __future__ import annotations

from collections.abc import Collection, Iterable, Iterator
from typing import Any, Self, SupportsIndex, cast, overload, override

import numpy as np
import numpy.typing as npt
import zarr
from numpy._typing import _ArrayLikeObject_co  # pyright: ignore[reportPrivateUsage]

from ezarr import indexing
from ezarr.indexing._typing import SELECTOR

_RESERVED_ATTRIBUTES = frozenset(("_array", "_index", "_exposed_attr", "size", "shape", "dtype", "array_type"))


class ArrayView[T](Collection[T]):
    """View on a zarr.Array that can be subsetted infinitely without copying."""

    __slots__: tuple[str, ...] = "_array", "_index", "_exposed_attr"

    def __init__(
        self,
        array: zarr.Array,
        index: SELECTOR | tuple[SELECTOR, ...] | indexing.Selection,
        exposed_attributes: Iterable[str] = (),
    ) -> None:
        self._array: zarr.Array = array
        self._index: indexing.Selection = (
            index if isinstance(index, indexing.Selection) else indexing.Selection.from_selector(index, array.shape)
        )
        self._exposed_attr: frozenset[str] = frozenset(exposed_attributes)

        if not self._exposed_attr.isdisjoint(_RESERVED_ATTRIBUTES):
            raise ValueError(
                f"Cannot expose reserved attributes : {_RESERVED_ATTRIBUTES.intersection(self._exposed_attr)}."
            )

    @override
    def __repr__(self) -> str:
        return repr(self._view()) + "*"

    def __array__(self, dtype: npt.DTypeLike = None, copy: bool | None = None) -> npt.NDArray[Any]:
        if dtype is None:
            return self._view(copy=copy)

        return self._view(copy=copy).astype(dtype)

    @override
    def __getattribute__(self, key: str) -> Any:
        if key in object.__getattribute__(self, "_exposed_attr"):
            return getattr(self._array, key)

        return super().__getattribute__(key)

    @overload
    def __getitem__(self, index: SupportsIndex | tuple[SupportsIndex, ...]) -> T: ...
    @overload
    def __getitem__(
        self,
        index: slice
        | npt.NDArray[np.integer]
        | npt.NDArray[np.bool_]
        | None
        | tuple[slice | npt.NDArray[np.integer] | npt.NDArray[np.bool_] | None, ...],
    ) -> ArrayView[T]: ...
    def __getitem__(self, index: SELECTOR | tuple[SELECTOR, ...]) -> ArrayView[T] | T:
        sel = indexing.Selection.from_selector(index, self.shape).cast_on(self._index)

        if np.prod(sel.out_shape) == 1:
            return cast(T, self._array[sel.get_indexers()])

        return ArrayView(self._array, sel, exposed_attributes=self._exposed_attr)

    def __setitem__(self, index: SELECTOR, values: Any) -> None:
        sel = indexing.Selection.from_selector(index, self.shape).cast_on(self._index)

        self._array[sel.get_indexers()] = values

    @override
    def __len__(self) -> int:
        return len(self._view())

    @override
    def __contains__(self, key: Any) -> bool:
        return key in self._view()

    @override
    def __iter__(self) -> Iterator[T]:
        return iter(self._view())

    @override
    def __eq__(self, __value: object) -> npt.NDArray[np.bool_]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._view().__eq__(__value)

    def __lt__(self, __value: _ArrayLikeObject_co) -> npt.NDArray[np.bool_]:
        return self._view().__lt__(__value)

    def __le__(self, __value: _ArrayLikeObject_co) -> npt.NDArray[np.bool_]:
        return self._view().__le__(__value)

    def __gt__(self, __value: _ArrayLikeObject_co) -> npt.NDArray[np.bool_]:
        return self._view().__gt__(__value)

    def __ge__(self, __value: _ArrayLikeObject_co) -> npt.NDArray[np.bool_]:
        return self._view().__ge__(__value)

    def __add__(self, other: Any) -> npt.NDArray[Any]:
        return cast(npt.NDArray[Any], self._view() + other)

    def __iadd__(self, other: Any) -> Self:
        index = self._index.get_indexers()
        self._array[index] += other
        return self

    def __sub__(self, other: Any) -> npt.NDArray[Any]:
        return cast(npt.NDArray[Any], self._view() - other)

    def __isub__(self, other: Any) -> Self:
        index = self._index.get_indexers()
        self._array[index] -= other
        return self

    def __mul__(self, other: Any) -> npt.NDArray[Any]:
        return cast(npt.NDArray[Any], self._view() * other)

    def __imul__(self, other: Any) -> Self:
        index = self._index.get_indexers()
        self._array[index] *= other
        return self

    def __truediv__(self, other: Any) -> npt.NDArray[Any]:
        return cast(npt.NDArray[Any], self._view() / other)

    def __itruediv__(self, other: Any) -> Self:
        index = self._index.get_indexers()
        self._array[index] /= other
        return self

    def __pow__(self, other: Any) -> npt.NDArray[Any]:
        return cast(npt.NDArray[Any], self._view() ** other)

    @property
    def size(self) -> int:
        return self._view().size

    @property
    def shape(self) -> tuple[int, ...]:
        return self._view().shape

    @property
    def dtype(self) -> np.dtype[Any]:
        return self._view().dtype

    @property
    def array_type(self) -> type[Any]:
        return type(self._array)

    def _view(self, copy: bool | None = None) -> npt.NDArray[Any]:
        array = cast(npt.NDArray[Any], self._array[self._index.get_indexers()])

        if copy is False:
            raise ValueError("Getting a view of a zarr.Array always creates a copy")

        return array

    def copy(self) -> npt.NDArray[Any]:
        return self._view().copy()

    def astype(self, dtype: npt.DTypeLike) -> npt.NDArray[Any]:
        return self._view().astype(dtype)

    def min(
        self, axis: int | tuple[int, ...] | None = None, out: npt.NDArray[Any] | None = None
    ) -> T | npt.NDArray[Any]:
        return self._view().min(axis=axis, out=out)

    def max(
        self, axis: int | tuple[int, ...] | None = None, out: npt.NDArray[Any] | None = None
    ) -> T | npt.NDArray[Any]:
        return self._view().max(axis=axis, out=out)

    def mean(
        self,
        axis: int | tuple[int, ...] | None = None,
        dtype: npt.DTypeLike | None = None,
        out: npt.NDArray[Any] | None = None,
    ) -> T | npt.NDArray[Any]:
        return self._view().mean(axis=axis, dtype=dtype, out=out)  # type: ignore[no-any-return, misc, arg-type]

    def flatten(self) -> npt.NDArray[Any]:
        return self._view().flatten()

    def tolist(self) -> list[T]:
        return self._view().tolist()
