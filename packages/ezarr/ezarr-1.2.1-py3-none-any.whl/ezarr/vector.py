from __future__ import annotations

from collections.abc import Collection, Iterable, Iterator, MutableSequence
import math
from pathlib import Path
from typing import Any, Self, cast, overload, override
import warnings

import numpy as np
import numpy.typing as npt
import zarr
from numpy._typing import _SupportsArray as SupportsArray  # pyright: ignore[reportPrivateUsage]
from zarr.core.common import AccessModeLiteral
from zarr.errors import BoundsCheckError, UnstableSpecificationWarning
from zarr.storage import StoreLike  # pyright: ignore[reportUnknownVariableType]

from ezarr.common import write_array  # pyright: ignore[reportUnknownVariableType]
from ezarr.names import UNKNOWN, Attribute, EZType
from ezarr.object import EZObject
from ezarr.types import DeferredCreationFunc


def deferred_EZVector(values: Collection[Any]) -> DeferredCreationFunc:
    def inner(grp: zarr.Group, name: str, overwrite: bool) -> None:
        arr = write_array(
            np.array(values),
            grp.store,
            name=name,
            attributes={Attribute.EZType: EZType.Vector, Attribute.EZVectorSize: len(values)},
            overwrite=overwrite,
        )
        arr[:] = values  # pyright: ignore[reportArgumentType]

    return inner


class EZVector[T: np.generic](EZObject[list[T]], MutableSequence[T]):
    """
    List-like object built on top of zarr.Array for storing a single kind of elements in a resizeable container.

    Args:
        array: a zarr.Array, the underlying buffer
        size: (optional) the number of elements stored in the buffer (default: the length of the buffer)

    Example:
        >>> EZVector(zarr.array([1, 2, 3]))
        EZVector[1 2 3]
    """

    def __init__(self, array: zarr.Array, size: int | None = None) -> None:
        assert array.ndim == 1
        self._array: zarr.Array = array

        self._size: int = array.shape[0]
        self._iter_index: int = 0

    @classmethod
    def from_list(
        cls,
        lst: Collection[T],
        *,
        store: StoreLike | None = None,
        name: str,
        path: str | None = None,
        dtype: npt.DTypeLike = None,
        overwrite: bool = False,
    ) -> Self:
        """
        Create an EZVector from a list-like object.

        Args:
            lst: list-like collection of values to store in an EZVector.
            store:
            name:
            path:
            dtype:
            overwrite:
        """
        path = f"{path.rstrip('/')}/{name}" if path else name
        if store is None:
            store = {}

        data = np.asarray(lst)
        if dtype is not None:
            data = data.astype(dtype)

        return cls(write_array(data, store, name=name, overwrite=overwrite))

    def __array__(self, dtype: np.dtype | None = None, copy: bool | None = None) -> npt.NDArray[Any]:
        if not copy:
            raise ValueError("converting to a numpy array always creates a copy.")

        data = cast(npt.NDArray[Any], self._array[: self._size])  # pyright: ignore[reportInvalidCast]

        if dtype is not None:
            return data.astype(dtype)

        return data

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}{np.array2string(self._array[: self._size])}"  # pyright: ignore[reportArgumentType]

    @override
    def __len__(self) -> int:
        return self._size

    @overload
    def __getitem__(self, key: int) -> T: ...
    @overload
    def __getitem__(self, key: slice[int] | slice[int, int] | slice[int, int, int]) -> npt.NDArray[T]: ...
    @override
    def __getitem__(self, key: int | slice[int, int, int]) -> T | npt.NDArray[T]:  # pyright: ignore[reportIncompatibleMethodOverride]
        try:
            return cast(npt.NDArray[T], self._array[: self._size])[key]  # pyright: ignore[reportInvalidCast]

        except IndexError:
            raise BoundsCheckError(f"index {key} is out of range for EZVector with size {self._size}")

    @overload
    def __setitem__(self, key: int, value: T) -> None: ...
    @overload
    def __setitem__(self, key: slice[int] | slice[int, int] | slice[int, int, int], value: Iterable[T]) -> None: ...
    @override
    def __setitem__(self, key: int | slice[int, int, int], value: T | Iterable[T]) -> None:
        if isinstance(key, slice):
            self._array[key] = np.asarray(value)
            return

        if key >= self._size:
            raise BoundsCheckError(f"index {key} is out of range for EZVector with size {self._size}")

        self._array[key] = np.array(value)

    @override
    def __delitem__(self, key: int | slice[int, int, int]) -> None:
        """
        Delete a value from this EZVector from an index.

        Args:
            key: value index.

        Example:
            >>> ez_vec = EZVector.from_list([1, 2, 3], name="data")
            >>> del ez_vec[1]
            >>> ez_vec
            EZVector[1 3]
        """
        if not isinstance(key, slice):
            key = slice(key, key + 1, None)

        start = 0 if key.start is None else key.start  # pyright: ignore[reportUnnecessaryComparison]
        stop = self._size if key.stop is None else key.stop  # pyright: ignore[reportUnnecessaryComparison]
        step = key.step or 1

        if start < 0:
            start = self._size + start

        if stop < 0:
            stop = self._size + stop

        if step <= 0:
            raise IndexError("Only steps >= 1 are supported")

        if stop > self._size:
            raise IndexError(f"Index {stop} if out of bounds")

        offset = 0
        for idx in range(start, stop, step):
            self._array[idx - offset : -1] = self._array[idx - offset + 1 :]
            offset += 1

        self._size -= offset

    @override
    def __iter__(self) -> Iterator[T]:
        self._iter_index = 0
        return self

    def __next__(self) -> T:
        if self._iter_index >= self._size:
            raise StopIteration

        obj = cast(T, self._array[self._iter_index])
        self._iter_index += 1

        return obj

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, list | SupportsArray):
            return False

        return np.array_equal(self._array[: self._size], other)  # pyright: ignore[reportUnknownArgumentType]

    @property
    def capacity(self) -> int:
        return self._array.shape[0]

    @classmethod
    @override
    def open(
        cls, store: StoreLike | None = None, *, name: str, mode: AccessModeLiteral = "a", path: str | None = None
    ) -> Self:
        """
        Open an EZVector from a store.

        Args:
            store: Store, path to a directory or name of a zip file.
            name: name for the EZVector, to use inside the store.
            mode: Persistence mode: 'r' means read only (must exist); 'r+' means
                read/write (must exist); 'a' means read/write (create if doesn't
                exist); 'w' means create (overwrite if exists); 'w-' means create
                (fail if exists).
            path: path within the store to open.

        Example:
            >>> ez_vec = EZVector.from_list([1, 2, 3], name="data")
            >>> ez_vec.save("/tmp/vec", overwrite=True)
            >>> EZVector.open("/tmp/vec", name="data")
            EZVector[1 2 3]
        """
        path = f"{path.rstrip('/')}/{name}" if path else name

        if isinstance(store, str | Path):
            store = Path(store).expanduser()

        arr = zarr.open_array(store, mode=mode, path=path)

        arr_type = cast(str, arr.attrs.get(Attribute.EZType, UNKNOWN))
        if arr_type != EZType.Vector:
            raise ValueError(
                f"Cannot read EZVector from Array marked with type '{arr_type}', should be '{EZType.Vector}'."
            )

        return cls(arr, int(arr.attrs[Attribute.EZVectorSize]))  # pyright: ignore[reportArgumentType]

    @override
    def save(
        self,
        store: StoreLike,
        *,
        name: str | None = None,
        mode: AccessModeLiteral = "a",
        path: str | None = None,
        overwrite: bool = False,
    ) -> None:
        """
        Save this EZVector to a local file system.

        Args:
            store: Store, path to a directory or name of a zip file.
            name: name for the EZVector, to use inside the store. (default: same as name used during EZVector's creation)
            mode: Persistence mode: 'r' means read only (must exist); 'r+' means
                read/write (must exist); 'a' means read/write (create if doesn't
                exist); 'w' means create (overwrite if exists); 'w-' means create
                (fail if exists).
            path: path within the store where the EZVector will be saved.
            overwrite: overwrite EZVector if a group with name `name` already exists ? (default: False)

        Example:
            >>> from pathlib import Path
            >>> ez_vec = EZVector.from_list([1, 2, 3], name="data")
            >>> ez_vec.save("/tmp/vec", overwrite=True)
            >>> Path("/tmp/vec").exists()
            True
        """
        if name is None:
            name = self._array.name

        path = f"{path.rstrip('/')}/{name}" if path else name

        with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
            write_array(
                self._array,
                store,
                name=path,
                attributes={Attribute.EZType: EZType.Vector, Attribute.EZVectorSize: self._size},
                overwrite=overwrite,
            )

    @override
    def copy(self) -> list[T]:
        """
        Convert this EZVector into a Python list, loading all the data into memory.

        Example:
            >>> ez_vec = EZVector.from_list([1, 2, 3], name="data")
            >>> ez_vec.copy()
            [1, 2, 3]
        """
        return self._array[: self._size].tolist()  # pyright: ignore[reportUnknownVariableType, reportAttributeAccessIssue]

    @classmethod
    def defer(cls, values: Collection[Any]) -> DeferredCreationFunc:
        r"""
        Create an EZVector from a list-like object, but defer its storage.
        This function returns a function that can be called to finalize the EZVector creation and storage,
        with parameters:
            grp: (zarr.Group) a group in which to store the EZVector
            name: (str) name for the EZVector, to use inside the store.
            overwrite: (bool) overwrite object if a group with name `name` already exists ? (default: False)

        This is usually used as a convenience function to create an EZVector in an existing EZDict.

        Args:
            values: list-like collection of values to store in an EZVector.

        Example:
            >>> from ezarr import EZDict
            >>> d = EZDict(zarr.open_group({}))
            >>> d["vec"] = EZVector.defer([1, 2, 3])
            >>> repr(d)
            'EZDict{\n\tvec: EZVector[1 2 3]\n}'
        """
        return deferred_EZVector(values)

    @override
    def append(self, value: T) -> None:
        """
        Append a value to the end of an EZVector.

        Args:
            value: value to be appended.

        Example:
            >>> ez_vec = EZVector.from_list([1, 2, 3], name="data")
            >>> ez_vec.append(4)
            >>> ez_vec
            EZVector[1 2 3 4]
        """
        if self._size == self._array.shape[0]:
            self._array.resize((self._array.shape[0] * 2,))

        self._array[self._size] = value
        self._size += 1

    @override
    def extend(self, values: Iterable[T]) -> None:
        """
        Append multiple values to the end of an EZVector.

        Args:
            values: values to be appended.

        Example:
            >>> ez_vec = EZVector.from_list([1, 2, 3], name="data")
            >>> ez_vec.extend([4, 5, 6])
            >>> ez_vec
            EZVector[1 2 3 4 5 6]
        """
        values = list(values)
        n_values = len(values)

        if self._array.shape[0] - self._size < n_values:
            new_size = 2 ** math.ceil(math.log2(self._size + n_values))
            self._array.resize((new_size,))

        self._array[self._size : self._size + n_values] = values
        self._size += n_values

    @override
    def insert(self, index: int, value: T) -> None:
        """
        Insert a value in an EZList before `index`.

        Args:
            value: value to be inserted.

        Example:
            >>> ez_vec = EZVector.from_list([1, 2, 3], name="data")
            >>> ez_vec.insert(1, 4)
            >>> ez_vec
            EZVector[1 4 2 3]
        """
        if index < 0:
            index = self._size + index

        if self._size == self._array.shape[0]:
            self._array.resize((self._array.shape[0] * 2,))

        self._array[index + 1 :] = self._array[index:-1]
        self._array[index] = value
        self._size += 1
