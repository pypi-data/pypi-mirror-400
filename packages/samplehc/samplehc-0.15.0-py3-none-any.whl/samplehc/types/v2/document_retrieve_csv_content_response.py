# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List

from ..._models import BaseModel

__all__ = ["DocumentRetrieveCsvContentResponse"]


class DocumentRetrieveCsvContentResponse(BaseModel):
    """Successfully retrieved CSV content."""

    data: List[Dict[str, str]]
    """An array of objects, where each object represents a row from the CSV."""
