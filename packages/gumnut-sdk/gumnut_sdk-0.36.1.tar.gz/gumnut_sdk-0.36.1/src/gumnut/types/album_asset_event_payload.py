# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel
from .album_asset_response import AlbumAssetResponse

__all__ = ["AlbumAssetEventPayload"]


class AlbumAssetEventPayload(BaseModel):
    """Event payload for album_asset entities."""

    data: AlbumAssetResponse
    """Full album_asset data"""

    entity_type: Optional[Literal["album_asset"]] = None
