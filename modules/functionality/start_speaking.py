import os
import time
import asyncio

import soundfile as sf
import numpy as np
import sounddevice as sd
from asyncio import AbstractEventLoop


class StartSpeaking:
    def __init__(
        self, 
        start_talking:asyncio.Event, 
        start_idle:asyncio.Event, 
        start_thinking:asyncio.Event, 
        loop:AbstractEventLoop
    ) -> None:
        
        self.file_path = "temp_output.mp3"
        self.start_talking = start_talking
        self.start_idle = start_idle
        self.start_thinking = start_thinking
        self.loop = loop

    async def update_state(self, talking:bool) -> None:
        if talking:
            self.start_talking.set()
            self.start_idle.clear()
        else:
            self.start_talking.clear()
            self.start_idle.set()

    def compute_rms(
        self,
        y: np.ndarray,  
        frame_size: int = 2048,  
        hop_length: int = 512,   
    ) -> np.ndarray:    
        
        """Compute Root Mean Square (RMS) energy of audio frames."""
        result =  np.array([
            np.sqrt(np.mean(y[i:i + frame_size] ** 2))
            for i in range(0, len(y) - frame_size, hop_length)
        ])

        return result

    def begin(self) -> None:
        y, sr = sf.read(self.file_path)
        if y.ndim > 1:
            y = np.mean(y, axis=1)  # stereo → mono

        rms = self.compute_rms(y, frame_size=2048, hop_length=512)
        frame_times = np.arange(len(rms)) * 512 / sr

        sd.play(y, sr)
        start_time = time.monotonic()
        silence_threshold = 0.01
        is_talking = False

        self.start_thinking.clear()

        while sd.get_stream().active:
            current_time = time.monotonic() - start_time
            current_frame = np.searchsorted(frame_times, current_time)

            voice_active = (
                current_frame < len(rms) and
                rms[current_frame] >= silence_threshold
            )

            if voice_active != is_talking:
                is_talking = voice_active
                asyncio.run_coroutine_threadsafe(
                    self.update_state(is_talking), self.loop
                )

            time.sleep(0.01)

