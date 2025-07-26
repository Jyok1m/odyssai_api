#type: ignore

from uuid import uuid4
from langchain_core.runnables import RunnableLambda
from app.modules import PromptManager
from app.pipelines import validate_json, convert_json_array_to_documents, save_documents_to_chroma

# ------------------------------------------------------------------ #
#                         Generate the world                         #
# ------------------------------------------------------------------ #

def generate_world(_, **kwargs):
    data = _
    
    prompt = PromptManager()
    data["world_id"] = str(uuid4())

    llm_json = prompt.initiate_world(
        world_id=data["world_id"],
        world_name=data["world_name"],
    )

    data["llm_json"] = llm_json

    # Data output properties : world_name, world_id, llm_json
    return data

# ---------------------------- PIPELINE ---------------------------- #

world_builder_pipeline = (
    RunnableLambda(generate_world)
    .pipe(RunnableLambda(lambda x: validate_json(x, step="lore")))
    .pipe(RunnableLambda(convert_json_array_to_documents))
    .pipe(RunnableLambda(lambda x: save_documents_to_chroma(x, collection_name="worlds")))
)