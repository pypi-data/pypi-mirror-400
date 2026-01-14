# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel
from .album_response import AlbumResponse

__all__ = ["AlbumEventPayload"]


class AlbumEventPayload(BaseModel):
    """Event payload for album entities."""

    data: AlbumResponse
    """Full album data"""

    entity_type: Optional[Literal["album"]] = None
