import warnings
from typing import Any, Literal, SupportsIndex, cast

import numpy as np
import numpy.typing as npt
import zarr
from numpy._typing import ArrayLike, _ArrayLikeInt_co  # pyright: ignore[reportPrivateUsage]
from zarr.errors import UnstableSpecificationWarning

from ezarr.common import apply_op, cast_array
from ezarr.view import ArrayView


def _check_axis(arr: zarr.Array, axis: SupportsIndex | None) -> int:
    if arr.ndim > 1 and axis is None:
        raise NotImplementedError("Cannot flatten zarr.Array while working inplace")

    if axis is None:
        return 0

    return int(axis)


def _clamp_index(arr: zarr.Array, axis: SupportsIndex, obj: _ArrayLikeInt_co | slice) -> np.integer:
    if not isinstance(obj, int | np.integer):
        raise NotImplementedError("Advanced indexing is not supported yet")

    obj = cast(np.integer, obj)

    if obj > arr.shape[axis]:
        raise IndexError(f"Index {obj} is out of bounds for axis {axis} with size {arr.shape[axis]}.")

    elif obj < 0:
        obj = cast(np.integer, obj + arr.shape[axis])

    return obj


def delete[A: zarr.Array | npt.NDArray[Any]](
    arr: A, obj: _ArrayLikeInt_co | slice, axis: SupportsIndex | None = None
) -> A:
    if not isinstance(arr, zarr.Array):
        return np.delete(arr, obj, axis)

    axis = _check_axis(arr, axis)
    obj = _clamp_index(arr, axis, obj)

    prefix = (slice(None),) * axis
    if obj < (arr.shape[axis] - 1):
        # transfer data one row to the left, starting from the column after the one to delete
        # matrix | 0 1 2 3 4 | with index of the column to delete = 2
        #   ==>  | 0 1 3 4 . |
        index_dest = prefix + (slice(obj, -1),)
        index_source = prefix + (slice(obj + 1, None),)
        arr[index_dest] = arr[index_source]

    # resize the arrays to drop the extra column at the end
    # matrix | 0 1 3 4 . |
    #   ==>  | 0 1 3 4 |
    new_shape = arr.shape[:axis] + (arr.shape[axis] - 1,) + arr.shape[axis + 1 :]

    with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
        arr.resize(new_shape)

    return arr


def insert[A: zarr.Array | npt.NDArray[Any]](
    arr: A, obj: _ArrayLikeInt_co | slice, values: ArrayLike, axis: SupportsIndex | None = None
) -> A:
    """
    Insert values along the given axis before the given indices.

    Args:
        arr: input zarr.Array.
        obj: object that defines the index or indices before which `values` is inserted.
        values: values to inset into `arr`. If the type of `values` is different from that of `arr`, `values` is
            converted to the type of `arr`. `values` should be shaped so that `arr[...,obj,...] = values` is legal.
        axis: (optional) axis along which to insert `values`. If axis is None then arr is flattened first.
    """
    if not isinstance(arr, zarr.Array):
        return np.insert(arr, obj, values, axis)

    axis = _check_axis(arr, axis)
    obj = _clamp_index(arr, axis, obj)

    # resize the arrays to make room for the extra values
    new_shape = arr.shape[:axis] + (arr.shape[axis] + 1,) + arr.shape[axis + 1 :]

    with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
        arr.resize(new_shape)

    prefix = (slice(None),) * axis
    if obj < (arr.shape[axis] - 1):
        # transfer data 1 row to the right, starting from the column after the insertion index
        # matrix | 0 1 2 3 4 | with index of the insertion column = 2
        #   ==>  | 0 1 . 2 3 4 |
        index_source = prefix + (slice(obj, -1),)
        index_dest = prefix + (slice(obj + 1, None),)
        arr[index_dest] = arr[index_source]

    arr.set_orthogonal_selection(prefix + (obj,), values)  # pyright: ignore[reportArgumentType]

    return arr


def add[A: zarr.Array | npt.NDArray[Any] | ArrayView[Any]](
    x1: A, x2: ArrayLike, /, casting: Literal["no", "equiv", "safe", "same_kind", "unsafe"] = "same_kind"
) -> A:
    if not isinstance(x1, zarr.Array):
        if isinstance(x1, ArrayView):
            x1 += x2
            return x1

        return np.add(x1, x2)

    is_scalar = np.isscalar(x2)

    x2 = np.asarray(x2)
    x1 = cast_array(x1, np.result_type(x1.dtype, x2.dtype), casting)

    if is_scalar:

        async def _add_scalar(chunk_coords: tuple[int, ...] | slice, _data: zarr.Array) -> None:
            arr = await _data._async_array.getitem(chunk_coords)  # pyright: ignore[reportPrivateUsage]
            await _data._async_array.setitem(chunk_coords, arr + x2)  # pyright: ignore[reportPrivateUsage]

        apply_op(x1, _add_scalar)

    else:

        async def _add_array(chunk_coords: tuple[int, ...] | slice, _data: zarr.Array) -> None:
            arr = await _data._async_array.getitem(chunk_coords)  # pyright: ignore[reportPrivateUsage]
            await _data._async_array.setitem(chunk_coords, arr + x2[chunk_coords])  # pyright: ignore[reportPrivateUsage]

        apply_op(x1, _add_array)

    return x1


def sub[A: zarr.Array | npt.NDArray[Any] | ArrayView[Any]](
    x1: A, x2: ArrayLike, /, casting: Literal["no", "equiv", "safe", "same_kind", "unsafe"] = "same_kind"
) -> A:
    if not isinstance(x1, zarr.Array):
        if isinstance(x1, ArrayView):
            x1 -= x2
            return x1

        return np.subtract(x1, x2)

    is_scalar = np.isscalar(x2)

    x2 = np.asarray(x2)
    x1 = cast_array(x1, np.result_type(x1.dtype, x2.dtype), casting)

    if is_scalar:

        async def _add_scalar(chunk_coords: tuple[int, ...] | slice, _data: zarr.Array) -> None:
            arr = await _data._async_array.getitem(chunk_coords)  # pyright: ignore[reportPrivateUsage]
            await _data._async_array.setitem(chunk_coords, arr - x2)  # pyright: ignore[reportPrivateUsage]

        apply_op(x1, _add_scalar)

    else:

        async def _add_array(chunk_coords: tuple[int, ...] | slice, _data: zarr.Array) -> None:
            arr = await _data._async_array.getitem(chunk_coords)  # pyright: ignore[reportPrivateUsage]
            await _data._async_array.setitem(chunk_coords, arr - x2[chunk_coords])  # pyright: ignore[reportPrivateUsage]

        apply_op(x1, _add_array)

    return x1


def multiply[A: zarr.Array | npt.NDArray[Any] | ArrayView[Any]](
    x1: A, x2: ArrayLike, /, casting: Literal["no", "equiv", "safe", "same_kind", "unsafe"] = "same_kind"
) -> A:
    if not isinstance(x1, zarr.Array):
        if isinstance(x1, ArrayView):
            x1 *= x2
            return x1

        return np.multiply(x1, x2)

    is_scalar = np.isscalar(x2)

    x2 = np.asarray(x2)
    x1 = cast_array(x1, np.result_type(x1.dtype, x2.dtype), casting)

    if is_scalar:

        async def _add_scalar(chunk_coords: tuple[int, ...] | slice, _data: zarr.Array) -> None:
            arr = await _data._async_array.getitem(chunk_coords)  # pyright: ignore[reportPrivateUsage]
            await _data._async_array.setitem(chunk_coords, arr * x2)  # pyright: ignore[reportPrivateUsage]

        apply_op(x1, _add_scalar)

    else:

        async def _add_array(chunk_coords: tuple[int, ...] | slice, _data: zarr.Array) -> None:
            arr = await _data._async_array.getitem(chunk_coords)  # pyright: ignore[reportPrivateUsage]
            await _data._async_array.setitem(chunk_coords, arr * x2[chunk_coords])  # pyright: ignore[reportPrivateUsage]

        apply_op(x1, _add_array)

    return x1


def true_divide[A: zarr.Array | npt.NDArray[Any] | ArrayView[Any]](
    x1: A, x2: ArrayLike, /, casting: Literal["no", "equiv", "safe", "same_kind", "unsafe"] = "same_kind"
) -> A:
    if not isinstance(x1, zarr.Array):
        if isinstance(x1, ArrayView):
            x1 /= x2
            return x1

        return np.divide(x1, x2)

    is_scalar = np.isscalar(x2)

    x2 = np.asarray(x2)
    x1 = cast_array(x1, np.result_type(x1.dtype, x2.dtype), casting)

    if is_scalar:

        async def _add_scalar(chunk_coords: tuple[int, ...] | slice, _data: zarr.Array) -> None:
            arr = await _data._async_array.getitem(chunk_coords)  # pyright: ignore[reportPrivateUsage]
            await _data._async_array.setitem(chunk_coords, arr / x2)  # pyright: ignore[reportPrivateUsage]

        apply_op(x1, _add_scalar)

    else:

        async def _add_array(chunk_coords: tuple[int, ...] | slice, _data: zarr.Array) -> None:
            arr = await _data._async_array.getitem(chunk_coords)  # pyright: ignore[reportPrivateUsage]
            await _data._async_array.setitem(chunk_coords, arr / x2[chunk_coords])  # pyright: ignore[reportPrivateUsage]

        apply_op(x1, _add_array)

    return x1
