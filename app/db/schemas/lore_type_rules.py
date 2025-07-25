from pydantic import BaseModel
from typing import Literal, Optional

class Metadata(BaseModel):
    world_id: str
    type: Literal["origin_myth", "magic_system", "religion", "prophecy", "timeline_event"]
    title: str
    theme: str
    importance: Literal["major", "minor", "local"]
    keyword: str
    language: Literal["en", "fr"]
    region: Optional[str] = None
    visible_in_game: Optional[bool] = True
    world: Optional[str] = None

class LoreEntry(BaseModel):
    page_content: str
    metadata: Metadata