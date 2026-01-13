# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["MessageGetAttachmentResponse"]


class MessageGetAttachmentResponse(BaseModel):
    """Attachment retrieved successfully as a document resource."""

    id: str

    file_name: str = FieldInfo(alias="fileName")
