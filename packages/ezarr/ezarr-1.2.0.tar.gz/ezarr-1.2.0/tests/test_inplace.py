import zarr
import numpy as np

import ezarr.inplace as ezi


def test_delete():
    array = zarr.create_array({}, data=np.array([[1, 2, 3], [4, 5, 6]]))
    assert np.array_equal(np.array(ezi.delete(array, 1, axis=1)), np.array([[1, 3], [4, 6]]))


def test_insert():
    array = zarr.create_array({}, data=np.array([[1, 2, 3], [4, 5, 6]]))
    assert np.array_equal(np.array(ezi.insert(array, 1, [7, 8], axis=1)), np.array([[1, 7, 2, 3], [4, 8, 5, 6]]))


def test_add():
    array = zarr.create_array({}, data=np.array([[1, 2, 3], [4, 5, 6]]))
    ezi.add(array, 1)

    assert np.array_equal(np.array(array), np.array([[2, 3, 4], [5, 6, 7]]))
