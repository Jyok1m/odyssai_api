from app.pipelines import query_pipeline, lore_pipeline

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
            result = lore_pipeline.invoke({
                "collection_name": "lores",
                "world_name": "Elyseïa",
                "n_lores": 1
            })            
            return result
        
    result = invoke_pipeline("setup")
    print(result)