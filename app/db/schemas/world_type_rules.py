from pydantic import BaseModel
from typing import Literal, Optional


class Metadata(BaseModel):
    world_id: str
    type: Literal["world"]
    name: str
    genre: str
    technology_level: str
    dominant_species: str
    governance: str
    magic_presence: bool
    language: Literal["en", "fr"]
    visible_in_game: Optional[bool] = True

    class Config:
        extra = "forbid"


class WorldEntry(BaseModel):
    page_content: str
    metadata: Metadata
