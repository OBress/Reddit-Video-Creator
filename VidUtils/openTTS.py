import openai
import os
from pydub import AudioSegment
from pydub.effects import normalize
import numpy as np
from scipy.io import wavfile

class openTTS:
    def __init__(self, key):
        self.ssml_limit = 3000
        openai.api_key = key

    def createAudio(self, text, output_folder, gender='M', file_name='speech.wav'):
        voice_id = 'echo'
        # if gender == 'F':
        #     voice_id = 'shimmer'

        # Split the text to comply with Polly's limits
        segments = self._split_text(text)

        # Temporary storage for audio segments
        combined = AudioSegment.empty()
        
        for i, segment in enumerate(segments):
            print(f"Creating Audio Segment ({i+1}/{len(segments)}))")


            try:
                # Process and concatenate the audio segment
                segment_file_name = f'temp_segment_{i}.mp3'

                response = openai.audio.speech.create(
                    model="tts-1-hd",
                    voice=voice_id,
                    input=segment,
                    speed=1
                )
                # Save the audio to a file
                response.stream_to_file(segment_file_name)

                segment_sound = AudioSegment.from_mp3(segment_file_name)
                combined += segment_sound

                # Add 0.5 seconds of silence after the title is read
                if i == 0:
                    silence = AudioSegment.silent(duration=300)
                    combined += silence

                # Remove temporary segment file
                os.remove(segment_file_name)

            except Exception as e:
                print(f"An error occurred while processing segment {i}: {e}")

        # Final audio adjustments and export
        try:
            # louder_combined = combined + 5  # Increase volume
            final_file_path = os.path.join(output_folder, file_name)
            combined += AudioSegment.silent(duration=700)
            combined.export(final_file_path, format='wav')

            audio = AudioSegment.from_wav(final_file_path)

            speed_up_rate = 1.1  # 10% increase
            audio = audio.speedup(playback_speed=speed_up_rate)

            audio = normalize(audio)

            # Apply a high-pass filter to reduce low-frequency noise
            audio = audio.high_pass_filter(80)

            speed_up_rate = 1.1  # 10% increase

            # increased_volume = audio.speedup(playback_speed=speed_up_rate)
            audio.export(final_file_path, format="wav")

            print(f"Speech saved to {final_file_path}")
        except Exception as e:
            print(f"An error occurred while saving the final audio: {e}")

        return final_file_path
    
    
    def _split_text(self, text):
        """Splits text into segments that fit within Polly's SSML limit."""
        title, body = text.split('\n\n\n\n')

        if title.endswith('.') or title.endswith('!') or title.endswith('?'):
            title = title[:-1]
        
        words = body.split()
        segments = []
        current_segment = []

        for word in words:
            # Check if adding the next word would exceed the limit
            if len(' '.join(current_segment + [word]).encode('utf-8')) < self.ssml_limit:
                current_segment.append(word)
            else:
                # Current segment is full, add it to the segments list
                segments.append(' '.join(current_segment))
                current_segment = [word]  # Start a new segment

        # Add the last segment if it has content
        if current_segment:
            segments.append(' '.join(current_segment))

        segments.insert(0, title)
        
        return segments
