import os
from app.modules.utils import Recorder, Transcriber, Speaker
from app.db.chroma_db import ChromaManager


def query_by_voice(collection_name="test_collection", n_results=1, search_type="mmr"):
    """
    This function handles voice queries.
    It processes the voice input and returns the corresponding response.
    """
    # Initialize the recorder
    recorder = Recorder()

    # Start recording upon user input
    input("Press Enter to start recording...")
    recorder.start()

    # Stop recording upon user input
    input("Press Enter to stop recording...")
    audio_path = recorder.stop()

    # TODO: Add language detection

    # Transcribe the recorded audio
    transcriber = Transcriber()
    transcription = transcriber.get_transcription(audio_path)

    # Remove the audio file after transcription
    os.remove(audio_path)

    # Use the transcription to query the database
    chroma_manager = ChromaManager()
    queried_docs = chroma_manager.query_documents(
        collection_name=collection_name,
        query=transcription,
        n_results=n_results,
        search_type=search_type
    )
    query_response = queried_docs[0].page_content

    # Process the queried documents with TTS
    speaker = Speaker(language_code="fr-FR")
    speaker_file = speaker.synthesize(text=query_response)
    
    return speaker_file

query_by_voice()