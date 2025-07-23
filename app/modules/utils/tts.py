import os
from google.cloud import texttospeech
from uuid import uuid4


class Speaker:
    """
    Utility class to convert text to speech using Google Cloud Text-to-Speech.
    """

    def __init__(
        self, credentials_path="./secrets/google_tts.json", language_code="fr-FR", voice_name="fr-FR-Wavenet-D"
    ):
        """
        Initializes the Speaker with the specified language code and voice name.
        Defaults to French (France) and a specific Wavenet voice.
        credentials_path defaults to '../../secrets/google_tts.json'.
        """
        if language_code not in ["fr-FR", "en-US"]:
            raise ValueError("Supported languages are: 'fr-FR', 'en-US'.")
        if not voice_name:
            raise ValueError("Voice name cannot be empty.")
        if not os.path.isfile(credentials_path):
            raise FileNotFoundError(
                f"The credentials file {credentials_path} does not exist."
            )
        else:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        self.__client = texttospeech.TextToSpeechClient()
        self.language_code = language_code
        self.voice_name = voice_name
        self.output_path = None

    def synthesize(self, text: str, save_folder="./tmp"):
        """
        Converts the given text to speech and saves it to the specified output file.
        Defauklt save folder is './tmp'.
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string.")

        synthesis_input = texttospeech.SynthesisInput(text=text)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        voice = texttospeech.VoiceSelectionParams(
            language_code=self.language_code, name=self.voice_name
        )
        synthesized_result = self.__client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        if not synthesized_result.audio_content:
            raise RuntimeError(
                "Failed to synthesize speech. No audio content returned."
            )

        self.output_path = f"{save_folder}/{uuid4()}.mp3"
        with open(self.output_path, "wb") as out:
            out.write(synthesized_result.audio_content)

        return self.output_path


# Example usage:
def text_to_speech(
    text: str,
    language_code="fr-FR",
    voice_name="fr-FR-Wavenet-D",
):
    speaker = Speaker(language_code, voice_name)
    output_file = speaker.synthesize(text)
    return output_file


# print(
#     text_to_speech("Ceci est un test !", "../../secrets/google_tts.json")
# )
