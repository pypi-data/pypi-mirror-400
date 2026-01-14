from ezarr.indexing.base import Indexer, as_indexer, boolean_array_as_indexer
from ezarr.indexing.list import ListIndex
from ezarr.indexing.selection import Selection, get_indexer
from ezarr.indexing.single import SingleIndex
from ezarr.indexing.slice import FullSlice, map_slice
from ezarr.indexing.special import EmptyList, NewAxis, NewAxisType

type LengthedIndexer = ListIndex | FullSlice | EmptyList

__all__ = [
    "Indexer",
    "Selection",
    "get_indexer",
    "boolean_array_as_indexer",
    "map_slice",
    "FullSlice",
    "ListIndex",
    "SingleIndex",
    "NewAxis",
    "NewAxisType",
    "as_indexer",
    "EmptyList",
]
