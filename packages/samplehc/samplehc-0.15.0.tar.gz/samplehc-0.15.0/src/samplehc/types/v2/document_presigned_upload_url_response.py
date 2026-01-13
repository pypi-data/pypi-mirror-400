# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DocumentPresignedUploadURLResponse"]


class DocumentPresignedUploadURLResponse(BaseModel):
    """Successfully generated presigned URL and initial document metadata."""

    id: str

    file_name: str = FieldInfo(alias="fileName")

    presigned_url: str = FieldInfo(alias="presignedUrl")
