import os
from pydub import AudioSegment
import subprocess
import re
from datetime import datetime, timedelta
from textgrid import TextGrid


class ForcedAligner:
    def __init__(self, language='english', max_length=12):
        self.language = language
        self.max_length = max_length
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    def break_into_phrases(self, words, max_length):
        phrases = []
        current_phrase = ""


        for word in words:
            if word == 'i':
                word = 'I'
            elif word == "i'm":
                word = "I'm"

            if (((len(current_phrase) + len(word)) > max_length) and current_phrase) or current_phrase.endswith(('.', '?', '!', ',', ':', ';', '¡', '¿', '»', '"', "'")):
                phrases.append(current_phrase.strip())
                current_phrase = ""
            current_phrase += " " + word

        if current_phrase:
            phrases.append(current_phrase.strip())

        return phrases
    
    def convert_mp3_to_wav(self, mp3_file, wav_file):
        """Convert an MP3 file to WAV format."""
        audio = AudioSegment.from_mp3(mp3_file)
        audio.export(wav_file, format="wav")
        os.remove(mp3_file)
    
    def convert_wav_to_mp3(self, wav_file, mp3_file):
        """Convert a WAV file to MP3 format."""
        audio = AudioSegment.from_wav(wav_file)
        audio.export(mp3_file, format="mp3")
        os.remove(wav_file)

    def run_mfa(self, corpus_dir, dictionary_path, model_path, output_dir):
        """Run MFA to align audio and transcript files."""
        
        os.makedirs(output_dir, exist_ok=True)

        subprocess.run([
            "mfa", "align", 
            "--single_speaker", 
            "--clean", 
            corpus_dir, 
            dictionary_path, 
            model_path, 
            output_dir,
            "--beam", "200",
        ])


    def convert_textgrid_to_srt(self, textgrid_file, srt_file):
        """Convert a TextGrid file to SRT format."""
        tg = TextGrid()
        tg.read(textgrid_file)

        with open(srt_file, 'w', encoding='utf8') as srt:
            for i, interval in enumerate(tg[0]):
                start = interval.minTime
                end = interval.maxTime
                text = interval.mark

                if text.strip():
                    srt.write(f"{i + 1}\n")
                    srt.write(f"{self.format_timestamp(start)} --> {self.format_timestamp(end)}\n")
                    srt.write(f"{text}\n\n")

    def parse_srt(srt_content):
        pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\s+(.+)\s')
        matches = pattern.findall(srt_content)
        return [(datetime.strptime(start, '%H:%M:%S,%f'), 
                datetime.strptime(end, '%H:%M:%S,%f'), text) for start, end, text in matches]

    def get_words(self, srt_file):
        srt = ""
        with open(srt_file, 'r', encoding='utf8', errors='ignore') as file:
            srt = file.read()
        srt = [chunk for chunk in srt.split('\n\n') if len(chunk.split('\n')) == 3]

        words = [word.split('\n')[2] for word in srt]

        return words


    def format_timestamp(self, time):
        """Format time in seconds to SRT timestamp format."""
        hours = int(time // 3600)
        minutes = int((time % 3600) // 60)
        seconds = int(time % 60)
        milliseconds = int((time - int(time)) * 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    def combine_srt_phrases(self, srt_file, phrases, bPhrases):
        """Combine words in the SRT file based on an array of phrases."""
        with open(srt_file, 'r', encoding='utf8') as file:
            srt = file.read().split('\n\n')

        split = ' --> '
        split_srt = [chunk.split('\n') for chunk in srt if chunk.strip()]
        # [(start, end), (word)]
        split_srt = [(chunk[1].split(split), str(chunk[2])) for chunk in split_srt]
        split_srt[0][0][0] = "00:00:00,000"
        output = []

        cutoff = 0
        # Index for phrases
        pIndex = 0
        # Index for aligner words
        p1 = 0
        p2 = 0
        while pIndex < len(phrases) and p2 <= len(split_srt):
            phrase = phrases[pIndex]

            start = split_srt[p1][0][0]
            if p1 == p2:
                end = split_srt[p2][0][1]
                if p2+1 < len(split_srt):
                    end = split_srt[p2+1][0][0]

            if p2 == len(split_srt):
                end = split_srt[-1][0][1]

                output.append(str(pIndex+1) + '\n')
                output.append(start + split + end + '\n')
                output.append(phrase + '\n')
                output.append('\n')
                break
            # print(split_srt[p2][1], end=' ')
            wordIndex = None
                
            
            if split_srt[p2][1].lower() in phrase[cutoff:].lower():
                wordIndex = phrase[cutoff:].lower().index(split_srt[p2][1].lower())
                cutoff = wordIndex + len(split_srt[p2][1])
                end = split_srt[p2][0][1]
                if p2+1 < len(split_srt):
                    end = split_srt[p2+1][0][0]
                
            
            else:
                try:
                    # if the next word is the start of the next phrase then must be a mis translation by MFA and should make end anyway
                    if pIndex+1 < len(phrases) and p2+1 < len(split_srt) and phrases[pIndex+1].lower().index(split_srt[p2+1][1]) < 2:
                        end = split_srt[p2+1][0][0]
                        p2 += 1
                except ValueError:
                    # Subtract one since the next word is the start of the next line
                    pass
                output.append(str(pIndex+1) + '\n')
                output.append(start + split + end + '\n')
                output.append(phrase + '\n')
                output.append('\n')

                cutoff = 0
                pIndex += 1
                p1 = p2
                p2 -= 1

            
            p2 += 1
            

        
        
        if end == split_srt[-1][0][1]:
            with open(srt_file, 'w', encoding='utf8') as file:
                file.writelines(output)

        elif bPhrases == 'broken':
            print("SUBITLTES ARE BROKEN FOR SOME REASON CAUSE THEY AIN'T LINING UP")
            exit()

        else:
            self.combine_srt_phrases(srt_file, bPhrases, 'broken')


    def align(self, corpus_dir, output_dir):
        """Convert MP3 to WAV, run MFA alignment, and convert TextGrid to SRT."""
        print("Creating text alignment for video...")
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Convert MP3 to WAV
        for file_name in os.listdir(corpus_dir):
            if file_name.endswith(".mp3"):
                mp3_file = os.path.join(corpus_dir, file_name)
                wav_file = os.path.join(corpus_dir, file_name.replace(".mp3", ".wav"))
                self.convert_mp3_to_wav(mp3_file, wav_file)

        # # Run MFA alignment
        self.run_mfa(corpus_dir, "english_us_arpa", "english_us_arpa", output_dir)


        # # Convert TextGrid to SRT
        for file_name in os.listdir(output_dir):
            if file_name.endswith(".TextGrid"):
                textgrid_file = os.path.join(output_dir, file_name)
                srt_file = os.path.join(output_dir, file_name.replace(".TextGrid", ".srt"))
                self.convert_textgrid_to_srt(textgrid_file, srt_file)
                os.remove(textgrid_file)

        # combine srt file into phrases
        for file_name in os.listdir(output_dir):
            if file_name.endswith(".srt"):
                name = file_name[:-4]
                with open(f"{corpus_dir}/{name}.txt", 'r', encoding='utf8') as file:
                    story = file.read()
                    words = story.split()
                # print(name)
                backup = self.get_words(output_dir+'/'+file_name)
                phrases = self.break_into_phrases(words, self.max_length)
                bPhrases = self.break_into_phrases(backup, self.max_length)

                self.combine_srt_phrases(output_dir+'/'+file_name, phrases, bPhrases)



if __name__ == "__main__":
    corpus_dir = "ztesting"  # Directory with MP3 and TXT files
    output_dir = corpus_dir # Directory for alignment results


    MFA = ForcedAligner()
    MFA.align(corpus_dir, output_dir)
