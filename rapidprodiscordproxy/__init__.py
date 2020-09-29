"""This encapsulates the logic for the rapidpro discord proxy, which
enables communication with discord (which uses long-lived websockets) and
rapidpro's courier, which uses http REST"""
from typing import List, Optional
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel

__version__ = "0.0.1"


class RapidProMessage(BaseModel):
    """This is the pydantic model which represents messages that courier will send."""

    id: str
    text: str
    to: int
    # from_: Optional[int] = Field(alias="from")
    channel: UUID
    attachments: Optional[List[AnyHttpUrl]]
    quick_replies: List[str]
