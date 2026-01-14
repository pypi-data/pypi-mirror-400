# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import Annotated, TypeAlias

from .._utils import PropertyInfo
from .._models import BaseModel
from .exif_event_payload import ExifEventPayload
from .face_event_payload import FaceEventPayload
from .album_event_payload import AlbumEventPayload
from .asset_event_payload import AssetEventPayload
from .person_event_payload import PersonEventPayload
from .album_asset_event_payload import AlbumAssetEventPayload

__all__ = ["EventsResponse", "Data"]

Data: TypeAlias = Annotated[
    Union[
        AssetEventPayload,
        AlbumEventPayload,
        PersonEventPayload,
        FaceEventPayload,
        AlbumAssetEventPayload,
        ExifEventPayload,
    ],
    PropertyInfo(discriminator="entity_type"),
]


class EventsResponse(BaseModel):
    """Response containing events."""

    data: List[Data]
    """
    List of events, ordered by entity type priority, then updated_at, then entity_id
    """
