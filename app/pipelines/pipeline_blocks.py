# type: ignore

import json5
from langchain_core.documents import Document
from app.db import ChromaManager
from app.modules import PromptManager
from app.db import ChromaManager, LoreEntry, WorldEntry, EventEntry, CharacterEntry
from uuid import uuid4

# ------------------------------------------------------------------ #
#                     Retrieve full world context                    #
# ------------------------------------------------------------------ #


def retrieve_world_context(_, **kwargs):
    data = _

    step_type = kwargs["step"]

    chroma_manager = ChromaManager()

    # -------------------------- World context ------------------------- #

    world_search = chroma_manager.query_context_by_similarity(
        world_name=data["world_name"], collection_name="worlds", step_type=step_type
    )

    if not world_search:
        data["world_context"] = ""
        data["world_id"] = str(uuid4())
    else:
        data["world_context"] = world_search["context"]
        data["world_id"] = world_search["world_id"]

    # -------------------------- Lore context -------------------------- #

    lore_search = chroma_manager.query_context_by_similarity(
        world_name=data["world_name"], collection_name="lores", step_type=step_type
    )

    if not lore_search:
        data["lore_context"] = ""
    else:
        data["lore_context"] = lore_search["context"]

    # -------------------------- Event context ------------------------- #

    event_search = chroma_manager.query_context_by_similarity(
        world_name=data["world_name"], collection_name="events", step_type=step_type
    )

    if not event_search:
        data["event_context"] = ""
    else:
        data["event_context"] = event_search["context"]

    # ------------------------ Character context ----------------------- #

    character_search = chroma_manager.query_context_by_similarity(
        world_name=data["world_name"], collection_name="characters", step_type=step_type
    )

    if not character_search:
        data["character_context"] = ""
    else:
        data["character_context"] = character_search["context"]

    return data


# ------------------------------------------------------------------ #
#            LLM-generate JSON documents based on context            #
# ------------------------------------------------------------------ #


def generate_new_entries(_, **kwargs):
    data = _

    step_type = kwargs["step"]
    n_entries = kwargs["n_entries"]

    prompt = PromptManager()

    llm_json = prompt.initiate_build(
        world_id=data["world_id"],
        world_name=data["world_name"],
        step_type=step_type,
        n=n_entries,
        world_context=data["world_context"],
        lore_context=data["lore_context"],
        event_context=data["event_context"],
        character_context=data["character_context"],
    )

    data["llm_json"] = llm_json
    return data


# ------------------------------------------------------------------ #
#                      Validate the json format                      #
# ------------------------------------------------------------------ #


def validate_json(_, **kwargs):
    data = _

    raw_json = data["llm_json"]
    parsed_json = json5.loads(raw_json)

    if not isinstance(parsed_json, list):
        raise TypeError(f"The format must be a list of JSON objects.")

    step = kwargs["step"]

    validated_json = []
    for obj in parsed_json:
        try:
            if step == "world":
                pydantic_entry = WorldEntry(**obj)
            elif step == "lore":
                pydantic_entry = LoreEntry(**obj)
            elif step == "event":
                pydantic_entry = EventEntry(**obj)
            elif step == "character":
                pydantic_entry = CharacterEntry(**obj)
            validated_json.append(pydantic_entry)
        except Exception as e:
            print(f"Entry {obj} is invalid: {e}")
            continue

    data["llm_json"] = validated_json
    return data


# ------------------------------------------------------------------ #
#                         Convert to Document                        #
# ------------------------------------------------------------------ #


def convert_json_array_to_documents(_, **kwargs):
    data = _

    converted_docs = []
    for obj in data["llm_json"]:
        converted_docs.append(
            Document(page_content=obj.page_content, metadata=obj.metadata.dict())
        )

    data["document_list"] = converted_docs
    return data


# ------------------------------------------------------------------ #
#                      Save documents to Chroma                      #
# ------------------------------------------------------------------ #


def save_documents_to_chroma(_, **kwargs):
    data = _

    collection_name = kwargs["collection_name"]

    chroma_manager = ChromaManager()
    chroma_manager.add_documents(
        collection_name=collection_name, documents=data["document_list"]
    )

    print(
        f"{len(data["document_list"])} documents have been saved to collection: {collection_name}"
    )

    data.pop("llm_json")
    data.pop("document_list")

    # Final pipeline output :
    # world_id, world_name
    return data
