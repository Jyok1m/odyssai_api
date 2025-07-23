import os
import sounddevice as sd
import numpy as np
from pathlib import Path
from scipy.io.wavfile import write
from uuid import uuid4


class Recorder:
    """
    Class to handle audio recording using sounddevice.
    """

    def __init__(self):
        self.__samplerate = 44100  # Utilisation par défaut de 44100 Hz en fréq
        self.__channels = 1  # mono channel
        self.__dtype = "int16"  # Format d'échantillonnage 16 bits
        self.__recording = []
        self.__stream = None
        self.is_recording = False
        self.output_path = None

    def _callback(self, indata, frames, time, status):
        """
        Callback function to process audio input.
        """
        self.__recording.append(indata.copy())  # Copy to avoid overwriting

    def start(self):
        """
        Start recording audio.
        """
        if self.is_recording:
            raise RuntimeError("Enregistrement déjà en cours.")

        # Remove existing file if any
        for file in Path("./tmp").glob("*.wav"):
            file.unlink()

        for file in Path("./tmp").glob("*.mp3"):
            file.unlink()

        self.__recording = []
        self.__stream = sd.InputStream(
            samplerate=self.__samplerate,
            channels=self.__channels,
            dtype=self.__dtype,
            callback=self._callback,
            blocksize=0,  # optimal pour éviter les saccades
        )
        self.__stream.start()
        self.is_recording = True
        print("Recording started...")

    def stop(self, save_folder="./tmp"):
        """
        Stop recording audio and save to a file.
        Default save folder is './tmp'.
        """
        if not self.is_recording or not self.__stream:
            raise RuntimeError("Recording is not active or stream is not initialized.")

        self.__stream.stop()
        self.__stream.close()
        self.is_recording = False
        print("Recording stopped.")

        # Write the recorded audio to a file
        print("Saving recorded audio...")

        audio_data = np.concatenate(self.__recording, axis=0)
        
        self.output_path = f"{save_folder}/{uuid4()}.wav"
        write(self.output_path, self.__samplerate, audio_data)

        print(f"File successfully saved: {self.output_path}")
        return self.output_path


if __name__ == "__main__":
    rec = Recorder()
    input("Press Enter to start recording...")
    rec.start()

    input("Press Enter to stop recording...")
    rec.stop()
