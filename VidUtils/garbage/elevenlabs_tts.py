from elevenlabs import set_api_key, generate, voices, save
import os


class ElevenlabsTTS:
    def __init__(self, env):
        self.env = env
        set_api_key(env['ELEVENLABS_API_KEY'])
        self.voices = voices()
        self.Paola = self.findVoice(self.voices, "Paola")
        self.Arthur = self.findVoice(self.voices, "Arthur")

    def findVoice(self, voices, name):
        for voice in voices:
            if voice.name == name:
                return voice
        return None

    def createAudio(self, text, gender, filePrefix, language="english", key="", voice=None):
        if voice is not None:
            voice = self.findVoice(self.voices, voice)
        else:
            voice = self.Paola
            if gender == "M":
                voice = self.Arthur

        audio = generate(
            text, voice=voice, model="eleven_monolingual_v1")
        fileName = os.path.join('tts-audio-files', f'{language}-{filePrefix}.mp3')

        save(audio, fileName)
        return fileName
