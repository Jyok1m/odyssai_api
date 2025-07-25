from app.pipelines import query_pipeline, setup_pipeline

if __name__ == "__main__":
    def invoke_pipeline(pipeline_type: str):
        if pipeline_type == "query":
            result = query_pipeline.invoke({
                "collection_name": "test_collection",
                "n_results": 1,
                "search_type": "mmr",
                "credentials_path": "./secrets/google_tts.json",
                "language_code": "fr-FR",
                "voice_name": "fr-FR-Wavenet-D"
            })
            return result["speaker_file"]
        elif pipeline_type == "setup":
            result = setup_pipeline.invoke({
                "world_name": "Elyseïa",
                "n_lores": 1
            })
            return result
        
    invoke_result = invoke_pipeline("setup")
    print(invoke_result)