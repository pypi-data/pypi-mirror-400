# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List

from .._models import BaseModel

__all__ = ["V1QueryAuditLogsResponse"]


class V1QueryAuditLogsResponse(BaseModel):
    """
    A successful response containing a list of audit log entries that match the provided query.
    """

    data: List[Dict[str, object]]
    """An array of audit log records matching the query."""
