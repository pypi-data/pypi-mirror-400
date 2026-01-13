# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DocumentGenerateCsvResponse", "Document"]


class Document(BaseModel):
    """Metadata of the newly generated CSV document."""

    id: str

    file_name: str = FieldInfo(alias="fileName")


class DocumentGenerateCsvResponse(BaseModel):
    """CSV document generated successfully."""

    document: Document
    """Metadata of the newly generated CSV document."""
