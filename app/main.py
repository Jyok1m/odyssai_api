from app.pipelines import (
    query_pipeline,
    world_creation_pipeline,
    world_context_building_pipeline,
    world_creation_graph,
    world_context_building_graph,
)

if __name__ == "__main__":

    def voice_query_from_db():
        result = query_pipeline.invoke(
            {
                "collection_name": "worlds",
                "n_results": 1,
                "search_type": "mmr",
                "credentials_path": "./secrets/google_tts.json",
                # "language_code": "fr-FR",
                # "voice_name": "fr-FR-Wavenet-D",
                "language_code": "en-US",
                "voice_name": "en-US-Wavenet-D",
            }
        )
        return result["speaker_file"]

    def build_world_and_context(world_name: str):
        world_creation_graph.invoke({"world_name": world_name})
        return f"World and context built for world {world_name}"

    def build_context(world_name: str):
        world_context_building_graph.invoke({"world_name": world_name})
        return f"Context built for world {world_name}"

    function_call = build_context("Elysia")
    print(function_call)
