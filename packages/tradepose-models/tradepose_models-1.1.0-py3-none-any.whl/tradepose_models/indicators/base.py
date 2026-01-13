"""
Base utilities for indicator models

Provides Polars Expr field handling for strategy models.
"""

import json
from io import StringIO
from typing import Union

import polars as pl


class PolarsExprField:
    """自定義 Polars Expr 字段處理"""

    @staticmethod
    def serialize(expr: pl.Expr) -> dict:
        """序列化 Polars Expr 為 dict（與服務器格式一致）

        Python Polars 1.33+ 的 expr.meta.serialize() 已輸出與 Rust Polars 0.51 兼容的格式：
        - Window variant (not Over)
        - options: {"Over": "GroupsToRows"} (correct WindowType format)
        """
        json_str = expr.meta.serialize(format="json")
        return json.loads(json_str)

    @staticmethod
    def deserialize(data: Union[str, dict, pl.Expr]) -> pl.Expr:
        """反序列化為 Polars Expr"""
        if isinstance(data, pl.Expr):
            # 已經是 Expr 對象
            return data
        elif isinstance(data, dict):
            # API 返回的 dict（優先處理）
            json_str = json.dumps(data)
            return pl.Expr.deserialize(StringIO(json_str), format="json")
        elif isinstance(data, str):
            # JSON 字符串（向後兼容）
            return pl.Expr.deserialize(StringIO(data), format="json")
        else:
            raise ValueError(f"無法反序列化類型: {type(data)}")
