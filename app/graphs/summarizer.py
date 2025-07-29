from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableLambda, RunnableMap
from typing_extensions import TypedDict

from app.graphs.helpers import log_graph_step
from app.pipelines import retrieve_world_context
from app.modules import PromptManager, Speaker
from app.db import ChromaManager


class State(TypedDict):
    world_name: str
    world_id: str
    world_context: str
    lore_context: str
    event_context: str
    character_context: str
    summary_text: str
    audio_path: str


builder = StateGraph(state_schema=State)


def fetch_contexts(state: State) -> State:
    chroma = ChromaManager()
    bundle = chroma.query_all_contexts(state["world_name"])
    return {**state, **bundle}  # type: ignore


def generate_summary(state: State) -> State:
    summarizer = PromptManager()
    summary = summarizer.generate_narrative_summary_prompt(
        world_name=state["world_name"],
        world_context=state["world_context"],
        lore_context=state["lore_context"],
        event_context=state["event_context"],
        character_context=state["character_context"],
        lang="English",
    )
    return {**state, "summary_text": summary}  # type: ignore


def generate_audio(state: State) -> State:
    speaker = Speaker(
        credentials_path="./secrets/google_tts.json",
        language_code="en-US",
        voice_name="en-US-Wavenet-D",
    )
    audio_path = speaker.synthesize(text=state["summary_text"], save_folder="./tmp")
    return {**state, "audio_path": audio_path}  # type: ignore


# ------------------------ Graph constructor ----------------------- #

builder.add_node("fetch_contexts", RunnableLambda(fetch_contexts))
builder.add_node("generate_summary", RunnableLambda(generate_summary))
builder.add_node("generate_audio", RunnableLambda(generate_audio))

builder.set_entry_point("fetch_contexts")
builder.add_edge("fetch_contexts", "generate_summary")
builder.add_edge("generate_summary", "generate_audio")
builder.add_edge("generate_audio", END)

summarizer_graph = builder.compile()
