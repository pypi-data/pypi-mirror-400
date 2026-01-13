# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DocumentCombineResponse", "Document"]


class Document(BaseModel):
    """Metadata of the newly created combined PDF document."""

    id: str

    file_name: str = FieldInfo(alias="fileName")


class DocumentCombineResponse(BaseModel):
    """Successfully combined documents into a single PDF."""

    document: Document
    """Metadata of the newly created combined PDF document."""
