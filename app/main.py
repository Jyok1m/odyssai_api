from api.app.pipelines.main_pipeline import main_pipeline

if __name__ == "__main__":
    result = main_pipeline.invoke({
        "collection_name": "test_collection",
        "n_results": 1,
        "search_type": "mmr",
        "credentials_path": "./secrets/google_tts.json",
        "language_code": "fr-FR",
        "voice_name": "fr-FR-Wavenet-D"
    })


    print("Final file :", result["speaker_file"])