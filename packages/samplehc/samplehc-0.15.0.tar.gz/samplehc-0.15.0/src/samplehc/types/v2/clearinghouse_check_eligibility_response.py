# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ClearinghouseCheckEligibilityResponse"]


class ClearinghouseCheckEligibilityResponse(BaseModel):
    """
    Successfully checked eligibility, returns the eligibility details from the payer.
    """

    eligibility: Optional[object] = None
