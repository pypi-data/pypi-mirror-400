# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypedDict

__all__ = ["TaskUpdateColumnParams"]


class TaskUpdateColumnParams(TypedDict, total=False):
    key: Required[str]
    """The column key to update or insert."""

    value: Required[Union[str, float, bool, None]]
    """The value to set for the column."""

    type: Literal["string", "number", "boolean", "date", "datetime"]
    """The semantic type of the column. Defaults to string when omitted."""
