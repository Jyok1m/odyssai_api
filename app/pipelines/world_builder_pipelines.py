from langchain_core.runnables import RunnableLambda
from app.pipelines import (
    retrieve_world_context,
    generate_new_entries,
    validate_json,
    convert_json_array_to_documents,
    save_documents_to_chroma,
)

# ------------------------------------------------------------------ #
#                           World pipeline                           #
# ------------------------------------------------------------------ #

world_builder_pipeline = (
    RunnableLambda(lambda x: retrieve_world_context(x, step="world"))
    .pipe(RunnableLambda(lambda x: generate_new_entries(x, step="world", n_entries=1)))
    .pipe(RunnableLambda(lambda x: validate_json(x, step="world")))
    .pipe(RunnableLambda(convert_json_array_to_documents))
    .pipe(
        RunnableLambda(lambda x: save_documents_to_chroma(x, collection_name="worlds"))
    )
)

# ------------------------------------------------------------------ #
#                            Lore pipeline                           #
# ------------------------------------------------------------------ #

lore_builder_pipeline = (
    RunnableLambda(lambda x: retrieve_world_context(x, step="lore"))
    .pipe(RunnableLambda(lambda x: generate_new_entries(x, step="lore", n_entries=3)))
    .pipe(RunnableLambda(lambda x: validate_json(x, step="lore")))
    .pipe(RunnableLambda(convert_json_array_to_documents))
    .pipe(
        RunnableLambda(lambda x: save_documents_to_chroma(x, collection_name="lores"))
    )
)

# ------------------------------------------------------------------ #
#                           Event pipeline                           #
# ------------------------------------------------------------------ #

event_builder_pipeline = (
    RunnableLambda(lambda x: retrieve_world_context(x, step="lore"))
    .pipe(RunnableLambda(lambda x: generate_new_entries(x, step="event", n_entries=3)))
    .pipe(RunnableLambda(lambda x: validate_json(x, step="event")))
    .pipe(RunnableLambda(convert_json_array_to_documents))
    .pipe(
        RunnableLambda(lambda x: save_documents_to_chroma(x, collection_name="events"))
    )
)

# ------------------------------------------------------------------ #
#                         Character pipeline                         #
# ------------------------------------------------------------------ #

character_builder_pipeline = (
    RunnableLambda(lambda x: retrieve_world_context(x, step="character"))
    .pipe(RunnableLambda(lambda x: generate_new_entries(x, step="character", n_entries=3)))
    .pipe(RunnableLambda(lambda x: validate_json(x, step="character")))
    .pipe(RunnableLambda(convert_json_array_to_documents))
    .pipe(
        RunnableLambda(lambda x: save_documents_to_chroma(x, collection_name="characters"))
    )
)
