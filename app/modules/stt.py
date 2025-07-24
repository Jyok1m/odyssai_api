import os
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser
from langchain_community.document_loaders.generic import GenericLoader
from dotenv import load_dotenv, find_dotenv

# Load env variables
load_dotenv(find_dotenv())


class Transcriber:
    """
    Utility class to transcribe audio files using OpenAI's Whisper model.
    I am using the langchain_community library for this purpose for compatibility.
    """

    def __init__(self, lang="fr", model_name="whisper-1"):
        """
        Initializes the Transcriber with the specified Whisper model.
        Defaults to "whisper-1".
        """
        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("Missing OPENAI_API_KEY environment variable.")

        self.__parser = OpenAIWhisperParser(
            api_key=os.getenv("OPENAI_API_KEY"),
            chunk_duration_threshold=0.7,  # Disregard audio chunks shorter than 0.7 seconds
            language=lang,  # Specify the language of the audio
            response_format="text",
            temperature=0.0,
            model=model_name,
        )

    def get_transcription(self, audio_file_path: str):
        """
        Transcribes the audio file at the specified path.
        Returns the transcription as a string.
        """
        if not os.path.isfile(audio_file_path):
            raise FileNotFoundError(f"The file {audio_file_path} does not exist.")

        if not audio_file_path.lower().endswith((".mp3", ".wav", ".m4a")):
            raise ValueError("Supported formats are: .mp3, .wav, .m4a.")

        # Create a GenericLoader to load the audio file
        loader = GenericLoader.from_filesystem(
            path=audio_file_path,
            suffixes=[".mp3", ".wav", ".m4a"],
            show_progress=True,
            parser=self.__parser,
        )

        documents = loader.load()

        if not documents:
            raise ValueError("No documents were loaded from the audio file.")

        transcription = " ".join(doc.page_content for doc in documents)
        return transcription


# Example usage:
def transcribe_audio(file_path: str, lang="fr"):
    transcriber = Transcriber(lang=lang)
    transcription = transcriber.get_transcription(file_path)
    return transcription


# print(transcribe_audio("../../data/audio/test_whisper_2.m4a", lang="fr"))
