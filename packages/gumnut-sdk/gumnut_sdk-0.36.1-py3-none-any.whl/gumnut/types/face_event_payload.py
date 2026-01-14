# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel
from .face_response import FaceResponse

__all__ = ["FaceEventPayload"]


class FaceEventPayload(BaseModel):
    """Event payload for face entities."""

    data: FaceResponse
    """Full face data"""

    entity_type: Optional[Literal["face"]] = None
