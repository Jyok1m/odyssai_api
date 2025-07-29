from langchain_core.runnables import RunnableLambda
from app.pipelines import (
    world_builder_pipeline,
    lore_builder_pipeline,
    event_builder_pipeline,
    character_builder_pipeline,
)

world_creation_pipeline = (
    RunnableLambda(lambda x: world_builder_pipeline.invoke(x))
    .pipe(lore_builder_pipeline)
    .pipe(event_builder_pipeline)
    .pipe(character_builder_pipeline)
    .pipe(lore_builder_pipeline)
    .pipe(event_builder_pipeline)
    .pipe(character_builder_pipeline)
    .pipe(lore_builder_pipeline)
    .pipe(event_builder_pipeline)
    .pipe(character_builder_pipeline)
)

world_context_building_pipeline = (
    RunnableLambda(lambda x: lore_builder_pipeline.invoke(x))
    .pipe(event_builder_pipeline)
    .pipe(character_builder_pipeline)
    .pipe(lore_builder_pipeline)
    .pipe(event_builder_pipeline)
    .pipe(character_builder_pipeline)
    .pipe(lore_builder_pipeline)
    .pipe(event_builder_pipeline)
    .pipe(character_builder_pipeline)
)
