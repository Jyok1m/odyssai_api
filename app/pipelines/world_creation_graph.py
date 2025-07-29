from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from typing import TypedDict, Any
from app.pipelines import (
    world_builder_pipeline,
    lore_builder_pipeline,
    event_builder_pipeline,
    character_builder_pipeline,
)


class ContextState(TypedDict, total=False):
    world_name: str
    world_id: str
    world_context: str
    lore_context: str
    event_context: str
    character_context: str
    llm_json: Any
    document_list: Any


def log_step(step_name: str) -> RunnableLambda:
    return RunnableLambda(lambda x: print(f"LangGraph Step => {step_name}") or x)


builder = StateGraph(state_schema=ContextState)

# Node 1 log_world
builder.add_node("log_world", log_step("World"))

# Node 2 world to create the world
builder.add_node("world", world_builder_pipeline)

# Point d'entrée
builder.set_entry_point("log_world")

# Point de sortie et enchainement de neoud
builder.add_edge("log_world", "world")

# Boucle sur les passes
n_passes = 3
last_node = "world"

for i in range(1, n_passes + 1):
    for step in ["lore", "event", "character"]:
        log_node = f"log_{step}_{i}"
        step_node = f"{step}_{i}"

        # On ajoute les nodes
        builder.add_node(log_node, log_step(f"{step.capitalize()} Pass {i}"))
        builder.add_node(
            step_node,
            {
                "lore": lore_builder_pipeline,
                "event": event_builder_pipeline,
                "character": character_builder_pipeline,
            }[step],
        )

        # On connecte les points d'arrêt
        builder.add_edge(last_node, log_node)
        builder.add_edge(log_node, step_node)
        last_node = step_node

builder.add_edge(last_node, END)

# Compile
world_creation_graph = builder.compile()
