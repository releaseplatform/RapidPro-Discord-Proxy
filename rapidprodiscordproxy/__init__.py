__version__ = "0.0.1"

from pydantic import BaseModel
from uuid import UUID


class RapidProMessage(BaseModel):
    id: str
    text: str
    to: int
    # from_: Optional[int] = Field(alias="from")
    channel: UUID
