# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel
from .asset_response import AssetResponse

__all__ = ["AssetEventPayload"]


class AssetEventPayload(BaseModel):
    """Event payload for asset entities."""

    data: AssetResponse
    """Full asset data"""

    entity_type: Optional[Literal["asset"]] = None
