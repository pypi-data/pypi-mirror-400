# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel
from .exif_response import ExifResponse

__all__ = ["ExifEventPayload"]


class ExifEventPayload(BaseModel):
    """Event payload for exif entities."""

    data: ExifResponse
    """Full exif data"""

    entity_type: Optional[Literal["exif"]] = None
