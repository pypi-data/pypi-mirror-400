# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["PatientSearchParams"]


class PatientSearchParams(TypedDict, total=False):
    reqdelete: Annotated[str, PropertyInfo(alias="REQDELETE")]
    """Delete flag (Y/N)"""

    reqdispin: Annotated[str, PropertyInfo(alias="REQDISPIN")]
    """Disposition filter"""

    reqlvl6_in: Annotated[str, PropertyInfo(alias="REQLVL6IN")]
    """Facility ID"""

    reqnamein: Annotated[str, PropertyInfo(alias="REQNAMEIN")]
    """Patient name to search"""

    reqnonprosp: Annotated[str, PropertyInfo(alias="REQNONPROSP")]
    """Non-prospect flag (Y/N)"""

    reqprosp: Annotated[str, PropertyInfo(alias="REQPROSP")]
    """Prospect flag (Y/N)"""

    reqsortin: Annotated[str, PropertyInfo(alias="REQSORTIN")]
    """Sort field"""
