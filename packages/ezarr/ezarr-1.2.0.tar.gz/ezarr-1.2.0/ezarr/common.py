from collections.abc import Awaitable
from typing import Any, Literal
from collections.abc import Callable

import numpy as np
import numpy.typing as npt
import zarr.codecs
import zarr.core.config
from zarr.codecs import VLenUTF8Codec
from zarr.core.array import (
    DEFAULT_FILL_VALUE,
    CompressorsLike,
    FiltersLike,
    ShardsLike,
    _parse_keep_array_attr,  # pyright: ignore[reportPrivateUsage]
    init_array,
)
from zarr.core.array_spec import ArrayConfig
from zarr.core.common import JSON, concurrent_map
from zarr.core.dtype import VariableLengthUTF8, ZDType, ZDTypeLike, parse_dtype
from zarr.core.sync import sync
from zarr.errors import ContainsArrayError
from zarr.storage import StoreLike  # pyright: ignore[reportUnknownVariableType]
from zarr.storage._common import make_store_path  # pyright: ignore[reportUnknownVariableType]

from ezarr.errors import InplaceCastingError


def find_1d(arr: zarr.Array, value: Any) -> int | None:
    assert arr.ndim == 1
    w = np.argwhere(np.array(arr) == value)

    if not w.size:
        return None

    return w[0, 0]


async def _from_array(arr: zarr.Array, dtype: ZDType[np.dtype[np.generic], np.generic]):
    mode: Literal["a"] = "a"
    config = ArrayConfig.from_dict({})
    store_path = await make_store_path(arr.store, path=arr.basename, mode=mode, storage_options=None)

    (
        chunks,
        shards,
        filters,
        compressors,
        serializer,
        fill_value,
        order,
        zarr_format,
        chunk_key_encoding,
        dimension_names,
    ) = _parse_keep_array_attr(
        data=arr,
        chunks="keep",
        shards="keep",
        filters="keep",
        compressors="keep",
        serializer="keep",
        fill_value=DEFAULT_FILL_VALUE,
        order=None,
        zarr_format=None,
        chunk_key_encoding=None,
        dimension_names=None,
    )

    result = await init_array(
        store_path=store_path,
        shape=arr.shape,
        dtype=dtype,
        chunks=chunks,
        shards=shards,
        filters=filters,
        compressors=compressors,
        serializer=serializer,
        fill_value=fill_value,
        order=order,
        zarr_format=zarr_format,
        attributes=None,
        chunk_key_encoding=chunk_key_encoding,
        dimension_names=dimension_names,
        overwrite=True,
        config=config,
    )

    async def _copy_array_region(chunk_coords: tuple[int, ...] | slice, _data: zarr.Array) -> None:
        arr = await _data._async_array.getitem(chunk_coords)  # pyright: ignore[reportPrivateUsage]
        await result.setitem(chunk_coords, np.array(arr)[()].astype(dtype.to_native_dtype()))

    # Stream data from the source array to the new array
    await concurrent_map(
        [(region, arr) for region in result._iter_shard_regions()],  # pyright: ignore[reportPrivateUsage]
        _copy_array_region,
        zarr.core.config.config.get("async.concurrency"),
    )

    return result


def cast_array(
    arr: zarr.Array, dtype: ZDTypeLike, casting: Literal["no", "equiv", "safe", "same_kind", "unsafe"]
) -> zarr.Array:
    if arr.dtype == dtype or dtype is None:
        return arr

    zdtype = parse_dtype(dtype, zarr_format=arr.metadata.zarr_format)
    if not np.can_cast(arr.dtype, zdtype.to_native_dtype(), casting):
        raise InplaceCastingError(
            f"Could not cast zarr.Array to type '{zdtype.to_native_dtype()}' according to casting rule '{casting}'"
        )

    return zarr.Array(sync(_from_array(arr, zdtype)))  # pyright: ignore[reportArgumentType]


def write_array(
    arr: zarr.Array | npt.NDArray[np.generic],
    store: StoreLike,
    *,
    name: str,
    dtype: npt.DTypeLike = None,
    casting: Literal["no", "equiv", "safe", "same_kind", "unsafe"] = "same_kind",
    chunks: tuple[int, ...] | Literal["auto"] = "auto",
    shards: ShardsLike | None = None,
    filters: FiltersLike = "auto",
    compressors: CompressorsLike = "auto",
    attributes: dict[str, JSON] | None = None,
    overwrite: bool = False,
) -> zarr.Array:
    """
    Write an array to a store while infering the correct dtype.

    Args:
        store: StoreLike
        arr: array to write
        dtype:
        overwrite: overwrite array if it exists (default: False)
    """
    if isinstance(arr, zarr.Array) and arr.store is store and arr.basename == name:
        if not overwrite:
            raise ContainsArrayError(f"An array already exists in store {store} at path '{name}'")

        arr = cast_array(arr, dtype, casting)

        if attributes is not None:
            arr.attrs.put(attributes)

        return arr

    # NOTE: for now, F-style ordering is not handled
    arr = np.ascontiguousarray(arr)

    if dtype is not None:
        arr = arr.astype(dtype, casting=casting)

    if arr.dtype == object:
        if arr.size:
            arr = arr.astype(type(arr.flat[0]))

        if arr.dtype == object:
            raise TypeError(f'Failed interpreting the "Object" data type to a non ambiguous data type for array {arr}')

    if np.issubdtype(arr.dtype, np.str_):
        z_arr = zarr.create_array(
            store,
            name=str(name),
            shape=arr.shape,
            dtype=VariableLengthUTF8(),
            serializer=VLenUTF8Codec(),
            chunks=chunks,
            shards=shards,
            filters=filters,
            compressors=compressors,
            overwrite=overwrite,
            attributes=attributes,
        )
        z_arr[:] = arr
        return z_arr

    return zarr.create_array(
        store,
        name=str(name),
        data=arr,
        chunks=chunks,
        shards=shards,
        filters=filters,
        compressors=compressors,
        overwrite=overwrite,
        attributes=attributes,
    )


async def _concurrent_apply_op(arr: zarr.Array, op: Callable[..., Awaitable[Any]]) -> None:
    await concurrent_map(
        [(region, arr) for region in arr._iter_shard_regions()],  # pyright: ignore[reportPrivateUsage]
        op,
        zarr.core.config.config.get("async.concurrency"),
    )


def apply_op(arr: zarr.Array, op: Callable[..., Awaitable[Any]]) -> None:
    sync(_concurrent_apply_op(arr, op))
