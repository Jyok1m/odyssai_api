#type: ignore

import json5
from langchain_core.documents import Document
from app.db import ChromaManager, LoreEntry, WorldEntry

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
            validated_json.append(pydantic_entry)
        except Exception as e:
            print(f"Entry {obj} is invalid: {e}")
            continue

    data["llm_json"] = validated_json
    return data

def convert_json_array_to_documents(_, **kwargs):
    data = _

    converted_docs = []
    for obj in data["llm_json"]:
        converted_docs.append(
            Document(
                page_content=obj.page_content,
                metadata=obj.metadata.dict()
            )
        )

    data["document_list"] = converted_docs
    return data

def save_documents_to_chroma(_, **kwargs):
    data = _

    collection_name = kwargs["collection_name"]

    chroma_manager = ChromaManager()
    chroma_manager.add_documents(
        collection_name=collection_name,
        documents=data["document_list"]
    )
    
    print(f"{len(data["document_list"])} documents have been saved to collection: {collection_name}")

    data.pop("llm_json")
    data.pop("document_list")
    
    # Final pipeline output :
    # world_id, world_name
    return data