from collections.abc import Iterable
from types import EllipsisType
from typing import SupportsIndex

from numpy._typing import _ArrayLikeInt_co  # pyright: ignore[reportPrivateUsage]

type ONE_AXIS_SELECTOR = int | bool | SupportsIndex
type PARTIAL_SELECTOR = None | EllipsisType | slice | range | Iterable[int] | Iterable[bool] | _ArrayLikeInt_co
type SELECTOR = ONE_AXIS_SELECTOR | PARTIAL_SELECTOR
