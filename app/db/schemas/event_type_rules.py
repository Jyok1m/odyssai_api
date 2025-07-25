from pydantic import BaseModel
from typing import Literal, Optional


class Metadata(BaseModel):
    world_id: str
    type: Literal["timeline_event"]
    title: str
    date: str
    location: str
    scope: str
    impact: str
    theme: str
    language: Literal["en", "fr"]
    visible_in_game: Optional[bool] = True
    world: Optional[str] = None

    # class Config:
    #     extra = "forbid"


class EventEntry(BaseModel):
    page_content: str
    metadata: Metadata
