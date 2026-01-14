import numpy as np
import pandas as pd

from ezarr.dataframe import EZDataFrame


def test_can_replace_column(ezdf: EZDataFrame) -> None:
    ezdf["col_int"] = [-1, -2, -3]
    assert ezdf["col_int"].equals(pd.Series([-1, -2, -3]))


def test_can_set_column_from_series(ezdf: EZDataFrame) -> None:
    ezdf["new_col"] = pd.Series([-1, -2, -3])
    assert np.array_equal(ezdf.columns, ["col_int", "col_str", "col_float", "new_col"])
