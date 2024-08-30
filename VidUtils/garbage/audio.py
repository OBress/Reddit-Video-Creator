from gtts import gTTS

with open("ztesting/4.txt", 'r', encoding='utf8') as file:
    text = file.read()


# Language in which you want to convert
language = 'en'  # English

# Creating an instance of gTTS
tts = gTTS(text=text, lang=language, slow=False)

# Saving the converted audio in a mp3 file
tts.save("ztesting/4.wav")
