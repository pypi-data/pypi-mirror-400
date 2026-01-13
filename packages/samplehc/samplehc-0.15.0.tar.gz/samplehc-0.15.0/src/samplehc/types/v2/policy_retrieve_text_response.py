# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["PolicyRetrieveTextResponse"]


class PolicyRetrieveTextResponse(BaseModel):
    """Successfully retrieved policy text"""

    text: str
    """Raw text content of the policy document"""
