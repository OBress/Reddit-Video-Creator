from aeneas.executetask import ExecuteTask
from aeneas.task import Task
from aeneas.task import TaskConfiguration
import tempfile
import os

class ForcedAligner:
    def __init__(self, language='english', max_length=10):
        self.language = language
        self.max_length = max_length

    def align(self, audio_file, text_string, subtitles_file):
        print("Starting Alignment")
        # Break the text string into phrases
        phrases = self.break_into_phrases(text_string, self.max_length)
        
        # Convert relative file paths to absolute
        audio_file = os.path.abspath(audio_file)
        subtitles_file = os.path.abspath(subtitles_file)

        # Create a temporary text file and write the phrases into it
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt', encoding='utf-8') as text_file:
            for phrase in phrases:
                text_file.write(phrase + "\n")
            text_path = text_file.name

        # Determine the language code based on the provided language
        language_code = self.get_language_code(self.language)

        # Configure the task for Aeneas
        print("Aeneas Starting Alignment")
        config_string = u"task_language=" + language_code + \
            "|is_text_type=plain|os_task_file_format=srt"
        task = Task(config_string=config_string)
        task.audio_file_path_absolute = audio_file
        task.text_file_path_absolute = text_path
        task.sync_map_file_path_absolute = subtitles_file

        # Execute the alignment task
        try:
            ExecuteTask(task).execute()
        except Exception as e:
            print(f"Error executing Aeneas task: {e}")

        task.output_sync_map_file()
        print("Aeneas Alignment Finished\n")
        os.remove(text_path)

        return subtitles_file

    def break_into_phrases(self, text, max_length):
        phrases = []
        words = text.split()
        current_phrase = ""

        for word in words:
            if (((len(current_phrase) + len(word)) > max_length) and current_phrase) or current_phrase.endswith(('.', '?', '!', ',', ':', ';', '¡', '¿', '»')):
                phrases.append(current_phrase.strip())
                current_phrase = ""
            current_phrase += " " + word

        if current_phrase:
            phrases.append(current_phrase.strip())

        return phrases

    def get_language_code(self, language):
        language_map = {
            "english": "en",
            "spanish": "es",
            "french": "fr",
            "italian": "it",
            "german": "de",
            "portuguese": "pt",
            "polish": "pl",
            "hindi": "hi"
        }
        return language_map.get(language, "en")
