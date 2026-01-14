# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from .._models import BaseModel

__all__ = ["AlbumAssetResponse"]


class AlbumAssetResponse(BaseModel):
    """Represents a link between an album and an asset."""

    id: str
    """Unique album*asset identifier with 'album_asset*' prefix"""

    album_id: str
    """ID of the album"""

    asset_id: str
    """ID of the asset"""

    created_at: datetime
    """When this link was created"""

    updated_at: datetime
    """When this link was last updated"""
