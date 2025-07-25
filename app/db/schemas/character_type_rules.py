from pydantic import BaseModel, Field
from typing import Literal, Optional


class Metadata(BaseModel):
    world_id: str
    type: Literal[
        "main_character", "side_character", "antagonist", "mythical_figure", "npc"
    ]
    name: str
    role: str
    faction: str
    alignment: Literal["heroic", "neutral", "villainous"]
    personality_traits: str  # chaîne unique, ex : "loyal, impulsive"
    race: str
    class_: str = Field(..., alias="class")  # `class` est un mot réservé
    language: Literal["en", "fr"]
    region: Optional[str] = None
    visible_in_game: Optional[bool] = True
    world: Optional[str] = None


class CharacterEntry(BaseModel):
    page_content: str
    metadata: Metadata
