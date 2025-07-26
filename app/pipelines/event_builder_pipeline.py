from langchain_core.runnables import RunnableLambda
from app.modules import PromptManager
from app.db import ChromaManager
from app.pipelines import (
    validate_json,
    convert_json_array_to_documents,
    save_documents_to_chroma,
)

# ------------------------------------------------------------------ #
#                        Retrieve the contexts                       #
# ------------------------------------------------------------------ #


def get_contexts(_, **kwargs):
    data = _
    chroma_manager = ChromaManager()

    world_search = chroma_manager.query_context_by_similarity(
        world_name=data["world_name"], collection_name="worlds"
    )

    data["world_id"] = world_search["world_id"]

    if not world_search:
        data["world_context"] = ""
    else:
        data["world_context"] = world_search["context"]

    lore_search = chroma_manager.query_context_by_similarity(
        world_name=data["world_name"], collection_name="lores"
    )

    if not lore_search:
        data["lore_context"] = ""
    else:
        data["lore_context"] = lore_search["context"]

    event_search = chroma_manager.query_context_by_similarity(
        world_name=data["world_name"], collection_name="events"
    )

    if not event_search:
        data["event_context"] = ""
    else:
        data["event_context"] = event_search["context"]

    return data


# ------------------------------------------------------------------ #
#                         Generate the events                        #
# ------------------------------------------------------------------ #


def generate_events(_, **kwargs):
    data = _
    prompt = PromptManager()

    llm_json = prompt.initiate_events(
        world_id=data["world_id"],
        world_name=data["world_name"],
        world_context=data["world_context"],
        lore_context=data["lore_context"],
        event_context=data["event_context"],
        n=5,
    )

    data["llm_json"] = llm_json
    return data


# ---------------------------- PIPELINE ---------------------------- #

event_builder_pipeline = (
    RunnableLambda(get_contexts)
    .pipe(RunnableLambda(generate_events))
    .pipe(RunnableLambda(lambda x: validate_json(x, step="event")))
    .pipe(RunnableLambda(convert_json_array_to_documents))
    .pipe(
        RunnableLambda(lambda x: save_documents_to_chroma(x, collection_name="events"))
    )
)
