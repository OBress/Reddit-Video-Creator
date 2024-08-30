import os
import torch
from TTS.api import TTS
from pydub import AudioSegment

class cusTTS:
    def __init__(self):
        self.ssml_limit = 1500

    def createAudio(self, text, gender='M', file_name='speech.mp3', wpm=175):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        
        output_path = f"tts-audio-files/{file_name}.mp3"
        print(f"Creating Audio For {file_name}")
        tts.tts_to_file(text=text, language="en", speaker="Dionisio Schuyler", file_path=output_path)
        print(f"Audio saved to {output_path}")
        
        return output_path
    def _split_text(self, text):
        """Splits text into segments that fit within Polly's SSML limit."""
        words = text.split()
        segments = []
        current_segment = []

        for word in words:
            if len(' '.join(current_segment + [word]).encode('utf-8')) < self.ssml_limit:
                current_segment.append(word)
            else:
                segments.append(' '.join(current_segment))
                current_segment = [word]

        if current_segment:
            segments.append(' '.join(current_segment))

        return segments
