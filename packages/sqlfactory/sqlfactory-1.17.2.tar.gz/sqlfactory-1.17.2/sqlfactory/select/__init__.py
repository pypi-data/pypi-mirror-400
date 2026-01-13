# noqa: A005  # shadows built-in select
"""SELECT statement builder."""

from sqlfactory.mixins.join import CrossJoin, InnerJoin, Join, LeftJoin, LeftOuterJoin, RightJoin, RightOuterJoin
from sqlfactory.select.aliased import Aliased, SelectColumn
from sqlfactory.select.column_list import ColumnList
from sqlfactory.select.cte import With
from sqlfactory.select.select import SELECT, Select
from sqlfactory.select.union import (
    EXCEPT,
    EXCEPT_ALL,
    EXCEPT_DISTINCT,
    INTERSECT,
    INTERSECT_ALL,
    INTERSECT_DISTINCT,
    UNION,
    UNION_ALL,
    UNION_DISTINCT,
    Except,
    ExceptAll,
    ExceptDistinct,
    Intersect,
    IntersectAll,
    IntersectDistinct,
    Union,
    UnionAll,
    UnionDistinct,
)

__all__ = [
    "EXCEPT",
    "EXCEPT_ALL",
    "EXCEPT_DISTINCT",
    "INTERSECT",
    "INTERSECT_ALL",
    "INTERSECT_DISTINCT",
    "SELECT",
    "UNION",
    "UNION_ALL",
    "UNION_DISTINCT",
    "Aliased",
    "ColumnList",
    "CrossJoin",
    "Except",
    "ExceptAll",
    "ExceptDistinct",
    "InnerJoin",
    "Intersect",
    "IntersectAll",
    "IntersectDistinct",
    "Join",
    "LeftJoin",
    "LeftOuterJoin",
    "RightJoin",
    "RightOuterJoin",
    "Select",
    "SelectColumn",
    "Union",
    "UnionAll",
    "UnionDistinct",
    "With",
]
