__version__ = "0.0.1"

from pydantic import BaseModel, Field


class RapidProMessage(BaseModel):
    id: str
    text: str
    to: int
    from_: int = Field(alias="from")
    channel: str
