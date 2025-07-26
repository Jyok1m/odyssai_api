from app.pipelines import (
    query_pipeline,
    world_builder_pipeline,
    lore_builder_pipeline,
    event_builder_pipeline,
)

if __name__ == "__main__":

    def invoke_pipeline(pipeline_type: str, world_name: str):
        if pipeline_type == "query":
            result = query_pipeline.invoke(
                {
                    "collection_name": "test_collection",
                    "n_results": 1,
                    "search_type": "mmr",
                    "credentials_path": "./secrets/google_tts.json",
                    "language_code": "fr-FR",
                    "voice_name": "fr-FR-Wavenet-D",
                }
            )
            return result["speaker_file"]
        elif pipeline_type == "world":
            result = world_builder_pipeline.invoke({"world_name": world_name})
            return "Done"
        elif pipeline_type == "lore":
            result = lore_builder_pipeline.invoke({"world_name": world_name})
            return "Done"
        elif pipeline_type == "event":
            result = event_builder_pipeline.invoke({"world_name": world_name})
            return "Done"

    # result = invoke_pipeline("world", "Elyseïa")
    # result = invoke_pipeline("lore", "Elyseïa")
    result = invoke_pipeline("event", "Elyseïa")
    print(result)
