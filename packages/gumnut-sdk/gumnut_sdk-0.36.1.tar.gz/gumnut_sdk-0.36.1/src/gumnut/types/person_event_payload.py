# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel
from .person_response import PersonResponse

__all__ = ["PersonEventPayload"]


class PersonEventPayload(BaseModel):
    """Event payload for person entities."""

    data: PersonResponse
    """Full person data"""

    entity_type: Optional[Literal["person"]] = None
