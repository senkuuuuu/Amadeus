import time
import os
import traceback
import speech_recognition as sr
from queue import Queue

class VoiceToText:
    def __init__(self) -> None:
        self.result_queue = Queue()
    
    def begin(self) -> None:
        try:
            time.sleep(0.2)
            recognizer = sr.Recognizer()

            audio_path = "temp_input.wav"
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file '{audio_path}' not found.")

            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)

            text = recognizer.recognize_google(audio_data, language="en-US")

            print(text)
            return text

        except Exception as e:
            print("Error:", e)
            traceback.print_exc()
            return 'Hows the Time machine going?'

    