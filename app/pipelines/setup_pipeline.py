import os
from langchain_core.runnables import RunnableLambda
from app.modules import PromptManager
from app.db import ChromaManager
from uuid import uuid4

def generate_lore(_, **kwargs):
    data = _
    world_uid = str(uuid4())
    prompt = PromptManager()
    generated_response = prompt.initiate_lore(
        world_id=world_uid,
        world_name=data["world_name"],
        n=data["n_lores"]
    )
    data["world_uid"] = world_uid
    data["lore_response"] = generated_response
    return data

setup_pipeline = (
    RunnableLambda(generate_lore)
)