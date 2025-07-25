import json5
from langchain_core.runnables import RunnableLambda
from langchain_core.documents import Document
from uuid import uuid4
from app.modules import PromptManager
from app.db import ChromaManager, LoreEntry

def get_existing_lore_context(_, **kwargs):
    data = _
    chroma_manager = ChromaManager()
    result = chroma_manager.query_by_world(
        world=data["world_name"],
        collection_name=data["collection_name"]
    )

    if not result:
        data["world_id"] = str(uuid4())
        data["pre_existing_context"] = ""
    else:
        data["world_id"] = result["world_id"]
        data["pre_existing_context"] = result["context"]

    return data

def generate_lore(_, **kwargs):
    data = _
    prompt = PromptManager()
    generated_response = prompt.initiate_lore(
        world_id=data["world_id"],
        world_name=data["world_name"],
        n=data["n_lores"],
        pre_existing_context=data["pre_existing_context"]
    )
    data["lore_response"] = generated_response
    return data

def verify_json_format(_, **kwargs):
    data = _
    raw = data["lore_response"]
    parsed_json = json5.loads(raw)

    if not isinstance(parsed_json, list):
        raise TypeError("Expected list of JSON objects.")

    validated = []
    for i, item in enumerate(parsed_json):
        try:
            entry = LoreEntry(**item) # type: ignore
            validated.append(entry)
        except:
            print(f"Entry {i} is invalid.")
            continue
    
    data["lore_response"] = validated
    return data

def convert_json_to_langchain_document(_, **kwargs):
    data = _
    documents_list = []

    for doc in data["lore_response"]:
        document = Document(
            page_content=doc.page_content,
            metadata=doc.metadata.dict()
        )
        documents_list.append(document)

    data["documents_list"] = documents_list
    return data

def upload_documents_to_db(_, **kwargs):
    data = _
    chroma_manager = ChromaManager()
    chroma_manager.add_documents(
        collection_name=data["collection_name"], 
        documents=data["documents_list"]
    )
    return f"{len(data["documents_list"])} documents added to collection {data["collection_name"]}."


lore_pipeline = (
    RunnableLambda(get_existing_lore_context)
    .pipe(RunnableLambda(generate_lore))
    .pipe(RunnableLambda(verify_json_format))
    .pipe(RunnableLambda(convert_json_to_langchain_document))
    .pipe(RunnableLambda(upload_documents_to_db))
)