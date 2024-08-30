import boto3
import os
from pydub import AudioSegment

class AWSTTS:
    def __init__(self):
        self.polly_client = boto3.client('polly')
        self.ssml_limit = 3000

    def createAudio(self, text, output_folder, gender='M', file_name='speech.wav', wpm=160):
        voice_id = 'Matthew'
        if gender == 'F':
            voice_id = 'Joanna'

        # Split the text to comply with Polly's limits
        segments = self._split_text(text)

        # Temporary storage for audio segments
        combined = AudioSegment.empty()
        
        for i, segment in enumerate(segments):
            print(f"Creating Audio Segment ({i+1}/{len(segments)}))")
            # Calculate the speaking rate percentage
            rate_percent = self._calculate_speaking_rate_percent(wpm)

            # Convert the segment to SSML format with the specified speaking rate
            ssml_text = f"<speak><prosody rate='{rate_percent}%'>{segment.strip()}</prosody></speak>"

            try:
                # Convert text segment to speech using SSML
                response = self.polly_client.synthesize_speech(
                    Text=ssml_text,
                    TextType='ssml',
                    OutputFormat='mp3',
                    VoiceId=voice_id,
                    Engine='neural'
                )

                # Process and concatenate the audio segment
                segment_file_name = f'temp_segment_{i}.mp3'
                with open(segment_file_name, 'wb') as segment_file:
                    segment_file.write(response['AudioStream'].read())
                
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
            increased_volume = audio + 9
            increased_volume.export(final_file_path, format="wav")

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

    def _calculate_speaking_rate_percent(self, wpm):
        default_wpm = 135
        rate_percent = (wpm / default_wpm) * 100
        return int(rate_percent)