import os
from langchain_core.runnables import RunnableLambda
from app.modules import Recorder, Transcriber, Speaker
from app.db import ChromaManager


def record_voice(data, **kwargs):
    config = data
    recorder = Recorder()
    input("Press Enter to start recording...")
    recorder.start()
    input("Press Enter to stop recording...")
    audio_path = recorder.stop()
    config["audio_path"] = audio_path
    return config


def transcribe_audio(data, **kwargs):
    config = data
    transcriber = Transcriber(lang=config["language_code"][:2])
    transcription = transcriber.get_transcription(config["audio_path"])
    config["transcription_to_query"] = transcription
    return config


def remove_tmp_file(data, **kwargs):
    config = data
    os.remove(config["audio_path"])
    config.pop("audio_path")
    return config


def query_documents(data, **kwargs):
    config = data
    chroma_manager = ChromaManager()
    results = chroma_manager.query_documents(
        collection_name=config["collection_name"],
        query=config["transcription_to_query"],
        n_results=config["n_results"],
        search_type=config["search_type"],
    )
    config["queried_texts"] = " ".join([doc.page_content for doc in results])
    return config


def voice_act_response(data, **kwargs):
    config = data
    speaker = Speaker(
        credentials_path=config["credentials_path"],
        language_code=config["language_code"],
        voice_name=config["voice_name"],
    )
    speaker_file = speaker.synthesize(text=config["queried_texts"])
    config["speaker_file"] = speaker_file
    config.pop("queried_texts")
    return config


query_pipeline = (
    RunnableLambda(record_voice)
    .pipe(RunnableLambda(transcribe_audio))
    .pipe(RunnableLambda(remove_tmp_file))
    .pipe(RunnableLambda(query_documents))
    .pipe(RunnableLambda(voice_act_response))
)
